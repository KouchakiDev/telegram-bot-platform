from __future__ import annotations

from dataclasses import dataclass

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.infrastructure.db.session import Database


@dataclass(slots=True)
class Container:
    settings: Settings
    database: Database

    @classmethod
    def build(cls, settings: Settings | None = None) -> "Container":
        resolved = settings or Settings()
        return cls(resolved, Database(resolved))

    async def shutdown(self) -> None:
        await self.database.dispose()
