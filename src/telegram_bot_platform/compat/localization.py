from __future__ import annotations

import json
import os
import re
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from telebot import TeleBot

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "resources" / "i18n" / "compat_catalog.json"
OVERRIDE_PATH = Path("data/i18n_overrides.json")
SUPPORTED_LOCALES = ("en", "fa")


def locale_for(language_code: str | None, default: str | None = None) -> str:
    selected = (language_code or default or os.getenv("DEFAULT_LOCALE", "en")).split("-")[0].lower()
    return selected if selected in SUPPORTED_LOCALES else "en"


def _catalog() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    try:
        rows = json.loads(CATALOG_PATH.read_text(encoding="utf-8")).get("items", [])
    except (OSError, json.JSONDecodeError):
        rows = []
    by_key: dict[str, dict[str, str]] = {}
    source_map: dict[str, str] = {}
    for row in rows:
        key = str(row.get("key", ""))
        source = str(row.get("source", ""))
        if key and source:
            by_key[key] = {locale: str(row.get(locale, source)) for locale in SUPPORTED_LOCALES}
            source_map[source] = key
    return by_key, source_map


CATALOG, SOURCE_MAP = _catalog()
TEMPLATE_PATTERNS: list[tuple[re.Pattern[str], str]] = []


def _compile_template_patterns() -> None:
    global TEMPLATE_PATTERNS
    patterns: list[tuple[re.Pattern[str], str]] = []
    for key, values in CATALOG.items():
        source = values.get("fa") or values.get("en") or ""
        if "{value_" not in source:
            continue
        pattern = re.escape(source)
        pattern = re.sub(r"\\\{value_\d+\\\}", r"(.+?)", pattern)
        try:
            patterns.append((re.compile(r"^" + pattern + r"$", re.DOTALL), key))
        except re.error:
            continue
    TEMPLATE_PATTERNS = patterns


_compile_template_patterns()


def _overrides() -> dict[str, dict[str, str]]:
    try:
        data = json.loads(OVERRIDE_PATH.read_text(encoding="utf-8"))
        return {locale: dict(data.get(locale, {})) for locale in SUPPORTED_LOCALES}
    except (OSError, json.JSONDecodeError):
        return {locale: {} for locale in SUPPORTED_LOCALES}


def reload_catalog() -> None:
    global CATALOG, SOURCE_MAP
    CATALOG, SOURCE_MAP = _catalog()
    _compile_template_patterns()
def localize(value: str | None, locale: str) -> str | None:
    if value is None:
        return None
    locale = locale_for(locale)
    overrides = _overrides()
    key = SOURCE_MAP.get(value)
    if key:
        return overrides.get(locale, {}).get(key) or CATALOG.get(key, {}).get(locale, value)
    for pattern, template_key in TEMPLATE_PATTERNS:
        match = pattern.match(value)
        if not match:
            continue
        template = overrides.get(locale, {}).get(template_key) or CATALOG.get(template_key, {}).get(locale, value)
        for index, captured in enumerate(match.groups()):
            template = template.replace("{value_%d}" % index, captured)
        return template
    return value


