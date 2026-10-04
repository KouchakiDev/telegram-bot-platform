from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.domain.enums import UserRole
from telegram_bot_platform.infrastructure.db.models import UserRoleModel


class UserRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_active(self, telegram_id: int) -> tuple[UserRole, ...]:
        result = await self.session.execute(
            select(UserRoleModel.role)
            .where(UserRoleModel.telegram_id == telegram_id, UserRoleModel.is_active.is_(True))
            .order_by(UserRoleModel.id)
        )
        return tuple(result.scalars().all())

    async def has(self, telegram_id: int, role: UserRole) -> bool:
        result = await self.session.execute(
            select(UserRoleModel.id).where(
                UserRoleModel.telegram_id == telegram_id,
                UserRoleModel.role == role,
                UserRoleModel.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None

    async def grant(self, telegram_id: int, role: UserRole) -> UserRoleModel:
        existing = await self.session.execute(
            select(UserRoleModel).where(
                UserRoleModel.telegram_id == telegram_id,
                UserRoleModel.role == role,
            )
        )
        model = existing.scalar_one_or_none()
        if model is None:
            model = UserRoleModel(telegram_id=telegram_id, role=role, is_active=True)
            self.session.add(model)
        else:
            model.is_active = True
        await self.session.flush()
        return model

    async def revoke(self, telegram_id: int, role: UserRole) -> bool:
        result = await self.session.execute(
            select(UserRoleModel).where(
                UserRoleModel.telegram_id == telegram_id,
                UserRoleModel.role == role,
                UserRoleModel.is_active.is_(True),
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        model.is_active = False
        await self.session.flush()
        return True
