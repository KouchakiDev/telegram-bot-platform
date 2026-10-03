from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from app.application.services.content_service import ContentService
from app.core.container import Container
from app.core.text import escape_telegram_html
from app.infrastructure.repositories.content import ContentRepository
from app.telegram.i18n import locale_for, text


class ContentModule:
    CALLBACK_PREFIX = "content:"

    def __init__(self, container: Container) -> None:
        self.container = container

    def handlers(self) -> list[object]:
        return [
            CommandHandler("content", self.show_content),
            CallbackQueryHandler(self.open_content, pattern=r"^content:\d+$"),
        ]

    async def show_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message:
            return
        user = update.effective_user
        locale = locale_for(user.language_code if user else None, self.container.settings.default_locale)
        async with self.container.database.session_factory() as session:
            items = await ContentService(session).list_published(20)
        if not items:
            await update.effective_message.reply_text(text("no_content", locale))
            return
        buttons = [
            [InlineKeyboardButton(str(item["title"]), callback_data=f"content:{item['id']}")]
            for item in items[:20]
        ]
        await update.effective_message.reply_text(text("content", locale), reply_markup=InlineKeyboardMarkup(buttons))

    async def open_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return
        await query.answer()
        content_id = int(query.data.split(":", 1)[1])
        async with self.container.database.session_factory() as session:
            item = await ContentRepository(session).get(content_id)
        if item is None:
            await query.edit_message_text(text("no_content", self.container.settings.default_locale))
            return
        safe_title = escape_telegram_html(item.title)
        safe_body = escape_telegram_html(item.body)
        await query.edit_message_text(f"<b>{safe_title}</b>\n\n{safe_body}", parse_mode="HTML")
