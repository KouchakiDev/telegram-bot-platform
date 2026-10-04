from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from telegram_bot_platform.infrastructure.repositories.localizations import LocalizationRepository

SUPPORTED_LOCALES = ("en", "fa")
RESOURCE_DIR = Path(__file__).resolve().parents[3] / "resources" / "i18n"
OVERRIDE_PATH = Path("data/i18n_overrides.json")
COMPAT_CATALOG = RESOURCE_DIR / "compat_catalog.json"
KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")


class LocalizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = LocalizationRepository(session)

    @staticmethod
    def _load(locale: str) -> dict[str, str]:
        path = RESOURCE_DIR / f"{locale}.json"
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    @classmethod
    def defaults(cls, locale: str) -> dict[str, str]:
        if locale not in SUPPORTED_LOCALES:
            locale = "en"
        data = cls._load(locale)
        try:
            compat_rows = json.loads(COMPAT_CATALOG.read_text(encoding="utf-8")).get("items", [])
            for row in compat_rows:
                key = str(row.get("key", ""))
                if key:
                    data[key] = str(row.get(locale, row.get("source", key)))
        except (OSError, json.JSONDecodeError):
            pass
        if OVERRIDE_PATH.exists():
            try:
                overrides = json.loads(OVERRIDE_PATH.read_text(encoding="utf-8"))
                data.update(overrides.get(locale, {}))
            except (OSError, json.JSONDecodeError):
                pass
        return data

    async def seed(self) -> None:
        en = self.defaults("en")
        fa = self.defaults("fa")
        for key in sorted(set(en) | set(fa)):
            for locale, source in (("en", en), ("fa", fa)):
                value = source.get(key, en.get(key, key))
                category = key.split(".")[0]
                await self.repo.upsert(key, locale, value, category=category, description=None)
        await self.session.commit()
        await self._export_all()

    async def get(self, key: str, locale: str, **values: object) -> str:
        locale = locale if locale in SUPPORTED_LOCALES else "en"
        row = await self.repo.get(key, locale)
        template = row.value if row else self.defaults(locale).get(key, key)
        try:
            return template.format(**values)
        except (KeyError, ValueError):
            return template

    async def bundle(self, locale: str) -> dict[str, str]:
        locale = locale if locale in SUPPORTED_LOCALES else "en"
        defaults = self.defaults(locale)
        rows = await self.repo.list_all(locale)
        defaults.update({row.key: row.value for row in rows})
        return defaults

    async def list_pairs(self) -> list[dict[str, object]]:
        en = await self.repo.list_all("en")
        fa = await self.repo.list_all("fa")
        en_map = {row.key: row for row in en}
        fa_map = {row.key: row for row in fa}
        keys = sorted(set(en_map) | set(fa_map))
        return [
            {
                "key": key,
                "category": (en_map.get(key) or fa_map[key]).category,
                "description": (en_map.get(key) or fa_map[key]).description,
                "en": (en_map.get(key).value if en_map.get(key) else self.defaults("en").get(key, "")),
                "fa": (fa_map.get(key).value if fa_map.get(key) else self.defaults("fa").get(key, "")),
            }
            for key in keys
        ]

    async def save_pair(self, key: str, en: str, fa: str, actor_id: int | None) -> None:
        if not KEY_PATTERN.fullmatch(key) or len(key) > 160:
            raise ValueError("Invalid localization key")
        category = key.split(".")[0]
        await self.repo.upsert(key, "en", en, category=category, description=None)
        await self.repo.upsert(key, "fa", fa, category=category, description=None)
        return

    @classmethod
    def _base_defaults(cls, locale: str) -> dict[str, str]:
        path_data = cls._load(locale)
        try:
            compat_rows = json.loads(COMPAT_CATALOG.read_text(encoding="utf-8")).get("items", [])
            for row in compat_rows:
                item_key = str(row.get("key", ""))
                if item_key:
                    path_data[item_key] = str(row.get(locale, row.get("source", item_key)))
        except (OSError, json.JSONDecodeError):
            pass
        return path_data

    async def reset(self, key: str, actor_id: int | None) -> None:
        if not KEY_PATTERN.fullmatch(key) or len(key) > 160:
            raise ValueError("Invalid localization key")
        en = self._base_defaults("en")
        fa = self._base_defaults("fa")
        for locale, source in (("en", en), ("fa", fa)):
            await self.repo.upsert(key, locale, source.get(key, key), category=key.split(".")[0], description=None)

    async def export_overrides(self) -> None:
        await self._export_all()

    async def _export_all(self) -> None:
        rows = await self.repo.list_all()
        payload: dict[str, dict[str, str]] = {locale: {} for locale in SUPPORTED_LOCALES}
        defaults = {locale: self._load(locale) for locale in SUPPORTED_LOCALES}
        for locale in SUPPORTED_LOCALES:
            payload[locale].update(defaults[locale])
        for row in rows:
            payload.setdefault(row.locale, {})[row.key] = row.value
        OVERRIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
        OVERRIDE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def merge_overrides(data: Mapping[str, Mapping[str, str]]) -> None:
    OVERRIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {locale: dict(values) for locale, values in data.items() if locale in SUPPORTED_LOCALES}
    OVERRIDE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
