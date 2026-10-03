from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from app.application.services.automation_service import AutomationService
from app.core.container import Container
from app.core.rate_limit import SlidingWindowGate
from app.infrastructure.repositories.chat_settings import ChatSettingsRepository


class AutoReplyModule:
    def __init__(self, container: Container) -> None:
        self.container = container
        self.service = AutomationService(
            container.database.session_factory,
            cache_ttl_seconds=container.settings.auto_reply_cache_ttl_seconds,
            max_rules=container.settings.auto_reply_max_rules,
        )
        self.gate = SlidingWindowGate(
            max_entries=50_000,
            requests=container.settings.rate_limit_requests,
            window_seconds=container.settings.rate_limit_window_seconds,
        )

    def handlers(self) -> list[MessageHandler]:
        return [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle)]

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message or not update.effective_message.text or not update.effective_user:
            return
        if not update.effective_chat or update.effective_chat.type != "private":
            return
        if not self.gate.allow(update.effective_user.id):
            return
        async with self.container.database.session_factory() as session:
            enabled = await ChatSettingsRepository(session).module_enabled(update.effective_chat.id, "auto_reply")
        if not enabled:
            return
        result = await self.service.match(update.effective_message.text)
        if result.response:
            await update.effective_message.reply_text(result.response)
