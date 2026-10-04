from telegram_bot_platform.compat.config.settings import *
from telebot import types
import re

from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="payments.log")


class PaymentsHandler:
    def __init__(self, bot, data, parent):
        self.bot = bot
        self.data = data
        self.parent = parent

    def handle_payments(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("ریالی", "رمزارز")
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "لطفا نوع واریز/پرداخت خود را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_payment_selection)

    def process_payment_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "ریالی":
            self.handle_rial_payments(message)
        elif text == "رمزارز":
            self.handle_crypto_payments(message)
        elif text == "اتصال به کیف پول":
            self.bot.send_message(chat_id, "این بخش هنوز فعال نیست.")
            self.handle_payments(message)
        elif text == "🔙 بازگشت به پنل":
            self.parent.user_account_handler.show_account_menu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_payment_selection)

    def handle_rial_payments(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("ثبت شماره کارت", "ویرایش کارت‌ها")
        markup.add("🔙 بازگشت به کیف پول/کارت")
        self.bot.send_message(
            chat_id, "لطفا یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_rial_payment_selection)

    def process_rial_payment_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "ثبت شماره کارت":
            telegram_id = message.from_user.id
            result = self.parent.db.select_dict(
                "staff", "telegram_id = ?", (telegram_id,))

            # Card number already exists
            if result and result[0].get("card_number"):
                self.bot.send_message(
                    chat_id, "❌ شما قبلاً شماره کارت ثبت کرده‌اید.\nبرای ویرایش از گزینه 'ویرایش کارت‌ها' استفاده کنید.")
                self.handle_rial_payments(message)
                return

            self.request_card_number(message)

        elif text == "ویرایش کارت‌ها":
            self.show_card_info(message)

        elif text == "🔙 بازگشت به کیف پول/کارت":
            self.handle_payments(message)

        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_rial_payment_selection)

    def show_card_info(self, message):
        chat_id = message.chat.id
        telegram_id = message.from_user.id
        result = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))

        if not result:
            self.bot.send_message(chat_id, "❌ اطلاعاتی برای شما یافت نشد.")
            self.handle_rial_payments(message)
            return

        card_number = result[0].get("card_number", "ثبت نشده")
        card_info = result[0].get("card_number_info", "ثبت نشده")

        msg = f"💳 *شماره کارت ثبت‌شده:*\n`{card_number}`\n\n🏦 *نام و بانک:*\n{card_info}"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✏️ ویرایش کارت", "🔙 بازگشت به کیف پول/کارت")
        self.bot.send_message(
            chat_id, msg, parse_mode="Markdown", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_card_edit_option)

    def handle_card_edit_option(self, message):
        text = message.text.strip() if message.text else None
        if text == "✏️ ویرایش کارت":
            self.request_card_number(message)
        elif text == "🔙 بازگشت به کیف پول/کارت":
            self.handle_rial_payments(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_card_edit_option)

    def request_card_number(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "💳 لطفا شماره کارت بانکی خود را وارد کنید (۱۶ رقم):", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.validate_card_number)

    def validate_card_number(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت به پنل":
            self.parent.login_handler.login_menu(message)
            return
        if text.isdigit() and len(text) == 16:
            self.data.setdefault(chat_id, {})["card_number"] = text
            self.request_name_and_bank(message)
        else:
            self.bot.send_message(
                chat_id, "❌ شماره کارت باید دقیقا ۱۶ رقم عددی باشد. لطفا مجددا وارد کنید:")
            self.bot.register_next_step_handler(
                message, self.validate_card_number)

    def request_name_and_bank(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id,
            "🏦 لطفا نام و نام خانوادگی و نام بانک را وارد کنید:\n\n📌 *مثال:* علی محمدی - بانک ملت",
            parse_mode="Markdown",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.validate_name_and_bank)

    def validate_name_and_bank(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت به پنل":
            self.parent.login_handler.login_menu(message)
            return

        if re.match(r'^[آ-ی\s]+ - [آ-ی\s]+$', text):
            self.data.setdefault(chat_id, {})["card_number_info"] = text

            # Store both card_number and card_number_info
            telegram_id = message.from_user.id
            result = self.parent.db.select_dict(
                "staff", "telegram_id = ?", (telegram_id,))
            if result:
                U_code = result[0].get("U_code")
                data_to_update = {
                    "card_number": self.data[chat_id].get("card_number"),
                    "card_number_info": self.data[chat_id].get("card_number_info"),
                }
                self.parent.db.ensure_table_and_columns(
                    "staff", data_to_update)
                self.parent.db.update(
                    "staff", data_to_update, "U_code = ?", (U_code,))

            self.bot.send_message(
                chat_id, "✅ اطلاعات شما ثبت شد. بازگشت به منوی واریز/پرداخت.")
            self.handle_rial_payments(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا اطلاعات را به درستی وارد کنید (مثال: علی محمدی - بانک ملت):")
            self.bot.register_next_step_handler(
                message, self.validate_name_and_bank)

    def handle_crypto_payments(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("ثبت کیف پول", "ویرایش کیف‌پول‌ها")
        markup.add("🔙 بازگشت به کیف پول/کارت")
        self.bot.send_message(
            chat_id, "💰 لطفا یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_crypto_payment_selection)

    def process_crypto_payment_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "ثبت کیف پول":
            # Check if wallet already exists
            result = self.parent.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if result and result[0].get("wallet"):
                self.bot.send_message(
                    chat_id, "⚠️ شما قبلاً کیف پول ثبت کرده‌اید. برای ویرایش از گزینه 'ویرایش کیف‌پول‌ها' استفاده کنید.")
                self.handle_crypto_payments(message)
            else:
                self.request_crypto_wallet(message)

        elif text == "ویرایش کیف‌پول‌ها":
            self.show_wallet_info(message)

        elif text == "🔙 بازگشت به کیف پول/کارت":
            self.handle_payments(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_crypto_payment_selection)

    def show_wallet_info(self, message):
        chat_id = message.chat.id
        telegram_id = message.from_user.id
        result = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        if not result:
            self.bot.send_message(chat_id, "❌ اطلاعاتی برای شما یافت نشد.")
            self.handle_crypto_payments(message)
            return

        wallet = result[0].get("wallet", "ثبت نشده")
        network = result[0].get("wallet_network", "ثبت نشده")

        msg = f"💰 *کیف پول ثبت‌شده:*\n`{wallet}`\n\n🌐 *شبکه:* {network}"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✏️ ویرایش کیف‌پول", "🔙 بازگشت به کیف پول/کارت")
        self.bot.send_message(
            chat_id, msg, parse_mode="Markdown", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_wallet_edit_option)

    def handle_wallet_edit_option(self, message):
        text = message.text.strip() if message.text else None
        if text == "✏️ ویرایش کیف‌پول":
            self.request_crypto_wallet(message)
        elif text == "🔙 بازگشت به کیف پول/کارت":
            self.handle_crypto_payments(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_wallet_edit_option)

    def request_crypto_wallet(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "💰 لطفا آدرس کیف پول رمزارزی خود را ارسال کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.validate_crypto_wallet)

    def validate_crypto_wallet(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت به پنل":
            self.parent.login_handler.login_menu(message)
            return
        if re.match(r'^(T|0x|bnb)[A-Za-z0-9]{20,50}$', text):
            self.data.setdefault(chat_id, {})["crypto_wallet"] = text
            self.request_crypto_network(message)
        else:
            self.bot.send_message(
                chat_id, "❌ آدرس کیف پول وارد شده معتبر نیست. لطفا مجددا ارسال کنید.")
            self.bot.register_next_step_handler(
                message, self.validate_crypto_wallet)

    def request_crypto_network(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("شبکه ترون TRC20", "شبکه اتریوم ERC20",
                   "شبکه بایننس چین BSC(BEP20)", "🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "🌐 لطفا شبکه انتقال را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.validate_crypto_network)

    def validate_crypto_network(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت به پنل":
            self.parent.login_handler.login_menu(message)
            return

        if text in ["شبکه ترون TRC20", "شبکه اتریوم ERC20", "شبکه بایننس چین BSC(BEP20)"]:
            self.data.setdefault(chat_id, {})["crypto_network"] = text

            # Internal implementation note: legacy behavior is preserved during modernization.
            telegram_id = message.from_user.id
            result = self.parent.db.select_dict(
                "staff", "telegram_id = ?", (telegram_id,))
            if result:
                U_code = result[0].get("U_code")
                data_to_update = {
                    "wallet": self.data[chat_id].get("crypto_wallet"),
                    "wallet_network": self.data[chat_id].get("crypto_network"),
                }
                self.parent.db.ensure_table_and_columns(
                    "staff", data_to_update)
                self.parent.db.update(
                    "staff", data_to_update, "U_code = ?", (U_code,))

            self.bot.send_message(
                chat_id, "✅ اطلاعات شما ثبت شد. بازگشت به منوی واریز/پرداخت.")
            self.handle_payments(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط از گزینه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.validate_crypto_network)
