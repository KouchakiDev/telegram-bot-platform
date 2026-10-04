from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from telegram_bot_platform.core.exceptions import AuthenticationError


class SessionSigner:
    def __init__(self, secret_key: str, max_age_seconds: int) -> None:
        self.max_age_seconds = max_age_seconds
        self.serializer = URLSafeTimedSerializer(secret_key, salt="telegram-platform-session")

    def issue(self, telegram_id: int, bot_key: str = "core", locale: str = "en") -> str:
        return self.serializer.dumps({"sub": telegram_id, "bot": bot_key, "locale": locale})

    def verify_context(self, token: str) -> tuple[int, str, str]:
        try:
            payload = self.serializer.loads(token, max_age=self.max_age_seconds)
            subject = int(payload["sub"])
            bot_key = str(payload.get("bot", "core"))
            locale = str(payload.get("locale", "en"))
        except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid or expired session") from exc
        return subject, bot_key, locale

    def verify(self, token: str) -> int:
        return self.verify_context(token)[0]
