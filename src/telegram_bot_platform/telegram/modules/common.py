from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from telegram_bot_platform.core.container import Container
from telegram_bot_platform.telegram.i18n import locale_for, text


class CommonModule:
    def __init__(self, container: Container) -> None:
        self.container = container
        self.settings = container.settings

    def handlers(self) -> list[object]:
        return [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("app", self.app),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown),
        ]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        locale = locale_for(update.effective_user.language_code if update.effective_user else None, self.settings.default_locale)
        buttons = []
        if self.settings.web_app_url:
            buttons = [[InlineKeyboardButton(text("bot.message.app", locale), web_app=WebAppInfo(url=str(self.settings.web_app_url)))]]
        reply = InlineKeyboardMarkup(buttons) if buttons else None
        if update.effective_message:
            await update.effective_message.reply_text(text("bot.message.welcome", locale, app_name=self.settings.app_name), reply_markup=reply)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        locale = locale_for(update.effective_user.language_code if update.effective_user else None, self.settings.default_locale)
        if update.effective_message:
            await update.effective_message.reply_text(text("bot.message.help", locale))

    async def app(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        locale = locale_for(update.effective_user.language_code if update.effective_user else None, self.settings.default_locale)
        if not update.effective_message:
            return
        if not self.settings.web_app_url:
            await update.effective_message.reply_text(text("errors.request_failed", locale))
            return
        buttons = [[InlineKeyboardButton(text("bot.message.app", locale), web_app=WebAppInfo(url=str(self.settings.web_app_url)))]]
        await update.effective_message.reply_text(text("bot.message.app", locale), reply_markup=InlineKeyboardMarkup(buttons))

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        locale = locale_for(update.effective_user.language_code if update.effective_user else None, self.settings.default_locale)
        if update.effective_message:
            await update.effective_message.reply_text(text("bot.message.unknown", locale))
