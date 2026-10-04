# handlers.py
def register_all_handlers(bot, db, back_to_main, back_to_settings):
    from telegram_bot_platform.compat.handlers.admin.admin_manager import AdminManager
    from telegram_bot_platform.compat.handlers.admin.request_manager import RequestManager
    from telegram_bot_platform.compat.handlers.admin.request_settings import RequestSettings
    from telegram_bot_platform.compat.handlers.admin.accounting_handler import AccountingHandler
    from telegram_bot_platform.compat.handlers.admin.client_manager import ClientManager
    from telegram_bot_platform.compat.handlers.admin.staff_manager import StaffManager
    from telegram_bot_platform.compat.handlers.admin.channel_group_settings import ChannelGroupSettings
    from telegram_bot_platform.compat.handlers.admin.ad_manager import AdManager
    from telegram_bot_platform.compat.handlers.admin.report_manager import ReportManager
    from telegram_bot_platform.compat.handlers.admin.message_manager import MessageManager

    admin_manager = AdminManager(bot, db, back_to_main)
    request_manager = RequestManager(bot, db, back_to_main, back_to_settings)
    settings_handler = RequestSettings(bot, db, back_to_main, back_to_settings)
    accounting_handler = AccountingHandler(
        bot, db, back_to_main, back_to_settings)
    client_manager = ClientManager(bot, db, back_to_main)
    staff_manager = StaffManager(bot, db, back_to_main)
    channel_settings = ChannelGroupSettings(bot, back_to_main)
    ad_manager = AdManager(bot, db, back_to_main)
    report_manager = ReportManager(bot, db, back_to_main)
    message_manager = MessageManager(bot, back_to_main)
    # Internal implementation note: legacy behavior is preserved during modernization.
    return {
        "admin_manager": admin_manager,
        "request_manager": request_manager,
        "settings": settings_handler,
        "accounting": accounting_handler,
        "client_manager": client_manager,
        "staff_manager": staff_manager,
        "channel_settings": channel_settings,
        "ad_manager": ad_manager,
        "report_manager": report_manager,
        "message_manager": message_manager,
    }
