# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
from __future__ import annotations

import os, sys, logging
from typing import Dict

# Internal implementation note: legacy behavior is preserved during modernization.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [BASE_DIR, os.path.join(BASE_DIR, '..')]

# Internal implementation note: legacy behavior is preserved during modernization.
import telebot
from telegram_bot_platform.compat.localization import LocalizedTeleBot
from telebot import types
from telegram_bot_platform.compat.config.settings import *          # Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

from telegram_bot_platform.compat.handlers.staff.message_handler            import MessagesHandler
from telegram_bot_platform.compat.handlers.staff.login_handler              import LoginHandler
from telegram_bot_platform.compat.handlers.staff.user_account_handler       import UserAccountHandler
from telegram_bot_platform.compat.handlers.staff.requests_handler           import RequestsHandler
from telegram_bot_platform.compat.handlers.staff.identity_verification_handler import IdentityVerificationHandler
from telegram_bot_platform.compat.handlers.staff.payments_handler           import PaymentsHandler
from telegram_bot_platform.compat.handlers.staff.services_handler           import ServicesHandler
from telegram_bot_platform.compat.handlers.staff.ad_creation_handler        import AdCreationHandler
from telegram_bot_platform.compat.handlers.staff.work_settings_handler      import WorkSettingsHandler
from telegram_bot_platform.compat.handlers.staff.registration_handler       import RegistrationHandler
from telegram_bot_platform.compat.runners.starter import Starter       # Internal implementation note: legacy behavior is preserved during modernization.
      # Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
