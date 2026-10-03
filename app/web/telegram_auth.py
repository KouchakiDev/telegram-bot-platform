from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from app.core.exceptions import AuthenticationError


@dataclass(slots=True, frozen=True)
class MiniAppUser:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    photo_url: str | None


def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86_400) -> MiniAppUser:
    if not init_data or len(init_data) > 10_000:
        raise AuthenticationError("Invalid Mini App init data")
    try:
        pairs = parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
    except ValueError as exc:
        raise AuthenticationError("Invalid Mini App init data") from exc
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise AuthenticationError("Duplicate Mini App fields are not allowed")
    parsed = dict(pairs)
    received_hash = parsed.pop("hash", None)
    if not received_hash or len(received_hash) != 64:
        raise AuthenticationError("Missing Mini App signature")

    check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise AuthenticationError("Mini App signature verification failed")

    auth_date_raw = parsed.get("auth_date")
    try:
        auth_date = int(auth_date_raw or "0")
    except ValueError as exc:
        raise AuthenticationError("Invalid Mini App auth date") from exc
    now = int(time.time())
    if auth_date <= 0 or now - auth_date > max_age_seconds:
        raise AuthenticationError("Mini App authentication data is expired")
    if auth_date - now > 60:
        raise AuthenticationError("Mini App authentication data is from the future")

    raw_user = parsed.get("user")
    if not raw_user:
        raise AuthenticationError("Mini App user data is missing")
    try:
        data = json.loads(raw_user)
        telegram_id = int(data["id"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise AuthenticationError("Mini App user data is invalid") from exc

    return MiniAppUser(
        telegram_id=telegram_id,
        username=data.get("username"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        language_code=data.get("language_code"),
        photo_url=data.get("photo_url"),
    )
