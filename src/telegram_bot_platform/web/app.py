from __future__ import annotations

import logging
import secrets
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from starlette.middleware.base import RequestResponseEndpoint

from telegram_bot_platform.application.services.admin_service import AdminService
from telegram_bot_platform.application.services.bot_service import BotProfileService
from telegram_bot_platform.application.services.content_service import ContentService
from telegram_bot_platform.application.services.localization_service import LocalizationService
from telegram_bot_platform.application.services.outbox_service import OutboxService
from telegram_bot_platform.application.services.role_service import RoleService
from telegram_bot_platform.application.services.settings_service import SettingsService
from telegram_bot_platform.application.services.user_service import UserService
from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.core.container import Container
from telegram_bot_platform.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from telegram_bot_platform.core.logging import configure_logging, request_id_var
from telegram_bot_platform.core.module_catalog import catalog_dict as module_catalog
from telegram_bot_platform.core.rate_limit import SlidingWindowGate
from telegram_bot_platform.core.settings_catalog import catalog_dict as setting_catalog
from telegram_bot_platform.domain.entities import ChatIdentity, ScheduledJobInput, UserIdentity
from telegram_bot_platform.domain.enums import ChatType, ContentStatus, MatchMode, TaskKind, UserRole
from telegram_bot_platform.infrastructure.db.models import AutoReplyRuleModel, ScheduledJobModel
from telegram_bot_platform.infrastructure.repositories.admin import AdminRepository
from telegram_bot_platform.infrastructure.repositories.audit import AuditRepository
from telegram_bot_platform.infrastructure.repositories.automation import AutoReplyRepository
from telegram_bot_platform.infrastructure.repositories.chat_settings import ChatSettingsRepository
from telegram_bot_platform.infrastructure.repositories.chats import ChatRepository
from telegram_bot_platform.infrastructure.repositories.content import ContentRepository
from telegram_bot_platform.infrastructure.repositories.roles import UserRoleRepository
from telegram_bot_platform.infrastructure.repositories.users import UserRepository
from telegram_bot_platform.infrastructure.repositories.work import WorkRepository
from telegram_bot_platform.telegram.i18n import SUPPORTED_LOCALES, locale_for
from telegram_bot_platform.web.session import SessionSigner
from telegram_bot_platform.web.telegram_auth import validate_init_data

logger = logging.getLogger("platform.web")
FRONTEND = Path(__file__).resolve().parents[3] / "frontend"


class AuthRequest(BaseModel):
    init_data: str = Field(min_length=1, max_length=10_000)


class ContentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=50_000)


class ContentStatusRequest(BaseModel):
    status: ContentStatus


class ScheduledMessageRequest(BaseModel):
    chat_id: int
    text: str = Field(min_length=1, max_length=4096)
    run_at: datetime
    parse_mode: str | None = Field(default=None, max_length=32)


class ScheduledContentRequest(BaseModel):
    content_id: int
    run_at: datetime
    target_chat_id: int | None = None


class AutoReplyRequest(BaseModel):
    trigger: str = Field(min_length=1, max_length=255)
    response: str = Field(min_length=1, max_length=50_000)
    match_mode: MatchMode
    priority: int = Field(default=100, ge=0, le=100_000)
    enabled: bool = True


class RolesRequest(BaseModel):
    roles: list[UserRole] = Field(default_factory=list, max_length=20)


class TranslationRequest(BaseModel):
    en: str = Field(min_length=1, max_length=20_000)
    fa: str = Field(min_length=1, max_length=20_000)


class SettingRequest(BaseModel):
    value: object


class BotProfileRequest(BaseModel):
    username: str | None = Field(default=None, max_length=255)
    enabled: bool | None = None
    default_locale: str | None = Field(default=None, min_length=2, max_length=5)
    modules: dict[str, bool] | None = None


def _ensure_future(run_at: datetime) -> datetime:
    if run_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="errors.run_at_timezone")
    value = run_at.astimezone(timezone.utc)
    if value <= datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="errors.run_at_future")
    return value


