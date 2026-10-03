from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BeforeValidator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_int_list(value: object) -> tuple[int, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, str):
        return tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if isinstance(value, (list, tuple, set)):
        return tuple(int(item) for item in value)
    raise TypeError("Expected a comma-separated list of integers")


def _parse_str_list(value: object) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    raise TypeError("Expected a comma-separated list of strings")


AdminIdList = Annotated[tuple[int, ...], BeforeValidator(_parse_int_list)]
StringList = Annotated[tuple[str, ...], BeforeValidator(_parse_str_list)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    environment: Literal["development", "testing", "staging", "production"] = "development"
    app_name: str = "Telegram Bot Platform"
    app_secret_key: SecretStr | None = None

    telegram_bot_token: SecretStr | None = None
    telegram_bot_username: str | None = None
    default_channel_id: int | None = None
    admin_user_ids: AdminIdList = ()
    telegram_concurrent_updates: int = 8
    telegram_connection_pool_size: int = 16
    telegram_overall_rate_per_second: float = 30.0
    telegram_group_rate_per_second: float = 20.0
    telegram_bootstrap_retries: int = 3

    web_host: str = "0.0.0.0"
    web_port: int = 8000
    web_app_url: str = "http://localhost:8000"
    cors_allowed_origins: StringList = ("http://localhost:8000",)
    session_cookie_name: str = "platform_session"
    session_max_age_seconds: int = 86_400
    session_cookie_secure: bool = False

    database_url: str = "sqlite+aiosqlite:///./data/platform.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 1_800

    log_level: str = "INFO"
    log_json: bool = False
    telegram_timeout_seconds: float = 10.0
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    scheduler_enabled: bool = True
    worker_batch_size: int = 20
    worker_poll_interval_seconds: float = 2.0
    outbox_max_attempts: int = 5
    auto_reply_cache_ttl_seconds: float = 30.0
    auto_reply_max_rules: int = 500

    default_locale: str = "en"

    def require_bot_token(self) -> str:
        if not self.telegram_bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required for the bot/worker process")
        return self.telegram_bot_token.get_secret_value()

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @classmethod
    def for_testing(cls) -> "Settings":
        return cls(
            environment="testing",
            app_secret_key=SecretStr("test-secret-key"),
            database_url="sqlite+aiosqlite:///:memory:",
            cors_allowed_origins=("http://testserver",),
        )
