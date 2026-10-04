import os
import sys
import multiprocessing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, '..'))
"""
ماژول BotAdmin
این ماژول شامل کلاس BotAdmin است که مسئول راه‌اندازی و مدیریت ربات ادمین، پرسنل و مشتری در یک نقطه ورود مشترک می‌باشد.
"""
# from admin_main import BotAdmin
from telegram_bot_platform.compat.utils.notification_manager import NotificationManager
from telegram_bot_platform.compat.handlers.admin.automatical_panel import AutomaticalPanel
from telegram_bot_platform.compat.handlers.admin.promo_manager import PromoManager

from telegram_bot_platform.compat.handlers.admin.message_manager import MessageManager
from telegram_bot_platform.compat.handlers.admin.report_manager import ReportManager
from telegram_bot_platform.compat.handlers.admin.ad_manager import AdManager
from telegram_bot_platform.compat.handlers.admin.channel_group_settings import ChannelGroupSettings
from telegram_bot_platform.compat.handlers.admin.staff_manager import StaffManager
from telegram_bot_platform.compat.handlers.admin.answer_manager import AnswerManager

from telegram_bot_platform.compat.handlers.admin.client_manager import ClientManager
from telegram_bot_platform.compat.handlers.admin.accounting_handler import AccountingHandler
from telegram_bot_platform.compat.handlers.admin.request_settings import RequestSettings
from telegram_bot_platform.compat.handlers.admin.request_manager import RequestManager
from telegram_bot_platform.compat.handlers.admin.admin_manager import AdminManager
from telegram_bot_platform.compat.handlers.client.show_staff_profile import StaffProfileHandler
from telegram_bot_platform.compat.handlers.admin.codes_manager import CodesManager   # Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.runners.archive.client_runner_archive import ClientBot
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
import json
from telegram_bot_platform.compat.utils.task_manager import ThreadManager
from telebot import types
import telebot
from telebot.types import Message
from telegram_bot_platform.compat.config.settings import *
from telegram_bot_platform.compat.database.setup import DatabaseSetup
# import threading
from io import BytesIO
from datetime import datetime
from telegram_bot_platform.compat.runners.starter import Starter       # Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.utils.user_search import InlineUserSearcher     # Internal implementation note: legacy behavior is preserved during modernization.

# Import existing handlers

# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
log = CustomLogger("main.log")
database = DatabaseManager(**DB_PARAMS)  # **DB_PARAMS)




