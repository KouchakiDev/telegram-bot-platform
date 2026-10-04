from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.infrastructure.repositories.bots import BotProfileRepository

BOT_DEFINITIONS = (
    ("core", "bots.core", "TELEGRAM_BOT_TOKEN", "telegram_bot_username", ("dashboard", "content", "scheduling", "automation")),
    ("admin", "bots.admin", "BOT_ADMIN_TOKEN", "admin_bot_username", ("dashboard", "content", "scheduling", "automation", "chat_settings", "roles", "audit", "settings", "translations", "bot_profiles", "module_registry")),
    ("client", "bots.client", "BOT_CLIENT_TOKEN", "client_bot_username", ("dashboard", "content", "automation")),
    ("staff", "bots.staff", "BOT_STAFF_TOKEN", "staff_bot_username", ("dashboard", "content", "automation", "scheduling")),
    ("auto_responder", "bots.auto_responder", "BOT_AUTO_RESPONDER_TOKEN", None, ("automation",)),
)


class BotProfileService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.repo = BotProfileRepository(session)

    async def ensure_defaults(self) -> None:
        for bot_key, name_key, env_key, username_field, modules in BOT_DEFINITIONS:
            username = getattr(self.settings, username_field) if username_field else None
            await self.repo.ensure(bot_key, name_key, env_key, username, self.settings.default_locale, {m: True for m in modules})
        await self.session.commit()

    async def list(self) -> list[dict[str, object]]:
        await self.ensure_defaults()
        rows = await self.repo.list_all()
        token_map = {k: token for k, token in self.settings.configured_bot_tokens()}
        return [
            {
                "bot_key": row.bot_key,
                "name_key": row.name_key,
                "token_env_key": row.token_env_key,
                "username": row.username,
                "enabled": row.enabled,
                "default_locale": row.default_locale,
                "modules": row.modules,
                "configured": bool(token_map.get(row.bot_key)),
                "token": "••••••••" if token_map.get(row.bot_key) else None,
                "editable_token": row.token_env_key,
            }
            for row in rows
        ]

    async def modules_for(self, bot_key: str) -> dict[str, bool]:
        row = await self.repo.get(bot_key)
        if row is not None:
            return {str(key): bool(value) for key, value in (row.modules or {}).items()}
        for key, _name_key, _env_key, _username_field, modules in BOT_DEFINITIONS:
            if key == bot_key:
                return {module: True for module in modules}
        return {}

    async def update(self, bot_key: str, payload: dict[str, object], actor_id: int) -> dict[str, object]:
        row = await self.repo.update(
            bot_key,
            username=str(payload.get("username")) if payload.get("username") is not None else None,
            enabled=bool(payload["enabled"]) if "enabled" in payload else None,
            default_locale=str(payload["default_locale"]) if payload.get("default_locale") else None,
            modules={str(k): bool(v) for k, v in dict(payload.get("modules", {})).items()} if payload.get("modules") is not None else None,
            actor_id=actor_id,
        )
        await self.session.commit()
        return {"bot_key": row.bot_key, "username": row.username, "enabled": row.enabled, "default_locale": row.default_locale, "modules": row.modules}
