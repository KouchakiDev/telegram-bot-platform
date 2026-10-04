# channel_group_settings.py
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telegram_bot_platform.compat.config.settings import BUTTONS, MESSAGES


class ChannelGroupSettings:
    def __init__(self, bot: telebot.TeleBot, back_to_main):
        self.bot = bot
        self.back_to_main = back_to_main

    def show_channel_settings(self, message):
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(KeyboardButton("قفل درج آگهی"),
                   KeyboardButton("باز کردن درج آگهی"))
        markup.add(KeyboardButton("تنظیم حداقل زمان بین پست‌ها"),
                   KeyboardButton("ارسال پست در زمان مشخص"))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(chat_id, "تنظیمات کانال:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_channel_selection)

    def handle_channel_selection(self, message):
        text = message.text.strip()
        chat_id = message.chat.id
        if text == "قفل درج آگهی":
            self.bot.send_message(chat_id, "درج آگهی در کانال قفل شد.")
        elif text == "باز کردن درج آگهی":
            self.bot.send_message(chat_id, "درج آگهی در کانال باز شد.")
        elif text == "تنظیم حداقل زمان بین پست‌ها":
            self.bot.send_message(chat_id, "حداقل زمان بین پست‌ها تنظیم شد.")
        elif text == "ارسال پست در زمان مشخص":
            self.bot.send_message(chat_id, "پست در زمان مشخص ارسال خواهد شد.")
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        else:
            self.bot.send_message(chat_id, "گزینه نامعتبر.")
        self.show_channel_settings(message)

    def show_group_settings(self, message):
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(KeyboardButton("قفل درج آگهی"),
                   KeyboardButton("باز کردن درج آگهی"))
        markup.add(KeyboardButton("تنظیم حداقل زمان بین پست‌ها"),
                   KeyboardButton("ارسال پست در زمان مشخص"))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(chat_id, "تنظیمات گروه:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_group_selection)

    def handle_group_selection(self, message):
        text = message.text.strip()
        chat_id = message.chat.id
        if text == "قفل درج آگهی":
            self.bot.send_message(chat_id, "درج آگهی در گروه قفل شد.")
        elif text == "باز کردن درج آگهی":
            self.bot.send_message(chat_id, "درج آگهی در گروه باز شد.")
        elif text == "تنظیم حداقل زمان بین پست‌ها":
            self.bot.send_message(chat_id, "حداقل زمان بین پست‌ها تنظیم شد.")
        elif text == "ارسال پست در زمان مشخص":
            self.bot.send_message(chat_id, "پست در زمان مشخص ارسال خواهد شد.")
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        else:
            self.bot.send_message(chat_id, "گزینه نامعتبر.")
        self.show_group_settings(message)
