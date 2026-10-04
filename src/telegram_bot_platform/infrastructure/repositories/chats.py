from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.domain.entities import ChatIdentity
from telegram_bot_platform.infrastructure.db.models import ChatModel, ChatSettingsModel


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, identity: ChatIdentity, locale: str) -> ChatModel:
        result = await self.session.execute(select(ChatModel).where(ChatModel.telegram_id == identity.telegram_id))
        model = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if model is None:
            model = ChatModel(
                telegram_id=identity.telegram_id,
                chat_type=identity.chat_type,
                title=identity.title,
                username=identity.username,
                locale=locale,
                updated_at=now,
            )
            self.session.add(model)
            await self.session.flush()
            self.session.add(ChatSettingsModel(chat_id=model.id, modules={"content": True, "auto_reply": True}))
        else:
            model.chat_type = identity.chat_type
            model.title = identity.title
            model.username = identity.username
            model.updated_at = now
        await self.session.flush()
        return model

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ChatModel]:
        result = await self.session.execute(
            select(ChatModel)
            .order_by(ChatModel.updated_at.desc(), ChatModel.id.desc())
            .offset(max(0, offset))
            .limit(max(1, min(limit, 200)))
        )
        return list(result.scalars())

    async def get_by_telegram_id(self, telegram_id: int) -> ChatModel | None:
        result = await self.session.execute(select(ChatModel).where(ChatModel.telegram_id == telegram_id))
        return result.scalar_one_or_none()
