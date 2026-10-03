from __future__ import annotations

import logging
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from pydantic import BaseModel, Field

from app.application.services.admin_service import AdminService
from app.application.services.content_service import ContentService
from app.application.services.outbox_service import OutboxService
from app.application.services.role_service import RoleService
from app.application.services.user_service import UserService
from app.core.config import Settings
from app.core.container import Container
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from app.core.logging import configure_logging, request_id_var
from app.core.rate_limit import SlidingWindowGate
from app.domain.entities import ChatIdentity, ScheduledJobInput, UserIdentity
from app.domain.enums import ChatType, TaskKind
from app.infrastructure.repositories.admin import AdminRepository
from app.infrastructure.repositories.content import ContentRepository
from app.infrastructure.repositories.users import UserRepository
from app.web.session import SessionSigner
from app.web.telegram_auth import validate_init_data

logger = logging.getLogger("platform.web")
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


class AuthRequest(BaseModel):
    init_data: str = Field(min_length=1, max_length=10_000)


class ContentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=50_000)


class ScheduledMessageRequest(BaseModel):
    chat_id: int
    text: str = Field(min_length=1, max_length=4096)
    run_at: datetime
    parse_mode: str | None = Field(default=None, max_length=32)


class ScheduledContentRequest(BaseModel):
    content_id: int
    run_at: datetime
    target_chat_id: int | None = None


