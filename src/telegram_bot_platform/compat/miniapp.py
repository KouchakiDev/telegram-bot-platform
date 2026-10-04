from __future__ import annotations

from telebot import types

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.telegram.i18n import locale_for, text


def send_mini_app(bot: object, message: object) -> None:
    settings = Settings()
    url = str(settings.web_app_url or "").strip()
    if not url:
        return
    user = getattr(message, "from_user", None)
    language_code = getattr(user, "language_code", None)
    locale = locale_for(language_code, settings.default_locale)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text("bot.message.app_button", locale), web_app=types.WebAppInfo(url=url)))
    chat = getattr(message, "chat", None)
    chat_id = getattr(chat, "id", None)
    if chat_id is not None:
        bot.send_message(chat_id, text("bot.message.app", locale), reply_markup=markup)
