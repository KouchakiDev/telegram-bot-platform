from enum import StrEnum


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    SUPPORT = "support"
    MODERATOR = "moderator"
    ANALYST = "analyst"
    CUSTOMER = "customer"
    MEMBER = "member"


class ContentStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class MatchMode(StrEnum):
    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"


class TaskStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskKind(StrEnum):
    PUBLISH_CONTENT = "publish_content"
    SEND_MESSAGE = "send_message"


class ChatType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"