logger = CustomLogger()          # Internal implementation note: legacy behavior is preserved during modernization.
log = logger
# Internal implementation note: legacy behavior is preserved during modernization.
class StaffBot:
    """Legacy-compatible behavior preserved for this callable."""
    # Internal implementation note: legacy behavior is preserved during modernization.
    def __init__(self, bots_token: Dict[str, str]) -> None:
        # 1) multi-bot dict
        self.bots = {
            "moshtari":  LocalizedTeleBot(bots_token["moshtari"]),
            "admin":     LocalizedTeleBot(bots_token["admin"]),
            "staff": LocalizedTeleBot(bots_token["staff"]),
        }
        self.bot: telebot.TeleBot = self.bots["staff"]

        # 2) DB layer
        self.db: DatabaseManager = DatabaseManager(**DB_PARAMS)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data: dict = {}

        # 4) instantiate *all* feature-handlers
        self._init_handlers()
        self._register_commands()
        
        self.starter = Starter(db=self.db, bot=self.bot, welcome_cb=self.send_welcome)
        self.starter.broadcast_fake_message_to_all()


    # Internal implementation note: legacy behavior is preserved during modernization.
    #  Internal helpers
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _init_handlers(self) -> None:
        """Create handler instances and wire their dependencies."""
        self.registration_handler  = RegistrationHandler(
            self.bot, self.db, self.data, registration_steps, self)

        self.work_settings_handler = WorkSettingsHandler(
            self.bot, self.db, self.data, work_settings_steps, self)

        self.ad_creation_handler   = AdCreationHandler(
            self.bot, self.data, self)

        self.services_handler      = ServicesHandler(
            self.bot, self.data, self, self.db)

        self.payments_handler      = PaymentsHandler(
            self.bot, self.data, self)

        self.identity_verification_handler = IdentityVerificationHandler(
            self.bot, self.data, self, self.db)

        self.requests_handler      = RequestsHandler(
            self.bot, self.data, self)

        self.user_account_handler  = UserAccountHandler(
            self.bot, self.db, self.data, self,
            self.work_settings_handler,
            self.identity_verification_handler,
            self.payments_handler)

        self.login_handler         = LoginHandler(
            self.bot, self.data,
            {
                "registration":          self.registration_handler,
                "work_settings":         self.work_settings_handler,
                "ad_creation":           self.ad_creation_handler,
                "services":              self.services_handler,
                "payments":              self.payments_handler,
                "identity_verification": self.identity_verification_handler,
            },
            self)

        self.messages_handler      = MessagesHandler(
            self.bot, self.db, self.data, self)
        self.login_handler.callBack_handler()
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _register_commands(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        @self.bot.message_handler(commands=['start'])
        def _on_start(message):
            logger.debug("[/start] received from %s", message.chat.id)
            self.starter.store_user_info(message)           # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
            self.send_welcome(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def clear_steps(self, chat_id: int) -> None:
        """Remove **all** pending step-handlers for this chat."""
        try:
            self.bot.clear_step_handler_by_chat_id(chat_id)
        except Exception as exc:
            logger.debug("clear_step_handler failed: %s", exc)

    # Internal implementation note: legacy behavior is preserved during modernization.
    

    # Internal implementation note: legacy behavior is preserved during modernization.
    #  UI flows
    # Internal implementation note: legacy behavior is preserved during modernization.
    def send_welcome(self, message) -> None:
        """Show either *Work panel* or *Auth menu* based on staff status."""
        chat_id     = message.chat.id
        telegram_id = message.from_user.id

        # guarantee single handler
        self.clear_steps(chat_id)

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            rows = self.db.select_dict("staff",
                                       "telegram_id = ?", (telegram_id,))
            if rows and rows[0].get("status") == "approved":
                name = rows[0].get("name", "کاربر عزیز")
                self.bot.send_message(chat_id, f"🎉 {name}\n عزیز خوش آمدی!")
                self.login_handler.login_menu(message)
                return
        except Exception as exc:
            logger.warning("Staff lookup failed: %s", exc, exc_info=True)

        # 2) Otherwise ask to register / login
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("ثبت نام", "ورود")
        self.bot.send_message(chat_id,
                              "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                              reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_main_menu)
    # Internal implementation note: legacy behavior is preserved during modernization.
    #  Compatibility helpers  (kept for older modules)
    # Internal implementation note: legacy behavior is preserved during modernization.
    def it_work_any_time(self, message) -> bool:
        """
        Legacy helper used by *login_handler* to allow typing **/start** at
        any stage. Returns *True* if the message was a command and the flow
        was reset.
        """
        txt = (message.text or "").strip()
        if txt.startswith("/"):
            self.send_welcome(message)
            return True
        return False
    # Internal implementation note: legacy behavior is preserved during modernization.
    def handle_main_menu(self, message) -> None:
        """Process the first menu after /start (Register | Login)."""
        chat_id = message.chat.id
        text    = (message.text or "").strip()

        # allow commands at any stage
        if text.startswith("/"):
            return self.send_welcome(message)

        # reset queue before registering new step
        self.clear_steps(chat_id)

        if text == "ثبت نام":
            self.registration_handler.confirm_registration_intro(message)
            return

        if text == "ورود":
            self.login_handler.start_login(message)
            return

        # invalid option
        self.bot.send_message(chat_id,
                              "❌ لطفاً فقط از دکمه‌های «ثبت نام» یا «ورود» استفاده کنید.")
        self.bot.register_next_step_handler(message, self.handle_main_menu)

    # Internal implementation note: legacy behavior is preserved during modernization.
    #  polling runner
    # Internal implementation note: legacy behavior is preserved during modernization.
    def start(self) -> None:
        logger.info("Staff-bot polling started.")
        # `none_stop=True` removed (deprecated); handled inside TeleBot
        self.bot.polling(
            none_stop=True,
            allowed_updates=['message', 'callback_query']
        )

        logger.warning("Staff-bot polling stopped.")

# Internal implementation note: legacy behavior is preserved during modernization.
def start_staff_bot() -> None:
    tokens = {
        "moshtari":  BOT_CLIENT_TOKEN,
        "admin":     BOT_ADMIN_TOKEN,
        "staff": BOT_STAFF_TOKEN,
    }
    try:
        StaffBot(tokens).start()
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user (Ctrl-C)")
    except Exception as exc:
        logger.exception("Fatal error – bot crashed: %s", exc)

# Internal implementation note: legacy behavior is preserved during modernization.
if __name__ == '__main__':
    start_staff_bot()
