from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.infrastructure.db.models import ChatModel, ChatSettingsModel


class ChatSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_modules(self, telegram_chat_id: int) -> dict[str, bool]:
        result = await self.session.execute(
            select(ChatSettingsModel.modules)
            .join(ChatModel, ChatSettingsModel.chat_id == ChatModel.id)
            .where(ChatModel.telegram_id == telegram_chat_id)
        )
        return dict(result.scalar_one_or_none() or {})

    async def module_enabled(self, telegram_chat_id: int, module: str) -> bool:
        modules = await self.get_modules(telegram_chat_id)
        return bool(modules.get(module, False))

    async def toggle_module(self, telegram_chat_id: int, module: str) -> bool:
        result = await self.session.execute(
            select(ChatSettingsModel)
            .join(ChatModel, ChatSettingsModel.chat_id == ChatModel.id)
            .where(ChatModel.telegram_id == telegram_chat_id)
        )
        settings = result.scalar_one_or_none()
        if settings is None:
            raise ValueError("Chat settings not found")
        modules = dict(settings.modules or {})
        enabled = not bool(modules.get(module, False))
        modules[module] = enabled
        settings.modules = modules
        settings.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return enabled
