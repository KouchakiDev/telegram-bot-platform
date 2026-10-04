from __future__ import annotations

import asyncio
import logging

from telegram import Bot

from telegram_bot_platform.application.services.content_service import ContentService
from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.core.container import Container
from telegram_bot_platform.core.text import escape_telegram_html
from telegram_bot_platform.domain.enums import TaskKind
from telegram_bot_platform.infrastructure.repositories.work import WorkRepository
from telegram_bot_platform.telegram.gateway import TelegramGateway

logger = logging.getLogger("platform.worker")


class OutboxWorker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.container = Container.build(settings)
        self.bot = Bot(settings.require_bot_token())
        self.gateway = TelegramGateway(self.bot)
        self._stopping = asyncio.Event()

    async def run(self) -> None:
        initialized = False
        try:
            logger.info("Worker started")
            await self.bot.initialize()
            initialized = True
            await self.bot.get_me()
            while not self._stopping.is_set():
                processed = await self._process_batch()
                if processed == 0:
                    try:
                        await asyncio.wait_for(
                            self._stopping.wait(), timeout=self.settings.worker_poll_interval_seconds
                        )
                    except asyncio.TimeoutError:
                        pass
        finally:
            if initialized:
                await self.bot.shutdown()
            await self.container.shutdown()
            logger.info("Worker stopped")

    async def _process_batch(self) -> int:
        total = 0
        async with self.container.database.session_factory() as session:
            repo = WorkRepository(session)
            jobs = (
                await repo.claim_due_jobs(self.settings.worker_batch_size)
                if self.settings.scheduler_enabled
                else []
            )
            for job in jobs:
                try:
                    if job.kind == TaskKind.SEND_MESSAGE:
                        await self.gateway.send_text(
                            int(job.payload["chat_id"]),
                            str(job.payload["text"]),
                            job.payload.get("parse_mode"),
                        )
                    elif job.kind == TaskKind.PUBLISH_CONTENT:
                        content_id = int(job.payload["content_id"])
                        content = await ContentService(session).repo.get(content_id)
                        if content is None:
                            raise ValueError("Content not found")
                        await ContentService(session).publish(content_id, int(job.payload["actor_id"]) if job.payload.get("actor_id") else None)
                        target_chat_id = job.payload.get("target_chat_id") or content.target_chat_id or self.settings.default_channel_id
                        if target_chat_id:
                            safe_title = escape_telegram_html(content.title)
                            safe_body = escape_telegram_html(content.body)
                            await self.gateway.send_text(
                                int(target_chat_id), f"<b>{safe_title}</b>\n\n{safe_body}", "HTML"
                            )
                    await repo.complete_job(job)
                    total += 1
                except Exception as exc:
                    logger.exception("Scheduled job failed")
                    await repo.fail_job(job, str(exc), self.settings.outbox_max_attempts)

            rows = await repo.claim_outbox(self.settings.worker_batch_size)
            for row in rows:
                try:
                    await self.gateway.send_text(row.chat_id, row.text, row.parse_mode)
                    await repo.complete_outbox(row)
                    total += 1
                except Exception as exc:
                    logger.exception("Outbox delivery failed")
                    await repo.fail_outbox(row, str(exc), self.settings.outbox_max_attempts)
            await session.commit()
        return total

    async def stop(self) -> None:
        self._stopping.set()


def main() -> None:
    import signal
    from telegram_bot_platform.core.logging import configure_logging

    settings = Settings()
    configure_logging(settings.log_level, settings.log_json)
    worker = OutboxWorker(settings)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(worker.stop()))
        except NotImplementedError:
            pass
    try:
        loop.run_until_complete(worker.run())
    finally:
        loop.close()
