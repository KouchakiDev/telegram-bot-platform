from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from telegram_bot_platform.core.container import Container
from telegram_bot_platform.telegram.i18n import locale_for, text
from telegram_bot_platform.application.services.content_service import ContentService


class ContentModule:
    def __init__(self, container: Container) -> None:
        self.container = container

    def handlers(self) -> list[object]:
        return [CommandHandler("content", self.show), CallbackQueryHandler(self.open_item, pattern=r"^content:\d+$")]

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        locale = locale_for(update.effective_user.language_code if update.effective_user else None, self.container.settings.default_locale)
        items = await self.container_content()
        if not items:
            if update.effective_message:
                await update.effective_message.reply_text(text("bot.message.no_content", locale))
            return
        buttons = [[InlineKeyboardButton(str(item["title"]), callback_data=f"content:{item['id']}")] for item in items]
        if update.effective_message:
            await update.effective_message.reply_text(text("bot.message.content", locale), reply_markup=InlineKeyboardMarkup(buttons))

    async def container_content(self) -> list[dict[str, object]]:
        async with self.container.database.session_factory() as session:
            return await ContentService(session).list_published(20)

    async def open_item(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None:
            return
        await query.answer()
        try:
            content_id = int((query.data or "").split(":", 1)[1])
        except (IndexError, ValueError):
            return
        async with self.container.database.session_factory() as session:
            items = await ContentService(session).list_published(100)
        item = next((row for row in items if row["id"] == content_id), None)
        if item and query.message:
            await query.message.reply_text(text("bot.message.content_item", locale, title=item["title"], body=item["body"]))