def _content_dict(row: object) -> dict[str, object]:
    return {
        "id": row.id,
        "title": row.title,
        "body": row.body,
        "status": row.status.value,
        "created_by": row.created_by,
        "target_chat_id": row.target_chat_id,
        "published_at": row.published_at,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _reply_dict(row: AutoReplyRuleModel) -> dict[str, object]:
    return {
        "id": row.id,
        "trigger": row.trigger,
        "response": row.response,
        "match_mode": row.match_mode.value,
        "priority": row.priority,
        "enabled": row.enabled,
        "usage_count": row.usage_count,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _job_dict(row: ScheduledJobModel) -> dict[str, object]:
    return {
        "id": row.id,
        "kind": row.kind.value,
        "run_at": row.run_at,
        "payload": row.payload,
        "status": row.status.value,
        "attempts": row.attempts,
        "last_error": row.last_error,
        "locked_at": row.locked_at,
        "finished_at": row.finished_at,
        "created_at": row.created_at,
    }


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
        async with container.database.session_factory() as session:
            await LocalizationService(session).seed()
            await BotProfileService(session, resolved).ensure_defaults()
        try:
            yield
        finally:
            await container.shutdown()

    app = FastAPI(title=resolved.app_name, version="2.2.0", lifespan=lifespan)
    api_gate = SlidingWindowGate(
        max_entries=50_000,
        requests=resolved.rate_limit_requests,
        window_seconds=resolved.rate_limit_window_seconds,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved.cors_allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def api_rate_limit(request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith("/health/"):
            return await call_next(request)
        client_host = request.client.host if request.client else "unknown"
        if not api_gate.allow(hash(client_host)):
            return JSONResponse(status_code=429, content={"detail": "errors.rate_limit"})
        return await call_next(request)

    @app.middleware("http")
    async def security_headers(request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(self)"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

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
            raise HTTPException(status_code=503, detail="auth.not_ready")
        return container

    async def session_context(
        session_token: Annotated[str | None, Cookie(alias=resolved.session_cookie_name)] = None,
    ) -> tuple[int, str, str]:
        if not session_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth.required")
        try:
            return signer.verify_context(session_token)
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    async def session_user(context: tuple[int, str, str] = Depends(session_context)) -> int:
        return context[0]

    async def ensure_admin(telegram_id: int, container: Container) -> None:
        async with container.database.session_factory() as session:
            try:
                await AdminService(session, resolved.admin_user_ids).ensure_admin(telegram_id)
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail="errors.permission") from exc

    async def localized_error(key: str, locale: str = "en") -> str:
        async with app.state.container.database.session_factory() as session:
            return await LocalizationService(session).get(key, locale)

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def ready(container: Container = Depends(get_container)) -> dict[str, str]:
        if not await container.database.ping():
            raise HTTPException(status_code=503, detail="errors.database")
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

    @app.get("/api/public/i18n")
    async def public_i18n(locale: str = "en") -> dict[str, object]:
        selected = locale_for(locale, resolved.default_locale)
        async with app.state.container.database.session_factory() as session:
            return {"locale": selected, "translations": await LocalizationService(session).bundle(selected)}

    @app.post("/api/auth/telegram")
    async def auth(request_body: AuthRequest, response: Response, container: Container = Depends(get_container)) -> dict[str, object]:
        user = None
        bot_key = "core"
        last_error: AuthenticationError | None = None
        for candidate_key, token in resolved.configured_bot_tokens():
            try:
                user = validate_init_data(request_body.init_data, token, resolved.session_max_age_seconds)
                bot_key = candidate_key
                break
            except AuthenticationError as exc:
                last_error = exc
        if user is None:
            raise HTTPException(status_code=401, detail=str(last_error or AuthenticationError("auth.invalid")))

        locale = locale_for(user.language_code, resolved.default_locale)
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
                ChatIdentity(telegram_id=user.telegram_id, chat_type=ChatType.PRIVATE, title=None, username=None),
            )
            bundle = await LocalizationService(session).bundle(locale)
            bot_modules = await BotProfileService(session, resolved).modules_for(bot_key)

        response.set_cookie(
            key=resolved.session_cookie_name,
            value=signer.issue(user.telegram_id, bot_key=bot_key, locale=locale),
            max_age=resolved.session_max_age_seconds,
            httponly=True,
            secure=resolved.session_cookie_secure,
            samesite="lax",
            path="/",
        )
        return {
            "ok": True,
            "bot_key": bot_key,
            "locale": locale,
            "supported_locales": list(SUPPORTED_LOCALES),
            "modules": bot_modules,
            "translations": bundle,
            "user": {"id": user.telegram_id, "name": user.first_name, "username": user.username, "photo_url": user.photo_url},
        }

    @app.post("/api/auth/logout")
    async def logout(response: Response) -> dict[str, bool]:
        response.delete_cookie(resolved.session_cookie_name, path="/")
        return {"ok": True}

    @app.get("/api/me")
    async def me(context: tuple[int, str, str] = Depends(session_context), container: Container = Depends(get_container)) -> dict[str, object]:
        telegram_id, bot_key, _locale = context
        async with container.database.session_factory() as session:
            user = await UserRepository(session).get_by_telegram_id(telegram_id)
            if user is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            roles = await RoleService(session).list_roles(telegram_id)
            role_values = {role.value for role in roles}
            is_admin = telegram_id in set(resolved.admin_user_ids) or await AdminRepository(session).is_active_admin(telegram_id) or bool(role_values & {"admin", "owner", "administrator"})
            bot_modules = await BotProfileService(session, resolved).modules_for(bot_key)
            return {
                "id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "language_code": user.language_code,
                "is_blocked": user.is_blocked,
                "is_admin": is_admin,
                "roles": [role.value for role in roles],
                "bot_key": bot_key,
                "modules": bot_modules,
            }

    @app.get("/api/i18n")
    async def i18n(locale: str = "en", container: Container = Depends(get_container), _: int = Depends(session_user)) -> dict[str, object]:
        selected = locale_for(locale, resolved.default_locale)
        async with container.database.session_factory() as session:
            return {"locale": selected, "translations": await LocalizationService(session).bundle(selected)}

    @app.get("/api/catalog")
    async def catalog(_: int = Depends(session_user)) -> dict[str, object]:
        return {"modules": module_catalog(), "settings": setting_catalog(), "locales": list(SUPPORTED_LOCALES)}

    @app.get("/api/dashboard")
    async def dashboard(telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        async with container.database.session_factory() as session:
            roles = await RoleService(session).list_roles(telegram_id)
            is_admin = telegram_id in set(resolved.admin_user_ids) or await AdminRepository(session).is_active_admin(telegram_id) or any(role.value in {"admin", "owner", "administrator"} for role in roles)
            summary = await AuditRepository(session).summary()
            recent_content = [_content_dict(row) for row in await ContentRepository(session).list_published(5)]
            return {"ready": await container.database.ping(), "scheduler_enabled": resolved.scheduler_enabled, "is_admin": is_admin, "stats": summary if is_admin else {"content": summary["content"]}, "recent_content": recent_content}

    @app.get("/api/content")
    async def content(limit: int = 50, _: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        async with container.database.session_factory() as session:
            rows = await ContentRepository(session).list_published(max(1, min(limit, 100)))
            return {"items": [_content_dict(row) for row in rows]}

    @app.get("/api/admin/summary")
    async def admin_summary(telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, int]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return await AuditRepository(session).summary()

    @app.get("/api/admin/content")
    async def admin_content(limit: int = 100, offset: int = 0, content_status: ContentStatus | None = None, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return {"items": [_content_dict(row) for row in await ContentRepository(session).list_all(limit, offset, content_status)]}

    @app.post("/api/content", status_code=201)
    async def create_content(payload: ContentCreateRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, int]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            try:
                content_id = await ContentService(session).create(payload.title, payload.body, telegram_id)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail="errors.validation") from exc
            return {"id": content_id}

    @app.put("/api/admin/content/{content_id}")
    async def update_content(content_id: int, payload: ContentCreateRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            repository = ContentRepository(session)
            content_row = await repository.get(content_id)
            if content_row is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            if content_row.status == ContentStatus.PUBLISHED:
                raise HTTPException(status_code=409, detail="errors.immutable_published")
            content_row.title = payload.title.strip()
            content_row.body = payload.body.strip()
            if not content_row.title or not content_row.body:
                raise HTTPException(status_code=422, detail="errors.validation")
            await session.flush()
            await AuditRepository(session).record(telegram_id, "content.updated", str(content_id))
            await session.commit()
            return _content_dict(content_row)

    @app.post("/api/content/{content_id}/publish")
    async def publish_content(content_id: int, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            try:
                await ContentService(session).publish(content_id, telegram_id)
            except NotFoundError as exc:
                raise HTTPException(status_code=404, detail="errors.not_found") from exc
            return {"ok": True}

    @app.post("/api/admin/content/{content_id}/archive")
    async def archive_content(content_id: int, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            row = await ContentRepository(session).get(content_id)
            if row is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            await ContentRepository(session).archive(row)
            await AuditRepository(session).record(telegram_id, "content.archived", str(content_id))
            await session.commit()
            return {"ok": True}

    @app.put("/api/admin/content/{content_id}/status")
    async def change_content_status(content_id: int, payload: ContentStatusRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            repo = ContentRepository(session)
            row = await repo.get(content_id)
            if row is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            if row.status == ContentStatus.PUBLISHED and payload.status != ContentStatus.ARCHIVED:
                raise HTTPException(status_code=409, detail="errors.immutable_published")
            if payload.status == ContentStatus.PUBLISHED:
                await repo.publish(row)
            elif payload.status == ContentStatus.ARCHIVED:
                await repo.archive(row)
            else:
                row.status = payload.status
                await session.flush()
            await AuditRepository(session).record(telegram_id, "content.status_changed", str(content_id), {"status": payload.status.value})
            await session.commit()
            return {"ok": True}

    @app.get("/api/admin/schedules")
    async def admin_schedules(limit: int = 100, offset: int = 0, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return {"items": [_job_dict(row) for row in await WorkRepository(session).list_jobs(limit, offset)]}

    @app.post("/api/admin/schedule-message", status_code=201)
    async def schedule_message(payload: ScheduledMessageRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, int]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            job_id = await OutboxService(session).enqueue_job(ScheduledJobInput(kind=TaskKind.SEND_MESSAGE, run_at=_ensure_future(payload.run_at), payload={"chat_id": payload.chat_id, "text": payload.text, "parse_mode": payload.parse_mode}))
            await AuditRepository(session).record(telegram_id, "schedule.message_created", str(job_id))
            await session.commit()
            return {"id": job_id}

    @app.post("/api/admin/schedule-content", status_code=201)
    async def schedule_content(payload: ScheduledContentRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, int]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            if await ContentRepository(session).get(payload.content_id) is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            job_id = await OutboxService(session).enqueue_job(ScheduledJobInput(kind=TaskKind.PUBLISH_CONTENT, run_at=_ensure_future(payload.run_at), payload={"content_id": payload.content_id, "target_chat_id": payload.target_chat_id, "actor_id": telegram_id}))
            await AuditRepository(session).record(telegram_id, "schedule.content_created", str(job_id))
            await session.commit()
            return {"id": job_id}

    @app.post("/api/admin/schedules/{job_id}/cancel")
    async def cancel_schedule(job_id: int, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            repo = WorkRepository(session)
            job = await repo.get_job(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            if not await repo.cancel_job(job):
                raise HTTPException(status_code=409, detail="common.confirm_action")
            await AuditRepository(session).record(telegram_id, "schedule.cancelled", str(job_id))
            await session.commit()
            return {"ok": True}

    @app.get("/api/admin/auto-replies")
    async def admin_auto_replies(limit: int = 100, offset: int = 0, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return {"items": [_reply_dict(row) for row in await AutoReplyRepository(session).list_all(limit, offset)]}

    @app.post("/api/admin/auto-replies", status_code=201)
    async def create_auto_reply(payload: AutoReplyRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            row = await AutoReplyRepository(session).create(payload.trigger.strip(), payload.response.strip(), payload.match_mode, payload.priority, payload.enabled)
            await AuditRepository(session).record(telegram_id, "auto_reply.created", str(row.id))
            await session.commit()
            return _reply_dict(row)

    @app.put("/api/admin/auto-replies/{rule_id}")
    async def update_auto_reply(rule_id: int, payload: AutoReplyRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            repo = AutoReplyRepository(session)
            row = await repo.get(rule_id)
            if row is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            await repo.update(row, trigger=payload.trigger.strip(), response=payload.response.strip(), match_mode=payload.match_mode, priority=payload.priority, enabled=payload.enabled)
            await AuditRepository(session).record(telegram_id, "auto_reply.updated", str(rule_id))
            await session.commit()
            return _reply_dict(row)

    @app.post("/api/admin/auto-replies/{rule_id}/toggle")
    async def toggle_auto_reply(rule_id: int, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            repo = AutoReplyRepository(session)
            row = await repo.get(rule_id)
            if row is None:
                raise HTTPException(status_code=404, detail="errors.not_found")
            await repo.toggle(row)
            await AuditRepository(session).record(telegram_id, "auto_reply.toggled", str(rule_id), {"enabled": row.enabled})
            await session.commit()
            return {"ok": True, "enabled": row.enabled}

    @app.delete("/api/admin/auto-replies/{rule_id}")
    async def delete_auto_reply(rule_id: int, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> Response:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            if not await AutoReplyRepository(session).delete(rule_id):
                raise HTTPException(status_code=404, detail="errors.not_found")
            await AuditRepository(session).record(telegram_id, "auto_reply.deleted", str(rule_id))
            await session.commit()
            return Response(status_code=204)

    @app.get("/api/admin/chats")
    async def admin_chats(limit: int = 100, offset: int = 0, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            rows = await ChatRepository(session).list_all(limit, offset)
            settings_repo = ChatSettingsRepository(session)
            items = [{"id": row.id, "telegram_id": row.telegram_id, "chat_type": row.chat_type.value, "title": row.title, "username": row.username, "locale": row.locale, "is_active": row.is_active, "modules": await settings_repo.get_modules(row.telegram_id), "updated_at": row.updated_at} for row in rows]
            return {"items": items}

    @app.post("/api/admin/chats/{chat_id}/modules/{module}/toggle")
    async def toggle_chat_module(chat_id: int, module: str, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        if not module or len(module) > 64 or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for char in module):
            raise HTTPException(status_code=422, detail="errors.validation")
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            try:
                enabled = await ChatSettingsRepository(session).toggle_module(chat_id, module)
            except ValueError as exc:
                raise HTTPException(status_code=404, detail="errors.not_found") from exc
            await AuditRepository(session).record(telegram_id, "chat.module_toggled", str(chat_id), {"module": module, "enabled": enabled})
            await session.commit()
            return {"ok": True, "enabled": enabled}

    @app.get("/api/admin/users")
    async def admin_users(limit: int = 100, offset: int = 0, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            rows = await UserRepository(session).list_all(limit, offset)
            role_repo = UserRoleRepository(session)
            items = [{"telegram_id": row.telegram_id, "username": row.username, "first_name": row.first_name, "last_name": row.last_name, "language_code": row.language_code, "is_bot": row.is_bot, "is_blocked": row.is_blocked, "created_at": row.created_at, "last_seen_at": row.last_seen_at, "roles": [role.value for role in await role_repo.list_active(row.telegram_id)]} for row in rows]
            return {"items": items}

    @app.put("/api/admin/users/{target_telegram_id}/roles")
    async def set_user_roles(target_telegram_id: int, payload: RolesRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        unique_roles = list(dict.fromkeys(payload.roles))
        async with container.database.session_factory() as session:
            repo = UserRoleRepository(session)
            current = set(await repo.list_active(target_telegram_id))
            desired = set(unique_roles)
            for role in current - desired:
                await repo.revoke(target_telegram_id, role)
            for role in desired - current:
                await repo.grant(target_telegram_id, role)
            await AuditRepository(session).record(telegram_id, "user.roles_replaced", str(target_telegram_id), {"roles": [role.value for role in unique_roles]})
            await session.commit()
            return {"ok": True, "roles": [role.value for role in unique_roles]}

    @app.get("/api/admin/audit")
    async def admin_audit(limit: int = 100, offset: int = 0, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            rows = await AuditRepository(session).list_recent(limit, offset)
            return {"items": [{"id": row.id, "actor_telegram_id": row.actor_telegram_id, "action": row.action, "target": row.target, "metadata_json": row.metadata_json, "created_at": row.created_at} for row in rows]}

    @app.get("/api/admin/settings")
    async def admin_settings(telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return {"items": await SettingsService(session, resolved).list()}

    @app.put("/api/admin/settings/{key:path}")
    async def update_setting(key: str, payload: SettingRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            try:
                result = await SettingsService(session, resolved).save(key, payload.value, telegram_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="errors.not_found") from exc
            except (PermissionError, ValueError, TypeError) as exc:
                raise HTTPException(status_code=422, detail="errors.validation") from exc
            await AuditRepository(session).record(telegram_id, "setting.updated", key)
            await session.commit()
            return result

    @app.delete("/api/admin/settings/{key:path}")
    async def reset_setting(key: str, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> Response:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            try:
                await SettingsService(session, resolved).reset(key, telegram_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="errors.not_found") from exc
            await AuditRepository(session).record(telegram_id, "setting.reset", key)
            await session.commit()
            return Response(status_code=204)

    @app.get("/api/admin/translations")
    async def admin_translations(telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return {"items": await LocalizationService(session).list_pairs()}

    @app.put("/api/admin/translations/{key:path}")
    async def update_translation(key: str, payload: TranslationRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, bool]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            service = LocalizationService(session)
            try:
                await service.save_pair(key, payload.en, payload.fa, telegram_id)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail="errors.validation") from exc
            await AuditRepository(session).record(telegram_id, "translation.updated", key)
            await session.commit()
            await service.export_overrides()
            return {"ok": True}

    @app.delete("/api/admin/translations/{key:path}")
    async def reset_translation(key: str, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> Response:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            service = LocalizationService(session)
            try:
                await service.reset(key, telegram_id)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail="errors.validation") from exc
            await AuditRepository(session).record(telegram_id, "translation.reset", key)
            await session.commit()
            await service.export_overrides()
            return Response(status_code=204)

    @app.get("/api/admin/bots")
    async def admin_bots(telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        async with container.database.session_factory() as session:
            return {"items": await BotProfileService(session, resolved).list()}

    @app.put("/api/admin/bots/{bot_key}")
    async def update_bot(bot_key: str, payload: BotProfileRequest, telegram_id: int = Depends(session_user), container: Container = Depends(get_container)) -> dict[str, object]:
        await ensure_admin(telegram_id, container)
        if payload.default_locale and payload.default_locale not in SUPPORTED_LOCALES:
            raise HTTPException(status_code=422, detail="errors.validation")
        async with container.database.session_factory() as session:
            try:
                result = await BotProfileService(session, resolved).update(bot_key, payload.model_dump(exclude_unset=True), telegram_id)
            except ValueError as exc:
                raise HTTPException(status_code=404, detail="errors.not_found") from exc
            await AuditRepository(session).record(telegram_id, "bot_profile.updated", bot_key)
            await session.commit()
            return result

    return app


app = create_app()


def main() -> None:
    import uvicorn

    settings = Settings()
    uvicorn.run(app, host=settings.web_host, port=settings.web_port, proxy_headers=True, server_header=False)
