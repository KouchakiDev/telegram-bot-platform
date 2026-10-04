"""Legacy-compatible behavior preserved for this callable."""

import re
from datetime import datetime
from typing import Dict, List, Optional , Callable

from telebot import types, TeleBot
from telebot.types import Message, CallbackQuery
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BLACKLIST_QUESTIONS = {
    "/start", "start", "🔙 بازگشت", "بازگشت", "back"
}

BUTTONS = {
    "root_add": "➕ ثبت پاسخ",
    "root_view": "📋 مشاهده پاسخ‌ها",
    "root_edit": "✏️ ویرایش پاسخ",
    "root_delete": "🗑 حذف پاسخ",
    "back": "🔙 بازگشت",
}

CALLBACK_PREFIX = {
    "view": "ans_view_",   # ans_view_<id>
    "edit": "ans_edit_",   # ans_edit_<id>
    "delete": "ans_del_",  # ans_del_<id>
}

LOG = CustomLogger("answer_manager.log")
log = LOG
logger = log

class AnswerManager:
    """Admin handler to manage *automatic* answers (FAQ / canned responses)."""

    # ---------------------------------------------------------------------
    # Construction helpers
    # ---------------------------------------------------------------------

    def __init__(self, bot : TeleBot,db: DatabaseManager,back_callback : Callable, start_callback : Callable,):
        self.bot = bot
        self.db = db
        self.back_callback = back_callback      # function(message)
        self.start_callback = start_callback    # function(message)
        self.tmp_mind = {}
        self._ensure_table()
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.states: Dict[int, Dict] = {}


        LOG.info("AnswerManager initialised.")

    # ------------------------------------------------------------------ DB
    def _ensure_table(self):
        """Create table if missing."""
        self.db.ensure_table_and_columns(
            table_name="auto_answers",
            data={
                "question":None,
                "answer":None,
                "usage_count":0,
            },
            column_types={
                "question":"TEXT    UNIQUE NOT NULL",
                "answer":"TEXT    NOT NULL",
                "usage_count":"INTEGER DEFAULT 0",
            },
        )
        LOG.debug("Ensured auto_answers table exists.")
    
    def is_back(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not isinstance(message, Message):
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            
            text = message.text
            if not text:
                return False
            log.debug(text)
            text = text.strip()
            chat_id = message.chat.id
            log.debug(chat_id)
            
            if text.startswith("/start"):
                self.start_callback(message)
                return True
            elif BUTTONS["back"] in text:
                self.back_callback(message)
                return True
            else:
                return False
        except Exception as e:
            logger.exception(f"[MessagesHandler.is_back] Exception occurred: {e}")
            return False
    
    def _back_markup(self, markup:types.ReplyKeyboardMarkup = None):
        if not  markup :
            markup = types.ReplyKeyboardMarkup(True , row_width=2)
        markup.add(BUTTONS["back"])
        return markup
    # --------------------------------------------------------------- Menu
    def show_root_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(BUTTONS["root_add"]),
            types.KeyboardButton(BUTTONS["root_view"]),
            types.KeyboardButton(BUTTONS["root_edit"]),
            types.KeyboardButton(BUTTONS["root_delete"]),
        )
        msg = self.bot.send_message(
            message.chat.id,
            "✳️ مدیریت پاسخ خودکار – لطفاً یکی از گزینه‌ها رو انتخاب کن:",
            reply_markup=self._back_markup(markup)
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(msg, self.handle_root_selection)

    def handle_root_selection(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text.strip()
        chat_id = message.chat.id
        
        if self.is_back(message):
            return
        
        if text == BUTTONS["root_add"]:
            return self.start_add_answer(message)
        elif text == BUTTONS["root_view"]:
            self.show_questions(message)
        elif text == BUTTONS["root_edit"]:
            self.show_edit_menu(message)
        elif text == BUTTONS["root_delete"]:
            self.show_delete_menu(message)
        else:
            LOG.warning(f"Unknown menu choice: {text}")
            self.bot.send_message(chat_id, "⚠️ گزینه نامعتبره. دوباره تلاش کن:")
            return self.show_root_menu(message)

    def start_add_answer(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        LOG.info("Starting add answer flow for chat %s", message.chat.id)
        if self.is_back(message):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "🔍 لطفاً سوال مورد نظر رو به صورت یک کلمه یا جمله ارسال کن:",
            reply_markup=self._back_markup()
        )
        self.bot.register_next_step_handler(msg, self.receive_question)

    def receive_question(self, message: Message):
        text = message.text.strip()
        chat_id = message.chat.id
        if self.is_back(message):
            return
        
        self.tmp_mind[chat_id] = {'question': text}
        LOG.info("Received question '%s' from chat %s", text, message.chat.id)
        msg = self.bot.send_message(
            message.chat.id,
            "✏️ حالا پاسخ مناسب رو ارسال کن:",
            reply_markup=self._back_markup()
        )
        self.bot.register_next_step_handler(msg, self.receive_answer)

    def receive_answer(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        user_id = message.chat.id
        text = message.text.strip()

        # Handle cancelation
        if self.is_back(message):
            return
        

        question = self.tmp_mind[user_id].get('question')
        if not question:
            LOG.error("Missing question context for user %s during answer input", user_id)
            self.bot.send_message(
                user_id,
                "⚠️ متأسفانه خطایی رخ داد: سوال پیدا نشد. دوباره تلاش کن.",
                reply_markup=self._back_markup()
            )
            return self.show_root_menu(message)

        answer = text
        record_id = None

        try:
            # Insert into DB
            payload = {"question": question, "answer": answer}
            self.db.insert("auto_answers", payload)
            LOG.debug("Inserted new auto-answer payload: %s", payload)

            # Retrieve ID of the newly inserted record
            rows = self.db.select_dict(
                "auto_answers",
                "question = ? AND answer = ?",
                (question, answer)
            )
            if rows:
                record_id = rows[0].get("id")
                LOG.info("Saved answer for question '%s' with ID %s", question, record_id)
            else:
                LOG.warning(
                    "Answer inserted but could not retrieve ID for question '%s'", question
                )

            # Notify user
            success_text = (
                f"✅ پاسخ با موفقیت ثبت شد!"
                + (f" (ID: {record_id})" if record_id else "")
            )
            self.bot.send_message(
                user_id,
                success_text,
                reply_markup=self._back_markup()
            )

        except Exception as e:
            LOG.exception("Failed to save auto-answer for user %s", user_id)
            self.bot.send_message(
                user_id,
                "❌ متأسفانه پاسخ ثبت نشد. لطفاً بعداً دوباره تلاش کن.",
                reply_markup=self._back_markup()
            )
        finally:
        # Return to root menu in all cases
            return self.show_root_menu(message)

    # ---------------------------------------------------------------- states helpers
  
            
    def show_questions(self, message: Message):
        """
        Display all registered questions as reply-keyboard buttons,
        two per row. On selection, show question details without exiting menu.
        """
        chat_id = message.chat.id
        try:
            # Fetch all questions with their stats
            rows = self.db.select_dict("auto_answers",)
            
            if self.is_back(message):
                return
        
            if not rows:
                self.bot.send_message(
                    chat_id,
                    "⚠️ هنوز هیچ سوالی ثبت نشده.",
                    reply_markup=self._back_markup()
                )
                return self.show_root_menu(message)

            # Build keyboard: each button text = "<id>. <question>"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btns = []
            for row in rows:
                qid = row["id"]
                qtext = row["question"]
                btn = types.KeyboardButton(f"{qid}. {qtext}")
                btns.append(btn)
            markup.add(*btns)
            # Add back button
            
            msg = self.bot.send_message(
                chat_id,
                "📋 لیست سوالات ثبت‌شده — یکی رو انتخاب کن تا جزئیاتشو ببینی:",
                reply_markup=self._back_markup(markup)
            )
            # Register handler for selection
            self.bot.register_next_step_handler(msg, self.handle_question_selection)
        except Exception:
            LOG.exception("Failed to fetch question list for user %s", chat_id)
            self.bot.send_message(
                chat_id,
                "❌ خطا در بارگذاری لیست سوال‌ها. لطفاً بعدا تلاش کن.",
                reply_markup=self._back_markup()
            )
            return self.show_root_menu(message)

    def handle_question_selection(self, message: Message):
        """
        Process user's question choice button.
        Show ID, question text, usage count, and the stored answer.
        Remain in this menu for further browsing.
        """
        chat_id = message.chat.id
        text = message.text.strip()

        # Allow back or restart
        if self.is_back(message):
            return
        

        # Parse "<id>. <question>" format
        try:
            qid_str, _ = text.split(".", 1)
            qid = int(qid_str)
        except ValueError:
            self.bot.send_message(
                chat_id,
                "⚠️ فرمت انتخاب نامعتبره. لطفاً یکی از دکمه‌ها رو بزن.",
                reply_markup=self._back_markup()
            )
            return self.show_questions(message)

        # Fetch record
        row = self.db.select_dict(
            "auto_answers",
            "id = ?",
            (qid,)
        )
        if not row:
            self.bot.send_message(
                chat_id,
                f"⚠️ سوال با شناسه {qid} پیدا نشد.",
                reply_markup=self._back_markup()
            )
            return self.show_questions(message)

        record = row[0]
        # Fetch usage count
        
        count = int(record["usage_count"])

        # Build detail message
        detail = (
            f"🆔 شناسه سؤال: {qid}\n"
            f"❓ سؤال: {record['question']}\n"
            f"💬 پاسخ ثبت‌شده:\n{record['answer']}"
            f"🔢 تعداد دفعات پرسیده شده: {count}\n"
        )
        self.bot.send_message(
            chat_id,
            detail,
            
        )
        # Stay in this handler until back
        return self.show_questions  # note: TeleBot ignores return value; handled via next_step

    def show_edit_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        
        try:
            rows = self.db.select_dict("auto_answers",)
            if not rows:
                self.bot.send_message(
                    chat_id,
                    "⚠️ هنوز هیچ سوالی برای ویرایش ثبت نشده.",
                    reply_markup=self._back_markup()
                )
                return self.show_root_menu(message)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            buttons = [
                types.KeyboardButton(f"{row['id']}. {row['question']}")
                for row in rows
            ]
            markup.add(*buttons)
            msg = self.bot.send_message(
                chat_id,
                "✏️ برای ویرایش، یکی از سوال‌ها رو انتخاب کن:",
                reply_markup=self._back_markup(markup)
            )
            self.bot.register_next_step_handler(msg, self.handle_edit_selection)
        except Exception:
            LOG.exception("Failed to load questions for edit menu for user %s", chat_id)
            self.bot.send_message(
                chat_id,
                "❌ خطا در نمایش سوال‌ها. لطفاً بعداً امتحان کن.",
                reply_markup=self._back_markup()
            )
            return self.show_root_menu(message)

    def handle_edit_selection(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()

        if self.is_back(message):
            return
        

        try:
            qid_str, _ = text.split(".", 1)
            qid = int(qid_str)
        except ValueError:
            self.bot.send_message(
                chat_id,
                "⚠️ فرمت انتخاب نامعتبر است. لطفاً دوباره گزینه‌ای از دکمه‌ها بزن.",
                reply_markup=self._back_markup()
            )
            return self.show_edit_menu(message)

        row = self.db.select_dict("auto_answers", "id = ?", (qid,))
        if not row:
            self.bot.send_message(
                chat_id,
                f"⚠️ سوال با شناسه {qid} پیدا نشد.",
                reply_markup=self._back_markup()
            )
            return self.show_edit_menu(message)

        record = row[0]
        count = record.get("usage_count", 0)
        detail = (
            f"🆔 ID: {qid}\n"
            f"❓ سؤال: {record['question']}\n"
            f"💬 پاسخ: {record['answer']}\n"
            f"🔢 تعداد پرسیده شده: {count}"
        )
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("✏️ ویرایش سؤال"),
            types.KeyboardButton("✏️ ویرایش پاسخ"),
        )
        

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.states[chat_id] = {"edit_qid": qid}
        LOG.info("User %s selected QID %s for editing", chat_id, qid)

        msg  = self.bot.send_message(chat_id, detail, reply_markup=self._back_markup(markup))
        self.bot.register_next_step_handler(msg, self.handle_edit_field_selection)

    def handle_edit_field_selection(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        state = self.states.get(chat_id, {})
        qid = state.get("edit_qid")

        if self.is_back(message):
            return
        

        if text == "✏️ ویرایش سؤال":
            field = "question"
            prompt = "لطفاً متن جدید سؤال را ارسال کن:"
        elif text == "✏️ ویرایش پاسخ":
            field = "answer"
            prompt = "لطفاً پاسخ جدید را ارسال کن:"
        else:
            self.bot.send_message(
                chat_id,
                "⚠️ گزینه نامعتبر. دوباره تلاش کن.",
                reply_markup=self._back_markup()
            )
            return self.show_edit_menu(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.states[chat_id]["edit_field"] = field
        LOG.info("User %s chose to edit field '%s' of QID %s", chat_id, field, qid)

        msg = self.bot.send_message(chat_id, prompt, reply_markup=self._back_markup())
        self.bot.register_next_step_handler(msg, self.handle_edit_input)

    def handle_edit_input(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        state = self.states.get(chat_id, {})
        qid = state.get("edit_qid")
        field = state.get("edit_field")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return
        

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(
                table_name="auto_answers",
                data={field: text},
                condition="id = ?",
                params=(qid,)
            )
            LOG.info("Updated QID %s: set %s = %s", qid, field, text)
            self.bot.send_message(
                chat_id,
                f"✅ فیلد {field} با موفقیت بروز شد!",
                reply_markup=self._back_markup()
            )
        except Exception:
            LOG.exception("Failed to update QID %s field %s for user %s", qid, field, chat_id)
            self.bot.send_message(
                chat_id,
                "❌ خطا در بروزرسانی. لطفاً دوباره تلاش کن.",
                reply_markup=self._back_markup()
            )
        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.states.pop(chat_id, None)
            return self.show_edit_menu(message)
        # -------------------------- DELETE FLOW --------------------------

    def show_delete_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        
        try:
            rows = self.db.select_dict("auto_answers",)
            if not rows:
                self.bot.send_message(
                    chat_id,
                    "⚠️ هنوز هیچ سوالی برای حذف ثبت نشده.",
                    reply_markup=self._back_markup()
                )
                return self.show_root_menu(message)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            buttons = [
                types.KeyboardButton(f"{row['id']}. {row['question']}")
                for row in rows
            ]
            markup.add(*buttons)
            

            msg = self.bot.send_message(
                chat_id,
                "🗑️ برای حذف یک سؤال، لطفاً آن را انتخاب کن:",
                reply_markup=self._back_markup(markup)
            )
            self.bot.register_next_step_handler(msg, self.handle_delete_selection)
        except Exception:
            LOG.exception("Failed to load questions for delete menu for user %s", chat_id)
            self.bot.send_message(
                chat_id,
                "❌ خطا در نمایش سوال‌ها. لطفاً بعداً امتحان کن.",
                reply_markup=self._back_markup()
            )
            return self.show_root_menu(message)

    def handle_delete_selection(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()

        if self.is_back(message):
            return
        

        try:
            qid_str, _ = text.split(".", 1)
            qid = int(qid_str)
        except ValueError:
            self.bot.send_message(
                chat_id,
                "⚠️ فرمت انتخاب نامعتبر است. دوباره گزینه‌ای بزن.",
                reply_markup=self._back_markup()
            )
            return self.show_delete_menu(message)

        row = self.db.select_dict("auto_answers", "id = ?", (qid,))
        if not row:
            self.bot.send_message(
                chat_id,
                f"⚠️ سوال با شناسه {qid} پیدا نشد.",
                reply_markup=self._back_markup()
            )
            return self.show_delete_menu(message)

        record = row[0]
        count = record.get("usage_count", 0)
        detail = (
            f"🆔 ID: {qid}\n"
            f"❓ سؤال: {record['question']}\n"
            f"💬 پاسخ: {record['answer']}\n"
            f"🔢 تعداد پرسیده شده: {count}\n\n"
            f"❗ آیا از حذف این مورد مطمئنی؟"
        )
        # confirm/cancel buttons
        confirm_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        confirm_markup.add(
            types.KeyboardButton("✅ بله، حذف کن"),
            types.KeyboardButton("❌ انصراف")
        )
        

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.states[chat_id] = {"delete_qid": qid}
        LOG.info("User %s requested deletion for QID %s", chat_id, qid)

        msg = self.bot.send_message(chat_id, detail, reply_markup=self._back_markup(confirm_markup))
        self.bot.register_next_step_handler(msg, self.handle_delete_confirmation)

    def handle_delete_confirmation(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        state = self.states.get(chat_id, {})
        qid = state.get("delete_qid")

        # cancel or back
        if self.is_back(message):
            return
        

        if text == "✅ بله، حذف کن":
            try:
                self.db.delete("auto_answers", "id = ?", (qid,))
                LOG.info("Deleted auto-answer QID %s for user %s", qid, chat_id)
                self.bot.send_message(
                    chat_id,
                    f"✅ سؤال و پاسخ با شناسه {qid} حذف شد.",
                    reply_markup=self._back_markup()
                )
            except Exception:
                LOG.exception("Failed to delete QID %s for user %s", qid, chat_id)
                self.bot.send_message(
                    chat_id,
                    "❌ خطا در حذف مورد. لطفاً دوباره تلاش کن.",
                    reply_markup=self._back_markup()
                )
        else:
            LOG.info("Deletion canceled by user %s for QID %s", chat_id, qid)
            self.bot.send_message(
                chat_id,
                "❎ حذف لغو شد.",
                reply_markup=self._back_markup()
            )

        # clear state and remain in delete menu
        self.states.pop(chat_id, None)
        return self.show_delete_menu(message)
    