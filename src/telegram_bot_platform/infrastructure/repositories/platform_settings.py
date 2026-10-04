from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.infrastructure.db.models import PlatformSettingModel


class PlatformSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, key: str) -> PlatformSettingModel | None:
        result = await self.session.execute(select(PlatformSettingModel).where(PlatformSettingModel.key == key))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[PlatformSettingModel]:
        result = await self.session.execute(select(PlatformSettingModel).order_by(PlatformSettingModel.category, PlatformSettingModel.key))
        return list(result.scalars())

    async def set(self, key: str, value: object, value_type: str, category: str, *, secret: bool, editable: bool, restart_required: bool, actor_id: int | None) -> PlatformSettingModel:
        row = await self.get(key)
        if row is None:
            row = PlatformSettingModel(key=key, value_json=value, value_type=value_type, category=category, is_secret=secret, editable=editable, restart_required=restart_required)
            self.session.add(row)
        else:
            row.value_json = value
            row.value_type = value_type
            row.category = category
            row.is_secret = secret
            row.editable = editable
            row.restart_required = restart_required
        row.updated_by = actor_id
        row.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return row

    async def delete(self, key: str) -> bool:
        result = await self.session.execute(delete(PlatformSettingModel).where(PlatformSettingModel.key == key))
        return bool(result.rowcount)
