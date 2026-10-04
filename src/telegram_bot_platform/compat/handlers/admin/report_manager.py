# report_manager.py
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telegram_bot_platform.compat.config.settings import BUTTONS, MESSAGES
from telegram_bot_platform.compat.database.database_manager import DatabaseManager


class ReportManager:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager, back_to_main):
        self.bot = bot
        self.db = db
        self.back_to_main = back_to_main

    def show_reports_menu(self, message):
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(KeyboardButton("گزارش درخواست‌ها"),
                   KeyboardButton("گزارش پرسنل"))
        markup.add(KeyboardButton("گزارش مشتریان"))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(chat_id, "منوی گزارش‌ها:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_reports_selection)

    def handle_reports_selection(self, message):
        text = message.text.strip()
        chat_id = message.chat.id
        if text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == "گزارش درخواست‌ها":
            self.generate_request_report(message)
        elif text == "گزارش پرسنل":
            self.generate_staff_report(message)
        elif text == "گزارش مشتریان":
            self.generate_client_report(message)
        else:
            self.bot.send_message(chat_id, "گزینه نامعتبر.")
        self.show_reports_menu(message)

    def generate_request_report(self, message):
        chat_id = message.chat.id
        count = self.db.count_rows("ads_staff", "status = ?", ("pending",))
        self.bot.send_message(chat_id, f"تعداد درخواست‌های آگهی: {count}")

    def generate_staff_report(self, message):
        chat_id = message.chat.id
        approved = self.db.count_rows("staff", "status = ?", ("approved",))
        rejected = self.db.count_rows("staff", "status = ?", ("rejected",))
        self.bot.send_message(
            chat_id, f"پرسنل تأیید شده: {approved}\nپرسنل رد شده: {rejected}")

    def generate_client_report(self, message):
        chat_id = message.chat.id
        approved = self.db.count_rows("clients", "status = ?", ("approved",))
        rejected = self.db.count_rows("clients", "status = ?", ("rejected",))
        self.bot.send_message(
            chat_id, f"مشتریان تأیید شده: {approved}\nمشتریان رد شده: {rejected}")
