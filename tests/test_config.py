from pytest import raises
from pydantic import SecretStr

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.web.app import create_app


def test_admin_id_parsing() -> None:
    settings = Settings(
        environment="testing",
        app_secret_key=SecretStr("secret"),
        admin_user_ids="1, 2,3",
    )
    assert settings.admin_user_ids == (1, 2, 3)


def test_production_web_app_requires_secret_key() -> None:
    with raises(RuntimeError, match="APP_SECRET_KEY is required in production"):
        create_app(Settings(environment="production"))
