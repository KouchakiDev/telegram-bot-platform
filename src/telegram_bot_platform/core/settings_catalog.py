from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from pydantic import SecretStr


@dataclass(frozen=True, slots=True)
class SettingDescriptor:
    key: str
    field_name: str
    env_name: str
    category: str
    label_key: str
    description_key: str
    secret: bool = False
    editable: bool = True
    restart_required: bool = False
    value_type: str | None = None


SETTING_DESCRIPTORS: tuple[SettingDescriptor, ...] = (
    SettingDescriptor("app.name", "app_name", "APP_NAME", "app", "app.brand", "app.subtitle", restart_required=True),
    SettingDescriptor("runtime.environment", "environment", "ENVIRONMENT", "runtime", "settings.environment", "settings.description", restart_required=True),
    SettingDescriptor("runtime.default_locale", "default_locale", "DEFAULT_LOCALE", "runtime", "nav.settings", "settings.description", restart_required=True),
    SettingDescriptor("telegram.core.username", "telegram_bot_username", "TELEGRAM_BOT_USERNAME", "telegram", "bots.username", "bots.description"),
    SettingDescriptor("telegram.core.token", "telegram_bot_token", "TELEGRAM_BOT_TOKEN", "telegram", "bots.token", "bots.description", secret=True, restart_required=True),
    SettingDescriptor("telegram.access.admin_user_ids", "admin_user_ids", "ADMIN_USER_IDS", "telegram", "settings.value", "settings.description", value_type="list"),
    SettingDescriptor("telegram.core.default_channel_id", "default_channel_id", "DEFAULT_CHANNEL_ID", "telegram", "scheduling.target_chat_id", "settings.description", value_type="int"),
    SettingDescriptor("telegram.concurrency.concurrent_updates", "telegram_concurrent_updates", "TELEGRAM_CONCURRENT_UPDATES", "telegram", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("telegram.concurrency.connection_pool_size", "telegram_connection_pool_size", "TELEGRAM_CONNECTION_POOL_SIZE", "telegram", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("telegram.rate.overall_per_second", "telegram_overall_rate_per_second", "TELEGRAM_OVERALL_RATE_PER_SECOND", "telegram", "settings.value", "settings.description", restart_required=True, value_type="float"),
    SettingDescriptor("telegram.rate.group_per_second", "telegram_group_rate_per_second", "TELEGRAM_GROUP_RATE_PER_SECOND", "telegram", "settings.value", "settings.description", restart_required=True, value_type="float"),
    SettingDescriptor("telegram.bootstrap_retries", "telegram_bootstrap_retries", "TELEGRAM_BOOTSTRAP_RETRIES", "telegram", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("telegram.timeout.seconds", "telegram_timeout_seconds", "TELEGRAM_TIMEOUT_SECONDS", "telegram", "settings.value", "settings.description", restart_required=True, value_type="float"),
    SettingDescriptor("web.host", "web_host", "WEB_HOST", "web", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("web.port", "web_port", "WEB_PORT", "web", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("web.url", "web_app_url", "WEB_APP_URL", "web", "bots.description", "settings.description", restart_required=True),
    SettingDescriptor("web.cors.allowed_origins", "cors_allowed_origins", "CORS_ALLOWED_ORIGINS", "security", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("web.session.cookie_name", "session_cookie_name", "SESSION_COOKIE_NAME", "security", "settings.key", "settings.description", restart_required=True),
    SettingDescriptor("web.session.max_age_seconds", "session_max_age_seconds", "SESSION_MAX_AGE_SECONDS", "security", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("web.session.cookie_secure", "session_cookie_secure", "SESSION_COOKIE_SECURE", "security", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("security.app_secret_key", "app_secret_key", "APP_SECRET_KEY", "security", "settings.key", "settings.description", secret=True, restart_required=True),
    SettingDescriptor("security.rate_limit_requests", "rate_limit_requests", "RATE_LIMIT_REQUESTS", "security", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("security.rate_limit_window_seconds", "rate_limit_window_seconds", "RATE_LIMIT_WINDOW_SECONDS", "security", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("worker.scheduler_enabled", "scheduler_enabled", "SCHEDULER_ENABLED", "worker", "dashboard.scheduler", "scheduling.description"),
    SettingDescriptor("worker.batch_size", "worker_batch_size", "WORKER_BATCH_SIZE", "worker", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("worker.poll_interval_seconds", "worker_poll_interval_seconds", "WORKER_POLL_INTERVAL_SECONDS", "worker", "settings.value", "settings.description", restart_required=True, value_type="float"),
    SettingDescriptor("worker.outbox_max_attempts", "outbox_max_attempts", "OUTBOX_MAX_ATTEMPTS", "worker", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("automation.cache_ttl_seconds", "auto_reply_cache_ttl_seconds", "AUTO_REPLY_CACHE_TTL_SECONDS", "automation", "settings.value", "automation.description", restart_required=True, value_type="float"),
    SettingDescriptor("automation.max_rules", "auto_reply_max_rules", "AUTO_REPLY_MAX_RULES", "automation", "settings.value", "automation.description", restart_required=True, value_type="int"),
    SettingDescriptor("database.url", "database_url", "DATABASE_URL", "database", "settings.key", "settings.description", secret=True, restart_required=True),
    SettingDescriptor("database.pool_size", "db_pool_size", "DB_POOL_SIZE", "database", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("database.max_overflow", "db_max_overflow", "DB_MAX_OVERFLOW", "database", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("database.pool_recycle", "db_pool_recycle", "DB_POOL_RECYCLE", "database", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("bots.admin.token", "bot_admin_token", "BOT_ADMIN_TOKEN", "bots", "bots.admin", "bots.description", secret=True, restart_required=True),
    SettingDescriptor("bots.client.token", "bot_client_token", "BOT_CLIENT_TOKEN", "bots", "bots.client", "bots.description", secret=True, restart_required=True),
    SettingDescriptor("bots.staff.token", "bot_staff_token", "BOT_STAFF_TOKEN", "bots", "bots.staff", "bots.description", secret=True, restart_required=True),
    SettingDescriptor("bots.auto_responder.token", "bot_autoresponder_token", "BOT_AUTO_RESPONDER_TOKEN", "bots", "bots.auto_responder", "bots.description", secret=True, restart_required=True),
    SettingDescriptor("bots.admin.username", "admin_bot_username", "ADMIN_BOT_USERNAME", "bots", "bots.username", "bots.description"),
    SettingDescriptor("bots.client.username", "client_bot_username", "CLIENT_BOT_USERNAME", "bots", "bots.description", "bots.description"),
    SettingDescriptor("bots.staff.username", "staff_bot_username", "STAFF_BOT_USERNAME", "bots", "bots.description", "bots.description"),
    SettingDescriptor("bots.admin.id", "admin_bot_id", "ADMIN_BOT_ID", "bots", "bots.bot", "bots.description"),
    SettingDescriptor("bots.client.id", "client_bot_id", "CLIENT_BOT_ID", "bots", "bots.description", "bots.description"),
    SettingDescriptor("bots.staff.id", "staff_bot_id", "STAFF_BOT_ID", "bots", "bots.description", "bots.description"),
    SettingDescriptor("channels.main.id", "compat_channel_id", "CHANNEL_ID", "channels", "settings.value", "settings.description"),
    SettingDescriptor("channels.archive.id", "compat_archive_channel_id", "ARCHIVE_CHANNEL", "channels", "settings.value", "settings.description"),
    SettingDescriptor("channels.photos.id", "compat_photos_channel_id", "PHOTOS_CHANNEL", "channels", "settings.value", "settings.description"),
    SettingDescriptor("channels.profile.tags", "profile_channel_tags", "PROFILE_CHANNEL_TAGS", "channels", "settings.value", "settings.description"),
    SettingDescriptor("database.legacy.name", "db_name", "DB_NAME", "database", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("database.legacy.host", "db_host", "DB_HOST", "database", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("database.legacy.user", "db_user", "DB_USER", "database", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("database.legacy.password", "db_password", "DB_PASSWORD", "database", "settings.value", "settings.description", secret=True, restart_required=True),
    SettingDescriptor("database.legacy.port", "db_port", "DB_PORT", "database", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("database.locations.path", "db_locations", "DB_LOCATIONS", "database", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("paths.images", "images_dir", "IMAGES_DIR", "paths", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("paths.watermark", "watermark_path", "WATERMARK_PATH", "paths", "settings.value", "settings.description", restart_required=True),
    SettingDescriptor("admin.primary.id", "primary_admin_id", "PRIMARY_ADMIN_ID", "admin", "settings.value", "settings.description", restart_required=True, value_type="int"),
    SettingDescriptor("admin.primary.username", "primary_admin_username", "PRIMARY_ADMIN_USERNAME", "admin", "settings.value", "settings.description"),
    SettingDescriptor("admin.primary.name", "primary_admin_name", "PRIMARY_ADMIN_NAME", "admin", "settings.value", "settings.description"),
    SettingDescriptor("admin.primary.phone", "primary_admin_phone", "PRIMARY_ADMIN_PHONE", "admin", "settings.value", "settings.description", secret=True),
    SettingDescriptor("admin.support.username", "admin_support_username", "ADMIN_SUPPORT_USERNAME", "admin", "settings.value", "settings.description"),
    SettingDescriptor("deploy.remote.host", "remote_host", "REMOTE_HOST", "deployment", "settings.value", "settings.description"),
    SettingDescriptor("deploy.remote.user", "remote_user", "REMOTE_USER", "deployment", "settings.value", "settings.description"),
    SettingDescriptor("deploy.remote.password", "remote_pass", "REMOTE_PASS", "deployment", "settings.value", "settings.description", secret=True),
    SettingDescriptor("deploy.remote.upload_dir", "remote_upload_dir", "REMOTE_UPLOAD_DIR", "deployment", "settings.value", "settings.description"),
    SettingDescriptor("deploy.work_dir", "deploy_work_dir", "DEPLOY_WORK_DIR", "deployment", "settings.value", "settings.description"),
    SettingDescriptor("deploy.backup_dir", "deploy_backup_dir", "DEPLOY_BACKUP_DIR", "deployment", "settings.value", "settings.description"),
    SettingDescriptor("deploy.zip_prefix", "deploy_zip_prefix", "DEPLOY_ZIP_PREFIX", "deployment", "settings.value", "settings.description"),
    SettingDescriptor("compat.favorites_enabled", "add_favorites_for_normal_users", "ADD_FAVORITES_FOR_NORMAL_USERS", "compatibility", "settings.value", "settings.description", value_type="bool"),
    SettingDescriptor("compat.duration_minutes", "duration_time", "DURATION_TIME", "compatibility", "settings.value", "settings.description", value_type="int"),
    SettingDescriptor("compat.booking_window_minutes", "betwin_time", "BETWIN_TIME", "compatibility", "settings.value", "settings.description", value_type="int"),
    SettingDescriptor("compat.dispatch_multiplier", "multiplier_dispatch", "MULTIPLIER_DISPATCH", "compatibility", "settings.value", "settings.description", value_type="int"),
)


def descriptor_map() -> dict[str, SettingDescriptor]:
    return {item.key: item for item in SETTING_DESCRIPTORS}


def serialize_value(value: Any, *, secret: bool = False) -> Any:
    if secret and value:
        return "••••••••"
    if isinstance(value, SecretStr):
        return "••••••••" if value.get_secret_value() else None
    if isinstance(value, tuple):
        return list(value)
    return value


def catalog_dict() -> list[dict[str, object]]:
    return [asdict(item) for item in SETTING_DESCRIPTORS]
