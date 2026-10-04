import hashlib
import hmac
import json
import time
from urllib.parse import quote

import pytest

from telegram_bot_platform.core.exceptions import AuthenticationError
from telegram_bot_platform.web.telegram_auth import validate_init_data


def make_init_data(token: str, user_id: int = 123) -> str:
    auth_date = int(time.time())
    user_json = json.dumps({"id": user_id, "first_name": "Test", "language_code": "en"}, separators=(",", ":"))
    values = {"auth_date": str(auth_date), "query_id": "query", "user": user_json}
    check = "\n".join(f"{k}={v}" for k, v in sorted(values.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    signature = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return f"auth_date={auth_date}&query_id=query&user={quote(user_json)}&hash={signature}"


def test_valid_init_data() -> None:
    result = validate_init_data(make_init_data("bot-token"), "bot-token")
    assert result.telegram_id == 123


def test_tampered_init_data_is_rejected() -> None:
    raw = make_init_data("bot-token").replace("Test", "Other")
    with pytest.raises(AuthenticationError):
        validate_init_data(raw, "bot-token")


def test_duplicate_fields_are_rejected() -> None:
    raw = make_init_data("bot-token")
    with pytest.raises(AuthenticationError):
        validate_init_data(raw + "&auth_date=1", "bot-token")
