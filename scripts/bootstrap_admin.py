from __future__ import annotations

import asyncio

from sqlalchemy import select

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.core.container import Container
from telegram_bot_platform.domain.enums import UserRole
from telegram_bot_platform.infrastructure.db.models import AdminModel
from telegram_bot_platform.infrastructure.repositories.roles import UserRoleRepository


async def bootstrap() -> None:
    settings = Settings()
    container = Container.build(settings)
    try:
        async with container.database.session_factory() as session:
            roles = UserRoleRepository(session)
            for telegram_id in settings.admin_user_ids:
                existing = await session.scalar(select(AdminModel).where(AdminModel.telegram_id == telegram_id))
                if existing is None:
                    session.add(AdminModel(telegram_id=telegram_id, role="administrator", is_active=True))
                await roles.grant(telegram_id, UserRole.ADMIN)
                await roles.grant(telegram_id, UserRole.OWNER)
            await session.commit()
    finally:
        await container.shutdown()


def main() -> None:
    asyncio.run(bootstrap())


if __name__ == "__main__":
    main()
