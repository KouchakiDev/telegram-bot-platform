from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.domain.entities import ChatIdentity, UserIdentity
from telegram_bot_platform.domain.enums import ChatType
from telegram_bot_platform.infrastructure.repositories.chats import ChatRepository
from telegram_bot_platform.infrastructure.repositories.users import UserRepository


class UserService:
    def __init__(self, session: AsyncSession, default_locale: str) -> None:
        self.session = session
        self.default_locale = default_locale

    async def touch_user_and_chat(self, user: UserIdentity | None, chat: ChatIdentity) -> None:
        locale = (user.language_code.split("-")[0] if user and user.language_code else self.default_locale)
        if user and not user.is_bot:
            await UserRepository(self.session).upsert(user)
        await ChatRepository(self.session).upsert(chat, locale)
        await self.session.commit()
