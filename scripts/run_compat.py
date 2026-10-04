from __future__ import annotations

import argparse
import importlib
import os
import sys
from typing import Callable


ENTRYPOINTS: dict[str, tuple[str, str]] = {
    "admin": ("telegram_bot_platform.compat.runners.admin_runner", "start_admin_bot"),
    "client": ("telegram_bot_platform.compat.runners.client_runner", "start_client_bot"),
    "staff": ("telegram_bot_platform.compat.runners.staff_runner", "start_staff_bot"),
    "auto-responder": ("telegram_bot_platform.compat.runners.auto_responder", "start_autoresponser_bot"),
}


def load_entrypoint(name: str) -> Callable[[], object]:
    module_name, function_name = ENTRYPOINTS[name]
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise SystemExit(
            "Compatibility runtime dependencies are missing. Install: "
            'pip install -e ".[legacy]"'
        ) from exc
    return getattr(module, function_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a preserved platform compatibility runtime.")
    parser.add_argument("role", choices=sorted(ENTRYPOINTS))
    args = parser.parse_args()
    if args.role == "client":
        # The fully wired legacy client runner expects explicit database and token arguments.
        from telegram_bot_platform.compat.config.settings import BOT_CLIENT_TOKEN, DB_PARAMS
        from telegram_bot_platform.compat.database.database_manager import DatabaseManager

        load_entrypoint("client")(BOT_CLIENT_TOKEN, DatabaseManager(**DB_PARAMS))
        return
    load_entrypoint(args.role)()


if __name__ == "__main__":
    main()
