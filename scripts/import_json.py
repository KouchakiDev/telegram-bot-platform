from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from telegram_bot_platform.application.services.content_service import ContentService
from telegram_bot_platform.application.services.user_service import UserService
from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.core.container import Container
from telegram_bot_platform.domain.entities import ChatIdentity, UserIdentity
from telegram_bot_platform.domain.enums import ChatType


async def import_data(path: Path) -> None:
    """Import a deliberately neutral export format into the new schema."""
    data = json.loads(path.read_text(encoding="utf-8"))
    container = Container.build(Settings())
    try:
        async with container.database.session_factory() as session:
            user_service = UserService(session, container.settings.default_locale)
            for item in data.get("users", []):
                await user_service.touch_user_and_chat(
                    UserIdentity(
                        telegram_id=int(item["telegram_id"]),
                        username=item.get("username"),
                        first_name=item.get("first_name"),
                        last_name=item.get("last_name"),
                        language_code=item.get("language_code"),
                        is_bot=bool(item.get("is_bot", False)),
                    ),
                    ChatIdentity(int(item["telegram_id"]), ChatType.PRIVATE, None, None),
                )
            service = ContentService(session)
            for item in data.get("content", []):
                await service.create(str(item["title"]), str(item["body"]), int(item["created_by"]))
    finally:
        await container.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a neutral JSON export into the platform")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    asyncio.run(import_data(args.path))


if __name__ == "__main__":
    main()
