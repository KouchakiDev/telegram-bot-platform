from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    def __init__(self, json_output: bool) -> None:
        super().__init__()
        self.json_output = json_output

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
        }
        request_id = request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if self.json_output:
            return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        prefix = f"[{payload['level']}] {payload['logger']}"
        suffix = f" request_id={request_id}" if request_id else ""
        return f"{payload['timestamp']} {prefix}{suffix} {message}"


def configure_logging(level: str = "INFO", json_output: bool = False) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter(json_output))
    root.addHandler(handler)
    for noisy in ("httpx", "httpcore", "asyncio", "telegram.ext._application"):
        logging.getLogger(noisy).setLevel(max(root.level, logging.WARNING))
