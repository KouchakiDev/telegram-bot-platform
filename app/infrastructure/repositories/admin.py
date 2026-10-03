from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import AdminModel


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def is_active_admin(self, telegram_id: int) -> bool:
        result = await self.session.execute(
            select(AdminModel.id).where(
                AdminModel.telegram_id == telegram_id,
                AdminModel.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None
