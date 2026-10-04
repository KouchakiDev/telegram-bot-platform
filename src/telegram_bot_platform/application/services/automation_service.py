from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from telegram_bot_platform.domain.enums import MatchMode
from telegram_bot_platform.infrastructure.repositories.audit import AuditRepository
from telegram_bot_platform.infrastructure.repositories.automation import AutoReplyRepository


@dataclass(slots=True, frozen=True)
class CachedRule:
    rule_id: int
    trigger: str
    response: str
    mode: MatchMode
    priority: int


@dataclass(slots=True, frozen=True)
class AutoReplyResult:
    response: str | None
    rule_id: int | None


class AutomationService:
    """Matches auto-reply rules while keeping a small TTL cache of stable rule data."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        cache_ttl_seconds: float = 30.0,
        max_rules: int = 500,
    ) -> None:
        self.session_factory = session_factory
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_rules = max_rules
        self._cache: tuple[float, tuple[CachedRule, ...]] | None = None

    async def _rules(self) -> tuple[CachedRule, ...]:
        now = time.monotonic()
        if self._cache and now - self._cache[0] < self.cache_ttl_seconds:
            return self._cache[1]
        async with self.session_factory() as session:
            rows = await AutoReplyRepository(session).enabled_rules(self.max_rules)
            rules = tuple(
                CachedRule(row.id, row.trigger.casefold(), row.response, row.match_mode, row.priority)
                for row in rows
            )
        self._cache = (now, rules)
        return rules

    async def match(self, text: str) -> AutoReplyResult:
        normalized = text.strip().casefold()
        if not normalized:
            return AutoReplyResult(None, None)
        for rule in await self._rules():
            matched = False
            if rule.mode == MatchMode.EXACT:
                matched = normalized == rule.trigger
            elif rule.mode == MatchMode.CONTAINS:
                matched = rule.trigger in normalized
            elif rule.mode == MatchMode.REGEX:
                try:
                    matched = re.search(rule.trigger, normalized, re.IGNORECASE) is not None
                except re.error:
                    continue
            if matched:
                async with self.session_factory() as session:
                    await AutoReplyRepository(session).increment_usage(rule.rule_id)
                    await session.commit()
                return AutoReplyResult(rule.response, rule.rule_id)
        return AutoReplyResult(None, None)

    async def record_admin_change(self, actor_id: int, action: str, target: str) -> None:
        async with self.session_factory() as session:
            await AuditRepository(session).record(actor_id, action, target)
            await session.commit()
