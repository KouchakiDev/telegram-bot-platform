# Security Checklist

- Store tokens and passwords only in environment/secrets management.
- Rotate any credentials exposed in a development archive.
- Keep `APP_SECRET_KEY` long, random, and environment-specific.
- Use HTTPS for the Mini App in production.
- Keep `SESSION_COOKIE_SECURE=true` in production.
- Limit `CORS_ALLOWED_ORIGINS` to trusted origins.
- Validate Mini App `initData` on every authentication exchange.
- Do not trust `initDataUnsafe` for authorization.
- Keep administrator IDs explicit; never infer admin status from usernames.
- Keep bot permissions minimal in target chats.
- Do not log authentication material or user-provided secrets.
