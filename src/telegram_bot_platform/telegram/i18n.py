from __future__ import annotations

import json
from pathlib import Path

SUPPORTED_LOCALES = ("en", "fa")
RESOURCE_DIR = Path(__file__).resolve().parents[3] / "resources" / "i18n"
OVERRIDE_FILE = Path("data/i18n_overrides.json")


def _load(locale: str) -> dict[str, str]:
    path = RESOURCE_DIR / f"{locale}.json"
    values: dict[str, str] = {}
    if path.exists():
        try:
            values.update(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    if OVERRIDE_FILE.exists():
        try:
            values.update(json.loads(OVERRIDE_FILE.read_text(encoding="utf-8")).get(locale, {}))
        except (OSError, json.JSONDecodeError):
            pass
    return values


CACHE: dict[str, dict[str, str]] = {locale: _load(locale) for locale in SUPPORTED_LOCALES}


def reload_catalog() -> None:
    CACHE.clear()
    CACHE.update({locale: _load(locale) for locale in SUPPORTED_LOCALES})


def locale_for(language_code: str | None, default: str = "en") -> str:
    candidate = (language_code or default).split("-")[0].lower()
    return candidate if candidate in SUPPORTED_LOCALES else (default if default in SUPPORTED_LOCALES else "en")


def text(key: str, locale: str = "en", **values: object) -> str:
    locale = locale_for(locale)
    template = CACHE.get(locale, {}).get(key) or CACHE.get("en", {}).get(key, key)
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return template
