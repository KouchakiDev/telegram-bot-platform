import pytest
pytest.importorskip("aiosqlite")
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from telegram_bot_platform.application.services.content_service import ContentService
from telegram_bot_platform.infrastructure.db.base import Base
from telegram_bot_platform.infrastructure.db import models  # noqa: F401


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        yield db
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_publish(session) -> None:
    service = ContentService(session)
    content_id = await service.create("Announcement", "Hello", 1)
    await service.publish(content_id, 1)
    items = await service.list_published()
    assert items[0]["title"] == "Announcement"
