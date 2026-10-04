# handlers/premium_requests_handler.py

from telebot import TeleBot, types
from telebot.types import *

from persiantools.jdatetime import JalaliDate
# from datetime import datetime, timedelta
from telegram_bot_platform.compat.config.settings import *
# Internal implementation note: legacy behavior is preserved during modernization.
import re
# import json
# import html
from datetime import datetime

# Internal implementation note: legacy behavior is preserved during modernization.
# import telebot
from telebot import TeleBot, types
from telebot.types import (

    ReplyKeyboardMarkup,
    KeyboardButton
)
# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# # Client Handlers
# from telegram_bot_platform.compat.handlers.client.filter import FilterHandler
# from telegram_bot_platform.compat.handlers.client.premium_manager import PREMIUMManager
# from telegram_bot_platform.compat.handlers.client.booking_flow import Reserve_manager
from telegram_bot_platform.compat.handlers.client.see_requests_results import SeeRequestsHandler
# from telegram_bot_platform.compat.handlers.client.show_staff_profile import StaffProfileHandler
# from telegram_bot_platform.compat.handlers.client.ads_handler import AdsHandler
# from telegram_bot_platform.compat.handlers.client.to_day_cods import TodayCodesFilterHandler

# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

log = CustomLogger()  # log_file="premium_r_H.log")


