

# Internal implementation note: legacy behavior is preserved during modernization.
# import telebot
from telebot import TeleBot, types

# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# Client Handlers

from telegram_bot_platform.compat.handlers.client.premium.premium_registeration import PREMIUMRegistration
from telegram_bot_platform.compat.handlers.client.premium.premium_user_panel import PREMIUMUserPanel
# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

log = CustomLogger("premium_manager")


class PREMIUMManager:
    def __init__(self, bot: TeleBot, db: DatabaseManager, back, start , see_Rr):
        self.bot = bot
        self.db = db
        self.back = back
        self.see_Rr = see_Rr
        self.premium_menu = PREMIUMUserPanel(
            self.bot, self.db,  self.back, self.show_main_menu, start, self.see_Rr)
        self.register_menu = PREMIUMRegistration(
            self.bot, self.db,  self.back, self.show_main_menu)

    def user_do_that(self, message, that):
        log.info(
            f"user {message.from_user.username if message.from_user.username else message.from_user.name}  {that}")

    def show_main_menu(self, message):
        chat_id = message.chat.id
        c_premium = self.db.table_exists("premium_clients")

        if c_premium:
            results = self.db.select_dict(
                "premium_clients",  "telegram_id = ? AND C_status = 'approved'", (chat_id,))
            print(results)
            if results:
                result = results[0]
                print(result)
                self.user_do_that(message, f"has a Premium member!")
                self.bot.send_message(
                    chat_id, MESSAGES["premium_panel_welcome"], reply_markup=None)
                self.premium_menu.show_panel(message)
                return
        self.user_do_that(message, f"in premium manager")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(BUTTONS["submit_premium_request"]),
            types.KeyboardButton(BUTTONS["back"]),
        )
        self.bot.send_message(
            chat_id, MESSAGES["please_fisrt_register"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.route)

    def route(self, message):
        text = message.text

        if text == BUTTONS["back"]:
            self.user_do_that(message, f"choice back menu")

            self.back(message)
            return
        elif text == BUTTONS["submit_premium_request"]:
            self.user_do_that(message, f"choice register menu")

            self.register_menu.start_registration(message)
            return
        else:
            self.bot.send_message(message.chat.id, "گزینه نامعتبر است.")
