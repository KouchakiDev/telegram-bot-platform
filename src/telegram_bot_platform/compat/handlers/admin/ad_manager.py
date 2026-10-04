# ad_manager.py
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telegram_bot_platform.compat.config.settings import BUTTONS, MESSAGES
from telegram_bot_platform.compat.database.database_manager import DatabaseManager


class AdManager:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager, back_to_main):
        self.bot = bot
        self.db = db
        self.back_to_main = back_to_main

    def show_ad_creation_menu(self, message):
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(KeyboardButton("ساخت آگهی واقعی"),
                   KeyboardButton("ساخت آگهی فیک"))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(chat_id, "انتخاب نوع آگهی:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_ad_creation_selection)

    def handle_ad_creation_selection(self, message):
        text = message.text.strip()
        chat_id = message.chat.id
        if text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == "ساخت آگهی واقعی":
            self.create_real_ad(message)
        elif text == "ساخت آگهی فیک":
            self.create_fake_ad(message)
        else:
            self.bot.send_message(chat_id, "گزینه نامعتبر.")
            self.show_ad_creation_menu(message)

    def create_real_ad(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id, "لطفاً توضیحات آگهی واقعی را وارد کنید:")
        self.bot.register_next_step_handler(message, self.process_real_ad)

    def process_real_ad(self, message):
        ad_description = message.text.strip()
        data = {
            # Internal implementation note: legacy behavior is preserved during modernization.
            "U_code": "real_ad",
            "ad_description": ad_description,
            "status": "pending"
        }
        self.db.insert("ads_staff", data)
        self.bot.send_message(message.chat.id, "آگهی واقعی با موفقیت ثبت شد.")
        self.back_to_main(message)

    def create_fake_ad(self, message):
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "لطفاً توضیحات آگهی فیک را وارد کنید:")
        self.bot.register_next_step_handler(message, self.process_fake_ad)

    def process_fake_ad(self, message):
        ad_description = message.text.strip()
        data = {
            "U_code": "fake_ad",  # Internal implementation note: legacy behavior is preserved during modernization.
            "ad_description": ad_description,
            "status": "pending"
        }
        self.db.insert("ads_staff", data)
        self.bot.send_message(message.chat.id, "آگهی فیک با موفقیت ثبت شد.")
        self.back_to_main(message)
