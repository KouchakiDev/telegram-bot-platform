from telegram_bot_platform.compat.config.settings import *
import re
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from telebot import types
from telebot import types
import re
import json
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="registration.log")
# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.utils.locations import LocationHandler
# Internal implementation note: legacy behavior is preserved during modernization.
_P2E = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

class RegistrationHandler(StepHandlerMixin):
    def __init__(self, bot, db :DatabaseManager ,data, registration_steps, parent):
        self.bot               = bot
        self.db                = db
        self.data              = data
        self.registration_steps= registration_steps
        self.parent            = parent

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.location_handler  = LocationHandler()
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.province_cities   = self.location_handler.get_all_cities(as_dict=True)
    # Internal implementation note: legacy behavior is preserved during modernization.
    def is_back(self, message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        text = (message.text or "").strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text.startswith("/start"):
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.data.pop(message.chat.id, None)
            self.parent.send_welcome(message)
            return True

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "🔙 بازگشت":
            reg = self.data.get(message.chat.id, {}).get("registration")
            if reg and reg["step_index"] > 0:
                reg["step_index"] -= 1
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self.execute_next_step(message, "registration")
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.parent.send_welcome(message)
                return True

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "❌ بازگشت به منوی اصلی":
            self.data.pop(message.chat.id, None)
            self.parent.send_welcome(message)
            return True

        return False
     # Internal implementation note: legacy behavior is preserved during modernization.
    def add_back_buttons(self,
                         markup: types.ReplyKeyboardMarkup,
                         *,
                         only_panel: bool = False) -> types.ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        if only_panel:
            markup.add("❌ بازگشت به منوی اصلی")
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            labels = {btn for row in getattr(markup, "keyboard", []) for btn in row}
            if "🔙 بازگشت" not in labels:
                markup.add("🔙 بازگشت")
            if "❌ بازگشت به منوی اصلی" not in labels:
                markup.add("❌ بازگشت به منوی اصلی")
        return markup
    # :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
    def confirm_registration_intro(self, message):
        chat_id = message.chat.id

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("✅ متوجه شدم")
        markup.add("🔙 بازگشت")

        self.bot.send_message(
            chat_id,
            "📋 *به فرآیند ثبت‌نام خوش آمدید!*\n\n"
            "لطفاً تمام اطلاعات را با دقت وارد کنید، زیرا برای ویرایش آن باید از قسمت *پروفایل* درخواست ارسال کنید.\n\n"
            "\n"
            "اگر آماده هستید با زدن دکمه «متوجه شدم» وارد فرآیند ثبت نام میشوید",
            parse_mode="Markdown",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.process_registration_intro)

    def process_registration_intro(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return

        if text == "🔙 بازگشت":
            self.parent.send_welcome(message)
            return
        elif text == "✅ متوجه شدم":
            self.start_registration(message)
            return
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.confirm_registration_intro(message)

    def start_registration(self, message):
        chat_id = message.chat.id
        self.data.setdefault(chat_id, {})
        self.data[chat_id]["registration"] = {
            "step_index": 0,
            "workflow": sorted(
                [step["name"]
                    for step in self.registration_steps if step["active"]],
                key=lambda name: next(
                    step["position"] for step in self.registration_steps if step["name"] == name)
            )
        }
        if not self.data[chat_id]["registration"]["workflow"]:
            self.bot.send_message(
                chat_id, "❌ خطای تنظیمات: هیچ مرحله‌ای فعال نیست.")
            return
        self.execute_next_step(message, "registration")

    def get_name(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name(
            "registration", "get_name")  # <-- pass section name
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        self.bot.send_message(
            chat_id, "لطفا نام مستعار خود را وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_name_response)

    def process_name_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name(
            "registration", "get_name")  # <-- pass section name
        if self.is_back(message):
            return

        if not message.text:
            self.bot.send_message(chat_id, "❌ لطفاً فقط متن وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_name_response)
            return

        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            # <-- pass section name
            self.execute_next_step(message, "registration")
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_name_response)
        else:
            name = message.text.strip() if message.text else None
            if re.match(r"^(?:[a-zA-Z]{2,25}(?: [a-zA-Z]{2,25})?|[\u0600-\u06FF]{2,25}(?:[\s‌][\u0600-\u06FF]{2,25})?)$", name):
                self.data[chat_id]['name'] = name
                # logger.info("User Data: %s", self.data,  indent=4)
                # <-- pass section name
                self.execute_next_step(message, "registration")
            else:
                self.bot.send_message(
                    chat_id, "❌ نام فقط می‌تواند شامل حروف فارسی و انگلیسی باشد. لطفا مجددا وارد کنید")
                self.bot.register_next_step_handler(
                    message, self.process_name_response)

    def get_age(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_age")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        self.bot.send_message(
            chat_id, "  لطفا سطح تجربه خود را وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_age_response)

    def process_age_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_age")
        if self.is_back(message):
            return
        if not message.text:
            self.bot.send_message(chat_id, "❌ لطفاً فقط متن وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_age_response)
            return

        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message)
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_age_response)
        else:
            age = message.text.strip() if message.text else None
            if age.isdigit() and 10 <= int(age) <= 100:
                self.data[chat_id]['age'] = int(age)
                # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
                self.execute_next_step(message, "registration")
            else:
                self.bot.send_message(
                    chat_id, "❌ سطح تجربه باید یک عدد بین ۱۰ تا ۱۰۰ باشد. لطفا مجددا وارد کنید")
                self.bot.register_next_step_handler(
                    message, self.process_age_response)

    def get_phone_number(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_phone_number")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))
        phone_button = types.KeyboardButton(
            text="📞 ارسال شماره تلفن", request_contact=True)
        cancel_button = types.KeyboardButton(text="❌ بازگشت به منوی اصلی")
        markup.add(phone_button, cancel_button)
        self.bot.send_message(
            chat_id, "  لطفا شماره تلفن خود را ارسال کنید فقط با دکمه زیر", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_phone_number_response)

    def process_phone_number_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_phone_number")
        if self.is_back(message):
            return
        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "registration")
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_phone_number_response)
        elif message.contact:
            phone_number = message.contact.phone_number[-10:]
            self.data[chat_id]['phone_number'] = phone_number
            if self.db.table_exists("staff"):
                existing = self.db.select_dict(
                    "staff", "phone_number = ?", (phone_number,))
                status = existing[0]['status'] if existing else None
                if existing and status in ["canceled", "rejected"]:
                    self.execute_next_step(message, "registration")
                elif existing and status == "blocked":
                    self.blocked(message)
                elif existing and status in ["approved", "pending"]:
                    self.bot.send_message(chat_id, "⚠️ شما قبلا ثبت نام کردید")
                    self.parent.send_welcome(message)
                elif not existing:
                    # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
                    self.execute_next_step(message, "registration")
            else:
                self.execute_next_step(message, "registration")
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط با دکمه ارسال شماره تلفن، شماره خود را ارسال کنید.")
            self.bot.register_next_step_handler(
                message, self.process_phone_number_response)

    def get_height(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_height")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))
        self.bot.send_message(
            chat_id, "  لطفا ظرفیت خود را به سانتی‌متر وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_height_response)

    def process_height_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_height")
        if self.is_back(message):
            return
        if not message.text:
            self.bot.send_message(chat_id, "❌ لطفاً فقط متن وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_height_response)
            return
        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message)
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_height_response)
        else:
            height = message.text.strip() if message.text else None
            if height.isdigit() and 100 <= int(height) <= 250:
                self.data[chat_id]['height'] = int(height)
                # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
                self.execute_next_step(message, "registration")
            else:
                self.bot.send_message(
                    chat_id, "❌ ظرفیت باید یک عدد سه‌رقمی بین ۱۰۰ تا ۲۵۰ باشد. لطفا مجددا وارد کنید")
                self.bot.register_next_step_handler(
                    message, self.process_height_response)

    def get_weight(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_weight")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))
        self.bot.send_message(
            chat_id, " لطفا حجم خدمات خود را به واحد وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_weight_response)

    def process_weight_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_weight")
        if self.is_back(message):
            return
        if not message.text:
            self.bot.send_message(chat_id, "❌ لطفاً فقط متن وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_weight_response)
            return
        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "registration")
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_weight_response)
        else:
            weight = message.text.strip() if message.text else None
            if weight.isdigit() and 10 <= int(weight) <= 300:
                self.data[chat_id]['weight'] = int(weight)
                # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
                self.execute_next_step(message, "registration")
            else:
                self.bot.send_message(
                    chat_id, "❌ حجم خدمات باید یک عدد دو یا سه‌رقمی بین ۱۰ تا ۳۰۰ باشد. لطفا مجددا وارد کنید")
                self.bot.register_next_step_handler(
                    message, self.process_weight_response)
                

    ##++++++++++++++++====================== Province, City & Region ===============================================
    def go_to_previous_step(self, chat_id, workflow_name):
        """Legacy-compatible behavior preserved for this callable."""
        reg = self.data.get(chat_id, {}).get(workflow_name)
        if reg and reg["step_index"] > 0:
            reg["step_index"] -= 1
    

    def get_province(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_province")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True , row_width=3)
        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons = []
        for province in self.province_cities:
            buttons.append(province)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(*buttons)
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))
        self.bot.send_message(
            chat_id,
            "🏞 لطفاً استان خود را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self.process_province_response)

    def process_province_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_province")
        text = (message.text or "").strip()
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            return self.parent.send_welcome(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "رد شدن" and step["skippable"]:
            return self.execute_next_step(message, "registration")
        elif text == "رد شدن":
            self.bot.send_message(chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            return self.get_province(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text in self.province_cities:
            self.data[chat_id]["province"] = text
            return self.execute_next_step(message, "registration")
        else:
            self.bot.send_message(chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            return self.get_province(message)

    def get_city(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_city")
        province = self.data.get(chat_id, {}).get("province")
        if not province:
            self.bot.send_message(chat_id, "❌ لطفاً ابتدا استان را انتخاب کنید.")
            return self.get_province(message)

        cities = self.province_cities.get(province, [])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []

        for city in cities:
             buttons.append(city)
        markup.add(*buttons)
        markup.add(types.KeyboardButton("🔙 برگشت به انتخاب استان"))
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))

        self.bot.send_message(
            chat_id,
            f"🏙 لطفاً شهر خود را از استان «{province}» انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self.process_city_response)

    def process_city_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_city")
        text = (message.text or "").strip()
        province = self.data.get(chat_id, {}).get("province")
        cities = self.province_cities.get(province, [])
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "🔙 برگشت به انتخاب استان":
            self.go_to_previous_step(chat_id, "registration")
            self.data[chat_id].pop("province", None)
            self.data[chat_id].pop("city", None)
            self.data[chat_id].pop("_region_buffer", None)
            return self.get_province(message)



        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            return self.parent.send_welcome(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "رد شدن" and step["skippable"]:
            return self.execute_next_step(message, "registration")
        elif text == "رد شدن":
            self.bot.send_message(chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            return self.get_city(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text in cities:
            self.data[chat_id]["city"] = text
            return self.execute_next_step(message, "registration")
        else:
            self.bot.send_message(chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            return self.get_city(message)

    def get_region(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_region")
        dispatch_mode = self.data.get(chat_id, {}).get("dispatch_mode", "")
        is_dispatch = (dispatch_mode == "🚗 ارائه در محل مشتری")

        city = self.data.get(chat_id, {}).get("city")
        if not city:
            self.bot.send_message(chat_id, "❌ لطفاً ابتدا شهر را انتخاب کنید.")
            return self.get_city(message)

        regions = self.location_handler.get_regions_by_city(city)
        if not regions:
            self.bot.send_message(chat_id, "⛔️ هیچ منطقه‌ای در دیتابیس برای این شهر تعریف نشده.")
            return self.parent.send_welcome(message)

        buffer = self.data[chat_id].setdefault("_region_buffer", [])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []

        # Internal implementation note: legacy behavior is preserved during modernization.
        for r in regions:
            label = f"{r} ✅" if is_dispatch and r in buffer else r
            buttons.append(label)
        markup.add(*buttons)
        if is_dispatch:
            markup.add(types.KeyboardButton("✔️ تأیید"))
        markup.add(types.KeyboardButton("🔙 برگشت به انتخاب شهر"))
        markup.add(types.KeyboardButton("❌ بازگشت به منوی اصلی"))
        if step["skippable"]:
            markup.add(types.KeyboardButton("رد شدن"))

        prompt = (
            "🌍 مناطق ارائه در محل مشتری خود را تیک بزنید و سپس «✔️ تأیید» را بزنید:"
            if is_dispatch else
            f"🏠 لطفاً منطقه کاری ثابت خود در شهر «{city}» را انتخاب کنید:"
        )
        self.bot.send_message(chat_id, prompt, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.region_response)

    def region_response(self, message):
        chat_id = message.chat.id
        text = (message.text or "").strip()
        dispatch_mode = self.data.get(chat_id, {}).get("dispatch_mode", "")
        is_dispatch = (dispatch_mode == "🚗 ارائه در محل مشتری")
        buffer = self.data[chat_id].setdefault("_region_buffer", [])
        city = self.data.get(chat_id, {}).get("city")
        regions = self.location_handler.get_regions_by_city(city)
        step = self.get_step_by_name("registration", "get_region")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "🔙 برگشت به انتخاب شهر":
            self.go_to_previous_step(chat_id, "registration")
            self.data[chat_id].pop("city", None)
            self.data[chat_id].pop("_region_buffer", None)
            return self.get_city(message)



        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            return self.parent.send_welcome(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "رد شدن" and step["skippable"]:
            return self.execute_next_step(message, "registration")
        elif text == "رد شدن":
            self.bot.send_message(chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            return self.get_region(message)

        if is_dispatch:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "✔️ تأیید":
                if not buffer:
                    self.bot.send_message(chat_id, "❌ حداقل یک منطقه انتخاب کنید.")
                    return self.get_region(message)
                self.data[chat_id]["region"] = ",".join(buffer)
                self.data[chat_id].pop("_region_buffer", None)
                return self.execute_next_step(message, "registration")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.

            # Internal implementation note: legacy behavior is preserved during modernization.
            if text.endswith("✅"):
                # Internal implementation note: legacy behavior is preserved during modernization.
                option = text[:-1].strip()
            else:
                option = text.strip()

            if option in regions:
                if option in buffer:
                    buffer.remove(option)
                else:
                    buffer.append(option)
            return self.get_region(message)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text in regions:
                self.data[chat_id]["region"] = text
                return self.execute_next_step(message, "registration")
            self.bot.send_message(chat_id, "❌ لطفاً یکی از مناطق موجود را انتخاب کنید.")
            return self.get_region(message)

    ##++++++++++++++++====================== Province, City & Region ===============================================

    def get_gender(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_gender")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*PROFILE_CATEGORY)
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")
        self.bot.send_message(
            chat_id, "لطفا پروفایلت خود را وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.get_gender_response)

    def get_gender_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_gender")
        if not message.text:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط یکی از گزینه‌های موجود را انتخاب کنید.")
            self.bot.register_next_step_handler(message, self.get_gender_response)
            return

        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "registration")
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(message, self.get_gender_response)
        elif message.text in  PROFILE_CATEGORY:
            self.data[chat_id]['profile_category'] = message.text
            # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
            self.execute_next_step(message, "registration")
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط یکی از گزینه‌های موجود را انتخاب کنید.")
            self.bot.register_next_step_handler(message, self.get_gender_response)
    def get_photo_pair(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_photo_pair")
        self.data[chat_id]["_photo_list"] = []
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")
        self.bot.send_message(
            chat_id,
            "📸 لطفاً *دو عکس* (یکی پرتره و یکی تمام‌ظرفیت) ارسال کنید.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        self.bot.register_next_step_handler(message, self._photo_pair_response)

    def _photo_pair_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_photo_pair")

        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return

        if not message.photo:
            self.bot.send_message(chat_id, "❌ فقط عکس ارسال کنید.")
            self.bot.register_next_step_handler(message, self._photo_pair_response)
            return

        file_id = self.save_media_to_channel(message , "photo")
        
        self.data[chat_id]["_photo_list"].append(file_id)
        
        if len(self.data[chat_id]["_photo_list"]) < 2:
            self.bot.send_message(chat_id, "✅ عکس اول دریافت شد. لطفاً عکس دوم را ارسال کنید.")
            self.bot.register_next_step_handler(message, self._photo_pair_response)
            return
        # for photo in 
        self.data[chat_id]["profile_photos"] = self.data[chat_id]["_photo_list"]
        self.data[chat_id].pop("_photo_list")
        self.execute_next_step(message, "registration")
        
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
    
    def get_dispatch_mode(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_dispatch_mode")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🏠 محل ثابت دارم", "🚗 ارائه در محل مشتری")
        markup.add("❌ بازگشت به منوی اصلی")
        self.bot.send_message(
            chat_id, "🏠 لطفاً مشخص کنید: مکان دارید یا 🚗 ارائه در محل مشتری هستید؟", reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self.dispatch_mode_response)

    def dispatch_mode_response(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_dispatch_mode")
        text = message.text.strip()

        if text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return

        if text not in ["🏠 محل ثابت دارم", "🚗 ارائه در محل مشتری"]:
            self.bot.send_message(chat_id, "❌ لطفاً فقط یکی از گزینه‌های موجود را انتخاب کنید.")
            self.bot.register_next_step_handler(message, self.dispatch_mode_response)
            return

        self.data[chat_id]["dispatch_mode"] = text
        self.execute_next_step(message, "registration")

    def skin_color(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "skin_color")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("سفید", "گندمی", "سبزه", "برنزه",
                   "سیاه", "❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")
        self.bot.send_message(
            chat_id, "لطفا دسته‌بندی خدمات خود را وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.skin_colorresponse)

    def skin_colorresponse(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "skin_color")
        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "registration")
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.skin_colorresponse)
        elif message.text in ["سفید", "گندمی", "سبزه", "برنزه", "سیاه"]:
            self.data[chat_id]['skin_color'] = message.text
            # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
            self.execute_next_step(message, "registration")
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط یکی از گزینه‌های موجود را انتخاب کنید.")
            self.bot.register_next_step_handler(
                message, self.skin_colorresponse)

    def get_video_message(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "get_video_message")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")
        self.bot.send_message(
            chat_id, "لطفاً یک ویدئوی تأیید ارسال کنید (از گردن به پایین):", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.video_message_response)

    def video_message_response(self, message):
        chat_id = message.chat.id

        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return

        if not message.video_note:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط یک ویدئومسیج ارسال کنید.")
            self.bot.register_next_step_handler(
                message, self.video_message_response)
            return

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            sent_msg = self.bot.send_video_note(
                STORAGE_CHANNEL,  # channel ID
                message.video_note.file_id
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.data[chat_id]['video_message'] = sent_msg.video_note.file_id
            # Internal implementation note: legacy behavior is preserved during modernization.

        except Exception as e:
            logger.error(" khta dr arsal vydmsyj bh kanal: s", e)
            self.bot.send_message(
                chat_id, "❌ خطا در ذخیره‌سازی ویدئو. لطفاً بعداً تلاش کنید.")
            return

        # logger.info("dadhhay tnzymat kary: s", json.dumps(self.data, ensure_ascii=False, indent=4))
        self.execute_next_step(message, "registration")

    def ref_code(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "ref_code")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if step["skippable"]:
            markup.add("ندارم")
        markup.add("❌ بازگشت به منوی اصلی")
        self.bot.send_message(
            chat_id, "لطفا کد معرف خود را وارد کنید", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.ref_coderesponse)

    def ref_coderesponse(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("registration", "ref_code")
        if not message.text:
            self.bot.send_message(chat_id, "❌ لطفاً فقط متن وارد کنید.")
            self.bot.register_next_step_handler(message, self.ref_coderesponse)
            return

        if message.text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
            return
        elif message.text == "ندارم" and step["skippable"]:
            self.show_preview_and_confirm(message)
        elif message.text == "ندارم":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(message, self.ref_coderesponse)
        else:
            self.data[chat_id]['ref_code'] = message.text.strip(
            ) if message.text else None
            # logger.info("User Data: %s", self.data, ensure_ascii=False, indent=4)
            self.show_preview_and_confirm(message)

    def generate_U_code(self):
        default_start = 1421
        max_code = default_start - 1
        if self.db.table_exists("staff"):
            rows = self.db.select("staff", "", ())
            for row in rows:
                for value in row:
                    if isinstance(value, str) and value.startswith('p'):
                        try:
                            num = int(value[1:])
                            if num > max_code:
                                max_code = num
                        except ValueError:
                            continue
        return f"p{max_code + 1}"

    def generate_U_refC(self):
        default_start = 1421
        max_code = default_start - 1
        if self.db.table_exists("staff"):
            rows = self.db.select("staff", "", ())
            for row in rows:
                for value in row:
                    if isinstance(value, str) and value.startswith('R'):
                        try:
                            num = int(value[1:])
                            if num > max_code:
                                max_code = num
                        except ValueError:
                            continue
        return f"R{max_code + 1}"
     
    def normalize_phone_number(self, number: str, *, with_plus: bool = True) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if not number:
            raise ValueError("شماره خالی است")

        # Internal implementation note: legacy behavior is preserved during modernization.
        cleaned = (str(number)
                   .translate(_P2E)            # Internal implementation note: legacy behavior is preserved during modernization.
                   .replace(" ", "")
                   .replace("-", "")
                   .replace("(", "")
                   .replace(")", "")
                   .lstrip())                  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        if cleaned.startswith("00"):
            cleaned = cleaned[2:]
        if cleaned.startswith("98"):
            cleaned = cleaned[2:]
        if cleaned.startswith("0"):
            cleaned = cleaned[1:]

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not re.fullmatch(r"9\d{9}", cleaned):
            raise ValueError(f"{number!r} یک شمارهٔ موبایل معتبر نیست")

        normalized = f"98{cleaned}"
        return f"+{normalized}" if with_plus else normalized
           
    def show_preview_and_confirm(self, message):
        chat_id = message.chat.id
        user = self.data.get(chat_id, {})

        # Internal implementation note: legacy behavior is preserved during modernization.
        preview = "📝 *پیش‌نمایش اطلاعات ثبت‌نام:*\n\n"
        preview += f"🔸 *نام:* {user.get('name', 'نامشخص')}\n"
        preview += f"🔸 *سطح تجربه:* {user.get('age', 'نامشخص')}\n"
        preview += (
            f"🔸 *شماره تلفن:* "
            f"{self.normalize_phone_number(user.get('phone_number', 'نامشخص'))}\n"
        )
        preview += f"🔸 *ظرفیت/حجم خدمات:* {user.get('height', '؟')} / {user.get('weight', '؟')}\n"
        preview += (
            f"🔸 *استان/شهر:* "
            f"{user.get('province', '؟')} / {user.get('city', '؟')}\n"
        )
        preview += f"🔸 *کد معرف:* {user.get('ref_code', 'ندارد')}\n"
        preview += (
            f"🔸 *نوع مراجعه:* {user.get('dispatch_mode', '؟')}\n"
            f"🔸 *مناطق/منطقه کاری:* \n({" , ".join(user.get('region', '؟').split(","))})\n"
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        photos = user.get('profile_photos', '')
        count = len(photos) if photos else 0
        preview += (
            f"🔸 *عکس‌ها:* "
            f"{'✅ ' + str(count) + ' عدد ارسال شده' if count else '❌ ارسال نشده'}\n\n"
        )

        preview += "آیا این اطلاعات را تأیید می‌کنید؟"

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("✅ تایید نهایی", "❌ بازگشت به منوی اصلی")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            preview,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        self.bot.register_next_step_handler(message, self.handle_preview_response)

    def handle_preview_response(self, message):
        chat_id = message.chat.id
        text = message.text

        if text == "✅ تایید نهایی":
            self.complete_registration(message)
        elif text == "❌ بازگشت به منوی اصلی":
            self.data.pop(chat_id, None)
            self.parent.send_welcome(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.show_preview_and_confirm(message)

    def complete_registration(self, message):
        chat_id = message.chat.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        U_code = self.generate_U_code()
        U_refC = self.generate_U_refC()

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data[chat_id]['U_code'] = U_code
        self.data[chat_id]['U_refC'] = U_refC

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            "🎉 ثبت‌نام شما با موفقیت تکمیل شد و برای پشتیبانی جهت بررسی و تأیید ارسال شد.\n\n"
            "📩 در صورت تأیید، یک نوتیفیکیشن به همراه *کد ورود* برای شما ارسال خواهد شد.\n\n"
            "📢 همچنین توجه داشته باشید پس از تأیید مدیریت، یک پروفایل از شما در کانال منتشر می‌شود.",
            parse_mode="Markdown"
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        for key in ['step_index', 'workflow',"_region_buffer", 'process_type', 'registration']:
            self.data[chat_id].pop(key, None)
        self.data[chat_id]['status'] = "pending"
        self.data[chat_id]['telegram_id'] = message.from_user.id
        self.data[chat_id]['username'] = message.from_user.username or ""

        # Internal implementation note: legacy behavior is preserved during modernization.
        # if isinstance(self.data[chat_id].get("_region_buffer"), list):
        #     self.data[chat_id]["_region_buffer"] = json.dumps(self.data[chat_id]["_region_buffer"])
        if isinstance(self.data[chat_id]["profile_photos"], list):
            self.data[chat_id]["profile_photos"] = json.dumps(self.data[chat_id]["profile_photos"])

        self.db.ensure_table_and_columns("staff", self.data[chat_id])
        if self.db.table_exists("staff"):
            existing = self.db.select_dict(
                "staff", "telegram_id = ?", (self.data[chat_id]["telegram_id"],)
            )
            if existing:
                status = existing[0].get("status")
                if status in ["pending", "rejected"]:
                    self.db.update(
                        "staff", self.data[chat_id],
                        "telegram_id = ?", (self.data[chat_id]["telegram_id"],)
                    )
                elif status == "blocked":
                    return self.blocked(message)
            else:
                self.db.insert("staff", self.data[chat_id])
        else:
            self.db.insert("staff", self.data[chat_id])

        # Internal implementation note: legacy behavior is preserved during modernization.
        del self.data[chat_id]
        return self.parent.send_welcome(message)

    def blocked(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardRemove()
        self.bot.send_message(chat_id, "شما بلاک هستید!", reply_markup=markup)
