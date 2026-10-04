import telebot
from telebot import types
from telebot.types import *

import datetime
from telegram_bot_platform.compat.config.settings import BUTTONS, MESSAGES, STATUS_TITLES 


class StaffManager:
    def __init__(self, bot, db, back_to_main, back_previous):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.db = db
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.admin_states = {}
        self.back_main = back_to_main
        self.back_pervious = back_previous

    # Internal implementation note: legacy behavior is preserved during modernization.
    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text
        if text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return True
        elif "start" in text:
            self.back_to_main(message)
            return True
        elif text == BUTTONS["back_to_previous"]:
            self.back_to_pervious(message)
            return True
        return False

    def add_back_buttons(self, markup):
        """Legacy-compatible behavior preserved for this callable."""
        buttons = [
            KeyboardButton(BUTTONS["back_to_main"]),
            KeyboardButton(BUTTONS["back_to_previous"])
        ]
        markup.add(*buttons)
        return markup

    def _make_keyboard(self, rows):
        """Legacy-compatible behavior preserved for this callable."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in rows:
            btns = [types.KeyboardButton(label) for label in row]
            markup.add(*btns)
        return markup

    def _send_message(self, message, text, keyboard=None):
        """Legacy-compatible behavior preserved for this callable."""
        if keyboard:
            sent = self.bot.send_message(
                message.chat.id, text, reply_markup=keyboard)
        else:
            sent = self.bot.send_message(message.chat.id, text)
        return sent

    # Internal implementation note: legacy behavior is preserved during modernization.

    def show_root_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        keyboard = self._make_keyboard([
            ["مشاهده پرسنل", "برنامه‌ریزی شیفت‌ها"],
            ["درخواست‌های پرسنل", "حسابداری و صورت‌حساب"],
            ["گزارشات", "ارسال پیام"],
            ["جستجو"]
        ])
        sent = self._send_message(message, MESSAGES["main_menu"], keyboard)
        self.admin_states[message.chat.id] = {"stage": "root_menu"}
        self.bot.register_next_step_handler(sent, self.handle_root_menu)

    def handle_root_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = (message.text or "").strip()
        if text == "مشاهده پرسنل":
            self.show_staff_menu(message)
        elif text == "برنامه‌ریزی شیفت‌ها":
            self.show_shift_planning_menu(message)
        elif text == "درخواست‌های پرسنل":
            self.show_requests_menu(message)
        elif text == "حسابداری و صورت‌حساب":
            self.show_accounting_menu(message)
        elif text == "گزارشات":
            self.show_reports_menu(message)
        elif text == "ارسال پیام":
            self.prompt_send_message_root(message)
        elif text == "جستجو":
            self.prompt_search_root(message)
        else:
            self.show_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def show_staff_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        keyboard = self._make_keyboard([
            [BUTTONS["approved_list"], BUTTONS["rejected_list"],
                BUTTONS["blocked_list"]],
            [BUTTONS["back"]]
        ])
        sent = self._send_message(
            message, "لطفاً وضعیت موردنظر را انتخاب کنید:", keyboard)
        self.admin_states[message.chat.id] = {"stage": "staff_menu"}
        self.bot.register_next_step_handler(sent, self.handle_staff_menu)

    def handle_staff_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = (message.text or "").strip()
        if text == BUTTONS["approved_list"]:
            self.list_staff_by_status(message, "approved")
        elif text == BUTTONS["rejected_list"]:
            self.list_staff_by_status(message, "rejected")
        elif text == BUTTONS["blocked_list"]:
            self.list_staff_by_status(message, "blocked")
        elif text == BUTTONS["back"]:
            self.show_root_menu(message)
        else:
            self.show_staff_menu(message)

    def list_staff_by_status(self, message, status_key):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        staff_list = self.db.get_staff_by_status(status_key)
        status_title = STATUS_TITLES.get(status_key, status_key)
        if not staff_list:
            self._send_message(message, MESSAGES["category_list"].format(
                status_title=status_title))
            self._send_message(message, MESSAGES["no_staff"])
            return self.show_root_menu(message)
        buttons = []
        selection_map = {}
        for idx, person in enumerate(staff_list, start=1):
            name = person.get("name", "—")
            username = person.get("username") or ""
            label = f"{idx}. {name} ({username})" if username else f"{idx}. {name}"
            buttons.append([label])
            selection_map[str(idx)] = person["id"]
        buttons.append([BUTTONS["back"]])
        keyboard = self._make_keyboard(buttons)
        list_title = MESSAGES["category_list"].format(
            status_title=status_title)
        sent = self._send_message(message, list_title, keyboard)
        self.admin_states[chat_id] = {
            "stage": "listing_staff",
            "status_key": status_key,
            "selection_map": selection_map
        }
        self.bot.register_next_step_handler(
            sent, self.handle_staff_list_selection)

    def handle_staff_list_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "listing_staff":
            return self.show_root_menu(message)
        if text == BUTTONS["back"]:
            return self.show_staff_menu(message)
        selection_map = state.get("selection_map", {})
        if text.isdigit() and text in selection_map:
            person_id = selection_map[text]
            self.show_person_detail(message, person_id)
        else:
            self.list_staff_by_status(
                message, state.get("status_key", "approved"))

    def show_person_detail(self, message, person_id):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        person = self.db.get_staff_by_id(person_id)
        ad = self.db.get_ad_by_staff(person_id)
        if not person:
            return self.go_back(message)
        name = person.get("name", "—")
        username = person.get("username", "—")
        status_key = person.get("status", "")
        status_title = STATUS_TITLES.get(status_key, status_key)
        ad_title = ad["title"] if ad else "—"
        ad_desc = ad["description"] if ad else "—"
        detail_text = MESSAGES["person_detail"].format(
            id=person_id, name=name, username=username,
            status_title=status_title, ad_title=ad_title, ad_desc=ad_desc
        )
        keyboard = self._make_keyboard([
            [BUTTONS["change_status"], BUTTONS["send_message"]],
            [BUTTONS["edit_name"], BUTTONS["edit_username"]],
            [BUTTONS["edit_ad_title"], BUTTONS["edit_ad_desc"]],
            [BUTTONS["back"]]
        ])
        sent = self._send_message(message, detail_text, keyboard)
        self.admin_states[chat_id] = {
            "stage": "person_detail",
            "person_id": person_id
        }
        self.bot.register_next_step_handler(
            sent, self.handle_person_detail_menu)

    def handle_person_detail_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "person_detail":
            return self.show_root_menu(message)
        person_id = state.get("person_id")
        if text == BUTTONS["change_status"]:
            return self.prompt_change_status(message)
        elif text == BUTTONS["send_message"]:
            return self.prompt_send_message_to_person(message)
        elif text == BUTTONS["edit_name"]:
            return self.prompt_edit_field(message, "name")
        elif text == BUTTONS["edit_username"]:
            return self.prompt_edit_field(message, "username")
        elif text == BUTTONS["edit_ad_title"]:
            return self.prompt_edit_field(message, "ad_title")
        elif text == BUTTONS["edit_ad_desc"]:
            return self.prompt_edit_field(message, "ad_desc")
        elif text == BUTTONS["back"]:
            return self.show_staff_menu(message)
        else:
            return self.show_person_detail(message, person_id)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def prompt_change_status(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "person_detail" or "person_id" not in state:
            return self.show_root_menu(message)
        person_id = state["person_id"]
        current_status = self.db.get_staff_by_id(
            person_id).get("status", "")
        status_buttons = []
        for key, title in STATUS_TITLES.items():
            if key != current_status:
                status_buttons.append([title])
        status_buttons.append([BUTTONS["back"]])
        keyboard = self._make_keyboard(status_buttons)
        sent = self._send_message(
            message, MESSAGES["choose_new_status"], keyboard)
        self.admin_states[chat_id]["stage"] = "awaiting_new_status"
        self.bot.register_next_step_handler(sent, self.handle_change_status)

    def handle_change_status(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "awaiting_new_status":
            return self.show_root_menu(message)
        if text == BUTTONS["back"]:
            return self.show_person_detail(message, state["person_id"])
        new_status_key = None
        for key, val in STATUS_TITLES.items():
            if val == text:
                new_status_key = key
                break
        if not new_status_key:
            return self.prompt_change_status(message)
        person_id = state["person_id"]
        old_status = self.db.get_staff_by_id(person_id).get("status", None)
        self.db.update_staff_status(person_id, new_status_key)
        if old_status:
            self.db.log_status_change(
                person_id, old_status, new_status_key, datetime.datetime.now()
            )
        status_title = STATUS_TITLES.get(new_status_key, new_status_key)
        confirm_text = MESSAGES["status_updated"].format(
            status_title=status_title)
        self._send_message(message, confirm_text)
        self.show_person_detail(message, person_id)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def prompt_edit_field(self, message, field):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "person_detail" or "person_id" not in state:
            return self.show_root_menu(message)
        if field == "name":
            prompt_text = MESSAGES["enter_new_name"]
        elif field == "username":
            prompt_text = MESSAGES["enter_new_username"]
        elif field == "ad_title":
            prompt_text = MESSAGES["enter_new_ad_title"]
        elif field == "ad_desc":
            prompt_text = MESSAGES["enter_new_ad_desc"]
        else:
            return self.show_person_detail(message, state["person_id"])
        keyboard = self._make_keyboard([[BUTTONS["back"]]])
        sent = self._send_message(message, prompt_text, keyboard)
        self.admin_states[chat_id]["stage"] = "awaiting_field_value"
        self.admin_states[chat_id]["edit_field"] = field
        self.bot.register_next_step_handler(sent, self.handle_edit_field)

    def handle_edit_field(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "awaiting_field_value":
            return self.show_root_menu(message)
        if text == BUTTONS["back"]:
            return self.show_person_detail(message, state.get("person_id"))
        person_id = state.get("person_id")
        field = state.get("edit_field")
        if field == "name":
            self.db.update_staff_field(person_id, "name", text)
            confirm_text = MESSAGES["name_updated"].format(name=text)
        elif field == "username":
            self.db.update_staff_field(person_id, "username", text)
            confirm_text = MESSAGES["username_updated"].format(username=text)
        elif field == "ad_title":
            ad = self.db.get_ad_by_staff(person_id)
            if ad:
                self.db.update_ad_field(ad["id"], "title", text)
            else:
                self.db.create_ad_for_staff(
                    person_id, title=text, description="")
            confirm_text = MESSAGES["ad_title_updated"].format(ad_title=text)
        elif field == "ad_desc":
            ad = self.db.get_ad_by_staff(person_id)
            if ad:
                self.db.update_ad_field(ad["id"], "description", text)
            else:
                self.db.create_ad_for_staff(
                    person_id, title="بدون عنوان", description=text)
            confirm_text = MESSAGES["ad_desc_updated"]
        else:
            return self.show_person_detail(message, person_id)
        self._send_message(message, confirm_text)
        self.show_person_detail(message, person_id)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def prompt_send_message_to_person(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "person_detail":
            return self.show_root_menu(message)
        keyboard = self._make_keyboard([[BUTTONS["back"]]])
        sent = self._send_message(
            message, MESSAGES["enter_message_text"], keyboard)
        self.admin_states[chat_id]["stage"] = "awaiting_person_message"
        self.bot.register_next_step_handler(
            sent, self.handle_send_message_to_person)

    def handle_send_message_to_person(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "awaiting_person_message":
            return self.show_root_menu(message)
        if text == BUTTONS["back"]:
            return self.show_person_detail(message, state.get("person_id"))
        person_id = state.get("person_id")
        # Internal implementation note: legacy behavior is preserved during modernization.
        person = self.db.get_staff_by_id(person_id)
        target_chat_id = person.get("chat_id") if person else None
        if target_chat_id:
            self.bot.send_message(target_chat_id, text)
            self._send_message(message, MESSAGES["message_sent"])
        else:
            self._send_message(message, "⚠️ شناسه چت پرسنل یافت نشد.")
        self.show_person_detail(message, person_id)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def prompt_search_root(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        keyboard = self._make_keyboard([[BUTTONS["back"]]])
        sent = self._send_message(message, MESSAGES["enter_search"], keyboard)
        self.admin_states[message.chat.id] = {"stage": "root_search"}
        self.bot.register_next_step_handler(sent, self.handle_root_search)

    def handle_root_search(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = (message.text or "").strip()
        if text == BUTTONS["back"]:
            return self.show_root_menu(message)
        self.perform_search(message, text)

    def perform_search(self, message, query):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        results = self.db.search_staff(query)
        if not results:
            self._send_message(message, MESSAGES["no_results"])
            return self.show_root_menu(message)
        buttons = []
        selection_map = {}
        for idx, person in enumerate(results, start=1):
            name = person.get("name", "—")
            username = person.get("username") or ""
            label = f"{idx}. {name} ({username})" if username else f"{idx}. {name}"
            buttons.append([label])
            selection_map[str(idx)] = person["id"]
        buttons.append([BUTTONS["back"]])
        keyboard = self._make_keyboard(buttons)
        result_text = MESSAGES["search_results"].format(query=query)
        sent = self._send_message(message, result_text, keyboard)
        self.admin_states[chat_id] = {
            "stage": "search_results",
            "selection_map": selection_map
        }
        self.bot.register_next_step_handler(sent, self.handle_search_results)

    def handle_search_results(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        state = self.admin_states.get(chat_id, {})
        if state.get("stage") != "search_results":
            return self.show_root_menu(message)
        if text == BUTTONS["back"]:
            return self.show_root_menu(message)
        selection_map = state.get("selection_map", {})
        if text.isdigit() and text in selection_map:
            person_id = selection_map[text]
            self.show_person_detail(message, person_id)
        else:
            self.show_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def show_shift_planning_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        self._send_message(
            message, "⏰ [Placeholder] منوی برنامه‌ریزی شیفت‌ها.")
        self.show_root_menu(message)

    def show_requests_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        self._send_message(message, "📄 [Placeholder] درخواست‌های پرسنل.")
        self.show_root_menu(message)

    def show_accounting_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        self._send_message(message, "💰 [Placeholder] حسابداری و صورت‌حساب.")
        self.show_root_menu(message)

    def show_reports_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        self._send_message(message, "📊 [Placeholder] گزارشات.")
        self.show_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.

    def start_conversation(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        self.show_root_menu(message)


# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
#
# import telebot
# from telegram_bot_platform.compat.config.settings import BOT_TOKEN
# from DataBaseManager import DataBaseManager
# from staff_manager import StaffManager
#
# bot = telebot.TeleBot(BOT_TOKEN)
# Internal implementation note: legacy behavior is preserved during modernization.
# staff_manager = StaffManager(bot, db_manager)
#
# @bot.message_handler(commands=['start'])
# def start_handler(message):
#     staff_manager.start_conversation(message)
#
# bot.polling()