def _ensure_future(run_at: datetime) -> datetime:
    if run_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="run_at must include a timezone")
    value = run_at.astimezone(timezone.utc)
    if value <= datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="run_at must be in the future")
    return value


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()
    if resolved.app_secret_key is None:
        if resolved.is_production:
            raise RuntimeError("APP_SECRET_KEY is required in production")
        session_secret = secrets.token_urlsafe(32)
    else:
        session_secret = resolved.app_secret_key.get_secret_value()
    signer = SessionSigner(session_secret, resolved.session_max_age_seconds)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(resolved.log_level, resolved.log_json)
        container = Container.build(resolved)
        app.state.container = container
        try:
            yield
        finally:
            await container.shutdown()

    app = FastAPI(title=resolved.app_name, version="1.0.0", lifespan=lifespan)
    api_gate = SlidingWindowGate(
        max_entries=50_000,
        requests=resolved.rate_limit_requests,
        window_seconds=resolved.rate_limit_window_seconds,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved.cors_allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def api_rate_limit(request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith("/health/"):
            return await call_next(request)
        client_host = request.client.host if request.client else "unknown"
        if not api_gate.allow(hash(client_host)):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        return await call_next(request)

    @app.middleware("http")
    async def request_context(request: Request, call_next: RequestResponseEndpoint) -> Response:
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_var.set(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_var.reset(token)

    def get_container(request: Request) -> Container:
        container = getattr(request.app.state, "container", None)
        if container is None:
            raise HTTPException(status_code=503, detail="Application is not ready")
        return container

    async def session_user(
        session_token: Annotated[str | None, Cookie(alias=resolved.session_cookie_name)] = None,
    ) -> int:
        if not session_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        try:
            return signer.verify(session_token)
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def ready(container: Container = Depends(get_container)) -> dict[str, str]:
        if not await container.database.ping():
            raise HTTPException(status_code=503, detail="database unavailable")
        return {"status": "ready"}

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")

    @app.get("/static/app.js", include_in_schema=False)
    async def javascript() -> FileResponse:
        return FileResponse(FRONTEND / "app.js", media_type="text/javascript")

    @app.get("/static/style.css", include_in_schema=False)
    async def stylesheet() -> FileResponse:
        return FileResponse(FRONTEND / "style.css", media_type="text/css")

    @app.post("/api/auth/telegram")
    async def auth(request_body: AuthRequest, response: Response, container: Container = Depends(get_container)) -> dict[str, object]:
        token = resolved.require_bot_token()
        try:
            user = validate_init_data(request_body.init_data, token, resolved.session_max_age_seconds)
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        async with container.database.session_factory() as session:
            await UserService(session, resolved.default_locale).touch_user_and_chat(
                UserIdentity(
                    telegram_id=user.telegram_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code,
                    is_bot=False,
                ),
                ChatIdentity(
                    telegram_id=user.telegram_id,
                    chat_type=ChatType.PRIVATE,
                    title=None,
                    username=None,
                ),
            )

        response.set_cookie(
            key=resolved.session_cookie_name,
            value=signer.issue(user.telegram_id),
            max_age=resolved.session_max_age_seconds,
            httponly=True,
            secure=resolved.session_cookie_secure,
            samesite="lax",
            path="/",
        )
        return {"ok": True, "user": {"id": user.telegram_id, "name": user.first_name, "username": user.username}}

    @app.post("/api/auth/logout")
    async def logout(response: Response) -> dict[str, bool]:
        response.delete_cookie(resolved.session_cookie_name, path="/")
        return {"ok": True}

    @app.get("/api/me")
    async def me(
        telegram_id: int = Depends(session_user), container: Container = Depends(get_container)
    ) -> dict[str, object]:
        async with container.database.session_factory() as session:
            user = await UserRepository(session).get_by_telegram_id(telegram_id)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            roles = await RoleService(session).list_roles(telegram_id)
            role_values = {role.value for role in roles}
            is_admin = (
                telegram_id in set(resolved.admin_user_ids)
                or await AdminRepository(session).is_active_admin(telegram_id)
                or bool(role_values & {"admin", "owner"})
            )
            return {
                "id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "is_admin": is_admin,
                "roles": [role.value for role in roles],
            }

    @app.get("/api/content")
    async def content(
        _: int = Depends(session_user), container: Container = Depends(get_container)
    ) -> dict[str, object]:
        async with container.database.session_factory() as session:
            return {"items": await ContentService(session).list_published()}

    @app.post("/api/content", status_code=201)
    async def create_content(
        payload: ContentCreateRequest,
        telegram_id: int = Depends(session_user),
        container: Container = Depends(get_container),
    ) -> dict[str, int]:
        async with container.database.session_factory() as session:
            service = AdminService(session, resolved.admin_user_ids)
            try:
                await service.ensure_admin(telegram_id)
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc
            content_id = await ContentService(session).create(payload.title, payload.body, telegram_id)
            return {"id": content_id}

    @app.post("/api/content/{content_id}/publish")
    async def publish_content(
        content_id: int,
        telegram_id: int = Depends(session_user),
        container: Container = Depends(get_container),
    ) -> dict[str, bool]:
        async with container.database.session_factory() as session:
            try:
                await AdminService(session, resolved.admin_user_ids).ensure_admin(telegram_id)
                await ContentService(session).publish(content_id, telegram_id)
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc
            except NotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            return {"ok": True}

    @app.get("/api/admin/summary")
    async def admin_summary(
        telegram_id: int = Depends(session_user), container: Container = Depends(get_container)
    ) -> dict[str, int]:
        async with container.database.session_factory() as session:
            try:
                return await AdminService(session, resolved.admin_user_ids).summary(telegram_id)
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc

    @app.post("/api/admin/schedule-message", status_code=201)
    async def schedule_message(
        payload: ScheduledMessageRequest,
        telegram_id: int = Depends(session_user),
        container: Container = Depends(get_container),
    ) -> dict[str, int]:
        async with container.database.session_factory() as session:
            try:
                await AdminService(session, resolved.admin_user_ids).ensure_admin(telegram_id)
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc
            job_id = await OutboxService(session).enqueue_job(
                ScheduledJobInput(
                    kind=TaskKind.SEND_MESSAGE,
                    run_at=_ensure_future(payload.run_at),
                    payload={"chat_id": payload.chat_id, "text": payload.text, "parse_mode": payload.parse_mode},
                )
            )
            return {"id": job_id}

    @app.post("/api/admin/schedule-content", status_code=201)
    async def schedule_content(
        payload: ScheduledContentRequest,
        telegram_id: int = Depends(session_user),
        container: Container = Depends(get_container),
    ) -> dict[str, int]:
        async with container.database.session_factory() as session:
            try:
                await AdminService(session, resolved.admin_user_ids).ensure_admin(telegram_id)
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc
            if await ContentRepository(session).get(payload.content_id) is None:
                raise HTTPException(status_code=404, detail="Content not found")
            job_id = await OutboxService(session).enqueue_job(
                ScheduledJobInput(
                    kind=TaskKind.PUBLISH_CONTENT,
                    run_at=_ensure_future(payload.run_at),
                    payload={
                        "content_id": payload.content_id,
                        "target_chat_id": payload.target_chat_id,
                        "actor_id": telegram_id,
                    },
                )
            )
            return {"id": job_id}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    settings = Settings()
    uvicorn.run(
        app,
        host=settings.web_host,
        port=settings.web_port,
        proxy_headers=True,
        server_header=False,
    )
