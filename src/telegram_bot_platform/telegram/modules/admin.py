from __future__ import annotations

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from telegram_bot_platform.application.services.admin_service import AdminService
from telegram_bot_platform.core.container import Container
from telegram_bot_platform.core.exceptions import AuthorizationError
from telegram_bot_platform.telegram.i18n import locale_for, text


class AdminModule:
    def __init__(self, container: Container) -> None:
        self.container = container

    def handlers(self) -> list[CommandHandler]:
        return [CommandHandler("admin", self.summary)]

    async def summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message or not update.effective_user:
            return
        locale = locale_for(update.effective_user.language_code, self.container.settings.default_locale)
        async with self.container.database.session_factory() as session:
            try:
                data = await AdminService(session, self.container.settings.admin_user_ids).summary(update.effective_user.id)
            except AuthorizationError:
                await update.effective_message.reply_text(text("admin_required", locale))
                return
        await update.effective_message.reply_text(text("admin_summary", locale, **data))
