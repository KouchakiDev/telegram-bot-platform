from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.domain.enums import UserRole
from telegram_bot_platform.infrastructure.repositories.audit import AuditRepository
from telegram_bot_platform.infrastructure.repositories.roles import UserRoleRepository


class RoleService:
    """Manage reusable platform roles without coupling authorization to Telegram handlers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRoleRepository(session)

    async def list_roles(self, telegram_id: int) -> tuple[UserRole, ...]:
        return await self.repository.list_active(telegram_id)

    async def has_role(self, telegram_id: int, role: UserRole) -> bool:
        return await self.repository.has(telegram_id, role)

    async def grant_role(self, actor_id: int, telegram_id: int, role: UserRole) -> None:
        await self.repository.grant(telegram_id, role)
        await AuditRepository(self.session).record(
            actor_id, "user.role_granted", str(telegram_id), {"role": role.value}
        )
        await self.session.commit()

    async def revoke_role(self, actor_id: int, telegram_id: int, role: UserRole) -> bool:
        changed = await self.repository.revoke(telegram_id, role)
        if changed:
            await AuditRepository(self.session).record(
                actor_id, "user.role_revoked", str(telegram_id), {"role": role.value}
            )
            await self.session.commit()
        return changed
