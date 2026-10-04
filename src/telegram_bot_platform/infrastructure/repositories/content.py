from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.domain.enums import ContentStatus
from telegram_bot_platform.infrastructure.db.models import ContentModel


class ContentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, title: str, body: str, created_by: int) -> ContentModel:
        model = ContentModel(title=title, body=body, created_by=created_by, status=ContentStatus.DRAFT)
        self.session.add(model)
        await self.session.flush()
        return model

    async def get(self, content_id: int) -> ContentModel | None:
        result = await self.session.execute(select(ContentModel).where(ContentModel.id == content_id))
        return result.scalar_one_or_none()

    async def list_published(self, limit: int = 20) -> list[ContentModel]:
        result = await self.session.execute(
            select(ContentModel)
            .where(ContentModel.status == ContentStatus.PUBLISHED)
            .order_by(ContentModel.published_at.desc(), ContentModel.id.desc())
            .limit(limit)
        )
        return list(result.scalars())

    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: ContentStatus | None = None,
    ) -> list[ContentModel]:
        statement = select(ContentModel)
        if status is not None:
            statement = statement.where(ContentModel.status == status)
        result = await self.session.execute(
            statement.order_by(ContentModel.updated_at.desc(), ContentModel.id.desc())
            .offset(max(0, offset))
            .limit(max(1, min(limit, 200)))
        )
        return list(result.scalars())

    async def publish(self, content: ContentModel) -> ContentModel:
        content.status = ContentStatus.PUBLISHED
        content.published_at = datetime.now(timezone.utc)
        await self.session.flush()
        return content

    async def archive(self, content: ContentModel) -> ContentModel:
        content.status = ContentStatus.ARCHIVED
        await self.session.flush()
        return content
