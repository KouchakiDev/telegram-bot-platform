from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OutboxMessageInput, ScheduledJobInput
from app.domain.enums import TaskStatus
from app.infrastructure.db.models import OutboxMessageModel, ScheduledJobModel


class WorkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def enqueue_message(self, message: OutboxMessageInput) -> OutboxMessageModel:
        model = OutboxMessageModel(chat_id=message.chat_id, text=message.text, parse_mode=message.parse_mode)
        self.session.add(model)
        await self.session.flush()
        return model

    async def enqueue_job(self, job: ScheduledJobInput) -> ScheduledJobModel:
        model = ScheduledJobModel(kind=job.kind, run_at=job.run_at, payload=job.payload)
        self.session.add(model)
        await self.session.flush()
        return model

    async def claim_due_jobs(self, limit: int) -> list[ScheduledJobModel]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(ScheduledJobModel)
            .where(ScheduledJobModel.status == TaskStatus.PENDING, ScheduledJobModel.run_at <= now)
            .order_by(ScheduledJobModel.run_at.asc(), ScheduledJobModel.id.asc())
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        jobs = list(result.scalars())
        for job in jobs:
            job.status = TaskStatus.PROCESSING
            job.attempts += 1
            job.locked_at = now
        await self.session.flush()
        return jobs

    async def claim_outbox(self, limit: int) -> list[OutboxMessageModel]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(OutboxMessageModel)
            .where(OutboxMessageModel.status == TaskStatus.PENDING)
            .order_by(OutboxMessageModel.created_at.asc(), OutboxMessageModel.id.asc())
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        rows = list(result.scalars())
        for row in rows:
            row.status = TaskStatus.PROCESSING
            row.attempts += 1
            row.locked_at = now
        await self.session.flush()
        return rows

    async def complete_job(self, job: ScheduledJobModel) -> None:
        job.status = TaskStatus.COMPLETED
        job.finished_at = datetime.now(timezone.utc)
        job.locked_at = None
        await self.session.flush()

    async def fail_job(self, job: ScheduledJobModel, error: str, max_attempts: int) -> None:
        job.last_error = error[:4000]
        job.locked_at = None
        job.status = TaskStatus.FAILED if job.attempts >= max_attempts else TaskStatus.PENDING
        await self.session.flush()

    async def complete_outbox(self, row: OutboxMessageModel) -> None:
        row.status = TaskStatus.COMPLETED
        row.finished_at = datetime.now(timezone.utc)
        row.locked_at = None
        await self.session.flush()

    async def fail_outbox(self, row: OutboxMessageModel, error: str, max_attempts: int) -> None:
        row.last_error = error[:4000]
        row.locked_at = None
        row.status = TaskStatus.FAILED if row.attempts >= max_attempts else TaskStatus.PENDING
        await self.session.flush()
