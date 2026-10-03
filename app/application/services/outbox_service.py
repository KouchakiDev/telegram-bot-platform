from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OutboxMessageInput, ScheduledJobInput
from app.infrastructure.repositories.work import WorkRepository


class OutboxService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = WorkRepository(session)

    async def enqueue_message(self, message: OutboxMessageInput) -> int:
        row = await self.repo.enqueue_message(message)
        await self.session.commit()
        return row.id

    async def enqueue_job(self, job: ScheduledJobInput) -> int:
        row = await self.repo.enqueue_job(job)
        await self.session.commit()
        return row.id
