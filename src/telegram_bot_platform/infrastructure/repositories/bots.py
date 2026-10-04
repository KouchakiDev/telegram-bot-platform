from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.infrastructure.db.models import BotProfileModel


class BotProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, bot_key: str) -> BotProfileModel | None:
        result = await self.session.execute(select(BotProfileModel).where(BotProfileModel.bot_key == bot_key))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[BotProfileModel]:
        result = await self.session.execute(select(BotProfileModel).order_by(BotProfileModel.id))
        return list(result.scalars())

    async def ensure(self, bot_key: str, name_key: str, token_env_key: str, username: str | None, default_locale: str, modules: dict[str, bool]) -> BotProfileModel:
        row = await self.get(bot_key)
        if row is None:
            row = BotProfileModel(bot_key=bot_key, name_key=name_key, token_env_key=token_env_key, username=username, default_locale=default_locale, modules=modules)
            self.session.add(row)
        else:
            row.name_key = name_key
            row.token_env_key = token_env_key
            if username is not None:
                row.username = username
            if not row.default_locale:
                row.default_locale = default_locale
            if not row.modules:
                row.modules = modules
        await self.session.flush()
        return row

    async def update(self, bot_key: str, *, username: str | None = None, enabled: bool | None = None, default_locale: str | None = None, modules: dict[str, bool] | None = None, actor_id: int | None = None) -> BotProfileModel:
        row = await self.get(bot_key)
        if row is None:
            raise ValueError("Bot profile not found")
        if username is not None:
            row.username = username
        if enabled is not None:
            row.enabled = enabled
        if default_locale is not None:
            row.default_locale = default_locale
        if modules is not None:
            row.modules = modules
        row.updated_by = actor_id
        row.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return row
