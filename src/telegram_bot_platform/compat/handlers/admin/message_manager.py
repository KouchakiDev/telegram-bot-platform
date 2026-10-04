#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# message_manager.py
# ------------------------------------------------------------------------------
# Module for handling messaging system in Telegram bot between staff and admin.
# This module implements:
#  - Admin viewing user tickets
#  - Marking tickets as read
#  - Replying to tickets
#  - Sending notifications to users
#  - Robust navigation and error handling
# ------------------------------------------------------------------------------
# Author: Your Name
# Created: 2025-05-29
# License: MIT
################################################################################

from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
import telebot 
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardMarkup,InlineKeyboardButton ,CallbackQuery
from typing import List, Dict, Any, Optional, Callable
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
import re
# ------------------------------------------------------------------------------
# Logger Configuration
# ------------------------------------------------------------------------------
logger = CustomLogger()
log = logger
# ------------------------------------------------------------------------------
# Constants and Configuration
# ------------------------------------------------------------------------------
from telegram_bot_platform.compat.config.settings import *

# messages table name
TICKETS_TABLE = 'tickets'
_P2E = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")   # Persian-to-English

# ------------------------------------------------------------------------------
# MessageManager Class
# ------------------------------------------------------------------------------
class MessageManager:
    """
    Manager for handling internal messaging between users and admin in the Telegram bot.

    Features:
    - show unread tickets to admin
    - mark tickets as read
    - allow admin to reply to tickets
    - update database flags is_read, is_replied, rep_is_read
    - notify user of admin replies
    - robust back navigation and error handling
    """

    def __init__(
        self,
        bot: telebot.TeleBot,
        bots: Dict[str, telebot.TeleBot],
        db: DatabaseManager,
        back_to_main: Callable[[Message], None]
    ):
        """
        Initialize MessageManager.

        :param bot: Instance of TeleBot
        :param db: Instance of DatabaseManager
        :param back_to_main: Callback to return to admin main panel
        """
        self.bot = bot
        self.bots = bots
        
        self.db = db
        self.back_to_main = back_to_main
        # Temporary per-admin storage
        self.temp_data: Dict[int, Dict[str, Any]] = {}
        self.handle_callback()
        
    def handle_callback(self):
        @self.bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("ticket_"))
        def _handle_ticket_callbacks(call: CallbackQuery):
            """Legacy-compatible behavior preserved for this callable."""
            try:
                self.handle_ticket_callback(call)
            except Exception as e:
                logger.exception(f"[CallbackQuery] Error while handling ticket callback: {e}")
                self.bot.answer_callback_query(call.id, "❌ خطا در پردازش درخواست.")

    # --------------------------------------------------------------------------
    # Navigation Helper
    # --------------------------------------------------------------------------
    def is_back(self, message: Message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if not isinstance(message, Message):
                return False
            if getattr(message, 'content_type', '') != 'text':
                return False

            text = message.text
            if not text:
                return False

            triggers = [
                '/start',
                BUTTONS.get('back_to_main', ''),
                '🔙 بازگشت'
            ]
            if text in triggers:
                
                logger.info(f"[MessageManager.is_back] trigger detected: {text} | chat_id={message.chat.id}")
                if text == '🔙 بازگشت':
                    self.show_messages_menu(message)   # Internal implementation note: legacy behavior is preserved during modernization.
                    return True
                else:
                    self.back_to_main(message)
                    return True
            return False
        except Exception as e:
            logger.exception(f"[MessageManager.is_back] Exception: {e}")
            return False

    def add_back_buttons(self , markup):
        
        markup.add(BUTTONS["back"], BUTTONS["back_to_main"])
        return markup
    # --------------------------------------------------------------------------
    # Display Unread Tickets
    # --------------------------------------------------------------------------
    def show_messages_menu(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            unread_count = self.db.count_rows(TICKETS_TABLE, "is_read = FALSE")

            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            label = f"📬 خوانده‌نشده"
            serfix = f"({unread_count})" if unread_count else ""
            markup.add(
                KeyboardButton(f"{label} {serfix}"),
                KeyboardButton("📖 خوانده‌شده"),
                KeyboardButton("📭 پاسخ‌داده‌شده"),
            )
            markup = self.add_back_buttons(markup)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                "📨 بخش پیام‌ها:\nلطفاً یک دسته را انتخاب کنید:",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self.handle_messages_menu_selection)

        except Exception as e:
            logger.exception(f"[show_messages_menu] Error: {e}")
            self.back_to_main(message)


    def handle_messages_menu_selection(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        try:
            if "خوانده‌نشده" in text:
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self.show_unread_messages_menu(message)

            if text == "📖 خوانده‌شده":
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self.show_read_tickets_menu(message)

            if text == "📭 پاسخ‌داده‌شده":
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self.show_replied_tickets_menu(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "❌ گزینه نامعتبر است.")
            return self.show_messages_menu(message)

        except Exception as e:
            logger.exception(f"[handle_messages_menu_selection] Error: {e}")
            self.bot.send_message(chat_id, "❌ خطا در پردازش انتخاب.")
            return self.show_messages_menu(message)


        
    def show_unread_messages_menu(self, message: Message) -> None:
        """
        Display a menu of unread tickets for admin to select.

        Fetches tickets where is_read=FALSE.
        """
        chat_id = message.chat.id
        if self.is_back(message):
            return
        try:
            tickets = self._fetch_unread_tickets()
            if not tickets:
                self.bot.send_message(chat_id, '❌ تیکتی یافت نشد.')
                return self.show_messages_menu(message)

            # Store for later use
            self.temp_data[chat_id] = {'tickets': tickets}

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            buttons = []
            for t in tickets:
                label = self._format_ticket_label(t)
                buttons.append(KeyboardButton(label))
            markup.add(*buttons)
            markup = self.add_back_buttons(markup)

            self.bot.send_message(
                chat_id,
                '📬 لطفاً یک تیکت را انتخاب کنید:',
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self.handle_ticket_selection)
        except Exception as e:
            logger.exception(f"[show_messages_menu] {e}")
            # In case of error, return to main
            self.back_to_main(message)
            
    def show_read_tickets_menu(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            tickets = self.db.select_dict(TICKETS_TABLE, "is_read = TRUE")
            if not tickets:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(chat_id, '📭 تیکت خوانده‌شده‌ای یافت نشد.', reply_markup=markup)
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.temp_data[chat_id] = {'reads_tickets': tickets}

            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            buttons = []
            for ticket in tickets:
                label = f"تیکت #{ticket.get('id')}"
                buttons.append(KeyboardButton(label))
            markup.add(*buttons)
            markup = self.add_back_buttons(markup)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "📖 لطفاً یکی از تیکت‌های خوانده‌شده را انتخاب کنید:", reply_markup=markup)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.register_next_step_handler(message, self.handle_read_ticket_selection)

        except Exception as e:
            logger.exception(f"[show_read_tickets_menu] Failed: {e}")
            self.bot.send_message(chat_id, "❌ خطا در نمایش تیکت‌ها.")

            return self.back_to_main(message)
    def handle_read_ticket_selection(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        try:
            if not "#" in text:
                return self.bot.register_next_step_handler(message , self.handle_read_ticket_selection)
                
            ticket_id = self._extract_ticket_id(text)
            if ticket_id is None:
                self.bot.send_message(chat_id, "❌ شناسه تیکت نامعتبر است.")
                return self.show_read_tickets_menu(message)

            tickets = self.temp_data.get(chat_id, {}).get("reads_tickets", [])
            ticket = next((t for t in tickets if t.get("id") == ticket_id), None)

            if not ticket:
                self.bot.send_message(chat_id, "❌ تیکت مورد نظر یافت نشد.")
                return self.show_read_tickets_menu(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            message_text = (
                f"📝 <b>متن تیکت:</b>\n{ticket.get('message', '—')}\n\n"
                f"📩 <b>پاسخ ادمین:</b>\n{ticket.get('replay_text', '—')}"
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            inline = InlineKeyboardMarkup(row_width=2)
            inline.add(InlineKeyboardButton("📤 پاسخ مجدد", callback_data=f"ticket_reply_again|{ticket_id}"))

            
           

            self.bot.send_message(chat_id, message_text, reply_markup=inline, parse_mode="HTML")

            # Internal implementation note: legacy behavior is preserved during modernization.
            # self.bot.register_next_step_handler(message, self.show_read_tickets_menu)

        except Exception as e:
            logger.exception(f"[handle_read_ticket_selection] Error: {e}")
            self.bot.send_message(chat_id, "❌ خطا در نمایش تیکت.")
            return self.show_read_tickets_menu(message)
        self.bot.register_next_step_handler(message , self.handle_read_ticket_selection)
    # --------------------------------------------------------------------------
    # Handle Ticket Selection
    # --------------------------------------------------------------------------
    def handle_ticket_selection(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        try:
            if not "#" in text:
                return self.bot.register_next_step_handler(message , self.handle_ticket_selection)
            ticket_id = self._extract_ticket_id(text)
            if ticket_id is None:
                self.bot.send_message(chat_id, "❌ شناسه تیکت نامعتبر است.")
                return self.show_messages_menu(message)

            ticket = self.db.select_dict(TICKETS_TABLE, "id = ?", (int(ticket_id),))

            if not ticket:
                self.bot.send_message(chat_id, "❌ تیکت مورد نظر یافت نشد.")
                return self.show_replied_tickets_menu(message)
            ticket = ticket[0] 

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.temp_data.setdefault(chat_id, {})["selected"] = ticket

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                staff = self.db.select_dict("staff", "U_code = ?", (ticket.get("U_code"),))
                if not staff:
                    self.bot.send_message(chat_id, "❌ اطلاعات پرسنل یافت نشد.")
                    return self.show_messages_menu(message)
                staff = staff[0]
            except Exception as e:
                logger.exception(f"[handle_ticket_selection] Failed to fetch staff data: {e}")
                self.bot.send_message(chat_id, "❌ خطا در دریافت اطلاعات پرسنل.")
                return self.show_messages_menu(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                staff_info = (
                    "🧑‍💼 ارائه‌دهنده: {} | سطح تجربه: {} | کد: {}\n".format(
                        staff.get("name", "نامشخص"),
                        staff.get("age", "-"),
                        staff.get("U_code", "---")
                    ) +
                    "📞 تلفن ارائه‌دهنده: {}\n".format(self.normalize_phone_number(staff.get("phone_number", "---"))) +
                    "📍 منطقه: {} | شهر: {}\n".format(
                        staff.get("region", "---"),
                        staff.get("city", "---")
                    )
                )
            except Exception as e:
                logger.exception(f"[handle_ticket_selection] Failed to build staff info: {e}")
                staff_info = "❌ خطا در بارگذاری مشخصات پرسنل."

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("📥 پاسخ", callback_data=f"ticket_reply|{ticket_id}"),
                    InlineKeyboardButton("✅ خوانده شد", callback_data=f"ticket_read|{ticket_id}")
                )
            except Exception as e:
                logger.exception(f"[handle_ticket_selection] Failed to create inline keyboard: {e}")
                markup = None

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.bot.send_message(chat_id, f"📝 مشخصات فرستنده:\n{staff_info}")
                self.bot.send_message(
                    chat_id,
                    f"📝 متن پیام:\n{ticket.get('message', '—')}",
                    reply_markup=markup
                )
            except Exception as e:
                logger.exception(f"[handle_ticket_selection] Failed to send message to admin: {e}")
                self.bot.send_message(chat_id, "❌ خطا در ارسال پیام تیکت.")

        except Exception as e:
            logger.exception(f"[handle_ticket_selection] Unexpected error: {e}")
            self.bot.send_message(chat_id, "❌ بروز خطا هنگام پردازش تیکت.")
            return self.show_messages_menu(message)
        self.bot.register_next_step_handler(message , self.handle_ticket_selection)
    # --------------------------------------------------------------------------
    # Handle Ticket Actions
    # --------------------------------------------------------------------------
    def handle_ticket_callback(self, call: CallbackQuery) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = call.message.chat.id
        # user_id = call.from_user.id
        data , ticket_id = call.data.split("|")
        
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            ticket = self.db.select_dict(TICKETS_TABLE , "id = ?",(int(ticket_id),))
            if not ticket:
                self.bot.answer_callback_query(call.id, "❌ تیکت یافت نشد.")
                return
            ticket = ticket[0]
            if data == "ticket_read":
                try:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self._mark_ticket_read(ticket_id)
                    logger.info(f"[TicketCallback] Ticket marked as read | msg_id={ticket['msg_id']}")
                    self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                    self.bot.send_message(chat_id, "✅ تیکت به‌عنوان خوانده‌شده علامت‌گذاری شد.")
                    return self.show_messages_menu(call.message)
                except Exception as e:
                    logger.exception(f"[TicketCallback] Failed to mark ticket as read: {e}")
                    self.bot.send_message(chat_id, "❌ خطا در علامت‌گذاری به عنوان خوانده‌شده.")

            elif data == "ticket_reply":
                self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                self.bot.send_message(chat_id, "📝 لطفاً پاسخ خود را وارد کنید:")
                return self.bot.register_next_step_handler(call.message, self.handle_admin_reply)
            elif data == "ticket_reply_again":
                self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                self.bot.send_message(chat_id, "📝 لطفاً پاسخ جدید خود را وارد کنید:")
                return self.bot.register_next_step_handler(call.message, self.handle_send_retry,ticket)


            else:
                self.bot.answer_callback_query(call.id, "❌ عملیات نامعتبر.")
                return

        except Exception as e:
            logger.exception(f"[TicketCallback] General error: {e}")
            self.bot.send_message(chat_id, "❌ خطا در پردازش درخواست.")
            return self.show_messages_menu(call.message)

    def handle_ticket_action(self, message: Message) -> None:
        """
        React to admin's choice: reply or mark as read.
        """
        chat_id = message.chat.id
        text = (message.text or '').strip()
        if self.is_back(message):
            return

        ticket = self.temp_data.get(chat_id, {}).get('selected')
        if not ticket:
            return self.show_messages_menu(message)

        ticket_id = ticket['id']

        if text == '✅ خوانده شد':
            self._mark_ticket_read(ticket_id)
            self.bot.send_message(chat_id, '✅ تیکت علامت‌گذاری شد.')
            return self.show_messages_menu(message)

        if text == '📥 پاسخ':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup = self.add_back_buttons(markup)
            self.bot.send_message(chat_id, '🖊 لطفاً پاسخ خود را وارد کنید:', reply_markup=markup)
            return self.bot.register_next_step_handler(message, self.handle_admin_reply)
        elif "#" in text:
            return self.handle_ticket_selection(message)

        # Unrecognized input => back to menu
        return self.show_messages_menu(message)
    
    def handle_send_retry(self, message: Message, ticket: Dict[str, Any]) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        reply_text = (message.text or "").strip()
        if self.is_back(message):
            return
        if not ticket:
            self.bot.send_message(chat_id, "❌ تیکت یافت نشد.")
            return self.show_messages_menu(message)

        ticket_id = ticket.get('id')
        user_tid = ticket.get('telegram_id')
        msg_id = ticket.get("msg_id")
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            full_text = (
                f"📩 پاسخ جدید به تیکت شما:\n{reply_text}"
            )
            self.bots["staff"].send_message(user_tid, full_text,reply_to_message_id=msg_id)
            self._update_ticket_reply(ticket_id , reply_text)
            logger.info(f"[TicketRetry] Retry reply sent for ticket_id={ticket_id} to user {user_tid}")
            self.bot.send_message(chat_id, "✅ پاسخ مجدد ارسال شد.")
        except Exception as e:
            logger.exception(f"[TicketRetry] Failed to send retry reply to user {user_tid}: {e}")
            self.bot.send_message(chat_id, "❌ ارسال پاسخ با خطا مواجه شد.")

        return self.show_replied_tickets_menu(message)
    # --------------------------------------------------------------------------
    # Handle Admin Reply Input
    # --------------------------------------------------------------------------
    def handle_admin_reply(self, message: Message ) -> None:
        """
        Receive admin's reply text, update DB, notify user.
        """
        chat_id = message.chat.id
        text = (message.text or '').strip()

        if self.is_back(message):
            return
        
        ticket = self.temp_data.get(chat_id, {}).get('selected')
        if not ticket:
            return self.show_messages_menu(message)

        ticket_id = ticket['id']
        user_tid = ticket['telegram_id']
        msg_id = ticket.get("msg_id")
        # Update database flags and reply_text
        self._update_ticket_reply(ticket_id, text)
        tex =  f"📥 تیکت شما پاسخ داده شد از بخش پیام ها ◀ مشاهده پیام ها \nمیتوانید پاسخ تیکت را مشاهده کنید"
        # Send reply to user
        try:
            self.bots["staff"].send_message(user_tid,tex , reply_to_message_id=msg_id)
        except Exception as e:
            logger.exception(f"[handle_admin_reply] Failed to send reply to user {user_tid}: {e}")

        # Notify admin of success
        self.bot.send_message(chat_id, '✅ پاسخ شما ثبت و ارسال شد.')

        # Return to ticket list
        return self.show_messages_menu(message)
    
    def handle_admin_reply(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return

        try:
            
            # Internal implementation note: legacy behavior is preserved during modernization.
            ticket = self.temp_data.get(chat_id, {}).get("selected")
            if not ticket:
                self.bot.send_message(chat_id, "❌ تیکت انتخاب نشده یا منقضی شده.")
                return self.show_messages_menu(message)

            ticket_id = ticket.get("id")
            user_tid = ticket.get("telegram_id")
            msg_id = ticket.get("msg_id")
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self._update_ticket_reply(ticket_id, text)
                logger.info(f"[TicketReply] Reply saved | ticket_id={ticket_id}")
            except Exception as e:
                logger.exception(f"[TicketReply] DB update failed for ticket_id={ticket_id}: {e}")
                self.bot.send_message(chat_id, "❌ خطا در ذخیره پاسخ در دیتابیس.")
                return self.show_messages_menu(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                reply_text = (
                    "📩 به تیکت شما پاسخ داده شد.\n"
                    "📨 برای مشاهده نتیجه، به بخش «پیام‌ها» مراجعه کنید."
                )

                self.bots["staff"].send_message(user_tid, reply_text,reply_to_message_id=msg_id)
                logger.info(f"[TicketReply] Reply sent to user {user_tid}")
            except Exception as e:
                logger.exception(f"[TicketReply] Failed to send reply to user {user_tid}: {e}")
                self.bot.send_message(chat_id, "⚠️ پاسخ ذخیره شد ولی ارسال به کاربر با خطا مواجه شد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "✅ پاسخ شما با موفقیت ثبت و ارسال شد.")

        except Exception as e:
            logger.exception(f"[handle_admin_reply] Unexpected error: {e}")
            self.bot.send_message(chat_id, "❌ خطا هنگام پردازش پاسخ.")

        return self.show_messages_menu(message)
    
    def show_replied_tickets_menu(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        try:
            tickets = self.db.select_dict(TICKETS_TABLE, "is_replied = TRUE")
            if not tickets:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(chat_id, '📭 هیچ تیکت پاسخ‌داده‌شده‌ای یافت نشد.', reply_markup=markup)
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.temp_data[chat_id] = {'replied_tickets': tickets}

            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            buttons = []
            for ticket in tickets:
                label = f"تیکت #{ticket.get('id')}"
                buttons.append(KeyboardButton(label))
            markup.add(*buttons)
            markup = self.add_back_buttons(markup)

            self.bot.send_message(chat_id, "📬 یک از تیکت‌های پاسخ‌داده‌شده را انتخاب کنید:", reply_markup=markup)
            self.bot.register_next_step_handler(message, self.handle_replied_ticket_selection)

        except Exception as e:
            logger.exception(f"[show_replied_tickets_menu] Error: {e}")
            self.bot.send_message(chat_id, "❌ خطا در نمایش تیکت‌ها.")
            return self.back_to_main(message)
        
    def handle_replied_ticket_selection(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text

        if self.is_back(message):
            return
        try:
            ticket_id = self._extract_ticket_id(text)
            if not "#" in text:
                return self.bot.register_next_step_handler(message , self.handle_replied_ticket_selection)
                
            if ticket_id is None:
                self.bot.send_message(chat_id, "❌ شناسه تیکت نامعتبر است.")
                return self.show_replied_tickets_menu(message)

            
            ticket = self.db.select_dict(TICKETS_TABLE, "id = ?", (int(ticket_id),))

            if not ticket:
                self.bot.send_message(chat_id, "❌ تیکت مورد نظر یافت نشد.")
                return self.show_replied_tickets_menu(message)
            ticket = ticket[0] 
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.temp_data.setdefault(chat_id, {})["selected"] = ticket

            # Internal implementation note: legacy behavior is preserved during modernization.
            msg_text = (
                f"📝 <b>متن تیکت:</b>\n{ticket.get('message', '—')}\n\n"
                f"📩 <b>پاسخ ادمین:</b>\n{ticket.get('replay_text', '—')}"
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            inline = InlineKeyboardMarkup(row_width=2)
            inline.add(InlineKeyboardButton("📤 پاسخ مجدد", callback_data=f"ticket_reply_again|{ticket_id}"))

            

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, msg_text, reply_markup=inline, parse_mode="HTML")
            # Internal implementation note: legacy behavior is preserved during modernization.

            # Internal implementation note: legacy behavior is preserved during modernization.
            # self.bot.register_next_step_handler(message, self.show_replied_tickets_menu)

        except Exception as e:
            logger.exception(f"[handle_replied_ticket_selection] Error: {e}")
            self.bot.send_message(chat_id, "❌ خطا در نمایش تیکت.")
            return self.show_replied_tickets_menu(message)
        self.bot.register_next_step_handler(message , self.handle_replied_ticket_selection)
        


 

    # --------------------------------------------------------------------------
    # Helper: Fetch unread tickets
    # --------------------------------------------------------------------------
    def _fetch_unread_tickets(self) -> List[Dict[str, Any]]:
        """
        Return list of tickets where is_read=False.
        """
        try:
            return self.db.select_dict(
                TICKETS_TABLE,
                "is_read = FALSE"
            
            )
        except Exception as e:
            logger.exception(f"[_fetch_unread_tickets] {e}")
            return []

    # --------------------------------------------------------------------------
    # Helper: Format button label for ticket
    # --------------------------------------------------------------------------
    def _format_ticket_label(self, ticket: Dict[str, Any]) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        return f"تیکت #{ticket.get('id', '')}"

    # --------------------------------------------------------------------------
    # Helper: Extract ticket ID from label
    # --------------------------------------------------------------------------
    def _extract_ticket_id(self, text: str) -> Optional[int]:
        """Legacy-compatible behavior preserved for this callable."""
        if not text or '#' not in text:
            return None
        try:
            return int(text.split('#', 1)[1].strip())
        except (IndexError, ValueError):
            return None


    # --------------------------------------------------------------------------
    # Helper: Find ticket in temp_data
    # --------------------------------------------------------------------------
    def _find_ticket(self, chat_id: int, ticket_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve ticket dict by id from temp_data.
        """
        tickets = self.temp_data.get(chat_id, {}).get('tickets', [])
        for t in tickets:
            if t.get('id') == ticket_id:
                return t
        return None

    # --------------------------------------------------------------------------
    # Helper: Mark ticket as read
    # --------------------------------------------------------------------------
    def _mark_ticket_read(self, ticket_id: int) -> None:
        """
        Update is_read flag to True.
        """
        try:
            self.db.update(
                TICKETS_TABLE,
                {'is_read': True},
                'id = ?',
                (ticket_id,)
            )
        except Exception as e:
            logger.exception(f"[_mark_ticket_read] {e}")

    # --------------------------------------------------------------------------
    # Helper: Update ticket reply fields
    # --------------------------------------------------------------------------
    def _update_ticket_reply(self, ticket_id: int, reply_text: str) -> None:
        """
        Set replay_text, is_replied, rep_is_read, is_read = True.
        """
        try:
            self.db.update(
                TICKETS_TABLE,
                {
                    'replay_text': reply_text,
                    'is_replied': True,
                    'is_read': True
                },
                'id = ?',
                (ticket_id,)
            )
        except Exception as e:
            logger.exception(f"[_update_ticket_reply] {e}")
       
    def normalize_phone_number(self , number , with_plus: bool = True) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        log.debug("normalize_phone_number called with number=%r, with_plus=%s", number, with_plus)

        # 1) Validate None
        if number is None:
            log.error("Input number is None")
            raise TypeError("شماره نمی‌تواند None باشد")

        # 2) Convert to string
        if isinstance(number, bytes):
            try:
                number_str = number.decode('utf-8')
                log.debug("Decoded bytes to string: %r", number_str)
            except UnicodeDecodeError as e:
                log.exception("UTF-8 decoding error")
                raise ValueError("خطا در رمزگشایی شماره") from e
        else:
            number_str = str(number)
            log.debug("Converted input to string: %r", number_str)

        # 3) Normalize digits and remove separators
        cleaned = number_str.translate(_P2E)
        log.debug("After Persian->English digits: %r", cleaned)
        for sep in (' ', '-', '(', ')', '.'):
            cleaned = cleaned.replace(sep, '')
        log.debug("After removing separators: %r", cleaned)
        cleaned = cleaned.lstrip()
        log.debug("After stripping leading whitespace: %r", cleaned)

        # 4) Remove international prefixes: '+', '00', '98', '0'
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
            log.debug("Removed '+': %r", cleaned)
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
            log.debug("Removed '00': %r", cleaned)
        if cleaned.startswith('98'):
            cleaned = cleaned[2:]
            log.debug("Removed '98': %r", cleaned)
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
            log.debug("Removed leading '0': %r", cleaned)

        # 5) Validate final pattern: exactly 10 digits starting with '9'
        if not re.fullmatch(r"9\d{9}", cleaned):
            log.error("Validation failed for cleaned number: %r", cleaned)
            raise ValueError(f"{number!r} یک شمارهٔ موبایل معتبر نیست")

        # 6) Prepend country code and return
        normalized = f"98{cleaned}"
        result = f"+{normalized}" if with_plus else normalized
        log.info("Normalized phone number: %r", result)
        return result
      
################################################################################
# End of message_manager.py
################################################################################
