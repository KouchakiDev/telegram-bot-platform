from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CommandHandler, ContextTypes

from app.application.services.user_service import UserService
from app.core.container import Container
from app.domain.entities import ChatIdentity, UserIdentity
from app.domain.enums import ChatType
from app.telegram.i18n import locale_for, text


class CommonModule:
    def __init__(self, container: Container) -> None:
        self.container = container
        self.settings = container.settings

    async def touch(self, update: Update) -> str:
        if update.effective_chat is None:
            return self.settings.default_locale
        user = update.effective_user
        identity = UserIdentity(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_bot=user.is_bot,
        ) if user else None
        chat = update.effective_chat
        async with self.container.database.session_factory() as session:
            service = UserService(session, self.settings.default_locale)
            locale = locale_for(user.language_code if user else None, self.settings.default_locale)
            await service.touch_user_and_chat(
                identity,
                ChatIdentity(
                    telegram_id=chat.id,
                    chat_type=ChatType(chat.type),
                    title=chat.title,
                    username=chat.username,
                ),
            )
            return locale

    def handlers(self) -> list[CommandHandler]:
        return [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("app", self.app),
        ]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message:
            return
        locale = await self.touch(update)
        buttons = []
        if update.effective_chat and update.effective_chat.type == "private":
            buttons = [[InlineKeyboardButton(text("app", locale), web_app=WebAppInfo(url=str(self.settings.web_app_url)))]]
        keyboard = [[KeyboardButton(text("content", locale))]]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, selective=True)
        await update.effective_message.reply_text(text("welcome", locale), reply_markup=reply)
        if buttons:
            await update.effective_message.reply_text(text("app", locale), reply_markup=InlineKeyboardMarkup(buttons))

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message:
            return
        locale = await self.touch(update)
        await update.effective_message.reply_text(text("help", locale))

    async def app(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message:
            return
        locale = await self.touch(update)
        if update.effective_chat and update.effective_chat.type != "private":
            await update.effective_message.reply_text("The Mini App is available in a private chat with the bot.")
            return
        await update.effective_message.reply_text(
            text("app", locale),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text("app", locale), web_app=WebAppInfo(url=str(self.settings.web_app_url)))]]
            ),
        )
