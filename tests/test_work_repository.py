import pytest

pytest.importorskip("aiosqlite")

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from telegram_bot_platform.domain.entities import ScheduledJobInput
from telegram_bot_platform.domain.enums import TaskKind, TaskStatus
from telegram_bot_platform.infrastructure.db.base import Base
from telegram_bot_platform.infrastructure.db import models  # noqa: F401
from telegram_bot_platform.infrastructure.repositories.work import WorkRepository


@pytest.mark.asyncio
async def test_claim_and_complete_due_job() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        repo = WorkRepository(session)
        job = await repo.enqueue_job(
            ScheduledJobInput(
                kind=TaskKind.SEND_MESSAGE,
                run_at=datetime.now(timezone.utc) - timedelta(seconds=1),
                payload={"chat_id": 1, "text": "hello"},
            )
        )
        await session.commit()
        claimed = await repo.claim_due_jobs(10)
        assert len(claimed) == 1
        assert claimed[0].id == job.id
        assert claimed[0].status == TaskStatus.PROCESSING
        await repo.complete_job(claimed[0])
        await session.commit()
        assert claimed[0].status == TaskStatus.COMPLETED
    await engine.dispose()