class LocalizedTeleBot(TeleBot):
    """Compatibility TeleBot with centralized bilingual output and button localization."""

    def __init__(self, token: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(token, *args, **kwargs)
        self._chat_locales: OrderedDict[int, str] = OrderedDict()
        self._callback_locales: OrderedDict[str, str] = OrderedDict()
        self._max_locale_cache = 20_000

    def _remember(self, chat_id: int | None, language_code: str | None) -> str:
        locale = locale_for(language_code)
        if chat_id is not None:
            self._chat_locales[chat_id] = locale
            self._chat_locales.move_to_end(chat_id)
            while len(self._chat_locales) > self._max_locale_cache:
                self._chat_locales.popitem(last=False)
        return locale

    def _locale_for_chat(self, chat_id: int | None) -> str:
        return self._chat_locales.get(int(chat_id or 0), locale_for(None))

    def register_message_handler(self, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        def wrapped(message: Any, *cb_args: Any, **cb_kwargs: Any) -> Any:
            user = getattr(message, "from_user", None)
            chat = getattr(message, "chat", None)
            self._remember(getattr(chat, "id", None), getattr(user, "language_code", None))
            return callback(message, *cb_args, **cb_kwargs)
        return super().register_message_handler(wrapped, *args, **kwargs)

    def register_callback_query_handler(self, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        def wrapped(call: Any, *cb_args: Any, **cb_kwargs: Any) -> Any:
            user = getattr(call, "from_user", None)
            message = getattr(call, "message", None)
            chat = getattr(message, "chat", None)
            locale = self._remember(getattr(chat, "id", None), getattr(user, "language_code", None))
            callback_id = getattr(call, "id", None)
            if callback_id:
                self._callback_locales[str(callback_id)] = locale
                self._callback_locales.move_to_end(str(callback_id))
                while len(self._callback_locales) > self._max_locale_cache:
                    self._callback_locales.popitem(last=False)
            return callback(call, *cb_args, **cb_kwargs)
        return super().register_callback_query_handler(wrapped, *args, **kwargs)

    @staticmethod
    def _localized_markup(markup: Any, locale: str) -> Any:
        if markup is None:
            return None
        try:
            clone = deepcopy(markup)
        except Exception:
            clone = markup
        for matrix_name in ("keyboard", "inline_keyboard"):
            matrix = getattr(clone, matrix_name, None)
            if matrix is None:
                continue
            for row in matrix:
                for button in row:
                    if hasattr(button, "text") and button.text:
                        button.text = localize(button.text, locale) or button.text
        return clone

    def send_message(self, chat_id: int, text: str, *args: Any, **kwargs: Any) -> Any:
        locale = self._locale_for_chat(chat_id)
        kwargs["reply_markup"] = self._localized_markup(kwargs.get("reply_markup"), locale)
        return super().send_message(chat_id, localize(text, locale) or text, *args, **kwargs)

    def reply_to(self, message: Any, text: str, *args: Any, **kwargs: Any) -> Any:
        chat_id = getattr(getattr(message, "chat", None), "id", None)
        locale = self._locale_for_chat(chat_id)
        kwargs["reply_markup"] = self._localized_markup(kwargs.get("reply_markup"), locale)
        return super().reply_to(message, localize(text, locale) or text, *args, **kwargs)

    def _media_localize(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        chat_id = kwargs.get("chat_id") if kwargs.get("chat_id") is not None else (args[0] if args else None)
        locale = self._locale_for_chat(chat_id)
        if "caption" in kwargs:
            kwargs["caption"] = localize(kwargs["caption"], locale)
        kwargs["reply_markup"] = self._localized_markup(kwargs.get("reply_markup"), locale)
        return getattr(super(), method_name)(*args, **kwargs)

    def send_photo(self, *args: Any, **kwargs: Any) -> Any:
        return self._media_localize("send_photo", *args, **kwargs)

    def send_video(self, *args: Any, **kwargs: Any) -> Any:
        return self._media_localize("send_video", *args, **kwargs)

    def send_document(self, *args: Any, **kwargs: Any) -> Any:
        return self._media_localize("send_document", *args, **kwargs)

    def send_audio(self, *args: Any, **kwargs: Any) -> Any:
        return self._media_localize("send_audio", *args, **kwargs)

    def send_voice(self, *args: Any, **kwargs: Any) -> Any:
        return self._media_localize("send_voice", *args, **kwargs)

    def send_animation(self, *args: Any, **kwargs: Any) -> Any:
        return self._media_localize("send_animation", *args, **kwargs)

    def edit_message_text(self, text: str, *args: Any, **kwargs: Any) -> Any:
        chat_id = kwargs.get("chat_id") or (args[0] if args else None)
        locale = self._locale_for_chat(chat_id)
        kwargs["reply_markup"] = self._localized_markup(kwargs.get("reply_markup"), locale)
        return super().edit_message_text(localize(text, locale) or text, *args, **kwargs)

    def edit_message_caption(self, *args: Any, **kwargs: Any) -> Any:
        chat_id = kwargs.get("chat_id") or (args[0] if args else None)
        locale = self._locale_for_chat(chat_id)
        if "caption" in kwargs:
            kwargs["caption"] = localize(kwargs["caption"], locale)
        return super().edit_message_caption(*args, **kwargs)

    def answer_callback_query(self, callback_query_id: str, text: str | None = None, *args: Any, **kwargs: Any) -> Any:
        locale = self._callback_locales.get(str(callback_query_id), locale_for(None))
        return super().answer_callback_query(callback_query_id, localize(text, locale) if text else text, *args, **kwargs)
