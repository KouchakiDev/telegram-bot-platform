from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from telegram_bot_platform.domain.enums import ChatType, MatchMode, TaskKind, UserRole


@dataclass(slots=True, frozen=True)
class UserIdentity:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    is_bot: bool


@dataclass(slots=True, frozen=True)
class ChatIdentity:
    telegram_id: int
    chat_type: ChatType
    title: str | None
    username: str | None


@dataclass(slots=True, frozen=True)
class ContentInput:
    title: str
    body: str
    created_by: int


@dataclass(slots=True, frozen=True)
class AutoReplyMatch:
    rule_id: int
    response: str


@dataclass(slots=True, frozen=True)
class ScheduledJobInput:
    kind: TaskKind
    run_at: datetime
    payload: dict[str, Any]


@dataclass(slots=True, frozen=True)
class OutboxMessageInput:
    chat_id: int
    text: str
    parse_mode: str | None = None


@dataclass(slots=True, frozen=True)
class AutoReplyRuleInput:
    trigger: str
    response: str
    match_mode: MatchMode
    priority: int = 100


@dataclass(slots=True, frozen=True)
class UserRoleAssignment:
    telegram_id: int
    role: UserRole
