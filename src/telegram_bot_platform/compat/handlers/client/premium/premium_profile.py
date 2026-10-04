from typing import Any, Callable, Dict
from telebot import TeleBot, types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telegram_bot_platform.compat.config.settings import *
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.utils.locations import LocationHandler

# from telegram_bot_platform.compat.handlers.client.identity_verification.identity_verification import AuthenticationManager, PhotoAuthStep, VideoAuthStep, ContactAuthStep
# from datetime import datetime
import json
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

logger = CustomLogger("premium_profile")

class PREMIUMProfile:
    """
    Improved PREMIUM Client Profile System for a Telegram bot.

    Features:
    - View Profile: Displays user data with translated labels and profile photo.
    - Edit Profile: Edits existing fields directly in the database.
    - Complete Profile: Submits requests for missing fields for admin approval.
    - IDENTITY_VERIFICATION Verification: Handles identity verification with progress tracking.
    """

    def __init__(self, bot: TeleBot, db: DatabaseManager, back_main, back_previous, start):
        """
        Initializes the PREMIUMProfile class.

        Args:
            bot (TeleBot): Telegram bot instance.
            db (DatabaseManager): Database manager instance.
            back_main_callback (Callable): Callback for returning to main menu.
            back_previous_callback (Callable): Callback for returning to previous menu.
        """
        self.location_handler = LocationHandler()

        self.bot = bot
        self.db = db
        self.back_main = back_main
        self.back_previous = back_previous
        self.auth_context = {}
        self.start = start
        self.temp_data = {}
        self.current_step = {}
        # Stores current action per chat_id
        self.current_action: Dict[int, str] = {}
        # Stores selected field per chat_id
        self.current_field: Dict[int, str] = {}

    def is_back(self, message: types.Message) -> bool:
        """
        Checks if the back button was pressed and triggers the respective callback.

        Args:
            message (types.Message): Incoming message from the user.

        Returns:
            bool: True if a back button was pressed; otherwise False.
        """
        text = message.text
        if text:
            if text == BUTTONS.get("back_to_main_menu"):
                self.back_main(message)
                return True
            elif text.startswith("/start"):
                self.start(message)
                return True
            elif text == BUTTONS.get("back_to_pervious_menu"):
                try:
                    self.back_previous(message)
                except:
                    self.back_main(message)
                return True
        return False

    def add_back_buttons(self, markup: ReplyKeyboardMarkup, justpervious=False) -> ReplyKeyboardMarkup:
        """
        Adds back-to-main and back-to-previous buttons to the given markup.

        Args:
            markup (ReplyKeyboardMarkup): The keyboard markup.

        Returns:
            ReplyKeyboardMarkup: Updated markup with back buttons.
        """
        if not justpervious:
            markup.add(
                KeyboardButton(BUTTONS.get("back_to_main_menu")),
                KeyboardButton(BUTTONS.get("back_to_pervious_menu")),
            )
        else:
            markup.add(
                # KeyboardButton(BUTTONS.get("back_to_main_menu")),
                KeyboardButton(BUTTONS.get("back_to_pervious_menu")),
            )

        return markup

    def _register_next(self, message: types.Message, handler: Callable[[types.Message], None], args: list = []) -> None:
        """
        Helper function to register the next step handler.

        Args:
            message (types.Message): The incoming message.
            handler (Callable): The next handler function.
        """
        self.bot.register_next_step_handler(message, handler, *args)

    def show_profile_menu(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.back_previous != self.show_profile_menu:
            if self.is_back(message):
                return
        self.back_previous = self.back_main

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(BUTTONS.get(
                "profile_view", "👤 مشاهده پروفایل")),
            types.KeyboardButton(BUTTONS.get(
                "identity_verification_verification", "🪪 احراز هویت")),
            types.KeyboardButton(BUTTONS.get("edit", "✏️ ویرایش پروفایل")),
            # types.KeyboardButton(BUTTONS.get(
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
        )
        markup = self.add_back_buttons(markup, True)
        self.bot.send_message(chat_id, MESSAGES.get(
            "profile_menu", "👤 منوی پروفایل:"), reply_markup=markup)
        self._register_next(message, self.handle_profile_menu_selection)

    def handle_profile_menu_selection(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text
        if self.is_back(message):
            return
        self.back_previous = self.show_profile_menu

        # Internal implementation note: legacy behavior is preserved during modernization.
        options = {
            BUTTONS.get("profile_view", "👤 مشاهده پروفایل"): self.show_profile,
            BUTTONS.get("edit", "✏️ ویرایش پروفایل"): self.edit_profile_menu,
            # Internal implementation note: legacy behavior is preserved during modernization.
            BUTTONS.get("identity_verification_verification", "🪪 احراز هویت"): self.identity_verification_verification,
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
        }

        action = options.get(text)
        if action:
            action(message)
        else:
            self.bot.send_message(chat_id, MESSAGES.get(
                "invalid_option", "❌ گزینه نامعتبر است. لطفاً یکی از گزینه‌های منو را انتخاب کنید."))
            self.show_profile_menu(message)

    def show_invites(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_code = self.get_user_code(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        invite_link = f"https://t.me/{self.bot.username}?start=invite_{user_code}"

        # Internal implementation note: legacy behavior is preserved during modernization.
        invited_users = self.db.get_invited_users(user_code)
        invited_text = "\n".join(
            [f"👤 {user['name']} - {user['date']}" for user in invited_users]) or "📭 هنوز کسی دعوت نشده است."

        text = f"🔗 لینک دعوت شما:\n{invite_link}\n\n📨 دعوت‌شده‌ها:\n{invited_text}"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(BUTTONS.get(
            "back_to_main", "🔙 بازگشت به منوی اصلی")))

        self.bot.send_message(chat_id, text, reply_markup=markup)

    def show_discounts(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        discounts = self.db.get_user_discounts(message.chat.id)

        if not discounts:
            text = "🎁 تخفیف فعالی برای شما ثبت نشده است."
        else:
            text = "🎁 لیست تخفیف‌های شما:\n\n" + "\n".join([
                f"- {item['title']}: {item['amount']}٪ تا {item['expires']}" for item in discounts
            ])

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(BUTTONS.get(
            "back_to_main", "🔙 بازگشت به منوی اصلی")))

        self.bot.send_message(chat_id, text, reply_markup=markup)

    def show_accounting_menu(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("👛 نمایش موجودی"),
            types.KeyboardButton("💳 تراکنش‌ها"),
            types.KeyboardButton("➕ شارژ کیف پول"),
            types.KeyboardButton("📤 ارسال فیش واریز"),
            types.KeyboardButton("💸 درخواست تسویه"),
            types.KeyboardButton(BUTTONS.get(
                "back_to_main", "🔙 بازگشت به منوی اصلی"))
        )
        self.bot.send_message(
            chat_id, "💰 لطفاً یک گزینه حسابداری را انتخاب کنید:", reply_markup=markup)
        self._register_next(message, self.handle_accounting_selection)

    def show_profile_history(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("📋 کدهای دائم"),
            types.KeyboardButton("🕓 کدهای ویژه"),
            types.KeyboardButton(BUTTONS.get(
                "back_to_main", "🔙 بازگشت به منوی اصلی"))
        )
        self.bot.send_message(
            chat_id, "📜 لطفاً نوع تاریخچه را انتخاب کنید:", reply_markup=markup)
        self._register_next(message, self.handle_history_selection)

    def convert_to_shamsi(self, date_str: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        from datetime import datetime
        from persiantools.jdatetime import JalaliDateTime

        if not date_str:
            return "نامشخص"

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            date_str = date_str.replace("⏰", "").strip()

            # Internal implementation note: legacy behavior is preserved during modernization.
            if '.' in date_str:
                date_str = date_str.split('.')[0]

            # Internal implementation note: legacy behavior is preserved during modernization.
            normalized = date_str.replace("/", "-")

            # Internal implementation note: legacy behavior is preserved during modernization.
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(normalized, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_str  # Internal implementation note: legacy behavior is preserved during modernization.

            jdt = JalaliDateTime(dt)

            formatted = f"\n  📅 {jdt.strftime('%Y/%m/%d')} تاریخ\n  " \
                f"🗓 {jdt.strftime('%A')} {jdt.day} {jdt.strftime('%B')}\n  " \
                f"⏰ ساعت : {jdt.strftime('%H:%M')}"

            # Internal implementation note: legacy behavior is preserved during modernization.
            days = {
                'Shanbeh': 'شنبه', 'Yekshanbeh': 'یک‌شنبه', 'Doshanbeh': 'دوشنبه',
                'Seshanbeh': 'سه‌شنبه', 'Chaharshanbeh': 'چهارشنبه',
                'Panjshanbeh': 'پنج‌شنبه', 'Jomeh': 'جمعه'
            }
            months = {
                'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
                'Tir': 'تیر', 'Mordad': 'عضواد', 'Shahrivar': 'شهریور',
                'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
                'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند'
            }

            for en, fa in days.items():
                formatted = formatted.replace(en, fa)
            for en, fa in months.items():
                formatted = formatted.replace(en, fa)

            return formatted

        except Exception:
            return date_str

    def show_profile(self, message: types.Message) -> None:
        """
        Retrieves user profile data from the database and displays it with translated labels.

        Args:
            message (types.Message): The incoming message.
        """
        chat_id = message.chat.id
        user_data = self.db.get_user_data(chat_id)
        if not user_data:
            self.bot.send_message(chat_id, MESSAGES.get(
                "user_not_found", "User not found."))
            self.show_profile_menu(message)
            return

        # Display profile photo if available
            # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            "premium_clients", "telegram_id = ?", (message.from_user.id,)
        )
        if not rows:
            self.bot.send_message(chat_id, MESSAGES.get(
                "user_not_found", "❌ پروفایل پیدا نشد."))
            return self.show_profile_menu(message)

        data = rows[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
        if data.get("avatar_url"):
            try:
                self.bot.send_photo(chat_id, data["avatar_url"])
            except Exception:
                pass  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        U_code = data.get("U_code", "-")
        name = data.get("name", "-")
        phone = data.get("phone", "-")
        city = data.get("city", "-")
        # username   = data.get("username", "-")

        # email = data.get("email", "-")

        join_date = self.convert_to_shamsi(data.get("created_at", "-"))

        # Internal implementation note: legacy behavior is preserved during modernization.
        profile_text = (
            f"<b>🆔 کد کاربری:</b> {U_code}\n"
            f"<b>👤 نام:</b> {name}\n"
            f"<b>📱 تلفن:</b> {phone}\n"
            f"<b>✉️ شهر:</b> {city}\n"
            f"<b>📅 تاریخ عضویت:</b> {join_date}\n"
            # f"{optional_rows}"
        ).strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, profile_text, parse_mode="HTML")

        self.show_profile_menu(message)
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.

    def edit_profile_menu(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("✏️ ویرایش نام"),
            types.KeyboardButton("✏️ ویرایش شهر"),
        )
        markup = self.add_back_buttons(markup)        # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            "🔧 فیلدی که می‌خواهید تغییر دهید را انتخاب کنید:",
            reply_markup=markup,
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(
            message, self.handle_edit_field_choice)

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def handle_edit_field_choice(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):       # Internal implementation note: legacy behavior is preserved during modernization.
            return

        text = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "✏️ ویرایش نام":
            self.current_step[chat_id] = "edit_name"
            self.bot.send_message(chat_id, "📝 نام جدید را وارد کنید:")
            self.bot.register_next_step_handler(
                message, self.handle_name_input)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "✏️ ویرایش شهر":
            self.current_step[chat_id] = "edit_city_province"
            return self.show_provinces_for_city(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, "❌ گزینه نامعتبر است.")
        self.edit_profile_menu(message)

    def handle_name_input(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        name = message.text.strip()
        if len(name) < 3 or not name.replace(' ', '').isalpha():
            self.bot.send_message(
                chat_id, "❌ نام باید حداقل ۳ حرف باشد و فقط شامل حروف فارسی یا انگلیسی. دوباره وارد کنید:"
            )
            return self.bot.register_next_step_handler(message, self.handle_name_input)

        self.db.update("premium_clients", {
                       "name": name}, "telegram_id = ?", (message.from_user.id,))
        self.bot.send_message(
            chat_id, f"✅ نام با موفقیت به '{name}' بروزرسانی شد.")
        self.show_profile_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def show_provinces_for_city(self, message):
        chat_id = message.chat.id
        provinces = self.location_handler.get_all_provinces()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for p in provinces:
            buttons.append(types.KeyboardButton(p))
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, "استان خود را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_province_for_city)

    def handle_province_for_city(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        province = message.text.strip()
        provinces = self.location_handler.get_all_provinces()
        if province not in provinces:
            self.bot.send_message(
                chat_id, "❌ استان نامعتبر است. دوباره انتخاب کنید:")
            return self.show_provinces_for_city(message)
        self.temp_data[chat_id] = {"province": province}
        return self.show_cities_for_city(message, province)

    def show_cities_for_city(self, message, province):
        chat_id = message.chat.id
        cities = self.location_handler.get_all_cities(
            as_dict=True).get(province, [])
        if not cities:
            self.bot.send_message(chat_id, "❌ شهرهای این استان موجود نیست.")
            return self.show_provinces_for_city(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for c in cities:
            buttons.append(types.KeyboardButton(c))
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id, "شهر خود را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_city_choice)

    def handle_city_choice(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return
    
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            city = message.text.strip()
            province = self.temp_data.get(chat_id, {}).get("province")
            cities = self.location_handler.get_all_cities(as_dict=True).get(province, [])
    
            if city not in cities:
                self.bot.send_message(chat_id, "❌ شهر نامعتبر است. دوباره انتخاب کنید:")
                return self.show_cities_for_city(message, province)
    
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.db.update(
                    "premium_clients",
                    {"city": city},
                    "telegram_id = ?",
                    (message.from_user.id,)
                )
                logger.info(f"City updated for user {message.from_user.id}: {city}")
            except Exception as db_err:
                logger.error(f"DB error while upsocial_service city for user {message.from_user.id}: {db_err}")
                self.bot.send_message(chat_id, "❗️ خطا در ذخیره‌سازی اطلاعات. لطفاً بعداً دوباره تلاش کنید.")
                return self.show_profile_menu(message)
    
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.temp_data.pop(chat_id, None)
            self.bot.send_message(chat_id, f"✅ شهر با موفقیت به «{city}» بروزرسانی شد.")
            self.show_profile_menu(message)
    
        except Exception as err:
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.exception(f"Unhandled error in handle_city_choice: {err}")
            self.bot.send_message(chat_id, "❌ خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید.")
            self.show_profile_menu(message)
    

    def complete_profile(self, message: types.Message) -> None:
        """
        Initiates the process to complete missing profile fields.

        Args:
            message (types.Message): The incoming message.
        """
        chat_id = message.chat.id
        user_data = self.db.get_user_data(chat_id)
        # Identify fields that are missing
        missing_fields = [f for f in editable_fields if not user_data.get(f)]
        if not missing_fields:
            self.bot.send_message(chat_id, MESSAGES.get(
                "profile_complete", "Your profile is complete."))
            self.show_profile_menu(message)
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for field in missing_fields:
            markup.add(KeyboardButton(field_labels.get(field, field)))
        markup.add(KeyboardButton(BUTTONS.get("back")))
        self.bot.send_message(chat_id, MESSAGES.get(
            "select_complete_field", "Select a field to complete:"), reply_markup=markup)
        self.current_action[chat_id] = "complete"
        self._register_next(message, self.handle_field_selection)

    def handle_field_selection(self, message: types.Message) -> None:
        """
        Processes the user's field selection for editing or completing.

        Args:
            message (types.Message): The incoming message.
        """
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS.get("back"):
            self.show_profile_menu(message)
            return

        # Determine field by matching the translated label from config
        selected_field = next((f for f, label in field_labels.items()
                               if label == text and f in editable_fields), None)
        if not selected_field:
            self.bot.send_message(chat_id, MESSAGES.get(
                "invalid_option", "Invalid option."))
            self.show_profile_menu(message)
            return

        self.current_field[chat_id] = selected_field
        current_field_type = field_types[selected_field]

        # Dispatch to appropriate handler based on field type
        if current_field_type == "text":
            self.bot.send_message(chat_id, MESSAGES.get(
                "enter_text", f"Enter new value for {text}:"))
            self._register_next(message, self.handle_text_input)
        elif current_field_type == "number":
            self.bot.send_message(chat_id, MESSAGES.get(
                "enter_number", f"Enter new number for {text}:"))
            self._register_next(message, self.handle_number_input)
        elif current_field_type == "choice":
            options = choice_options.get(selected_field, [])
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            for option in options:
                markup.add(KeyboardButton(option))
            markup.add(KeyboardButton(BUTTONS.get("back")))
            self.bot.send_message(chat_id, MESSAGES.get(
                "select_choice", f"Select new value for {text}:"), reply_markup=markup)
            self._register_next(message, self.handle_choice_input)
        elif current_field_type == "photo":
            self.bot.send_message(chat_id, MESSAGES.get(
                "send_photo", f"Send a new photo for {text}:"))
            self._register_next(message, self.handle_photo_input)

    def handle_text_input(self, message: types.Message) -> None:
        """Handles text input for a profile field."""
        chat_id = message.chat.id
        if message.text == BUTTONS.get("back"):
            self.show_profile_menu(message)
            return
        field = self.current_field.get(chat_id)
        if field is None:
            self.show_profile_menu(message)
            return
        value = message.text.strip()
        self._process_field_update(chat_id, field, value)
        self.show_profile_menu(message)

    def handle_number_input(self, message: types.Message) -> None:
        """Handles numeric input for a profile field."""
        chat_id = message.chat.id
        if message.text == BUTTONS.get("back"):
            self.show_profile_menu(message)
            return
        if not message.text.strip().isdigit():
            self.bot.send_message(chat_id, MESSAGES.get(
                "invalid_number", "Please enter a valid number."))
            self._register_next(message, self.handle_number_input)
            return
        field = self.current_field.get(chat_id)
        if field is None:
            self.show_profile_menu(message)
            return
        value = int(message.text.strip())
        self._process_field_update(chat_id, field, value)
        self.show_profile_menu(message)

    def handle_choice_input(self, message: types.Message) -> None:
        """Handles choice selection for a profile field."""
        chat_id = message.chat.id
        if message.text == BUTTONS.get("back"):
            self.show_profile_menu(message)
            return
        field = self.current_field.get(chat_id)
        if field is None:
            self.show_profile_menu(message)
            return
        if message.text.strip() not in choice_options.get(field, []):
            self.bot.send_message(chat_id, MESSAGES.get(
                "invalid_choice", "Invalid choice."))
            self._register_next(message, self.handle_choice_input)
            return
        self._process_field_update(chat_id, field, message.text.strip())
        self.show_profile_menu(message)

    def handle_photo_input(self, message: types.Message) -> None:
        """Handles photo input for a profile field."""
        chat_id = message.chat.id
        if not message.photo:
            self.bot.send_message(chat_id, MESSAGES.get(
                "invalid_photo", "Please send a valid photo."))
            self._register_next(message, self.handle_photo_input)
            return
        field = self.current_field.get(chat_id)
        if field is None:
            self.show_profile_menu(message)
            return
        file_id = message.photo[-1].file_id
        self._process_field_update(chat_id, field, file_id)
        self.show_profile_menu(message)

    def _process_field_update(self, chat_id: int, field: str, value: Any) -> None:
        """
        Updates the field based on the current action.
        If editing, updates the database immediately.
        If completing, inserts a request for admin approval.

        Args:
            chat_id (int): Telegram chat id.
            field (str): The field to update.
            value (Any): The new value for the field.
        """
        action = self.current_action.get(chat_id)
        if action == "edit":
            self.db.update_user_field(chat_id, field, value)
            self.bot.send_message(chat_id, MESSAGES.get(
                "update_success", f"{field_labels.get(field, field)} updated successfully"))
        elif action == "complete":
            # Save the update as a request with approved flag set to False
            data = {field: {"value": value, "approved": False}}
            self.db.insert_complete_profile_request(chat_id, data)
            self.bot.send_message(chat_id, MESSAGES.get(
                "request_submitted", f"Request for {field_labels.get(field, field)} submitted. Waiting for admin approval."))
        # Reset the current field action for this chat
        self.current_field[chat_id] = None

    def identity_verification_verification(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return
        if self.db.table_exists("identity_verification_requests"):
            res = self.db.select_dict(
                "identity_verification_requests", "telegram_id = ?", (user_id,))
            if res:
                user_data = res[0]
            else:
                user_data = {}
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            user_data = {}
        identity_verification_status_map = json.loads(user_data.get("identity_verification_docs", "{}") or "{}")
        rejection_map = json.loads(user_data.get(
            "rejection_reason", "{}") or "{}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        row_status = user_data.get("status")
        if row_status == "approved":
            approved_count = sum(
                1 for f in identity_verification_fields if identity_verification_status_map.get(f) is True
            )
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            approved_count = sum(
                1 for f in identity_verification_fields if user_data.get(f)
            )

        total = len(identity_verification_fields)
        percent = int((approved_count / total) * 100) if total else 0

        progress_text = f"📊 احراز هویت: {approved_count}/{total} تکمیل شده (٪{percent})"
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for field in identity_verification_fields:
            label = identity_verification_field_labels.get(field, field)
            status = identity_verification_status_map.get(field, None)
            if status is True:
                icon = "✅"
            elif status is False and row_status == "approved" and user_data.get(field):
                self.db.update("identity_verification_requests", {
                               field, None}, "telegram_id = ?", (user_id,))
                icon = "❌"
            elif not row_status == "approved" and status is False and field:
                icon = "⏳"
            elif not field:
                icon = "⚠️"
            else:
                icon = "⚠️"
            buttons.append(types.KeyboardButton(f"{label}({icon})"))
        markup.add(*buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, progress_text, reply_markup=markup)
        self.current_action[chat_id] = "identity_verification"
        self._register_next(message, self.handle_identity_verification_selection)

    def handle_identity_verification_selection(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text.endswith(')') and '(' in text:
            text = text[:text.rfind('(')].strip()
        label = text

        # Internal implementation note: legacy behavior is preserved during modernization.
        selected_field = next(
            (f for f, lbl in identity_verification_field_labels.items() if lbl == label), None)
        if not selected_field:
            self.bot.send_message(chat_id, MESSAGES["invalid_option"])
            return self.identity_verification_verification(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        user_data = self.db.select_dict(
            "identity_verification_requests", "telegram_id = ?", (user_id,))
        user_data = user_data[0] if user_data else {}
        identity_verification_status_map = json.loads(user_data.get("identity_verification_docs", "{}") or "{}")
        rejection_map = json.loads(user_data.get(
            "rejection_reason", "{}") or "{}")

        status = identity_verification_status_map.get(selected_field)
        rejected = selected_field in rejection_map

        # Internal implementation note: legacy behavior is preserved during modernization.
        if status is True:
            self.bot.send_message(
                chat_id,
                f"✅ اطلاعات مربوط به «{label}» قبلاً تأیید شده است.\nنیازی به ارسال مجدد نیست.",
            )
            return self.identity_verification_verification(message)

        elif status is False and user_data.get("status") == "approved" and user_data.get(selected_field):
            reason = rejection_map[selected_field].get("reason", "نامشخص")
            self.bot.send_message(
                chat_id,
                f"❌ اطلاعات قبلی مربوط به «{label}» رد شده است.\n"
                f"🚫 دلیل رد: {reason}\n"
                "📥 لطفاً فایل جدید را طبق نمونه ارسال کنید."
            )

        elif status is False:
            self.bot.send_message(
                chat_id,
                f"⏳ اطلاعات مربوط به «{label}» در صف بررسی است.\n"
                "در صورت تمایل می‌توانید آن را ویرایش و مجدداً ارسال کنید."
            )

        else:
            self.bot.send_message(
                chat_id,
                f"⚠️ هنوز هیچ فایلی برای «{label}» ارسال نشده است.\n"
                "📥 لطفاً فایل مورد نظر را طبق نمونه ارسال نمایید."
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_field[chat_id] = selected_field
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup = self.add_back_buttons(markup)

        # Internal implementation note: legacy behavior is preserved during modernization.
        caption, file_id = identity_verification_example.get(
            selected_field,
            (f"📷 لطفاً مدیا مربوط به «{label}» را ارسال نمایید.", None)
        )
        if selected_field == "video_message":

            self.bot.send_photo(chat_id, file_id, caption, reply_markup=markup)
            self._register_next(message, self.handle_identity_verification_input)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        # examples = identity_verification_example

        if file_id:
            self.bot.send_photo(chat_id, photo=file_id,
                                caption=caption, reply_markup=markup)
        else:
            self.bot.send_message(chat_id, caption, reply_markup=markup)

        self._register_next(message, self.handle_identity_verification_input)

    def save_media_to_channel(self, message, media_type="photo") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            forwarded = self.bot.forward_message(
                STORAGE_CHANNEL,  # Internal implementation note: legacy behavior is preserved during modernization.
                message.chat.id,
                message.message_id
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            if media_type == "photo" and forwarded.photo:
                return forwarded.photo[-1].file_id
            elif media_type == "video_note" and hasattr(forwarded, 'video_note'):
                return forwarded.video_note.file_id
            elif media_type == "document" and forwarded.document:
                return forwarded.document.file_id
            elif media_type == "video" and forwarded.video:
                return forwarded.video.file_id
            else:
                raise Exception("❌ مدیا معتبر یافت نشد.")
        except Exception as e:
            print(f"❌ خطا در ذخیره مدیا: {e}")
            return ""

    def handle_identity_verification_input(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_id = message.from_user.id
        field = self.current_field.get(chat_id)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            self.current_field.pop(chat_id, None)
            return self.show_profile_menu(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not field:
            return self.show_profile_menu(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if field == "video_message":
            if not message.video_note and not message.video:
                self.bot.send_message(chat_id, MESSAGES["invalid_video"])
                return self.bot.register_next_step_handler(message, self.handle_identity_verification_input)
            media_type = "video_note" if message.video_note else "video"
        else:
            if not message.photo:
                self.bot.send_message(chat_id, MESSAGES["invalid_photo"])
                return self.bot.register_next_step_handler(message, self.handle_identity_verification_input)
            media_type = "photo"

        # Internal implementation note: legacy behavior is preserved during modernization.
        file_id = self.save_media_to_channel(message, media_type)
        self.bot.send_message(chat_id, MESSAGES.get(
            "file_received", "فایل دریافت شد."))

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict("identity_verification_requests", "telegram_id = ?",
                                   (user_id,)) if self.db.table_exists("identity_verification_requests") else []
        user_data = rows[0] if rows else {}

        # Internal implementation note: legacy behavior is preserved during modernization.
        premium = self.db.select_dict(
            "premium_clients", "telegram_id = ?", (user_id,))
        U_code = premium[0]["U_code"] if premium else None

        # Internal implementation note: legacy behavior is preserved during modernization.
        identity_verification_docs = json.loads(user_data.get("identity_verification_docs") or "{}")
        identity_verification_docs[field] = False  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        data = {
            "U_code": U_code,
            "telegram_id": user_id,
            field: file_id,
            "identity_verification_docs": json.dumps(identity_verification_docs),
            "status": "pending",
        }
        data_type = {  # Internal implementation note: legacy behavior is preserved during modernization.
            "U_code": "TEXT UNIQUE",
            "telegram_id": "TEXT",
        }

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            if user_data:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.upsert("identity_verification_requests", data,
                               key="U_code", column_types=data_type)
            else:
                self.db.insert("identity_verification_requests", data, data_type)
        except Exception as err:
            self.bot.send_message(
                chat_id, "❗️ خطا در ذخیره‌سازی اطلاعات. لطفاً دوباره تلاش کنید.")
            print(f"[IDENTITY_VERIFICATION] DB error for user {user_id}: {err}")
            return  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, MESSAGES["request_submitted"])
        self.identity_verification_verification(message)
