from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from telegram_bot_platform.domain.enums import UserRole
from telegram_bot_platform.infrastructure.db.base import Base
from telegram_bot_platform.infrastructure.repositories.roles import UserRoleRepository

pytest.importorskip("aiosqlite")


@pytest.mark.asyncio
async def test_roles_can_be_granted_listed_and_revoked() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        repository = UserRoleRepository(session)
        await repository.grant(42, UserRole.CUSTOMER)
        await repository.grant(42, UserRole.STAFF)
        await session.commit()

        assert await repository.has(42, UserRole.CUSTOMER)
        assert await repository.list_active(42) == (UserRole.CUSTOMER, UserRole.STAFF)

        assert await repository.revoke(42, UserRole.CUSTOMER)
        await session.commit()
        assert not await repository.has(42, UserRole.CUSTOMER)
    await engine.dispose()
