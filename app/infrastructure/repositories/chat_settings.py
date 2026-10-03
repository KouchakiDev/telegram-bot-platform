from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import ChatModel, ChatSettingsModel


class ChatSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def module_enabled(self, telegram_chat_id: int, module: str) -> bool:
        result = await self.session.execute(
            select(ChatSettingsModel.modules)
            .join(ChatModel, ChatSettingsModel.chat_id == ChatModel.id)
            .where(ChatModel.telegram_id == telegram_chat_id)
        )
        modules = result.scalar_one_or_none() or {}
        return bool(modules.get(module, False))
