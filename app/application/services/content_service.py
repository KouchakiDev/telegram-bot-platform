from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.repositories.audit import AuditRepository
from app.infrastructure.repositories.content import ContentRepository


class ContentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ContentRepository(session)

    async def create(self, title: str, body: str, actor_id: int) -> int:
        title = title.strip()
        body = body.strip()
        if not title or not body:
            raise ValueError("Title and body are required")
        if len(title) > 255 or len(body) > 50_000:
            raise ValueError("Content size exceeds the configured limit")
        content = await self.repo.create(title, body, actor_id)
        await AuditRepository(self.session).record(actor_id, "content.created", str(content.id))
        await self.session.commit()
        return content.id

    async def publish(self, content_id: int, actor_id: int | None) -> None:
        content = await self.repo.get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        await self.repo.publish(content)
        await AuditRepository(self.session).record(actor_id, "content.published", str(content_id))
        await self.session.commit()

    async def list_published(self, limit: int = 20) -> list[dict[str, object]]:
        rows = await self.repo.list_published(max(1, min(limit, 100)))
        return [
            {"id": row.id, "title": row.title, "body": row.body, "published_at": row.published_at}
            for row in rows
        ]
