from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.domain.enums import MatchMode
from telegram_bot_platform.infrastructure.db.models import AutoReplyRuleModel


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

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[AutoReplyRuleModel]:
        result = await self.session.execute(
            select(AutoReplyRuleModel)
            .order_by(AutoReplyRuleModel.priority.asc(), AutoReplyRuleModel.id.asc())
            .offset(max(0, offset))
            .limit(max(1, min(limit, 200)))
        )
        return list(result.scalars())

    async def get(self, rule_id: int) -> AutoReplyRuleModel | None:
        result = await self.session.execute(
            select(AutoReplyRuleModel).where(AutoReplyRuleModel.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        trigger: str,
        response: str,
        match_mode: MatchMode,
        priority: int,
        enabled: bool,
    ) -> AutoReplyRuleModel:
        model = AutoReplyRuleModel(
            trigger=trigger,
            response=response,
            match_mode=match_mode,
            priority=priority,
            enabled=enabled,
        )
        self.session.add(model)
        await self.session.flush()
        return model

    async def update(
        self,
        model: AutoReplyRuleModel,
        *,
        trigger: str,
        response: str,
        match_mode: MatchMode,
        priority: int,
        enabled: bool,
    ) -> AutoReplyRuleModel:
        model.trigger = trigger
        model.response = response
        model.match_mode = match_mode
        model.priority = priority
        model.enabled = enabled
        model.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return model

    async def toggle(self, model: AutoReplyRuleModel) -> AutoReplyRuleModel:
        model.enabled = not model.enabled
        model.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return model

    async def delete(self, rule_id: int) -> bool:
        result = await self.session.execute(
            delete(AutoReplyRuleModel).where(AutoReplyRuleModel.id == rule_id)
        )
        return bool(result.rowcount)

    async def increment_usage(self, rule_id: int) -> None:
        await self.session.execute(
            update(AutoReplyRuleModel)
            .where(AutoReplyRuleModel.id == rule_id)
            .values(usage_count=AutoReplyRuleModel.usage_count + 1)
        )
