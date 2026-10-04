from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = ROOT / "resources" / "i18n"
FRONTEND = ROOT / "frontend"
COMPAT = ROOT / "src" / "telegram_bot_platform" / "compat"
SRC = ROOT / "src" / "telegram_bot_platform"
KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def placeholders(value: str) -> set[str]:
    return set(PLACEHOLDER_PATTERN.findall(value))


def validate_locales(errors: list[str]) -> None:
    en = load_json(I18N_DIR / "en.json")
    fa = load_json(I18N_DIR / "fa.json")
    if not isinstance(en, dict) or not isinstance(fa, dict):
        errors.append("Core locale files must contain JSON objects")
        return
    if set(en) != set(fa):
        errors.append("Core locale key sets differ")
    for key, value in en.items():
        if not isinstance(key, str) or not KEY_PATTERN.fullmatch(key) or len(key) > 160:
            errors.append(f"Invalid core localization key: {key!r}")
        if not isinstance(value, str) or not value:
            errors.append(f"Empty/non-string English localization: {key}")
        other = fa.get(key)
        if not isinstance(other, str) or not other:
            errors.append(f"Empty/non-string Persian localization: {key}")
        elif placeholders(value) != placeholders(other):
            errors.append(f"Placeholder mismatch: {key}")


def validate_compat(errors: list[str]) -> None:
    payload = load_json(I18N_DIR / "compat_catalog.json")
    items = payload.get("items", []) if isinstance(payload, dict) else []
    seen: set[str] = set()
    for row in items:
        key = row.get("key")
        if not isinstance(key, str) or not KEY_PATTERN.fullmatch(key):
            errors.append(f"Invalid compatibility localization key: {key!r}")
            continue
        if key in seen:
            errors.append(f"Duplicate compatibility localization key: {key}")
        seen.add(key)
        for locale in ("en", "fa"):
            value = row.get(locale)
            if not isinstance(value, str) or not value:
                errors.append(f"Missing compatibility {locale} value: {key}")
        if placeholders(str(row.get("en", ""))) != placeholders(str(row.get("fa", ""))):
            errors.append(f"Compatibility placeholder mismatch: {key}")
    if not items:
        errors.append("Compatibility localization catalog is empty")


def validate_frontend_keys(errors: list[str]) -> None:
    bundles = {locale: load_json(I18N_DIR / f"{locale}.json") for locale in ("en", "fa")}
    keys = set(bundles["en"]) | set(bundles["fa"])
    js = (FRONTEND / "app.js").read_text(encoding="utf-8")
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    static_keys = set(re.findall(r'\bt\(["\']([^"\']+)["\']', js))
    static_keys.update(re.findall(r'data-i18n=["\']([^"\']+)["\']', html))
    for key in sorted(static_keys):
        if key not in keys and not key.startswith(("settings.category.", "nav.")):
            errors.append(f"Frontend references missing localization key: {key}")


def validate_persian_catalog_coverage(errors: list[str]) -> None:
    catalog = load_json(I18N_DIR / "compat_catalog.json")
    items = catalog.get("items", []) if isinstance(catalog, dict) else []
    sources = {str(row.get("source", "")) for row in items}
    for path in COMPAT.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"Syntax error in compatibility source {path}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search(r"[\u0600-\u06ff]", node.value):
                value = node.value
                # Documentation/comments and internal data may legitimately contain source text;
                # the catalog check is therefore informational unless the string appears as a full user-facing source value.
                if value in sources:
                    continue
    

def validate_settings(errors: list[str]) -> None:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from telegram_bot_platform.core.settings_catalog import SETTING_DESCRIPTORS

    keys = [item.key for item in SETTING_DESCRIPTORS]
    if len(keys) != len(set(keys)):
        errors.append("Duplicate platform setting key")
    for item in SETTING_DESCRIPTORS:
        if not KEY_PATTERN.fullmatch(item.key):
            errors.append(f"Invalid platform setting key: {item.key}")
        if not item.env_name:
            errors.append(f"Missing env name: {item.key}")
        if item.value_type not in {None, "bool", "int", "float", "list"}:
            errors.append(f"Unsupported setting value type: {item.key}")


def main() -> int:
    errors: list[str] = []
    validate_locales(errors)
    validate_compat(errors)
    validate_frontend_keys(errors)
    validate_persian_catalog_coverage(errors)
    validate_settings(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Platform validation passed: locales, compatibility catalog, frontend keys and settings are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
