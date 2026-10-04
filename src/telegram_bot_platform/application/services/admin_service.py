from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.core.exceptions import AuthorizationError
from telegram_bot_platform.domain.enums import UserRole
from telegram_bot_platform.infrastructure.repositories.admin import AdminRepository
from telegram_bot_platform.infrastructure.repositories.audit import AuditRepository
from telegram_bot_platform.infrastructure.repositories.roles import UserRoleRepository


class AdminService:
    def __init__(self, session: AsyncSession, configured_ids: tuple[int, ...]) -> None:
        self.session = session
        self.configured_ids = set(configured_ids)

    async def ensure_admin(self, telegram_id: int) -> None:
        if telegram_id in self.configured_ids:
            return
        if await AdminRepository(self.session).is_active_admin(telegram_id):
            return
        role_repository = UserRoleRepository(self.session)
        if await role_repository.has(telegram_id, UserRole.ADMIN):
            return
        if await role_repository.has(telegram_id, UserRole.OWNER):
            return
        raise AuthorizationError("Administrator access required")

    async def summary(self, actor_id: int) -> dict[str, int]:
        await self.ensure_admin(actor_id)
        return await AuditRepository(self.session).summary()
