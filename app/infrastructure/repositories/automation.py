from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import MatchMode
from app.infrastructure.db.models import AutoReplyRuleModel


class AutoReplyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def enabled_rules(self, limit: int = 500) -> list[AutoReplyRuleModel]:
        result = await self.session.execute(
            select(AutoReplyRuleModel)
            .where(AutoReplyRuleModel.enabled.is_(True))
            .order_by(AutoReplyRuleModel.priority.asc(), AutoReplyRuleModel.id.asc())
            .limit(limit)
        )
        return list(result.scalars())

    async def increment_usage(self, rule_id: int) -> None:
        await self.session.execute(
            update(AutoReplyRuleModel)
            .where(AutoReplyRuleModel.id == rule_id)
            .values(usage_count=AutoReplyRuleModel.usage_count + 1)
        )
