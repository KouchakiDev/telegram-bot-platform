from __future__ import annotations

import logging
from telegram import BotCommand, Update
from telegram.ext import AIORateLimiter, Application, ApplicationBuilder, ContextTypes

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.core.container import Container
from telegram_bot_platform.core.logging import configure_logging
from telegram_bot_platform.telegram.modules.admin import AdminModule
from telegram_bot_platform.telegram.modules.auto_reply import AutoReplyModule
from telegram_bot_platform.telegram.modules.common import CommonModule
from telegram_bot_platform.telegram.modules.content import ContentModule

logger = logging.getLogger("platform.telegram")


def build_application(settings: Settings | None = None) -> tuple[Application, Container]:
    resolved = settings or Settings()
    token = resolved.require_bot_token()
    container = Container.build(resolved)

    builder = (
        ApplicationBuilder()
        .token(token)
        .rate_limiter(
            AIORateLimiter(
                overall_max_rate=resolved.telegram_overall_rate_per_second,
                group_max_rate=resolved.telegram_group_rate_per_second,
            )
        )
        .concurrent_updates(resolved.telegram_concurrent_updates)
        .connection_pool_size(resolved.telegram_connection_pool_size)
        .pool_timeout(resolved.telegram_timeout_seconds)
        .connect_timeout(resolved.telegram_timeout_seconds)
        .read_timeout(resolved.telegram_timeout_seconds)
        .write_timeout(resolved.telegram_timeout_seconds)
    )

    async def post_init(app: Application) -> None:
        configure_logging(resolved.log_level, resolved.log_json)
        await app.bot.set_my_commands([
            BotCommand("start", "Start"),
            BotCommand("app", "Open Mini App"),
            BotCommand("content", "Published content"),
            BotCommand("help", "Help"),
            BotCommand("admin", "Admin summary"),
        ])
        logger.info("Telegram application initialized")

    builder = builder.post_init(post_init)
    application = builder.build()

    common = CommonModule(container)
    content = ContentModule(container)
    admin = AdminModule(container)
    auto_reply = AutoReplyModule(container)

    for handler in common.handlers():
        application.add_handler(handler)
    for handler in content.handlers():
        application.add_handler(handler, group=10)
    for handler in admin.handlers():
        application.add_handler(handler, group=20)
    for handler in auto_reply.handlers():
        application.add_handler(handler, group=100)

    async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.exception("Unhandled Telegram update error", exc_info=context.error)

    application.add_error_handler(on_error)
    return application, container


def main() -> None:
    settings = Settings()
    application, container = build_application(settings)
    try:
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            bootstrap_retries=settings.telegram_bootstrap_retries,
            close_loop=False,
        )
    finally:
        import asyncio
        asyncio.run(container.shutdown())
