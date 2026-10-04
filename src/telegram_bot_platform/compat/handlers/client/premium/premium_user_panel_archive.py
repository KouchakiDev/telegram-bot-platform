# Internal implementation note: legacy behavior is preserved during modernization.
import json

# Internal implementation note: legacy behavior is preserved during modernization.
from telebot import TeleBot, types
from telebot.types import (

    ReplyKeyboardMarkup,
    KeyboardButton
)
# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.
import re

from telegram_bot_platform.compat.handlers.client.ads_handler import AdsHandler
from telegram_bot_platform.compat.handlers.client.to_day_cods import TodayCodesFilterHandler
# from telegram_bot_platform.compat.handlers.client.premium.premium_user_panel import PREMIUMUserPanel
# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.utils.locations import LocationHandler
# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.handlers.client.premium.premium_profile import PREMIUMProfile
from telegram_bot_platform.compat.handlers.client.premium.premium_requests_Handler import PREMIUMRequestsHandler
log = CustomLogger()  # log_file="premiume_user_p.log")


class PREMIUMUserPanel:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot: TeleBot, db: DatabaseManager, back_main, back_previous, start,see_Rr):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.db = db
        self.back_main = back_main
        self.see_Rr = see_Rr
        self.back_previous = self.show_panel
        # self.register_callback = register_callback
        # self.register_callback()
        self.temp_review_dict = {}  # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request = {}
        self.temp_data = {}
        self.user_data = {}
        self.premium_see_r = PREMIUMRequestsHandler(
            self.bot, self.db, back_main, back_previous, start)
        self.start = start
        self.ads = AdsHandler(self.bot, self.db)
        self.today = TodayCodesFilterHandler(
            self.bot, self.db, self.back_main, self.back_previous, self.start)
        self.profile = PREMIUMProfile(
            self.bot, self.db, self.back_main, self.back_previous, self.start)
        self.location_handler = LocationHandler()

    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text
        if text:
            if text == BUTTONS["back_to_main_menu"]:
                self.show_panel(message)
                return True
            elif text.startswith("/start"):
                self.start(message)
                return True
            elif text == BUTTONS["back_to_pervious_menu"]:
                self.back_previous(message)
                return True
        return False

    def add_back_buttons(self, markup: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        markup.add(
            KeyboardButton(BUTTONS["back_to_main_menu"]),
            KeyboardButton(BUTTONS["back_to_pervious_menu"]),
        )
        return markup

    def show_panel(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text
        results = self.db.select_dict(
            "premium_clients",
            "telegram_id = ? AND C_status = 'approved'",
            (chat_id,)
        )
        if results:
            if text in (BUTTONS["today_codes"], BUTTONS["requests"], BUTTONS["premium_favorites"], BUTTONS["profile"]):
                self.handle_selection(message)
            else:
                if text in BUTTONS.values():
                    self.bot.send_message(
                    chat_id, "کاربر گرامی از اینکه از منوی خود خارج شدید متاسفیم لطفا دوباره تلاش کنید")
                user = results[0]
                name = user.get("name", "کاربر")
                welcome_text = MESSAGES["premium_menu"].format(name=name)
                markup = self._build_premium_menu(message)
                self.bot.send_message(
                    chat_id, welcome_text, reply_markup=markup)
                self.bot.register_next_step_handler(
                    message, self.handle_selection)
        else:
            self.bot.send_message(chat_id, MESSAGES["not_premium"])
            self.back_main(message)

    def _build_premium_menu(self,message) -> ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        count = ""
        try:
            count = self.see_Rr.counter_of_requests_results(message)
        except Exception as e:
            log.warning(f"[send_welcome] request count failed: {e}")
            count = ""

        label = BUTTONS.get("see_requests", "📄 درخواست‌ها")
        suffix = f" ({count})" if count else ""
        markup.add(
            KeyboardButton(BUTTONS["today_codes"]),
            # KeyboardButton(BUTTONS["permanent_codes"]),
            KeyboardButton(f"{label}{suffix}"),
            KeyboardButton(BUTTONS["premium_favorites"]),
            KeyboardButton(BUTTONS["profile"])

        )
        # markup = self.add_back_buttons(markup)
        return markup

    # Internal implementation note: legacy behavior is preserved during modernization.
    def handle_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id   = message.chat.id
        text = message.text
        
        if text.endswith(')') and '(' in text:
            text = text[:text.rfind('(')].strip()

                # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == BUTTONS["today_codes"]:
            self.today._start(message)

        elif text.startswith(BUTTONS.get("see_requests", BUTTONS["requests"])):
            self.premium_see_r.show_requests_menu(message)

        elif text == BUTTONS["premium_favorites"]:
            self._send_favorites(message)

        elif text == BUTTONS["profile"]:
            self._show_profile(message)

        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])

    def _show_profile(self, message):
        chat_id = message.chat.id

        self.profile.show_profile_menu(message)

    def _send_today_codes(self, message: int):
        chat_id = message.chat.id

        """
        ارسال لیست کدهای امروز به کاربر PREMIUM.
        (اینجا منطق واقعی نمایش کدهای امروز باید نوشته شود.)
        """
        self.ads.handle_show_ads(message)
        # self.bot.send_message(chat_id, MESSAGES["today_code_menu_prompt"])

    def _send_permanent_codes(self, message: int):
        chat_id = message.chat.id

        """
        ارسال لیست کدهای دائم به کاربر PREMIUM.
        (اینجا منطق واقعی نمایش کدهای دائم باید نوشته شود.)
        """
        self.bot.send_message(chat_id, MESSAGES["permanent_code_menu_prompt"])

    def _send_premium_history(self, message: int):
        chat_id = message.chat.id

        """
        ارسال تاریخچه فعالیت‌های کاربر PREMIUM.
        (اینجا می‌توانید با استعلام از پایگاه داده، تاریخچه واقعی را ارسال نمایید.)
        """
        self.bot.send_message(chat_id, MESSAGES["activity_history_prompt"])

    def _send_favorites(self, message):
        chat_id = message.chat.id
        message.text = "WEAREINFAVORITS"
        # Internal implementation note: legacy behavior is preserved during modernization.
        user_rows = self.db.select_dict(
            "premium_clients",
            "telegram_id = ? AND C_status = 'approved'",
            (chat_id,)
        )

        if not user_rows:
            self.bot.send_message(chat_id, MESSAGES["not_premium"])
            self.back_main(message)
            return

        user = user_rows[0]
        favorites_raw = user.get("favorite_codes")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not favorites_raw:
            self.bot.send_message(
                chat_id, "📭 شما هیچ موردی را به علاقه‌مندی‌های خود اضافه نکرده‌اید.")
            self.show_panel(message)
            return

        try:
            favorite_codes = json.loads(favorites_raw)
        except:
            favorite_codes = []

        if not favorite_codes:
            self.bot.send_message(
                chat_id, "📭 شما هیچ موردی را به علاقه‌مندی‌های خود اضافه نکرده‌اید.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.InlineKeyboardMarkup()
        for code in favorite_codes:
            markup.add(
                types.InlineKeyboardButton(
                    text=f"🧍‍♀️ کد {code}",
                    callback_data=f"premium_fav_profile_{code}"
                )
            )

        self.bot.send_message(
            chat_id, "⭐ لیست کدهای مورد علاقه شما:", reply_markup=markup)
