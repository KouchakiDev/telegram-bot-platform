from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ChatIdentity
from app.infrastructure.db.models import ChatModel, ChatSettingsModel


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
