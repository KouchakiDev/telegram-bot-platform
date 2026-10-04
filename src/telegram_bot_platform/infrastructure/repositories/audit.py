from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.infrastructure.db.models import AuditEventModel, ChatModel, ContentModel, UserModel


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        actor_telegram_id: int | None,
        action: str,
        target: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.session.add(
            AuditEventModel(
                actor_telegram_id=actor_telegram_id,
                action=action,
                target=target,
                metadata_json=metadata or {},
            )
        )
        await self.session.flush()

    async def summary(self) -> dict[str, int]:
        users = int((await self.session.execute(select(func.count(UserModel.id)))).scalar_one())
        chats = int((await self.session.execute(select(func.count(ChatModel.id)))).scalar_one())
        content = int((await self.session.execute(select(func.count(ContentModel.id)))).scalar_one())
        audit_events = int((await self.session.execute(select(func.count(AuditEventModel.id)))).scalar_one())
        return {"users": users, "chats": chats, "content": content, "audit_events": audit_events}

    async def list_recent(self, limit: int = 100, offset: int = 0) -> list[AuditEventModel]:
        result = await self.session.execute(
            select(AuditEventModel)
            .order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
            .offset(max(0, offset))
            .limit(max(1, min(limit, 200)))
        )
        return list(result.scalars())