class PREMIUMRequestsHandler:
    """Legacy-compatible behavior preserved for this callable."""

    # Internal implementation note: legacy behavior is preserved during modernization.

    def __init__(self, bot: TeleBot, db: DatabaseManager, back_main, back_previous, start):
        self.bot = bot
        self.db = db
        self.see_handler = SeeRequestsHandler(bot, db)
        self.back_main = back_main
        self.back_previous = back_previous
        self.start = start
        self.see24r = self.see_handler.handle
        # Internal implementation note: legacy behavior is preserved during modernization.

    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text
        if text:
            if text == BUTTONS["back_to_main_menu"]:
                self.back_main(message)
                return True
            elif text.startswith("/start") or text.startswith("/"):
                self.start(message)
                return True
            elif text == BUTTONS["back_to_pervious_menu"]:
                try:
                    self.back_previous(message)
                except:
                    self.back_main(message)
                return True
        return False

    def add_back_buttons(self, markup: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        markup.add(
            KeyboardButton(BUTTONS["back_to_main_menu"]),
            KeyboardButton(BUTTONS["back_to_pervious_menu"]),
        )
        return markup

    def show_requests_menu(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(
            types.KeyboardButton(BUTTONS['requests_details']),
            types.KeyboardButton(BUTTONS['latest_request']),
            # types.KeyboardButton(BUTTONS['recent_requests_24h'])
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id,
            MESSAGES['requests_menu_prompt'],
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self.handle_rm_selection)

    def handle_rm_selection(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        text = message.text

        if text == BUTTONS['requests_details']:
            self._show_statuses(message)

        elif text == BUTTONS['latest_request']:
            self._just_show_last(message)
            self.show_requests_menu(message)
            return

        elif text == BUTTONS['recent_requests_24h']:
            self.see24r(message)
            self.show_requests_menu(message)
            return

        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                MESSAGES['invalid_option'],
                reply_markup=self.add_back_buttons(
                    types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                )
            )

    def _get_requests_current_year(self, ucode: str) -> list:
        """Legacy-compatible behavior preserved for this callable."""
        today_j = JalaliDate.today()
        start_j = JalaliDate(today_j.year, 1, 1)
        end_j = JalaliDate(today_j.year + 1, 1, 1)
        start_g = datetime(*start_j.to_gregorian().timetuple()[:6])
        end_g = datetime(*end_j.to_gregorian().timetuple()[:6])
        return self.db.select_dict(
            PREMIUM_REQUESTS_TABLE,
            'U_code = ? AND created_at >= ? AND created_at < ?',
            (ucode, start_g, end_g)
        )

    def _show_statuses(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(chat_id, "شما در سیستم ثبت نشده‌اید.")
            self.back_main(message)
            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        reqs = self._get_requests_current_year(ucode)
        counts = {}
        for r in reqs:
            counts[r['status']] = counts.get(r['status'], 0) + 1

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for st, info in STATUS_INFO.items():
            cnt = counts.get(st)
            if cnt:
                text = f"{info['emoji']} {info['title']} ({cnt})"
                buttons.append(types.KeyboardButton(text))
        markup.add(*buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)

        self.bot.send_message(
            chat_id,
            MESSAGES['status_overview_title'],
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_status_selection)
    # import re

    def handle_status_selection(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        text = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        text_cleaned = re.sub(r'^[^\w\s]+', '', text)   # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        text_cleaned = re.sub(r'\(\d+\)', '', text_cleaned)
        text_cleaned = text_cleaned.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        matched_status = None
        for status, info in STATUS_INFO.items():

            if info['title'] in text_cleaned:

                matched_status = status
                break

        if matched_status:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_status_actions(message, matched_status)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                MESSAGES['invalid_option'],
                reply_markup=self.add_back_buttons(
                    types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                )
            )

    def _show_status_actions(self, message: types.Message, status: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(
                chat_id, MESSAGES['no_requests'].format(status=status))
            self.show_requests_menu(message)

            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        all_reqs = self._get_requests_current_year(ucode)
        today = datetime.now().date()

        # Internal implementation note: legacy behavior is preserved during modernization.
        has_today = any(
            r['status'] == status and self._to_datetime(r['created_at']).date()
            == today
            for r in all_reqs
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(BUTTONS['view_by_date']),
            types.KeyboardButton(BUTTONS['view_latest_request']),
        )
        if has_today:
            markup.add(
                types.KeyboardButton(BUTTONS['view_today_requests'])
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)

        # Internal implementation note: legacy behavior is preserved during modernization.
        title = MESSAGES['select_action_prompt'].format(
            status=STATUS_INFO[status]['title']
        )

        self.bot.send_message(
            chat_id,
            title,
            reply_markup=markup,
            parse_mode='HTML'
        )
        self.bot.register_next_step_handler(
            message, self.handle_action_selection, status)

    def handle_action_selection(self, message: types.Message, status: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        text = message.text.strip()

        if text == BUTTONS['view_by_date']:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_months(message, status)
        elif text == BUTTONS['view_latest_request']:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._just_show_last(message, status)
        elif text == BUTTONS['view_today_requests']:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_today(message, status)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                MESSAGES['invalid_option'],
                reply_markup=self.add_back_buttons(
                    types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                )
            )

    def _just_show_last(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(chat_id, "شما در سیستم ثبت نشده‌اید.")
            self.back_main(message)
            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        requests = self.db.select_dict('service_requests', 'U_code = ?', (ucode,))
        if not requests:
            self.bot.send_message(chat_id, "درخواستی برای شما ثبت نشده است.")
            self.show_requests_menu(message)

            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        latest_request = max(requests, key=lambda r: r['id'])

        # Internal implementation note: legacy behavior is preserved during modernization.
        text = self.see_handler._compose_message(latest_request)
        self.bot.send_message(chat_id, text, parse_mode='HTML')

    

    def _show_today(self, message: types.Message, status: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(chat_id, MESSAGES['no_requests_today'])
            self.show_requests_menu(message)

            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        today = datetime.now().date()
        today_reqs = [
            r for r in self._get_requests_current_year(ucode)
            if r['status'] == status and self._to_datetime(r['created_at']).date() == today
        ]

        if not today_reqs:
            self.bot.send_message(chat_id, MESSAGES['no_requests_today'])
            self.show_requests_menu(message)

            return

        for r in today_reqs:
            self.bot.send_message(
                chat_id,
                self.see_handler._compose_message(r),
                parse_mode='HTML'
            )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.show_requests_menu(message)
        return

    def _show_months(self, message: types.Message, status: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(
                chat_id, MESSAGES['no_requests'].format(status=status))
            self.show_requests_menu(message)

            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        reqs = [r for r in self._get_requests_current_year(
            ucode) if r['status'] == status]
        months = sorted({
            JalaliDate.fromtimestamp(self._to_datetime(
                r['created_at']).timestamp()).month
            for r in reqs
        })

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for m in months:
            name = MONTH_NAMES_PERSIAN.get(str(m), str(m))

            buttons.append(types.KeyboardButton(name))
        markup.add(*buttons)

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)

        self.bot.send_message(
            chat_id,
            MESSAGES['select_month_title'],
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_month_selection, status)

    def handle_month_selection(self, message: types.Message, status: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        text = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        matched_month = None
        for month_num, month_name in MONTH_NAMES_PERSIAN.items():
            if text == month_name:
                matched_month = int(month_num)      # Internal implementation note: legacy behavior is preserved during modernization.

                break

        if matched_month:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_days(message, status, matched_month)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                MESSAGES['invalid_option'],
                reply_markup=self.add_back_buttons(
                    types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=3)
                )
            )

    def _show_days(self, message: types.Message, status: str, month: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(
                chat_id, MESSAGES['no_requests'].format(status=status))
            self.show_requests_menu(message)

            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        reqs = [
            r for r in self._get_requests_current_year(ucode)
            if r['status'] == status and JalaliDate.fromtimestamp(self._to_datetime(r['created_at']).timestamp()).month == month
        ]

        days = sorted({
            JalaliDate.fromtimestamp(self._to_datetime(
                r['created_at']).timestamp()).day
            for r in reqs
        })
        if not days:
            self.bot.send_message(chat_id, MESSAGES['no_requests_for_month'])
            self.show_requests_menu(message)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        buttons = []
        for d in days:
            buttons.append(types.KeyboardButton(str(d)))
        markup.add(*buttons)

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)

        self.bot.send_message(
            chat_id,
            MESSAGES['select_day_title'],
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_day_selection, status, month)

    def handle_day_selection(self, message: types.Message, status: str, month: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        text = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not text.isdigit():
            self.bot.send_message(
                chat_id,
                MESSAGES['invalid_option'],
            )
            self.show_requests_menu(message)

            return

        day = int(text)

        if 1 <= day <= 31:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_by_day(message, status, month, day)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                MESSAGES['invalid_option'],
                reply_markup=self.add_back_buttons(
                    types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3))
            )

    def _show_by_day(self, message: types.Message, status: str, month: int, day: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return

        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            'premium_clients', 'telegram_id = ?', (telegram_id,))
        if not rows:
            self.bot.send_message(chat_id, MESSAGES['no_requests_for_day'])
            self.show_requests_menu(message)

            return
        ucode = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        reqs = [
            r for r in self._get_requests_current_year(ucode)
            if r['status'] == status
            and JalaliDate.fromtimestamp(self._to_datetime(r['created_at']).timestamp()).month == month
            and JalaliDate.fromtimestamp(self._to_datetime(r['created_at']).timestamp()).day == day
        ]

        if not reqs:
            self.bot.send_message(chat_id, MESSAGES['no_requests_for_day'])
            self.show_requests_menu(message)

            return

        for r in reqs:
            self.bot.send_message(
                chat_id,
                self.see_handler._compose_message(r),
                parse_mode='HTML'
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
        self.show_requests_menu(message)
        return

    def _to_datetime(self, value):
        """Legacy-compatible behavior preserved for this callable."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Internal implementation note: legacy behavior is preserved during modernization.
                return datetime.strptime(value.split('.')[0], "%Y-%m-%d %H:%M:%S")
        raise ValueError(f"Cannot convert {value} to datetime")
