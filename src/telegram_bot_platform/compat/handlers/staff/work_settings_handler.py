from telegram_bot_platform.compat.config.settings import *
import re
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from telebot import types
import json
import re
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

logger = CustomLogger()  # log_file='work_settings.log', log_level=logging.DEBUG)


class WorkSettingsHandler(StepHandlerMixin):
    
    def __init__(self, bot, db, data, work_settings_steps, parent):
        
        self.bot = bot
        self.db = db
        self.data = data
        self.work_settings_steps = work_settings_steps
        self.parent = parent

    def cancel_markup(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به پنل")
        return markup

    def confirm_work_settings_intro(self, message):
        chat_id = message.chat.id

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📘 راهنما", "✅ متوجه شدم")
        markup.add("🔙 بازگشت")

        self.bot.send_message(
            chat_id,
            "📝 در این بخش، اطلاعات تکمیلی شما به صورت مرحله‌به‌مرحله ثبت خواهد شد.\n"
            "لطفاً با دقت به هر سؤال پاسخ دهید، زیرا برای ویرایش آن‌ها باید از بخش پروفایل درخواست ثبت کنید.\n\n"
            "در صورت نیاز می‌توانید راهنما را مطالعه کنید.\n\n"
            "آیا آماده‌اید؟",
            reply_markup=markup
        )

        self.bot.register_next_step_handler(
            message, self.process_work_settings_intro)

    def process_work_settings_intro(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "🔙 بازگشت":
            self.parent.user_account_handler.show_account_menu(message)
        elif text == "📘 راهنما":
            self.parent.login_handler.show_help_menu(message)
        elif text == "✅ متوجه شدم":
            self.start_work_settings(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.confirm_work_settings_intro(message)

    def start_work_settings(self, message):
        chat_id = message.chat.id
        telegram_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        REQUIRED_FIELD_TO_CHECK = "marital_status"

        # Step 1: Check if user already completed work settings
        result = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        if result:
            existing_data = result[0]
            if existing_data.get(REQUIRED_FIELD_TO_CHECK) not in [None, "", "null"]:
                self.bot.send_message(
                    chat_id,
                    "⚠️ شما قبلاً اطلاعات تکمیلی خود را وارد کردید.\nبرای ویرایش اطلاعات باید از بخش پروفایل درخواست ویرایش ارسال کنید."
                )
                self.bot.register_next_step_handler(
                    message, self.parent.login_handler.login_menu)
                return

        # Step 2: Proceed normally if not filled before
        self.data[chat_id] = {}
        self.data[chat_id]["work_settings"] = {
            "step_index": 0,
            "workflow": sorted(
                [step["name"]
                    for step in self.work_settings_steps if step["active"]],
                key=lambda name: next(
                    step["position"] for step in self.work_settings_steps if step["name"] == name)
            )
        }

        if not self.data[chat_id]["work_settings"]["workflow"]:
            self.bot.send_message(
                chat_id, "❌ خطای تنظیمات: هیچ مرحله‌ای فعال نیست.")
            return

        self.execute_next_step(message, "work_settings")

    def get_marital_status(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_marital_status")

        options = ["عمومی", "ویژه", "محدود", "غیرفعال"]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*options)
        markup.add("❌ بازگشت به منوی اصلی")

        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "لطفا وضعیت دسترسی خود را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_marital_status)

    def process_marital_status(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_marital_status")
        text = message.text.strip() if message.text else None

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_marital_status)
            return

        valid_options = ["عمومی", "ویژه", "محدود", "غیرفعال"]
        if text not in valid_options:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_marital_status)
            return
        self.data.setdefault(chat_id, {})["marital_status"] = text
        self.execute_next_step(message, "work_settings")

    def get_appearance(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_appearance")

        options = ["چاق", "لاغر", "ورزشکاری", "توپر", "معمولی"]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*options)
        markup.add("❌ بازگشت به منوی اصلی")

        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "لطفا سبک خدمت خود را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_appearance)

    def process_appearance(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_appearance")
        text = message.text.strip() if message.text else None

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_appearance)
            return

        valid_options = ["چاق", "لاغر", "ورزشکاری", "توپر", "معمولی"]
        if text not in valid_options:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_appearance)
            return

        self.data.setdefault(chat_id, {})["appearance"] = text
        self.execute_next_step(message, "work_settings")

    def get_eye_color(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_eye_color")

        options = ["سبز", "آبی", "قهوه ای", "خاکستری", "کهربایی"]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*options)
        markup.add("❌ بازگشت به منوی اصلی")

        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "لطفاً تخصص اصلی خود را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_eye_color)

    def process_eye_color(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_eye_color")
        text = message.text.strip() if message.text else None

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_eye_color)
            return

        valid_options = ["سبز", "آبی", "قهوه ای", "خاکستری", "کهربایی"]
        if text not in valid_options:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_eye_color)
            return

        self.data.setdefault(chat_id, {})["eye_color"] = text
        self.execute_next_step(message, "work_settings")

    def get_has_home(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_has_home")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("بله", "خیر")
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(chat_id, "آیا منزل دارید؟", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_has_home)

    def process_has_home(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_has_home")
        text = message.text.strip() if message.text else None

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(message, self.process_has_home)
            return

        if text not in ["بله", "خیر"]:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(message, self.process_has_home)
            return

        self.data.setdefault(chat_id, {})["has_home"] = (text == "بله")

        if text == "بله":
            self.bot.send_message(
                chat_id,
                "🏠 لطفاً آدرس منزل خود را وارد کنید:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            self.bot.register_next_step_handler(
                message, self.process_home_address)
        else:
            self.execute_next_step(message, "work_settings")

    def process_home_address(self, message):
        chat_id = message.chat.id
        address = message.text.strip() if message.text else None

        if address == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return

        if len(address) < 5:
            self.bot.send_message(
                chat_id, "❌ آدرس وارد شده خیلی کوتاه است. لطفاً دقیق‌تر وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_home_address)
            return

        self.data.setdefault(chat_id, {})["home_address"] = address
        self.execute_next_step(message, "work_settings")

    def get_visit_client_home(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name(
            "work_settings", "get_visit_client_home")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("بله", "خیر")
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "آیا مایل به مراجعه به منزل مشتری هستید؟", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_visit_client_home)

    def process_visit_client_home(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name(
            "work_settings", "get_visit_client_home")
        text = message.text.strip() if message.text else None

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_visit_client_home)
            return

        if text not in ["بله", "خیر"]:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_visit_client_home)
            return

        self.data.setdefault(chat_id, {})[
            "visit_client_home"] = (text == "بله")
        self.execute_next_step(message, "work_settings")

    def get_breast_size(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_breast_size")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "🔢 لطفاً پارامتر عددی را وارد کنید (فقط یک عدد دو رقمی):", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_breast_size)

    def process_breast_size(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_breast_size")
        text = message.text.strip() if message.text else None

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_breast_size)
            return

        if not text.isdigit() or not (10 <= int(text) <= 99):
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط یک عدد دو رقمی بین ۱۰ تا ۹۹ وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_breast_size)
            return

        self.data.setdefault(chat_id, {})["breast_size"] = int(text)
        self.execute_next_step(message, "work_settings")

    def get_hair_color(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_hair_color")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "🎨 لطفاً روش ارائهی خود را وارد کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_hair_color)

    def process_hair_color(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_hair_color")

        if message.text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_hair_color)
            return

        hair_color = message.text.strip() if message.text else None

        if not re.match(r'^[آ-ی\s]+$', hair_color):
            self.bot.send_message(
                chat_id, "❌ لطفاً روش ارائه را فقط با حروف فارسی وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_hair_color)
            return

        self.data.setdefault(chat_id, {})["hair_color"] = hair_color
        self.execute_next_step(message, "work_settings")

    def get_profile_photo(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_profile_photo")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id, "📷 لطفاً یک عکس برای پروفایل ارسال کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_profile_photo)

    def process_profile_photo(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_profile_photo")

        if message.text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif message.text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return
        elif message.text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_profile_photo)
            return

        if not message.photo:
            self.bot.send_message(chat_id, "❌ لطفاً فقط یک عکس ارسال کنید.")
            self.bot.register_next_step_handler(
                message, self.process_profile_photo)
            return

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            PRIVATE_CHANNEL_ID = STORAGE_CHANNEL
            sent_msg = self.bot.send_photo(
                PRIVATE_CHANNEL_ID, message.photo[-1].file_id)
            new_file_id = sent_msg.photo[-1].file_id

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.data.setdefault(chat_id, {})["profile_photo"] = new_file_id
            # logger.info(" aks prvfayl zkhyrh shd: s", new_file_id)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.execute_next_step(message, "work_settings")

        except Exception as e:
            logger.error(" khta dr arsal aks prsnly bh kanal: s", e)
            self.bot.send_message(
                chat_id, "❌ خطا در ذخیره‌سازی عکس. لطفاً بعداً تلاش کنید.")

    def get_photo_list(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_photo_list")

        self.data.setdefault(chat_id, {})["gallery_photos"] = []
        self.data[chat_id]["work_settings"]["photo_index"] = 1  # Start from 1

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")

        self.bot.send_message(
            chat_id,
            "📷 لطفاً ۳ عکس دیگر خود را ارسال کنید.\nهر عکس را جداگانه بفرستید. شروع کنیم! 📸\n\nالان لطفاً *اولین عکس* را ارسال کنید:",
            parse_mode="Markdown",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.process_gallery_photo)

    def process_gallery_photo(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_photo_list")
        photo_index = self.data[chat_id]["work_settings"].get("photo_index", 1)

        if message.text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return

        if not message.photo:
            self.bot.send_message(chat_id, f"❌ لطفاً فقط عکس ارسال کنید.")
            self.bot.register_next_step_handler(
                message, self.process_gallery_photo)
            return

        try:
            PRIVATE_CHANNEL_ID = STORAGE_CHANNEL
            sent_msg = self.bot.send_photo(
                PRIVATE_CHANNEL_ID, message.photo[-1].file_id)
            new_file_id = sent_msg.photo[-1].file_id

            self.data[chat_id]["gallery_photos"].append(new_file_id)

            if photo_index < 3:
                self.data[chat_id]["work_settings"]["photo_index"] += 1
                self.bot.send_message(
                    chat_id, f"✅ عکس {photo_index} ذخیره شد.\n\nحالا لطفاً عکس شماره {photo_index + 1} را ارسال کنید:")
                self.bot.register_next_step_handler(
                    message, self.process_gallery_photo)
            else:
                self.bot.send_message(
                    chat_id, "✅ تمام ۳ عکس با موفقیت ذخیره شدند.")
                self.execute_next_step(message, "work_settings")

        except Exception as e:
            logger.error(" khta dr zkhyrhsazy aks galry: s", e)
            self.bot.send_message(
                chat_id, "❌ مشکلی در ذخیره‌سازی عکس به‌وجود آمد. لطفاً دوباره تلاش کنید.")
            self.bot.register_next_step_handler(
                message, self.process_gallery_photo)

    def get_service_price(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_service_price")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ بازگشت به منوی اصلی")
        if step["skippable"]:
            markup.add("رد شدن")

        self.bot.send_message(
            chat_id,
            "💰 لطفاً قیمت خود را برای *هر بار سرویس* وارد کنید (بین ۱,۰۰۰,۰۰۰ تا ۱,۸۰۰,۰۰۰  تومان فقط عدد):",
            parse_mode="Markdown",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.process_service_price)

    def process_service_price(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("work_settings", "get_service_price")

        text = message.text.strip() if message.text else None.replace(",", "")

        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return

        if text == "رد شدن" and step["skippable"]:
            self.execute_next_step(message, "work_settings")
            return

        if text == "رد شدن":
            self.bot.send_message(
                chat_id, "❌ این مرحله اجباری است و نمی‌توانید آن را رد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_service_price)
            return

        if not text.isdigit() or not (1000000 <= int(text) <= 1800000):
            self.bot.send_message(
                chat_id, "❌ عدد وارد شده نامعتبر است. لطفاً عددی بین ۱,۰۰۰,۰۰۰ تا ۱,۸۰۰,۰۰۰ وارد کنید.")
            self.bot.register_next_step_handler(
                message, self.process_service_price)
            return

        self.data[chat_id]["service_price"] = int(text)
        self.execute_next_step(message, "work_settings")

    def complete_work_settings(self, message):
        """Legacy-compatible behavior preserved for this callable."""

        # Internal implementation note: legacy behavior is preserved during modernization.
        chat_id: int = message.chat.id
        telegram_id: int = message.from_user.id
        logger.info(f"[complete_work_settings] start tg_id={telegram_id}, chat_id={chat_id}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            result = self.parent.db.select_dict(
                "staff",                       # Internal implementation note: legacy behavior is preserved during modernization.
                "telegram_id = ?", (telegram_id,)  # Internal implementation note: legacy behavior is preserved during modernization.
            )
            logger.debug(f"[complete_work_settings] db-select -> {result}")
        except Exception as exc:
            logger.exception(f"[complete_work_settings] db-select error – {exc}")
            self.bot.send_message(chat_id, "❌ خطا در دریافت اطلاعات؛ لطفاً دوباره تلاش کنید.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not result:
            logger.warning(f"[complete_work_settings] no staff row for tg_id={telegram_id}")
            self.bot.send_message(chat_id, "❌ اطلاعات شما یافت نشد. لطفاً ثبت‌نام را دوباره انجام دهید.")
            self.parent.registration_handler.start_registration(message)
            return

        U_code: str = result[0].get("U_code")
        logger.info(f"[complete_work_settings] found U_code={U_code} for tg_id={telegram_id}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            work_data: dict = self.data.get(chat_id, {}).copy()
            logger.debug(f"[complete_work_settings] raw-memory -> {work_data}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            skip_keys = {"work_settings", "step_index", "workflow", "process_type", "status"}
            for key in list(work_data.keys()):
                if key in skip_keys:
                    logger.debug(f"[complete_work_settings] drop key={key}")
                    work_data.pop(key, None)

            # Internal implementation note: legacy behavior is preserved during modernization.
            for key, value in work_data.items():
                if isinstance(value, (dict, list)):
                    logger.debug(f"[complete_work_settings] json-dump key={key}")
                    work_data[key] = json.dumps(value, ensure_ascii=False)

            logger.debug(f"[complete_work_settings] sanitized-data -> {work_data}")
        except Exception as exc:
            logger.exception(f"[complete_work_settings] data-prep error – {exc}")
            self.bot.send_message(chat_id, "❌ خطا در پردازش اطلاعات؛ لطفاً دوباره تلاش کنید.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.parent.db.update("staff", work_data, "U_code = ?", (U_code,))
            logger.info(f"[complete_work_settings] db-update done for U_code={U_code}")
        except Exception as exc:
            logger.exception(f"[complete_work_settings] db-update error – {exc}")
            self.bot.send_message(chat_id, "❌ خطا در ذخیره‌سازی اطلاعات؛ لطفاً دوباره تلاش کنید.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.data.pop(chat_id, None)
            logger.debug(f"[complete_work_settings] memory cleared for chat_id={chat_id}")
        except Exception as exc:
            logger.exception(f"[complete_work_settings] mem-clear error – {exc}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, "✅ اطلاعات شما با موفقیت ثبت شد.")

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.parent.user_account_handler.show_account_menu(message)
        except Exception as exc:
            logger.exception(f"[complete_work_settings] open-menu error – {exc}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.parent.send_welcome(message)
