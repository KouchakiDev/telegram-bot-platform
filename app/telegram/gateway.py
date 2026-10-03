from __future__ import annotations

from telegram import Bot


class TelegramGateway:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send_text(self, chat_id: int, text: str, parse_mode: str | None = None) -> None:
        await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
