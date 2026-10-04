from telegram_bot_platform.compat.config.settings import *
from telebot import types
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telebot import types
import json
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="identity_verification.log")


class IdentityVerificationHandler:
    def __init__(self, bot, data, parent, db: DatabaseManager = DatabaseManager(**DB_PARAMS)):
        self.bot = bot
        self.data = data
        self.parent = parent
        self.db = db
        self.PRIVATE_CHANNEL_ID = STORAGE_CHANNEL
        self.identity_verification_column_types = {  # Internal implementation note: legacy behavior is preserved during modernization.
            "U_code": "TEXT UNIQUE",
            "telegram_id": "TEXT",
            "id_card_front": "TEXT",
            "id_card_back": "TEXT",
            "verification_photo_with_id": "TEXT",
            "location": "TEXT",
            "manual_address": "TEXT",
            "address_video": "TEXT",
            "health_card": "TEXT",
            "identity_verification_docs": "JSON",
            "status": "TEXT"
        }
        self.db.create_table("identity_verification_data", columns=self.identity_verification_column_types)

    def start_identity_verification(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🪪 ارسال عکس مدرک شناسایی (رو)", "🪪 ارسال عکس مدرک شناسایی (پشت)")
        markup.add("🤳 ارسال تصویر تأیید هویت", "💊 ارسال مدرک مجوز/تأیید")
        markup.add("📍 ثبت جزئیات آدرس")
        markup.add("✅ تأیید", "🔙 بازگشت به پنل")

        progress = False
        progress1 = self.db.select_dict(
            "staff", "telegram_id = ?", (chat_id,))
        if progress1:
            progress = self.db.select_dict(
                "identity_verification_data", "U_code = ?", (progress1[0]["U_code"],))

        total_steps = 5  # Internal implementation note: legacy behavior is preserved during modernization.
        count = 0
        check_status = self.db.select_dict(
            "identity_verification_data", "U_code = ? AND status = 'approved'", (progress1[0]["U_code"],))
        if check_status:
            identity_verification_docs = json.loads(check_status[0]["identity_verification_docs"])
            for k, v in identity_verification_docs.items():
                if v:
                    count += 1
                else:
                    self.db.update(
                        "identity_verification_data", {k: None}, "U_code = ?", (progress1[0]["U_code"],))

        elif progress:
            start_idx = list(progress[0].keys()).index("id_card_front")
            end_idx = list(progress[0].keys()).index("health_card")
            total_steps = len(list(progress[0].values())[start_idx: end_idx])
            # Internal implementation note: legacy behavior is preserved during modernization.
            for level in list(progress[0].values())[start_idx: end_idx]:
                if level:
                    count += 1

        if count == 0:
            text = """به فرآیند احراز هویت خوش آمدید ✅

        در صورتی که مراحل احراز هویت را تکمیل کنید، در آگهی شما برچسب «صددرصد تأیید شده» 🟢 ثبت خواهد شد و امکان جذب مشتری برای شما بیشتر خواهد بود.

        لطفاً با انتخاب هر گزینه، مدرک خواسته‌شده را ارسال نمایید."""
        else:
            percent = int((count / total_steps) * 100)
            text = f"""📊 میزان پیشرفت احراز هویت: {percent}٪

        شما تاکنون {count} از {total_steps} مرحله را تکمیل کرده‌اید.

        برای ادامه، لطفاً یکی از گزینه‌های زیر را انتخاب کرده و مدرک مربوطه را ارسال نمایید."""

        self.bot.send_message(chat_id, text, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.identity_verification_main_menu_handler)

    def identity_verification_main_menu_handler(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "🔙 بازگشت به پنل":
            return self.parent.user_account_handler.show_account_menu(message)

        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return
        U_code = result[0]["U_code"]

        if text == "🪪 ارسال عکس مدرک شناسایی (رو)":
            if self._identity_verification_field_exists(U_code, "id_card_front"):
                self._already_uploaded_options(
                    chat_id, "id_card_front", "مدرک شناسایی (رو)")
            else:
                self._ask_for_photo(
                    chat_id, "🪪 لطفاً عکس مدرک شناسایی (رو) را ارسال کنید", self.receive_id_card_photo)

        elif text == "🪪 ارسال عکس مدرک شناسایی (پشت)":
            if self._identity_verification_field_exists(U_code, "id_card_back"):
                self._already_uploaded_options(
                    chat_id, "id_card_back", "مدرک شناسایی (پشت)")
            else:
                self._ask_for_photo(
                    chat_id, "🪪 لطفاً عکس مدرک شناسایی (پشت) را ارسال کنید", self.receive_id_card_back_photo)

        elif text == "🤳 ارسال تصویر تأیید هویت":
            if self._identity_verification_field_exists(U_code, "verification_photo_with_id"):
                self._already_uploaded_options(
                    chat_id, "verification_photo_with_id", "تصویر تأیید هویت")
            else:
                self._ask_for_photo(
                    chat_id, "🤳 لطفاً تصویر تأیید هویت را ارسال کنید", self.receive_verification_photo_with_id)
        elif text == "💊 ارسال مدرک مجوز/تأیید":
            if self._identity_verification_field_exists(U_code, "health_card"):
                self._already_uploaded_options(
                    chat_id, "health_card", "مدرک مجوز/تأیید")
            else:
                self._ask_for_photo(
                    chat_id, "💊 لطفاً عکس مدرک مجوز/تأیید خود را ارسال کنید", self.receive_health_card_photo)

        elif text == "📍 ثبت جزئیات آدرس":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("📍 ارسال لوکیشن", "📬 آدرس دستی", "🎥 ارسال ویدئوی تأیید")
            markup.add("✅ تأیید", "🔙 بازگشت")
            self.bot.send_message(
                chat_id,
                "در این بخش، باید تمام اطلاعات خواسته شده را برای ما ارسال کنید تا مورد تأیید قرار بگیرد.\n"
                "برای ارسال لوکیشن، باید در موقعیت باشید و ویدئوی کوتاه باید در محیط روشن و قابل مشاهده ضبط شود تا فرایند تأیید هویت به‌درستی انجام شود",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(
                message, self.identity_verification_address_menu_handler)

        elif text == "✅ تأیید":
            self.bot.send_message(
                chat_id, "✅ اطلاعات شما ثبت شد. لطفا منتظر تایید باشید.")
            self.parent.user_account_handler.show_account_menu(message)

        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.start_identity_verification(message)

    def _identity_verification_field_exists(self, U_code, field):

        rows = self.db.select_dict("identity_verification_data", "U_code = ?", (U_code,))
        return rows and rows[0].get(field)

    def _ask_for_photo(self, chat_id, text, handler):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت")
        self.bot.send_message(chat_id, text, reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(chat_id, handler)

    def _already_uploaded_options(self, chat_id, field_name, label):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✏️ ویرایش", "🔙 بازگشت")
        self.bot.send_message(
            chat_id,
            f"⚠️ عکس {label} قبلاً ثبت شده و در حال بررسی است.\nدر صورت نیاز می‌توانید آن را ویرایش کنید.",
            reply_markup=markup
        )
        # <- store which field is being edited
        self.data.setdefault(chat_id, {})["edit_mode"] = field_name
        self.bot.register_next_step_handler_by_chat_id(
            chat_id,
            lambda msg: self._edit_or_back(msg, field_name, label)
        )

    def _edit_or_back(self, message, field_name, label):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        elif message.text == "✏️ ویرایش":
            if field_name == "id_card_front":
                self._ask_for_photo(
                    chat_id, "🪪 لطفاً عکس جدید مدرک شناسایی (رو) را ارسال کنید", self.receive_id_card_photo)
            elif field_name == "id_card_back":
                self._ask_for_photo(
                    chat_id, "🪪 لطفاً عکس جدید مدرک شناسایی (پشت) را ارسال کنید", self.receive_id_card_back_photo)
            elif field_name == "verification_photo_with_id":
                self._ask_for_photo(
                    chat_id, "🤳 لطفاً سلفی جدید با کارت ملی را ارسال کنید", self.receive_verification_photo_with_id)
            elif field_name == "location":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton(
                    "📤 ارسال موقعیت مکانی", request_location=True), "🔙 بازگشت")
                self.bot.send_message(
                    chat_id, "📍 لطفاً موقعیت مکانی جدید خود را ارسال کنید:", reply_markup=markup)
                self.bot.register_next_step_handler_by_chat_id(
                    chat_id, self.receive_location)

            elif field_name == "manual_address":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("🔙 بازگشت")
                self.bot.send_message(
                    chat_id, "📬 لطفاً آدرس دقیق جدید خود را وارد کنید:", reply_markup=markup)
                self.bot.register_next_step_handler_by_chat_id(
                    chat_id, self.receive_manual_address)

            elif field_name == "address_video":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("🔙 بازگشت")
                self.bot.send_message(
                    chat_id, "🎥 لطفاً ویدئومسیج جدید خود را ارسال کنید:", reply_markup=markup)
                self.bot.register_next_step_handler_by_chat_id(
                    chat_id, self.receive_address_video)

        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً از دکمه‌های موجود استفاده کنید.")
            self._already_uploaded_options(chat_id, field_name, label)

    def _save_identity_verification_photo(self, chat_id, message, field, label):
        try:
            sent_msg = self.bot.send_photo(
                self.PRIVATE_CHANNEL_ID, message.photo[-1].file_id)
            file_id = sent_msg.photo[-1].file_id

            edit_mode = self.data.get(chat_id, {}).pop("edit_mode", None)
            result = self.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if not result:
                self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
                return
            U_code = result[0]["U_code"]

            if not edit_mode:
                existing = self.db.select_dict(
                    "identity_verification_data", "U_code = ?", (U_code,))
                if existing and existing[0].get(field) == file_id:
                    self.bot.send_message(
                        chat_id, "❌ این عکس قبلاً ثبت شده است.")
                    return self._ask_for_photo(chat_id, f"لطفاً عکس جدید {label} را ارسال کنید", getattr(self, f"receive_{field}"))

            # Load existing identity_verification_docs
            existing = self.db.select_dict("identity_verification_data", "U_code = ?", (U_code,))
            identity_verification_docs = {}
            if existing and existing[0].get("identity_verification_docs"):
                try:
                    identity_verification_docs = json.loads(existing[0]["identity_verification_docs"])
                except:
                    pass

            # Update this field's status
            identity_verification_docs[field] = False
            identity_verification_type = {
                "U_code": "TEXT UNIQUE"
            }
            data = {
                "U_code": U_code,
                "telegram_id": message.from_user.id,
                field: file_id,
                "status": "pending",
                "identity_verification_docs": json.dumps(identity_verification_docs)
            }
            self.db.upsert("identity_verification_data", data=data,
                           key="U_code", column_types=identity_verification_type)
            self.bot.send_message(chat_id, f"✅ عکس {label} با موفقیت ثبت شد.")
            self.start_identity_verification(message)

        except Exception as e:
            logger.error(f"❌ Error saving {field}: {e}")
            self.bot.send_message(chat_id, "❌ خطا در ذخیره‌سازی عکس.")

    def receive_id_card_photo(self, message):
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if not message.photo:
            self.bot.send_message(
                message.chat.id, "❌ لطفا فقط یک عکس ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.receive_id_card_photo)
        self._save_identity_verification_photo(message.chat.id, message,
                             "id_card_front", "مدرک شناسایی (رو)")

    def receive_id_card_back_photo(self, message):
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if not message.photo:
            self.bot.send_message(
                message.chat.id, "❌ لطفا فقط یک عکس ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.receive_id_card_back_photo)
        self._save_identity_verification_photo(message.chat.id, message,
                             "id_card_back", "مدرک شناسایی (پشت)")

    def receive_health_card_photo(self, message):
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if not message.photo:
            self.bot.send_message(
                message.chat.id, "❌ لطفا فقط یک عکس ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.receive_health_card_photo)
        self._save_identity_verification_photo(message.chat.id, message,
                             "health_card", "کارت سلامت")

    def receive_verification_photo_with_id(self, message):
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if not message.photo:
            self.bot.send_message(
                message.chat.id, "❌ لطفا فقط یک عکس ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.receive_verification_photo_with_id)
        self._save_identity_verification_photo(message.chat.id, message,
                             "verification_photo_with_id", "تصویر تأیید هویت")

    def identity_verification_address_menu_handler(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        elif message.text == "📍 ارسال لوکیشن":
            result = self.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if not result:
                self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
                return
            U_code = result[0]["U_code"]

            if self._identity_verification_field_exists(U_code, "location"):
                self._already_uploaded_options(
                    chat_id, "location", "موقعیت مکانی")
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton(
                    "📤 ارسال موقعیت مکانی", request_location=True), "🔙 بازگشت")
                self.bot.send_message(
                    chat_id, "📍 لطفاً لوکیشن خود را ارسال کنید:", reply_markup=markup)
                self.bot.register_next_step_handler(
                    message, self.receive_location)

        elif message.text == "📬 آدرس دستی":
            result = self.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if not result:
                self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
                return
            U_code = result[0]["U_code"]

            if self._identity_verification_field_exists(U_code, "manual_address"):
                self._already_uploaded_options(
                    chat_id, "manual_address", "📬 آدرس دستی")
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("🔙 بازگشت")
                self.bot.send_message(
                    chat_id, "📬 لطفاً آدرس دقیق خود را وارد کنید:", reply_markup=markup)
                self.bot.register_next_step_handler(
                    message, self.receive_manual_address)
        elif message.text == "🎥 ارسال ویدئوی تأیید":
            result = self.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if not result:
                self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
                return
            U_code = result[0]["U_code"]

            if self._identity_verification_field_exists(U_code, "address_video"):
                self._already_uploaded_options(
                    chat_id, "address_video", "🎥 ارسال ویدئوی تأیید")
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("🔙 بازگشت")
                self.bot.send_message(
                    chat_id, "🎥 لطفاً ویدئومسیج خود را ارسال کنید:", reply_markup=markup)
                self.bot.register_next_step_handler(
                    message, self.receive_address_video)
        elif message.text == "✅ تأیید":
            self.bot.send_message(chat_id, "✅ اطلاعات ثبت شد.")
            self.parent.login_handler.login_menu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.start_identity_verification(message)

    def receive_location(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if not message.location:
            self.bot.send_message(chat_id, "❌ لطفاً فقط لوکیشن ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.receive_location)

        edit_mode = self.data.get(chat_id, {}).pop("edit_mode", None)

        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return
        U_code = result[0]["U_code"]

        if not edit_mode and self._identity_verification_field_exists(U_code, "location"):
            self._already_uploaded_options(chat_id, "location", "موقعیت مکانی")
            return

        location_data = {
            "latitude": message.location.latitude,
            "longitude": message.location.longitude
        }
        self._save_field_to_identity_verification(message, "location", json.dumps(location_data))
        self.bot.send_message(chat_id, "✅ لوکیشن با موفقیت ذخیره شد.")
        self.start_identity_verification(message)

    def receive_manual_address(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if len(message.text.strip() if message.text else None) < 5:
            self.bot.send_message(chat_id, "❌ لطفاً آدرس دقیق‌تری وارد کنید.")
            return self.bot.register_next_step_handler(message, self.receive_manual_address)

        edit_mode = self.data.get(chat_id, {}).pop("edit_mode", None)

        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return
        U_code = result[0]["U_code"]

        if not edit_mode and self._identity_verification_field_exists(U_code, "manual_address"):
            self._already_uploaded_options(
                chat_id, "manual_address", "آدرس دستی")
            return

        self._save_field_to_identity_verification(
            message, "manual_address", message.text.strip() if message.text else None)
        self.bot.send_message(chat_id, "✅ آدرس با موفقیت ثبت شد.")
        self.start_identity_verification(message)

    def receive_address_video(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.start_identity_verification(message)
        if not message.video_note:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط یک ویدئومسیج ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.receive_address_video)

        edit_mode = self.data.get(chat_id, {}).pop("edit_mode", None)

        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return
        U_code = result[0]["U_code"]

        if not edit_mode and self._identity_verification_field_exists(U_code, "address_video"):
            self._already_uploaded_options(
                chat_id, "address_video", "ویدئومسیج آدرس")
            return

        self._save_field_to_identity_verification(message, "address_video",
                                message.video_note.file_id)
        self.bot.send_message(chat_id, "✅ ویدئو با موفقیت ذخیره شد.")
        self.start_identity_verification(message)

    def _save_field_to_identity_verification(self, message, field, value):
        chat_id = message.chat.id
        telegram_id = message.from_user.id
        result = self.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        if not result:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return
        U_code = result[0]["U_code"]

        # Load existing identity_verification_docs
        existing = self.db.select_dict("identity_verification_data", "U_code = ?", (U_code,))
        identity_verification_docs = {}
        if existing and existing[0].get("identity_verification_docs"):
            try:
                identity_verification_docs = json.loads(existing[0]["identity_verification_docs"])
            except:
                pass

        # Internal implementation note: legacy behavior is preserved during modernization.
        identity_verification_docs[field] = False

        data = {
            "U_code": U_code,
            "telegram_id": message.from_user.id,
            field: value,
            "status": "pending",
            "identity_verification_docs": json.dumps(identity_verification_docs)
        }
        self.db.upsert("identity_verification_data", data=data, key="U_code")
