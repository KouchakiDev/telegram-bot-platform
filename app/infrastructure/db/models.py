from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PythonEnum
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import ChatType, ContentStatus, MatchMode, TaskKind, TaskStatus, UserRole
from app.infrastructure.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def enum_values(enum_type: type[PythonEnum]) -> list[str]:
    return [str(member.value) for member in enum_type]


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    language_code: Mapped[str | None] = mapped_column(String(16))
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class UserRoleModel(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, values_callable=enum_values), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    __table_args__ = (UniqueConstraint("telegram_id", "role", name="uq_user_roles"),)


class ChatModel(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    chat_type: Mapped[ChatType] = mapped_column(Enum(ChatType, native_enum=False, values_callable=enum_values), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255))
    locale: Mapped[str] = mapped_column(String(16), default="fa", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ChatSettingsModel(Base):
    __tablename__ = "chat_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), unique=True, nullable=False)
    modules: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)



class AdminModel(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(64), default="administrator", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ContentModel(Base):
    __tablename__ = "content_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus, native_enum=False, values_callable=enum_values), default=ContentStatus.DRAFT, nullable=False, index=True)
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    target_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class AutoReplyRuleModel(Base):
    __tablename__ = "auto_reply_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trigger: Mapped[str] = mapped_column(String(255), nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    match_mode: Mapped[MatchMode] = mapped_column(Enum(MatchMode, native_enum=False, values_callable=enum_values), default=MatchMode.CONTAINS, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ScheduledJobModel(Base):
    __tablename__ = "scheduled_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[TaskKind] = mapped_column(Enum(TaskKind, native_enum=False, values_callable=enum_values), nullable=False, index=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False, values_callable=enum_values), default=TaskStatus.PENDING, nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_scheduled_jobs_due", "status", "run_at"),)


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    parse_mode: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False, values_callable=enum_values), default=TaskStatus.PENDING, nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_outbox_messages_pending", "status", "created_at"),)


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_telegram_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    target: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
