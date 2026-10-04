from telebot import types, TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from re import match
import json
from telegram_bot_platform.compat.config.settings import MESSAGES, BUTTONS, SERVICES
from telegram_bot_platform.compat.utils.locations import LocationHandler
from telegram_bot_platform.compat.utils.location_utils import get_location_details
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Internal implementation note: legacy behavior is preserved during modernization.
NAME_PATTERN = r"^(?:[a-zA-Z]{2,25}(?: [a-zA-Z]{2,25})?|[\u0600-\u06FF]{2,25}(?:[\s‌][\u0600-\u06FF]{2,25})?)$"


class PREMIUMRegistration:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot: TeleBot, db: DatabaseManager, back_main, back_previous):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.db = db
        self.back_main = back_main
        self.back_previous = back_previous
        self.location_handler = LocationHandler()
        self.temp_review_dict = {}  # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request = {}
        self.temp_data = {}         # Internal implementation note: legacy behavior is preserved during modernization.

    def is_back(self, message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text
        if text == BUTTONS["back_to_main_menu"]:
            self.back_main(message)
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

    def start_registration(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        if not message.from_user.username:
            self.bot.send_message(
                chat_id, MESSAGES["premium_reg_request_username"])
            self.back_previous(message)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_data[chat_id] = {
            "telegram_id": chat_id,
            "username": message.from_user.username,
            "C_status": "approved"
        }

        # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.

        self.create_checkbox_panel(message)

    def handle_contact(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        if not message.contact:
            self.bot.send_message(chat_id, MESSAGES["premium_reg_ask_phone"])
            self.bot.register_next_step_handler(message, self.handle_contact)
            return

        self.temp_data[chat_id]["phone"] = message.contact.phone_number

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, MESSAGES["premium_reg_ask_name"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_name)

    def handle_name(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        name = message.text.strip()
        if not name or not match(NAME_PATTERN, name):
            self.bot.send_message(chat_id, MESSAGES["wrong_name"])
            self.bot.register_next_step_handler(message, self.handle_name)
            return

        self.temp_data[chat_id]["name"] = name

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.show_province_menu(message)

    def show_province_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        provinces = self.location_handler.get_all_provinces()
        if not provinces:
            self.bot.send_message(chat_id, MESSAGES["no_provinces"])
            return

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        buttons = [KeyboardButton(province) for province in provinces]
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)

        self.bot.send_message(
            chat_id, MESSAGES["select_province"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.handle_province_selection)

    def handle_province_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        province = message.text.strip()
        provinces = self.location_handler.get_all_provinces()
        if province not in provinces:
            self.bot.send_message(chat_id, MESSAGES["invalid_province"])
            self.show_province_menu(message)
            return

        self.temp_data[chat_id]["province"] = province
        cities_dict = self.location_handler.get_all_cities(as_dict=True)
        if province not in cities_dict:
            self.bot.send_message(
                chat_id, "خطا در دریافت شهرهای استان انتخاب شده.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        cities = cities_dict[province]
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        buttons = [KeyboardButton(city) for city in cities]
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)

        self.bot.send_message(
            chat_id, MESSAGES["select_city"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.handle_city_selection)

    def handle_city_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        city = message.text.strip()
        province = self.temp_data[chat_id].get("province")
        cities_dict = self.location_handler.get_all_cities(as_dict=True)
        if province not in cities_dict or city not in cities_dict[province]:
            self.bot.send_message(chat_id, MESSAGES["invalid_city"])
            self.show_province_menu(message)
            return

        self.temp_data[chat_id]["city"] = city
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.ask_for_gps(message)

    def ask_for_gps(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton(BUTTONS["send_gps"], request_location=True),
            KeyboardButton(BUTTONS["skip_send_gps"]),
        )
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, MESSAGES["gps_prompt"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_gps_location)

    def handle_gps_location(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        locations = ""
        if message.location:
            lat = message.location.latitude
            lon = message.location.longitude
            self.temp_data[chat_id]["latitude"] = lat
            self.temp_data[chat_id]["longitude"] = lon
            locations = get_location_details(lat, lon)
            self.temp_data[chat_id]["locations"] = json.dumps(locations)

        # Internal implementation note: legacy behavior is preserved during modernization.
        province = self.temp_data[chat_id].get("province")
        city = self.temp_data[chat_id].get("city")

        confirmation_text = MESSAGES["premium_reg_confirm_location"].format(
            province=province, city=city, loc=f"📍 لوکیشن ارسالی شما:\n🗺️ استان: {locations.get('province', '-')}\n🏙️ شهر: {locations.get('city', '-')}\n📌 منطقه: {locations.get('area', '-')}" if locations else ""
        )
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True, row_width=2)
        markup.add(BUTTONS["confirm"], BUTTONS["edit"])
        markup = self.add_back_buttons(markup)
        self.bot.send_message(chat_id, confirmation_text, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_location_confirmation)

    def handle_location_confirmation(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        if message.text.strip() == BUTTONS["confirm"]:
            self.temp_data[chat_id]["location_confirmed"] = True
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True)
            markup.add(BUTTONS["i_dont_have"])
            markup = self.add_back_buttons(markup)

            self.bot.send_message(
                chat_id, MESSAGES["premium_reg_ask_referral"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.handle_referral)
            # self.handle_referral(message)
        elif message.text.strip() == BUTTONS["edit"]:
            self.show_province_menu(message)
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            self.bot.register_next_step_handler(
                message, self.handle_location_confirmation)

    @staticmethod
    def invert_dict(d: dict) -> dict:
        """Legacy-compatible behavior preserved for this callable."""
        return {v: k for k, v in d.items()}

    def create_checkbox_panel(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        self.bot.send_message(chat_id, MESSAGES["premium_ask_custom_fantasy"])

        # Internal implementation note: legacy behavior is preserved during modernization.
        display_keys = list(SERVICES.keys())

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_review_dict[chat_id] = {k: False for k in display_keys}

        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for key in display_keys:
            label = SERVICES.get(key, key)
            value = self.temp_review_dict[chat_id][key]
            icon = "✅" if value else ""
            button_text = f"{icon} {label}" if icon else label
            buttons.append(KeyboardButton(button_text))

        for i in range(0, len(buttons), 3):
            markup.add(*buttons[i:i + 3])

        markup.add(KeyboardButton(BUTTONS["submit_favorits"]), KeyboardButton(
            BUTTONS["skip_custom_fantasy"]))
        markup.add(
            KeyboardButton(BUTTONS["back_to_pervious_menu"]),
            KeyboardButton(BUTTONS["back_to_main_menu"])
        )

        self.bot.send_message(
            chat_id, MESSAGES["Choice_Favorites"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.toggle_review_checkbox)

    def show_check_box(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return

        check_boxes = self.temp_review_dict.get(chat_id, {})
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for box in check_boxes:
            label = SERVICES.get(box, box)
            status = "✅" if check_boxes[box] else ""
            button_text = f"{status} {label}" if status else label
            buttons.append(KeyboardButton(button_text))

        for i in range(0, len(buttons), 3):
            markup.add(*buttons[i:i + 3])

        markup.add(KeyboardButton(BUTTONS["submit_favorits"]), KeyboardButton(
            BUTTONS["skip_custom_fantasy"]))
        markup.add(
            KeyboardButton(BUTTONS["back_to_pervious_menu"]),
            KeyboardButton(BUTTONS["back_to_main_menu"])
        )

        self.bot.send_message(
            chat_id, MESSAGES["Choice_Favorites"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.toggle_review_checkbox)

    def toggle_review_checkbox(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        text = message.text
        if text == BUTTONS["submit_favorits"] or text == BUTTONS["skip_custom_fantasy"]:
            self.handle_preferences_selection(message)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text.startswith("✅"):
            service_label = text[2:].strip()
        else:
            service_label = text.strip()

        conv = self.invert_dict(SERVICES)
        service_key = conv.get(service_label, service_label)
        if service_key in self.temp_review_dict.get(chat_id, {}):
            self.temp_review_dict[chat_id][service_key] = not self.temp_review_dict[chat_id][service_key]
        self.show_check_box(message)

    def route_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if message.text.strip() == BUTTONS["back_to_main_menu"]:
            self.back_main(message)
        elif message.text.strip() == BUTTONS["back_to_pervious_menu"]:
            self.back_previous(message)

    def handle_preferences_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        conv = self.invert_dict(SERVICES)
        self.temp_data[chat_id]["favority"] = json.dumps({
            conv.get(k, k): v for k, v in self.temp_review_dict.get(chat_id, {}).items()
        })
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        button = KeyboardButton(BUTTONS["send_contact"], request_contact=True)
        markup.add(button)
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, MESSAGES["premium_reg_ask_phone"], reply_markup=markup)

        self.bot.register_next_step_handler(message, self.handle_contact)

    def handle_referral(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return

        self.temp_data[chat_id]["referral"] = message.text.strip()
        self.finalize_registration(message)

    def finalize_registration(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_data = self.temp_data.get(chat_id, {})

        if self.is_back(message):
            return
        user_exists = self.db.select_dict(
            "clients", "telegram_id = ?", (user_id,)
        )
        if not user_exists:
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_idx = self.db.count_rows(
                "clients") if self.db.table_exists("clients") else 0
            U_code = f"c{next_idx + 1 + 3420}"
            user_data["U_code"] = U_code

        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            U_code = user_exists[0].get("U_code")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # current_name = user_exists[0].get("name", "")
            # new_name = self.current_request[chat_id].get("name", "")
            # if not current_name and new_name:
            #     self.db.update("clients", {"name": new_name},
            #                    "telegram_id = ?", (user_id,))
            # self.db.update("clients", {"name": new_name},
            #                "telegram_id = ?", (user_id,))
            user_data["U_code"] = U_code
        print(user_data)
        self.db.insert("premium_clients", user_data)
        self.bot.send_message(
            chat_id, MESSAGES["premium_reg_registration_success"])
        try:
            self.back_previous(message)
        except:
            self.back_main(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_data.pop(chat_id, None)