class AdminBot:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, admin_token, staff_token, client_token, db: DatabaseManager):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db = db

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot = telebot.TeleBot(admin_token)
        self.per_bot = telebot.TeleBot(staff_token)
        self.cus_bot = telebot.TeleBot(client_token)
        self.T_M = ThreadManager()
        self.ProfPer = StaffProfileHandler(self.bot, db)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bots = {
            'admin': self.bot,
            'staff': self.per_bot,
            'client': self.cus_bot,
            'clients': self.cus_bot
        }
        self.notification_manager = NotificationManager(self.bots, self.db)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.admin_manager = AdminManager(
            self.bot, self.db, self.send_welcome, self.manage_members_menu)
        self.request_manager = RequestManager(
            self.bot, self.db, self.send_welcome, self.settings_menu, self.bots, self.T_M,self)
        #manage_rejection_reasons
        self.setting = RequestSettings(
            self.bot, self.db, self.send_welcome, self.requests_menu)
        self.accounting_handler = AccountingHandler(
            self.bot, self.db, self.send_welcome, self.settings_menu)
        self.client_manager = ClientManager(
            self.bot, self.db,self.send_welcome,  self.manage_members_menu )
        self.staff_manager = StaffManager(
            self.bot, self.db, self.send_welcome, self.manage_members_menu)
        self.channel_settings = ChannelGroupSettings(
            self.bot, self.send_welcome)
        self.ad_manager = AdManager(self.bot, self.db, self.send_welcome)
        self.report_manager = ReportManager(
            self.bot, self.db, self.send_welcome)
        self.message_manager = MessageManager(self.bot, self.bots , self.db,  self.manage_members_menu)
        self.auto_panel = AutomaticalPanel(
           self.bots ,  self.bot, self.db, self.send_welcome, self.requests_menu,self.send_back_up, self.T_M)
        self.codes_manager = CodesManager(
            self.bot,
            self.db,
            back_callback=self.manage_members_menu,
            start_callback=self.send_welcome# Internal implementation note: legacy behavior is preserved during modernization.
        )
        self.auto_answer = AnswerManager(
            self.bot,
            self.db,
            back_callback=self.settings_menu,
            start_callback=self.send_welcome# Internal implementation note: legacy behavior is preserved during modernization.
        )
        self.promo_manager = PromoManager(
            bot=self.bot,
            db=self.db,
            back_to_main=self.send_welcome,
            back_to_settings=self.requests_menu,
            on_interval_update=self.auto_panel._reschedule_promo_tasks  # Internal implementation note: legacy behavior is preserved during modernization.
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.auto_panel.start_auto_approval_thread()
        # p = multiprocessing.Process(target=self.T_M.start())
        # p.start()
        # self.T_M.add_task(self.send_back_up,
        #                   10 * 60, "send  backup  to admin")
        self.send_back_up()
        self.inline_search = InlineUserSearcher(self.db, self.bot)
        self.inline_search.register_handlers()
        self.setup_handlers()
        
        self.starter = Starter(self.db, self.bot, welcome_cb=self.send_welcome)
        self.starter.broadcast_fake_message_to_all()

    
    def send_back_up(self):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            admin = self.db.select_dict("admins", "id = ?", (1,))
            if not admin:
                log.warning("[BackupSender] Cannot find admin with id = 1 for sending backup.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            backup_bytes = self.db.full_database_backup()

            now_str =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Internal implementation note: legacy behavior is preserved during modernization.
            backup_file = BytesIO(backup_bytes)
            backup_file.name = f"lotus_backup_{now_str.replace(':', '_').replace(" ", "_")}.sql"

            caption = f"📦 بک‌آپ دیتابیس در تاریخ:\n{ self.request_manager.convert_to_shamsi(now_str)}"
            self.bot.send_document(
                admin[0]["telegram_id"],
                backup_file,
                caption=caption,
            )

            log.info("[BackupSender] Backup sent to admin.")

        except Exception as e:
            log.exception(f"[BackupSender] Failed to send backup: {e}")
      
    
    def is_admin(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            user_id = str(message.from_user.id)
            username = getattr(message.from_user, "username", "")

            log.info(f"Checking admin status: {user_id}, @{username}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            result = self.db.select_dict(
                "admins", "telegram_id = ? AND A_status = 'active'", (user_id,)
            )
            if result:
                log.info(f"Admin found by telegram_id: {user_id}")
                return json.loads(result[0]["permissions"])

            # Internal implementation note: legacy behavior is preserved during modernization.
            has_sign = False
            if username:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if "@" in username:
                    has_sign = True
                # Internal implementation note: legacy behavior is preserved during modernization.
                result_by_username = self.db.select_dict(
                    "admins", "username = ? AND A_status = 'active'", (
                        username,)
                )
                if result_by_username:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.update(
                        "admins", {"telegram_id": user_id},
                        "username = ? AND A_status = 'active'", (username,)
                    )
                    log.info(
                        f"Admin found by username: @{username}, updated telegram_id to {user_id}")
                    return json.loads(result_by_username[0]["permissions"])
                # Internal implementation note: legacy behavior is preserved during modernization.
                if has_sign:
                    base_username = username.replace("@", "")
                    log.debug(
                        f"Username contains '@', trying without sign: {base_username}")
                    result_base = self.db.select_dict(
                        "admins", "username = ? AND A_status = 'active'", (
                            base_username,)
                    )
                    if result_base:
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        self.db.update(
                            "admins", {"telegram_id": user_id},
                            "username = ? AND A_status = 'active'", (
                                base_username,)
                        )
                        log.info(
                            f"Admin found by username: @{base_username}, updated telegram_id to {user_id}")
                        return json.loads(result_base[0]["permissions"])

            # Internal implementation note: legacy behavior is preserved during modernization.
            log.warning(f"No active admin found for {user_id or username}")
            return False

        except Exception as e:
            log.error(f"Error checking admin status: {e}")
            return False

    def notif_counter(self):
        """Legacy-compatible behavior preserved for this callable."""
        settings = REQUEST_SETTINGS
        counter = 0
        for table, cfg in settings.items():
            try:
                if not self.db.table_exists(table):
                    continue
                status_col = cfg["status_column"]
                count = self.db.count_rows(
                    table, f"{status_col} = ?", ('pending',))
                if count > 0:
                    counter += count
            except Exception as e:
                log.exception(f"Error counting pending on {table}: {e}")
        return counter

    def get_main_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        permissions = self.is_admin(message)
        if not permissions:
            return types.ReplyKeyboardRemove()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []

        if permissions.get("manage_requests", False):
            count = self.notif_counter()
            label = BUTTONS["view_requests"]
            suffix = f"({count})" if count else ""
            buttons.append(types.KeyboardButton(f"{label} {suffix}"))
        if permissions.get("bot_settings", False):
            buttons.append(types.KeyboardButton(BUTTONS["settings"]))
        if permissions.get("manage_codes", False):
            buttons.append(types.KeyboardButton(BUTTONS["manage_codes"]))
        # if permissions.get("view_reports", False):
        #     buttons.append(types.KeyboardButton(BUTTONS["reports"]))
        # if permissions.get("manage_messages", False):
        #     count = self.db.count_rows("tickets", "is_read = 'False'")
        #     label = BUTTONS["messages"]
        #     suffix = f"({count})" if count else ""
        #     buttons.append(types.KeyboardButton(f"{label} {suffix}"))

        markup.add(*buttons)
        return markup

    def send_welcome(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        permissions = self.is_admin(message)
        if not permissions:
            self.bot.send_message(
                message.chat.id,
                MESSAGES["you_dont_have_permission"],
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        markup = self.get_main_menu(message)
        self.bot.send_message(
            message.chat.id,
            MESSAGES["welcome"],
            reply_markup=markup
        )
    
    def settings_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        permissions = self.is_admin(message)
        if not permissions:
            self.bot.send_message(
                message.chat.id,
                MESSAGES["you_dont_have_permission"]
            )
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []

        if any(permissions.get(key, False) for key in ["manage_admins", "manage_clients", "manage_staff", "messages"]):
            buttons.append(types.KeyboardButton(BUTTONS["Manage_members"]))
        # if any(permissions.get(key, False) for key in ["manage_requests", "request_settings", "automatical"]):
        #     buttons.append(types.KeyboardButton(BUTTONS["see_requests"]))
        if permissions.get("manage_requests", False):
            count = self.notif_counter()
            label = BUTTONS["view_requests"]
            suffix = f"({count})" if count else ""
            buttons.append(types.KeyboardButton(f"{label}{suffix}"))
            buttons.append(types.KeyboardButton(BUTTONS["manage_rejection_reasons"]))
        if any(permissions.get(key, False) for key in ["channel_settings", "group_settings"]):
            buttons.append(types.KeyboardButton(BUTTONS["BotAndChannel"])) 
            
        if permissions.get("auto_answer" , False):
            buttons.append(types.KeyboardButton(BUTTONS["auto_answer"])) 
        # if any(permissions.get(key, False) for key in ["channel_settings", "group_settings"]):
        #     buttons.append(types.KeyboardButton(BUTTONS["GropAndChannel"]))
          # Internal implementation note: legacy behavior is preserved during modernization.
        # if permissions.get("view_reports", False):
        #     buttons.append(types.KeyboardButton(BUTTONS["reports"]))
        # if permissions.get("create_ad", False) or permissions.get("ads_setting", False):
        #     buttons.append(types.KeyboardButton(BUTTONS["ads"]))
        # if permissions.get("accounting", False):
        #     buttons.append(types.KeyboardButton(BUTTONS["accounting"]))

        markup.add(*buttons)
        markup.add(types.KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(
            message.chat.id,
            MESSAGES["Pchoice_setting_m"],
            reply_markup=markup
        )

    def manage_members_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        permissions = self.is_admin(message)
        if not permissions:
            self.bot.send_message(
                message.chat.id,
                MESSAGES["you_dont_have_permission"]
            )
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        if permissions.get("manage_admins", False):
            buttons.append(types.KeyboardButton(BUTTONS["manage_admins"]))
        if permissions.get("manage_clients", False):
            buttons.append(types.KeyboardButton(BUTTONS["manage_clients"]))
        # if permissions.get("manage_staff", False):
        #     buttons.append(types.KeyboardButton(BUTTONS["manage_staff"]))
        if permissions.get("manage_users", False):
            buttons.append(types.KeyboardButton(BUTTONS["search_users"])) 
        # if permissions.get("manage_messages", False):
        #     buttons.append(types.KeyboardButton(BUTTONS["messages"]))
        if permissions.get("manage_codes", False):
            buttons.append(types.KeyboardButton(BUTTONS["manage_codes"]))

        markup.add(*buttons)
        markup.add(
            types.KeyboardButton(BUTTONS["back_to_main"]),
            types.KeyboardButton(BUTTONS["back_to_settings"])
        )
        self.bot.send_message(
            message.chat.id,
            MESSAGES["Pchoice_manage_member_m"],
            reply_markup=markup
        )

    def gropAndchannel_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        permissions = self.is_admin(message)
        if not permissions:
            self.bot.send_message(
                message.chat.id,
                MESSAGES["you_dont_have_permission"]
            )
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        if permissions.get("channel_settings", False):
            buttons.append(types.KeyboardButton(BUTTONS["channel_settings"]))
        if permissions.get("group_settings", False):
            buttons.append(types.KeyboardButton(BUTTONS["group_settings"]))
        markup.add(*buttons)
        markup.add(
            types.KeyboardButton(BUTTONS["back_to_main"]),
            types.KeyboardButton(BUTTONS["back_to_settings"])
        )
        self.bot.send_message(
            message.chat.id,
            MESSAGES["GropAndChannellSettings"],
            reply_markup=markup
        )

    def requests_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        permissions = self.is_admin(message)
        if not permissions:
            self.bot.send_message(
                message.chat.id,
                MESSAGES["you_dont_have_permission"]
            )
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        if permissions.get("manage_requests", False):
            count = self.notif_counter()
            label = BUTTONS["view_requests"]
            suffix = f"({count})" if count else ""
            buttons.append(types.KeyboardButton(f"{label}{suffix}"))
        if permissions.get("request_settings", False):
            buttons.append(types.KeyboardButton(BUTTONS["request_settings"]))
        if permissions.get("automatical", False):
            buttons.append(types.KeyboardButton(BUTTONS["auto_operations"]))
        buttons.extend([
            types.KeyboardButton(BUTTONS["back_to_main"]),
            types.KeyboardButton(BUTTONS["back_to_settings"])
        ])
        markup.add(*buttons)
        self.bot.send_message(
            message.chat.id,
            MESSAGES["Pchoice_manage_member_m"],
            reply_markup=markup
        )

    def handle_text_messages(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text.strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        # if text.endswith(')') and '(' in text:
        #     text = text[:text.rfind('(')].strip()
        permissions = self.is_admin(message)
        if not permissions:
            self.bot.send_message(
                message.chat.id,
                MESSAGES["you_dont_have_permission"]
            )
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if BUTTONS["view_requests"]  in text and permissions.get("manage_requests", False):
            self.request_manager.handle_requests_menu(message)
        if BUTTONS["auto_answer"]  in text and permissions.get("auto_answer", False):
            self.auto_answer.show_root_menu(message)
        elif text == BUTTONS["BotAndChannel"] and (permissions.get("channel_settings", False) or permissions.get("group_settings", False)):
            self.promo_manager.show_root_menu(message)
        elif text == BUTTONS["manage_codes"] and permissions.get("manage_codes", False):
            self.codes_manager.show_root_menu(message)
        elif text == BUTTONS["manage_rejection_reasons"] and permissions.get("manage_requests", False):
            self.setting.manage_rejection_reasons(message)
        elif BUTTONS["messages"]  in text  and permissions.get("manage_messages", False):
            self.message_manager.show_messages_menu(message)
        elif BUTTONS["see_requests"] in  text and (permissions.get("manage_requests", False) or permissions.get("request_settings", False)):
            self.requests_menu(message)
        elif text == BUTTONS["request_settings"] and permissions.get("request_settings", False):
            self.setting.main_settings_menu(message)
        elif text in [BUTTONS["settings"], BUTTONS["back_to_settings"]] and permissions.get("bot_settings", False):
            self.settings_menu(message)
        elif text == BUTTONS["GropAndChannel"] and (permissions.get("channel_settings", False) or permissions.get("group_settings", False)):
            self.gropAndchannel_menu(message)
        elif text == BUTTONS["reports"] and permissions.get("view_reports", False):
            self.report_manager.show_reports_menu(message)
        elif text == BUTTONS["Manage_members"] and any(permissions.get(k, False) for k in ["manage_admins", "manage_clients", "manage_staff"]):
            self.manage_members_menu(message)
        elif text == BUTTONS["manage_admins"] and permissions.get("manage_admins", False):
            self.admin_manager.MANAGE_ADMINS_menu(message)
        elif text == BUTTONS["manage_clients"] and permissions.get("manage_clients", False):
            self.client_manager.start_menu(message)
        elif text == BUTTONS["manage_staff"] and permissions.get("manage_staff", False):
            self.staff_manager.show_root_menu(message)
        elif text == BUTTONS["channel_settings"] and permissions.get("channel_settings", False):
            self.channel_settings.show_channel_settings(message)
        elif text == BUTTONS["group_settings"] and permissions.get("group_settings", False):
            self.channel_settings.show_group_settings(message)
        # elif (text == BUTTONS["create_ad"] and permissions.get("create_ad", False)) or permissions.get("ads_setting", False):
        #     self.add_menu(message)
        elif text == BUTTONS["accounting"] and permissions.get("accounting", False):
            self.accounting_handler.handle_accounting_menu(message)
        elif text == BUTTONS["auto_operations"] and permissions.get("automatical", False):
            self.auto_panel.auto_operations_menu(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif text == BUTTONS["search_users"] and permissions.get("manage_users", False):
            try:
                bot_username = self.bot.get_me().username  # @BotUsername

                # Internal implementation note: legacy behavior is preserved during modernization.
                inline_markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(
                        text="🔎 جست‌وجو",
                        switch_inline_query_current_chat=""
                    )
                ).add(
                    types.InlineKeyboardButton("📥 اکسل کل کاربران", callback_data="export_all_users"),
                ).add(
                    types.InlineKeyboardButton("📥 اکسل کاربران امروز", callback_data="export_today_users"),
                ).add(
                    types.InlineKeyboardButton("📥 اکسل یک کاربر", callback_data="export_one_user"),
                )


                # Internal implementation note: legacy behavior is preserved during modernization.
                reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton(BUTTONS["back_to_settings"])
                )

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(
                    message.chat.id,
                    (
                        "✳️ برای جستجوی کاربران کافی است روی دکمهٔ زیر بزنید\n"
                        "یا به‌صورت دستی در چت بنویسید:\n\n"
                        f"<code>@{bot_username} علی</code>\n\n"
                        "🔸 به محض تایپ، نتایج به‌صورت لحظه‌ای نمایش داده می‌شود.\n"
                        "🔸 همچنین می‌توانید اکسل کاربران را دریافت کنید.\n"
                        "🔸 برای خروج، دکمه «🔙 بازگشت» را بزنید."
                    ),
                    parse_mode="HTML",
                    reply_markup=inline_markup
                )

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(
                    message.chat.id,
                    "📦 برای دریافت فایل اکسل کاربران، یکی از گزینه‌ها را انتخاب کنید:",
                    reply_markup=reply_markup
                )

            except Exception as e:
                log.error(f"[SEARCH_USERS] failed: {e}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطا در آماده‌سازی جستجوی کاربران. لطفاً دوباره تلاش کنید."
                )
            return  # Internal implementation note: legacy behavior is preserved during modernization.

        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                message.chat.id,
                MESSAGES.get("invalid_choice",
                             "گزینه نامعتبر است، لطفاً دوباره تلاش کنید.")
            )
            self.send_welcome(message)

    def setup_handlers(self):
        """Legacy-compatible behavior preserved for this callable."""
        @self.bot.message_handler(regexp=r'^/p\d+$')
        def _handle_staff_command(message):
            """Legacy-compatible behavior preserved for this callable."""
            self.ProfPer.handle_staff_profile(message)
        
        @self.bot.message_handler(commands=["start"])
        def start_handler(message: Message):
            log.debug("[/start] received from %s", message.chat.id)
            chat_id = message.chat.id
            args = message.text.split()
            import re
            if len(args) > 1:
                param = args[1]
                regexp = r'^p\d+$'
                if re.match(regexp , param):
                    message.text = f"/{param}"
                    self.ProfPer.handle_staff_profile(message)
            self.starter.store_user_info(message)           # Internal implementation note: legacy behavior is preserved during modernization.
          # Internal implementation note: legacy behavior is preserved during modernization.
            self.send_welcome(message)
        @self.bot.message_handler(commands=["publish_now"])
        def manual_publish(message):
            if not self.is_admin(message):  # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.reply_to(message, "⛔ فقط ادمین می‌تواند این دستور را اجرا کند.")
                return
        
            try:
                self.bot.reply_to(message, "⏳ در حال اجرای انتشار شبانه به‌صورت دستی...")
                self.auto_panel._run_nightly_publish()
            except Exception as e:
                self.bot.reply_to(message, f"❌ خطا در اجرای انتشار: {e}")
                log.exception(f"[MANUAL PUBLISH] Failed: {e}")


        @self.bot.message_handler(func=lambda message: True)
        def text_handler(message: Message):
            self.handle_text_messages(message)
    
    def run(self):
        """Legacy-compatible behavior preserved for this callable."""
        log.info("🤖 Bot is running...")
        self.bot.polling(none_stop=True)


def start_admin_bot():
    """Legacy-compatible behavior preserved for this callable."""
    # Internal implementation note: legacy behavior is preserved during modernization.
    setup = DatabaseSetup()
    setup.setup_admin()  # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    db = DatabaseManager(**DB_PARAMS)  # **DB_PARAMS)
    log = CustomLogger("admin_runner.log")
    log.info("📦 Database initialized and logger set.")

    # Internal implementation note: legacy behavior is preserved during modernization.
    try:
        bot_admin = AdminBot(
            BOT_ADMIN_TOKEN,
            BOT_STAFF_TOKEN,
            BOT_CLIENT_TOKEN,
            db=db
        )
        log.info("✅ Admin bot instance created. Starting polling...")
        bot_admin.run()
    except Exception as e:
        log.exception(f"❌ Failed to start admin bot: {e}")


if __name__ == "__main__":
    start_admin_bot()
