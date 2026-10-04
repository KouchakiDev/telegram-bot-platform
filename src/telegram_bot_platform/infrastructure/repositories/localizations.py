from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.infrastructure.db.models import LocalizationModel


class LocalizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, locale: str | None = None) -> list[LocalizationModel]:
        statement = select(LocalizationModel)
        if locale:
            statement = statement.where(LocalizationModel.locale == locale)
        result = await self.session.execute(statement.order_by(LocalizationModel.key.asc(), LocalizationModel.locale.asc()))
        return list(result.scalars())

    async def get(self, key: str, locale: str) -> LocalizationModel | None:
        result = await self.session.execute(
            select(LocalizationModel).where(LocalizationModel.key == key, LocalizationModel.locale == locale)
        )
        return result.scalar_one_or_none()

    async def upsert(self, key: str, locale: str, value: str, *, category: str, description: str | None, is_system: bool = True) -> LocalizationModel:
        row = await self.get(key, locale)
        if row is None:
            row = LocalizationModel(key=key, locale=locale, value=value, category=category, description=description, is_system=is_system)
            self.session.add(row)
        else:
            row.value = value
            row.category = category
            row.description = description
            row.is_system = is_system
        await self.session.flush()
        return row

    async def delete(self, key: str, locale: str) -> bool:
        result = await self.session.execute(
            delete(LocalizationModel).where(LocalizationModel.key == key, LocalizationModel.locale == locale)
        )
        return bool(result.rowcount)
