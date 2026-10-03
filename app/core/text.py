from __future__ import annotations

import html


def escape_telegram_html(value: str) -> str:
    """Escape untrusted text before embedding it in Telegram HTML markup."""
    return html.escape(value, quote=False)
