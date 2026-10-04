from telegram_bot_platform.compat.config.settings import *

from telebot import types


from datetime import datetime
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telebot import types , TeleBot
from telebot.types import Message ,ReplyKeyboardMarkup,KeyboardButton

from datetime import datetime
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="message.log")


class MessagesHandler:
    def __init__(self, bot:TeleBot, db:DatabaseManager, data, parent):
        self.bot = bot
        self.db = db
        self.bots = parent.bots
        self.data = data
        self.parent = parent
        self.temp_data = {}
        
    
    def is_back(self, message: Message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not isinstance(message, Message):
                return False
            if getattr(message, "content_type", None) != "text":
                return False

            # Internal implementation note: legacy behavior is preserved during modernization.
            text = (message.text or "").strip()
            if not text:
                return False

            # Internal implementation note: legacy behavior is preserved during modernization.
            back_triggers = [
                "/start",
                "🔙 بازگشت",
                "🔙 بازگشت به پنل",
                "بازگشت"
            ]

            if text in back_triggers:
                logger.info(f"[MessagesHandler.is_back] Back command detected: {text} | chat_id={message.chat.id}")
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.parent.login_handler.show_work_panel(message)
                return True

            return False

        except Exception as e:
            logger.exception(f"[MessagesHandler.is_back] Exception occurred: {e}")
            return False

    

    def show_messages_menu(self, message: Message):
        chat_id = message.chat.id
        pm_count = self.db.count_rows(
            "tickets",
            "telegram_id = ? AND is_replied = TRUE AND rep_is_read = FALSE",
            (chat_id,)
        )
        pm_label = f"({pm_count}) 📬 مشاهده پیام‌ها" if pm_count else "📬 مشاهده پیام‌ها"

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✉️ ارسال پیام به ادمین", pm_label)
        markup.add("🔙 بازگشت به پنل")

        self.bot.send_message(
            chat_id,
            "لطفاً یکی از گزینه‌های پیام‌رسانی را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_messages_menu_selection
        )


    def handle_messages_menu_selection(self, message):
        text = message.text.strip() if message.text else None
        if "📬 مشاهده پیام‌ها" in text:
            return self.see_my_messages(message)
        elif text == "✉️ ارسال پیام به ادمین":
            return self.start_send_message_to_admin(message)
        elif text == "🔙 بازگشت به پنل":
            return self.parent.login_handler.show_work_panel(message)
        else:
            self.bot.send_message(
                message.chat.id, "❗ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.show_messages_menu(message)
        
    def see_my_messages(self, message: Message):
        chat_id = message.chat.id
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        msgs = self.db.select_dict(
            "tickets",
            "telegram_id = ? AND is_replied = TRUE AND rep_is_read = FALSE",
            (chat_id,)
        )
        if not msgs:
            self.bot.send_message(chat_id, "❌ پیامی یافت نشد.")
            return self.parent.login_handler.show_work_panel(message)
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_data.setdefault(chat_id, {})["messages"] = msgs
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [f"تیکت شماره #{m['id']}" for m in msgs]
        markup.add(*buttons)
        markup.add("🔙 بازگشت")
    
        self.bot.send_message(chat_id, "📬 لطفاً یک تیکت را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handler_my_message_selection)
            

    
    def handler_my_message_selection(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "🔙 بازگشت" or self.is_back(message):
            logger.info(f"[handler_my_message_selection] User requested back → chat_id={chat_id}")
            return self.parent.login_handler.show_work_panel(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if "#" not in text:
            logger.warning(f"[handler_my_message_selection] Invalid format → text='{text}' | chat_id={chat_id}")
            return self.bot.send_message(
                chat_id, "❗ انتخاب نامعتبر",
                reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("🔙 بازگشت")
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            ticket_id = int(text.split("#")[1].strip())
        except (ValueError, IndexError):
            logger.warning(f"[handler_my_message_selection] Failed to extract ticket_id from text='{text}' | chat_id={chat_id}")
            return self.bot.send_message(
                chat_id, "❗ شناسه تیکت نامعتبر است.",
                reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("🔙 بازگشت")
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        messages = self.temp_data.get(chat_id, {}).get("messages", [])
        matched = [m for m in messages if m.get("id") == ticket_id]
        
        if not matched:
            logger.warning(f"[handler_my_message_selection] Ticket not found → ticket_id={ticket_id} | chat_id={chat_id}")
            self.bot.send_message(chat_id, "❌ تیکتی با این شماره یافت نشد.")
            return self.parent.login_handler.show_work_panel(message)
        
        msg = matched[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            
            self.bot.send_message(
                chat_id,
                msg.get("replay_text", ""),
                reply_to_message_id=msg.get("msg_id")
            )
            logger.info(f"[handler_my_message_selection] Sent reply to msg_id={msg.get('msg_id')} | ticket_id={ticket_id} | chat_id={chat_id}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.db.update("tickets", {"rep_is_read": True}, "id = ?", (ticket_id,))
                logger.info(f"[handler_my_message_selection] rep_is_read updated → ticket_id={ticket_id}")
            except Exception as db_err:
                logger.exception(f"[handler_my_message_selection] DB update failed for ticket_id={ticket_id}: {db_err}")
        except Exception as e:
            logger.exception(f"[handler_my_message_selection] Error sending reply → ticket_id={ticket_id}: {e}")
            self.bot.send_message(chat_id, "❌ خطا در ارسال پاسخ.")

        return self.parent.login_handler.show_work_panel(message)

       

    def start_send_message_to_admin(self, message):
        chat_id = message.chat.id

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت")

        self.bot.send_message(
            chat_id,
            "📝 لطفاً پیام خود را برای ادمین وارد کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_admin_message_input)

    def handle_admin_message_input(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip() if message.text else ""

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "🔙 بازگشت":
            return self.parent.login_handler.show_work_panel(message)

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            staff = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
            if not staff:
                self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
                return self.parent.login_handler.show_work_panel(message)

            user = staff[0]
            U_code = user.get("U_code", "")
            telegram_id = user.get("telegram_id", "")

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.db.insert("tickets", {
                    "msg_id": message.id,
                    "message": text,
                    "replay_text": "",
                    "telegram_id": telegram_id,
                    "U_code": U_code,
                    "rep_is_read": False,
                    "is_read": False,
                    "is_replied": False
                })
                logger.info(f"[Ticket] New ticket inserted by U_code={U_code}")
            except Exception as e:
                logger.exception(f"[Ticket] Failed to insert ticket: {e}")
                self.bot.send_message(chat_id, "❌ ثبت پیام با خطا مواجه شد.")
                return self.parent.login_handler.show_work_panel(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                admin_list = self.db.select_dict("admins")
                for admin in admin_list:
                    try:
                        permissions = admin.get("permissions", {})
                        if isinstance(permissions, str):
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            import json
                            permissions = json.loads(permissions)

                        if permissions.get("manage_messages"):
                            admin_id = admin.get("telegram_id")
                            if not admin_id:
                                continue
                            self.bots["admin"].send_message(
                                admin_id,
                                f"📬 پرسنل با کد /{U_code} یک پیام جدید ثبت کرده است.\n"
                                f"برای مشاهده و پاسخ‌دهی به بخش پیام‌ها مراجعه کنید."
                            )
                            logger.info(f"[AdminNotify] Message notification sent to admin {admin_id}")
                    except Exception as e:
                        logger.exception(f"[AdminNotify] Failed to notify admin {admin.get('telegram_id')}: {e}")
            except Exception as e:
                logger.exception(f"[AdminNotify] Failed to fetch admins list or send notifications: {e}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "✅ پیام شما برای ادمین ارسال شد.")
            return self.parent.login_handler.show_work_panel(message)

        except Exception as e:
            logger.exception(f"[handle_admin_message_input] General error: {e}")
            self.bot.send_message(chat_id, "❌ بروز خطا هنگام پردازش پیام.")
            return self.parent.login_handler.show_work_panel(message)


    def handle_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "🔙 بازگشت":
            return self.parent.login_handler.show_work_panel(message)

        label_map = self.data.get(chat_id, {}).get("label_map", {})
        message_id = label_map.get(text)

        if not message_id:
            self.bot.send_message(chat_id, "❌ پیام یافت نشد.")
            return self.show_messages(message)

        msg = self.db.select_dict("messages", "id = ?", (message_id,))
        if not msg:
            return self.bot.send_message(chat_id, "❌ پیام پیدا نشد.")

        self.db.update("messages", {"is_read": True}, "id = ?", (message_id,))
        self.bot.send_message(chat_id, f"📝 {msg[0]['message']}")
        return self.show_messages(message)

    def get_unread_count(self, U_code):
        unread = self.db.select_dict(
            "messages", "to_u_code = ? AND is_read = 0", (U_code,))
        return len(unread)
