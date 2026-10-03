from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError
from app.infrastructure.repositories.admin import AdminRepository
from app.infrastructure.repositories.audit import AuditRepository


class AdminService:
    def __init__(self, session: AsyncSession, configured_ids: tuple[int, ...]) -> None:
        self.session = session
        self.configured_ids = set(configured_ids)

    async def ensure_admin(self, telegram_id: int) -> None:
        if telegram_id in self.configured_ids:
            return
        if not await AdminRepository(self.session).is_active_admin(telegram_id):
            raise AuthorizationError("Administrator access required")

    async def summary(self, actor_id: int) -> dict[str, int]:
        await self.ensure_admin(actor_id)
        return await AuditRepository(self.session).summary()
