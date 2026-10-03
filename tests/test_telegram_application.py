import pytest
from pydantic import SecretStr

pytest.importorskip("telegram")
pytest.importorskip("aiolimiter")
pytest.importorskip("aiosqlite")

from app.core.config import Settings
from app.telegram.bot import build_application


@pytest.mark.asyncio
async def test_telegram_application_builds() -> None:
    settings = Settings(
        environment="testing",
        app_secret_key=SecretStr("test-secret-key"),
        telegram_bot_token=SecretStr("123456789:ABCDEF"),
        database_url="sqlite+aiosqlite:///:memory:",
    )
    application, container = build_application(settings)
    try:
        assert application.bot is not None
        assert application.handlers
    finally:
        await container.shutdown()
