# Internal implementation note: legacy behavior is preserved during modernization.

from datetime import datetime, timedelta
from telebot.util import content_type_media
import json
import traceback
# Internal implementation note: legacy behavior is preserved during modernization.
from telebot import TeleBot
from telebot.types import (

    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# Client Handlers

from telegram_bot_platform.compat.handlers.client.ads_handler import AdsHandler
from telegram_bot_platform.compat.utils.temporary_state import save_filter_snapshot
# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger


log = CustomLogger()  # log_file="tD_code.log")


class TodayCodesFilterHandler:
    def __init__(self, bot: TeleBot, db: DatabaseManager, back_main, back_previous, start):
        self.bot = bot
        self.db = db
        self.back_main = back_main
        self.back_previous = back_previous
        self.start = start
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.ads_handler = AdsHandler(bot, db)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # chat_id -> { filters: {...}, codes: [...], page: int, msg_id: int }
        self.user_state = {}

    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text or ''
        if text == BUTTONS["back_to_main_menu"]:
            self.back_main(message)
            return True
        if text.startswith("/start"):
            self.start(message)
            return True
        if text == BUTTONS["back_to_pervious_menu"]:
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
            KeyboardButton(BUTTONS["back_to_pervious_menu"])
        )
        return markup

    def _start(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        self.back_previous = self.back_main

        self.user_state[chat_id] = {
            'filters': {},
            'codes': [],
            'page': 1,
            'msg_id': None,
            'premium': False,
            'city': None,
            'province': None,
        }

        premium = self.db.select_dict(
            "premium_clients",
            "telegram_id = ? AND C_status = 'approved'",
            (chat_id,)
        )
        if premium:
            self.user_state[chat_id]['premium'] = True
            self._show_premium_menu(message)
        else:
            self._ask_location(message)

    def _show_premium_menu(self, message):
        chat_id = message.chat.id
        self.back_previous = self._start
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton(BUTTONS["premium_search_same_city"]),
            KeyboardButton(BUTTONS["premium_search_all"]),
            KeyboardButton(BUTTONS["premium_search_all_codes"])
        )
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, MESSAGES["premium_search_mode"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self._handle_premium_menu_selection)

    def _handle_premium_menu_selection(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        if self.is_back(message):
            return
        self.back_previous = self._show_premium_menu

        choice = message.text
        if choice == BUTTONS["premium_search_same_city"]:
            user_data = self.db.select_dict(
                "premium_clients", "telegram_id = ?", (user_id,))
            if user_data:
                self.user_state[chat_id]['filters']['province'] = user_data[0].get(
                    'province')
                self.user_state[chat_id]['filters']['city'] = user_data[0].get(
                    'city')
                self._choose_area_or_all(chat_id)
            else:
                self.bot.send_message(chat_id, MESSAGES["user_city_not_found"])
                self._start(message)
        elif choice == BUTTONS["premium_search_all"]:
            self._ask_location(message)
        elif choice == BUTTONS["premium_search_all_codes"]:
            self._perform_search_all_codes(chat_id)

        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            self._show_premium_menu(message)

    def _perform_search_all_codes(self, chat_id):
        # today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # tomorrow = today + timedelta(days=1)

        staff_matched = self.db.select_dict(
            "staff",  # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
        )

        pucodes = [staff['U_code'] for staff in staff_matched]

        if not pucodes:
            self.bot.send_message(chat_id, MESSAGES["no_codes_today"])
            self._show_premium_menu(chat_id)
            return

        self.user_state[chat_id]['codes'] = pucodes
        self.user_state[chat_id]['page'] = 1

        self._show_codes_page(chat_id)

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    #  Client_handlers/to_day_cods.py
    # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.

    def _ask_location(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        self.back_previous = self._start  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            rows = self.db.select_dict("staff")
            provinces = {row["province"]
                         for row in rows if row.get("province")}
        except Exception:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                "❌ خطا در دریافت اطلاعات استان‌ها. لطفاً بعداً دوباره تلاش کنید.",
            )
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not provinces:
            self.bot.send_message(
                chat_id,
                "⚠️ لیست استان‌ها در حال حاضر در دسترس نیست.\n"
                "🔄 لطفاً بعداً دوباره امتحان کنید.",
            )
            return  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*[KeyboardButton(p) for p in sorted(provinces)])
        markup = self.add_back_buttons(markup)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id]["provinces"] = provinces

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            "🌍 لطفاً استان مورد نظر را انتخاب کنید:",
            reply_markup=markup,
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler_by_chat_id(
            chat_id,
            self._handle_province_selection,
        )

    # Internal implementation note: legacy behavior is preserved during modernization.

    def _handle_province_selection(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        self.back_previous = self._ask_location

        province = message.text
        if province not in self.user_state[chat_id]["provinces"]:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            self._ask_location(message)
            return

        self.user_state[chat_id]['filters']['province'] = province
        Pu_codes = self.db.select_dict(
            "staff", "province = ?", (province,))
        cities = set([p['city'] for p in Pu_codes])
        if not cities:
            self.bot.send_message(chat_id, MESSAGES["no_cities"])
            self._ask_location(message)
            return

        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True, row_width=3)
        buttons = [KeyboardButton(c) for c in cities]
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)
        self.user_state[chat_id]['cities'] = cities
        self.bot.send_message(
            chat_id, MESSAGES["select_city"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self._handle_city_selection)

    def _handle_city_selection(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        self.back_previous = self._handle_province_selection

        city = message.text
        if city not in self.user_state[chat_id]['cities']:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            message.text = self.user_state[chat_id]['filters']['province']
            self._handle_province_selection(message)
            return

        self.user_state[chat_id]['filters']['city'] = city

        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            KeyboardButton(MESSAGES["select_area"]),
            KeyboardButton(MESSAGES["search_entire_city"])
        )
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, MESSAGES["choose_area_or_all"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self._handle_area_or_search)

    def extract_available_areas(self, province, city, date_from, date_to):
        staff = self.db.select_dict(
            "staff", "province = ? AND city = ?", (province, city)
        )
        pucodes = [p['U_code'] for p in staff]
        if not pucodes:
            return [], []

        placeholders = ",".join(["?"] * len(pucodes))
        ads = self.db.select_dict(
            "ads",
            f"U_code IN ({placeholders}) ",
            (*pucodes,)
        )

        areas = set()
        for ad in ads:
            if ad.get("region"):
                for region in str(ad['region']).split(','):
                    cleaned = region.strip()
                    if cleaned:
                        areas.add(cleaned)
        return list(sorted(areas)), pucodes

    def show_area_selection_menu(self, chat_id, areas, prompt, next_handler):
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True, row_width=3)
        buttons = []
        for area in areas:
            buttons.append(KeyboardButton(area))
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)
        self.bot.send_message(chat_id, prompt, reply_markup=markup)
        self.back_previous = self._reask_area_or_search
        self.bot.register_next_step_handler_by_chat_id(chat_id, next_handler)

    def _handle_area_or_search(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return

        text = message.text
        province = self.user_state[chat_id]['filters'].get('province')
        city = self.user_state[chat_id]['filters'].get('city')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        if text == MESSAGES['select_area']:
            areas, _ = self.extract_available_areas(
                province, city, today, tomorrow)
            if not areas:
                self.bot.send_message(chat_id, MESSAGES["no_areas_found"])
                return self._reask_area_or_search(chat_id)
            self.show_area_selection_menu(
                chat_id, areas, MESSAGES["select_area_specific"], self._handle_area_selection)

        elif text == MESSAGES['search_entire_city']:
            self.user_state[chat_id]['filters']['area'] = None
            self._perform_search(chat_id)
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            return self._reask_area_or_search(chat_id)

    def _handle_area_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        area = message.text
        province = self.user_state[chat_id]['filters'].get('province')
        city = self.user_state[chat_id]['filters'].get('city')

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.back_previous = self._reask_area_or_search

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        # Internal implementation note: legacy behavior is preserved during modernization.
        areas, pucodes = self.extract_available_areas(
            province, city, today, tomorrow)
        if area not in areas:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            return self.show_area_selection_menu(
                chat_id, areas, MESSAGES["select_area_specific"], self._handle_area_selection
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id]['filters']['area'] = area

        # Internal implementation note: legacy behavior is preserved during modernization.
        filtered_codes = []
        placeholders = ",".join(["?"] * len(pucodes))
        ads = self.db.select_dict(
            "ads",
            f"U_code IN ({placeholders})",
            (*pucodes,)
        )
        for ad in ads:
            if area in str(ad.get("region", "")):
                filtered_codes.append(ad["U_code"])

        self.user_state[chat_id]['codes'] = list(set(filtered_codes))
        self.user_state[chat_id]['page'] = 1

        if not filtered_codes:
            self.bot.send_message(chat_id, MESSAGES["no_codes"])
            return self._reask_area_or_search(chat_id)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._show_codes_page(chat_id)

    def _handle_area_or_city_selection(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return

        text = message.text
        province = self.user_state[chat_id]['filters'].get('province')
        city = self.user_state[chat_id]['filters'].get('city')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        if text == BUTTONS["select_specific_area"]:
            areas, _ = self.extract_available_areas(
                province, city, today, tomorrow)
            if not areas:
                self.bot.send_message(chat_id, MESSAGES["no_areas_found"])
                return self._choose_area_or_all(chat_id)
            self.show_area_selection_menu(
                chat_id, areas, MESSAGES["select_area_prompt"], self._handle_area_selection)

        elif text == BUTTONS["search_entire_city"]:
            self.user_state[chat_id]['filters']['area'] = None
            self._perform_search(chat_id)
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            self._choose_area_or_all(chat_id)

    def _choose_area_or_all(self, chat_id):
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            KeyboardButton(BUTTONS["select_specific_area"]),
            KeyboardButton(BUTTONS["search_entire_city"])
        )
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id,
            MESSAGES["choose_area_or_all"],
            reply_markup=markup
        )
        self.bot.register_next_step_handler_by_chat_id(
            chat_id,
            self._handle_area_or_city_selection
        )

    def _reask_area_or_search(self, chat_id):
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            KeyboardButton(MESSAGES["select_area"]),
            KeyboardButton(MESSAGES["search_entire_city"])
        )
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id,
            MESSAGES["choose_area_or_all"],
            reply_markup=markup
        )
        self.bot.register_next_step_handler_by_chat_id(
            chat_id,
            self._handle_area_or_search
        )

    # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _perform_search(self, message_or_id):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        if isinstance(message_or_id, int):
            chat_id = message_or_id
        else:
            message = message_or_id
            chat_id = message.chat.id
            if self.is_back(message):
                return

        province = self.user_state[chat_id]['filters'].get('province')
        city = self.user_state[chat_id]['filters'].get('city')

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        # Internal implementation note: legacy behavior is preserved during modernization.
        staff_matched = self.db.select_dict(
            "staff",
            "province = ? AND city = ?",
            (province, city)
        )

        pucodes = [staff['U_code'] for staff in staff_matched]

        if not pucodes:
            self.bot.send_message(
                chat_id, MESSAGES["no_codes_to_this_city_today"])
            self._choose_area_or_all(chat_id)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id]['codes'] = pucodes
        self.user_state[chat_id]['page'] = 1

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._show_codes_page(chat_id)
    # import json
    
    def make_json_safe(self , obj):
        """Legacy-compatible behavior preserved for this callable."""
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: self.make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.make_json_safe(i) for i in obj]
        else:
            return obj

    def _show_codes_page(self, chat_id):
        """Legacy-compatible behavior preserved for this callable."""
        codes = self.user_state[chat_id]['codes']
        page = self.user_state[chat_id]['page']
        if chat_id not in self.user_state:
            log.warning(f"[CodesList] No state found for chat {chat_id}")
            return

        PAGE_SIZE = 20  # Internal implementation note: legacy behavior is preserved during modernization.

        total_pages = (len(codes) + PAGE_SIZE - 1) // PAGE_SIZE
        page = max(1, min(page, total_pages))  # Internal implementation note: legacy behavior is preserved during modernization.

        start_idx = (page - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_codes = codes[start_idx:end_idx]

        markup = InlineKeyboardMarkup(row_width=3)
        row = []
        for idx, code in enumerate(page_codes, 1):
            row.append(InlineKeyboardButton(
                text=f"🧍‍♀️ کد {code}",
                callback_data=f"premium_fav_profile_{code}"
            ))
            if idx % 3 == 0:
                markup.row(*row)
                row = []
        if row:
            markup.row(*row)

        snapshot_id = save_filter_snapshot(
            self.db, chat_id, self.user_state[chat_id])
        markup.add(
            InlineKeyboardButton(
                "🛠 فیلتر جستجو", callback_data=f"filter_search|{snapshot_id}"),
            InlineKeyboardButton(
                "✅ فعال‌های امروز", callback_data=f"Actives|{snapshot_id}")
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(
                "⬅️ صفحه قبلی", callback_data=f"codes_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(
                "➡️ صفحه بعدی", callback_data=f"codes_page_{page+1}"))
        if nav_buttons:
            markup.row(*nav_buttons)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.user_state[chat_id].get('msg_id'):
            try:
                self.bot.edit_message_reply_markup(
                    chat_id, self.user_state[chat_id]['msg_id'], reply_markup=markup)
                return
            except:
                self.user_state[chat_id]['msg_id'] = None

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            msg = self.bot.send_message(
                chat_id,
                MESSAGES["codes_list_info"].format(current=page, total=total_pages),
                reply_markup=markup
            )
            log.info(f"[CodesList] Page {page} of {total_pages} sent to user {chat_id}.")



            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    reply_markup_json = json.dumps(markup.to_dict(), ensure_ascii=False)
                except Exception:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    reply_markup_json = ""
                    log.warning("[Filters] failed to serialize reply-markup\n" +
                                traceback.format_exc())

                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    state_json = json.dumps(self.make_json_safe(self.user_state[chat_id]), ensure_ascii=False)
                except Exception:
                    state_json = "{}"
                    log.warning("[Filters] failed to serialize user_state\n" +
                                traceback.format_exc())

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.upsert(
                    "filters",
                    {
                        "msg_id":            msg.message_id,
                        "telegram_id":       chat_id,
                        "reply_markup_json": reply_markup_json,
                        "user_state":        state_json,
                        "snapshot_id":snapshot_id,
                        "U_codes" : json.dumps(page_codes)
                    },
                    key="telegram_id",          # Internal implementation note: legacy behavior is preserved during modernization.
                    unique_column="telegram_id",
                    column_types={"user_state":"JSON","reply_markup_json":"JSON","snapshot_id":"TEXT"}
                    # Internal implementation note: legacy behavior is preserved during modernization.
                )

                log.debug(f"[Filters] list saved → msg_id={msg.message_id} chat={chat_id}")

            except Exception as e:
                log.exception(f"[Filters] DB-save failed for chat {chat_id}: {e}")


            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.user_state.setdefault(chat_id, {})["msg_id"] = msg.message_id
                log.debug(f"[UserState] Updated msg_id for user {chat_id}.")
            except Exception as e:
                log.exception(f"[UserState] Failed to update msg_id for user {chat_id}: {e}")

        except Exception as e:
            log.exception(f"[CodesList] Failed to send paginated codes message to user {chat_id}: {e}")

    def _get_today_active_ucodes(self) -> set:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()  # YYYY-MM-DD
            # Internal implementation note: legacy behavior is preserved during modernization.
            ads = self.db.select_dict(
                "ads",
                "status = 'approved' AND date(created_at) = ?",
                (today,)
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            active_ucodes = {ad['U_code'] for ad in ads if ad.get('U_code')}
            return active_ucodes
        except Exception as exc:
            log.exception(f"[TodayFilter] failed to load today-active ads: {exc}")
            return set()

    def _show_codes_page(self, chat_id):
        """Legacy-compatible behavior preserved for this callable."""
        if chat_id not in self.user_state:
            log.warning(f"[CodesList] No state found for chat {chat_id}")
            return

        codes = self.user_state[chat_id].get('codes', [])
        page = self.user_state[chat_id].get('page', 1)

        PAGE_SIZE = 20  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        active_ucodes = self._get_today_active_ucodes()
        active_codes = [code for code in codes if code in active_ucodes]

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id]["today_filter"] = True
        self.user_state[chat_id]["backup_codes"] = codes
        # Internal implementation note: legacy behavior is preserved during modernization.
        total_pages = (len(active_codes) + PAGE_SIZE - 1) // PAGE_SIZE if active_codes else 1
        page = max(1, min(page, total_pages))  # Internal implementation note: legacy behavior is preserved during modernization.

        start_idx = (page - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_codes = active_codes[start_idx:end_idx]

        markup = InlineKeyboardMarkup(row_width=4)  # Internal implementation note: legacy behavior is preserved during modernization.

        if page_codes:
            row = []
            for idx, code in enumerate(page_codes, 1):
                row.append(InlineKeyboardButton(
                    text=f"🧍‍♀️ کد {code}",
                    callback_data=f"premium_fav_profile_{code}"
                ))
                if idx % 4 == 0:
                    markup.row(*row)
                    row = []
            if row:
                markup.row(*row)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(InlineKeyboardButton(
                "❌ هیچ کد فعالی در حال حاضر موجود نمی‌باشد.",
                callback_data="no_active_codes"
            ))

        # Internal implementation note: legacy behavior is preserved during modernization.
        snapshot_id = save_filter_snapshot(self.db, chat_id, self.user_state[chat_id])

        # Internal implementation note: legacy behavior is preserved during modernization.
        # markup.add(
        #     InlineKeyboardButton(
        # Internal implementation note: legacy behavior is preserved during modernization.
        #     )
        # )
        markup.add(
            InlineKeyboardButton(
                "🛠 فیلتر جستجو", callback_data=f"filter_search|{snapshot_id}"),
            InlineKeyboardButton(
                "👁 مشاهده همه", callback_data=f"Actives|{snapshot_id}")
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        if total_pages > 1:
            nav_buttons = []
            if page > 1:
                nav_buttons.append(InlineKeyboardButton(
                    "⬅️ صفحه قبلی", callback_data=f"codes_page_{page-1}"))
            if page < total_pages:
                nav_buttons.append(InlineKeyboardButton(
                    "➡️ صفحه بعدی", callback_data=f"codes_page_{page+1}"))
            if nav_buttons:
                markup.row(*nav_buttons)

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            if self.user_state[chat_id].get('msg_id'):
                self.bot.edit_message_reply_markup(
                    chat_id, self.user_state[chat_id]['msg_id'], reply_markup=markup)
                return
        except Exception as e:
            log.warning(f"[CodesList] Failed to edit message markup for user {chat_id}: {e}")
            self.user_state[chat_id]['msg_id'] = None

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            text_msg = MESSAGES.get("codes_list_info",
                "صفحه {current} از {total}").format(current=page, total=total_pages)

            msg = self.bot.send_message(
                chat_id,
                text_msg,
                reply_markup=markup
            )
            log.info(f"[CodesList] Page {page} of {total_pages} sent to user {chat_id}.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state.setdefault(chat_id, {})["msg_id"] = msg.message_id

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                reply_markup_json = json.dumps(markup.to_dict(), ensure_ascii=False)
            except Exception:
                reply_markup_json = ""
                log.warning("[Filters] failed to serialize reply-markup\n" + traceback.format_exc())

            try:
                state_json = json.dumps(self.make_json_safe(self.user_state[chat_id]), ensure_ascii=False)
            except Exception:
                state_json = "{}"
                log.warning("[Filters] failed to serialize user_state\n" + traceback.format_exc())

            self.db.upsert(
                "filters",
                {
                    "msg_id": msg.message_id,
                    "telegram_id": chat_id,
                    "reply_markup_json": reply_markup_json,
                    "user_state": state_json,
                    "snapshot_id": snapshot_id,
                    "U_codes": json.dumps(page_codes)
                },
                key="telegram_id",
                unique_column="telegram_id",
                column_types={"user_state": "JSON", "reply_markup_json": "JSON", "snapshot_id": "TEXT"}
            )
            log.debug(f"[Filters] List saved → msg_id={msg.message_id} chat={chat_id}")

        except Exception as e:
            log.exception(f"[CodesList] Failed to send paginated codes message to user {chat_id}: {e}")
