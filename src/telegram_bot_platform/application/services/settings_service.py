from __future__ import annotations

from typing import Any

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.core.settings_catalog import SETTING_DESCRIPTORS, SettingDescriptor, serialize_value
from telegram_bot_platform.infrastructure.repositories.platform_settings import PlatformSettingsRepository


class SettingsService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.repo = PlatformSettingsRepository(session)

    @staticmethod
    def _type_name(value: Any) -> str:
        if isinstance(value, SecretStr):
            return "secret"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, (tuple, list)):
            return "list"
        return "string"

    def descriptor(self, key: str) -> SettingDescriptor:
        for item in SETTING_DESCRIPTORS:
            if item.key == key:
                return item
        raise KeyError(key)

    def default_value(self, item: SettingDescriptor) -> Any:
        return getattr(self.settings, item.field_name)

    async def list(self) -> list[dict[str, object]]:
        rows = {row.key: row for row in await self.repo.list_all()}
        output: list[dict[str, object]] = []
        for item in SETTING_DESCRIPTORS:
            row = rows.get(item.key)
            raw = row.value_json if row else self.default_value(item)
            output.append({
                "key": item.key,
                "category": item.category,
                "env_name": item.env_name,
                "label_key": item.label_key,
                "description_key": item.description_key,
                "type": item.value_type or (row.value_type if row else self._type_name(raw)),
                "value": serialize_value(raw, secret=item.secret),
                "secret": item.secret,
                "editable": item.editable,
                "restart_required": item.restart_required,
                "overridden": row is not None,
            })
        return output

    def _coerce(self, item: SettingDescriptor, value: object) -> object:
        target = item.value_type or self._type_name(self.default_value(item))
        if target == "secret":
            return SecretStr(str(value))
        if target == "bool":
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled"}
        if target == "int":
            return int(value)
        if target == "float":
            return float(value)
        if target == "list":
            if isinstance(value, str):
                return tuple(x.strip() for x in value.split(",") if x.strip())
            if isinstance(value, (list, tuple)):
                return tuple(str(x) for x in value if str(x).strip())
            raise TypeError("Expected a list or comma-separated string")
        text = str(value)
        if item.key == "runtime.default_locale" and text not in {"en", "fa"}:
            raise ValueError("Unsupported locale")
        if item.key == "runtime.environment" and text not in {"development", "testing", "staging", "production"}:
            raise ValueError("Unsupported environment")
        return text

    async def save(self, key: str, value: object, actor_id: int | None) -> dict[str, object]:
        item = self.descriptor(key)
        if not item.editable:
            raise PermissionError(key)
        if item.secret and (value is None or str(value) in {"", "••••••••"}):
            raise ValueError("Secret values must be supplied explicitly when changed")
        coerced = self._coerce(item, value)
        stored = coerced.get_secret_value() if isinstance(coerced, SecretStr) else coerced
        row = await self.repo.set(
            key, stored, self._type_name(coerced), item.category,
            secret=item.secret, editable=item.editable, restart_required=item.restart_required, actor_id=actor_id,
        )
        return {"key": row.key, "value": serialize_value(coerced, secret=item.secret), "restart_required": item.restart_required}

    async def reset(self, key: str, actor_id: int | None) -> None:
        self.descriptor(key)
        await self.repo.delete(key)
