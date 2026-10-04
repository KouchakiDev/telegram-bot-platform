# -*- coding: utf-8 -*-
"""Legacy-compatible behavior preserved for this callable."""

from __future__ import annotations
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, '..'))

import datetime as _dt
import functools
import threading
from typing import Dict, List, Optional ,Callable
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup , InlineKeyboardButton
# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.runners.starter import Starter

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
import time
# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import (
    BOT_STAFF_TOKEN,
    BOT_CLIENT_TOKEN,
    BOT_ADMIN_TOKEN,
    DB_PARAMS
)
import datetime

# ----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ----------------------------------------------------------------------------
MIN_DELAY_BEFORE_START: int = 0
INTERVAL_BETWEEN_HOURS: int = 60
ROUND_TO_NEAREST_HOUR: bool = True
DURATION_AFTER_START: int = 2*60
MINUTES_BEFORE_MIDNIGHT: int = 0
LAST_START_TIME_LIMIT: str = "22:00"
DAILY_NOTIFICATION_TIME: str = "10:00"
SUBMIT_TO_DAY_ACTIVITY : str = "📊 تعیین فعالیت امروز"
ALREATE_TIME  = "10:00"
# ----------------------------------------------------------------------------
logger = CustomLogger("StaffRunner")


# ----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ----------------------------------------------------------------------------
def license_required(fn):
    @functools.wraps(fn)
    def wrapper(self, message, *args, **kwargs):
        # Internal implementation note: legacy behavior is preserved during modernization.
        code = self.get_code_by_telegram(message)
        if not code:
            sent = self.bot.send_message(
                message.chat.id,
                "🔒 لطفاً ابتدا کد ورود معتبر وارد کنید:"
            )
            self.bot.register_next_step_handler(sent, self._check_license)
            return
        return fn(self, message, *args, **kwargs)
    return wrapper

# ----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ----------------------------------------------------------------------------from typing import Dict

# ----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ----------------------------------------------------------------------------
class StaffBot:
    """Legacy-compatible behavior preserved for this callable."""

    # ------------------------------------------------------------------
    def __init__(self, tokens: Dict[str, str]) -> None:
        self.bot = TeleBot(tokens["staff"])
        self.bots = {
            "client": TeleBot(tokens["client"]),
            "admin": TeleBot(tokens["admin"]),
        }
        self.db = DatabaseManager(**DB_PARAMS)
        self._recent_starts = {}
        self.user_state = {}  # Internal implementation note: legacy behavior is preserved during modernization.
        self.starter = Starter(self.db, self.bot, welcome_cb=self.get_code_by_telegram)

        self._register_handlers()

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _register_handlers(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""

        @self.bot.message_handler(commands=["start"])
        def _handle_start(message: types.Message):
            """Legacy-compatible behavior preserved for this callable."""
            self.starter.store_user_info(message)
            chat_id = message.chat.id
            now = time.time()


            last_ts = self._recent_starts.get(chat_id, 0)
            if now - last_ts < 2:
                logger.info(f"[START] Ignored repeated /start from {chat_id}")
                return  # Internal implementation note: legacy behavior is preserved during modernization.

            self._recent_starts[chat_id] = now
            time.sleep(1)  # Internal implementation note: legacy behavior is preserved during modernization.

            code = self.get_code_by_telegram(message)
            if code:
                self.send_activity_button(chat_id)
            else:
                sent = self.bot.send_message(chat_id, "👋 سلام! لطفاً کد ورود خود را وارد کنید:")
                self.bot.register_next_step_handler(sent, self._check_license)

        self.bot.message_handler(func=lambda m: m.text == SUBMIT_TO_DAY_ACTIVITY)(self._on_activity)
        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(commands=['start_activity'])
        def start_activity(message: types.Message):
            code = self.get_code_by_telegram(message)
            if not code:
                self.bot.send_message(
                    message.chat.id,
                    "🔒 ابتدا کد ورود معتبر وارد کنید.",
                    reply_markup=types.ReplyKeyboardRemove()
                )
                sent = self.bot.send_message(message.chat.id, "لطفاً کد ورود را وارد کنید:")
                self.bot.register_next_step_handler(sent, self._check_license)
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.prompt_start_time(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("request_drafts:"))
        def _handle_tmp_client_callback(call: types.CallbackQuery):
            _, action, req_id_str = call.data.split(":")
            request_id = int(req_id_str)
            chat_id = call.message.chat.id

            # Internal implementation note: legacy behavior is preserved during modernization.
            row = self.db.select_dict("request_drafts", "id = ?", (request_id,))
            if not row:
                self.bot.answer_callback_query(call.id, "❌ درخواستی یافت نشد.")
                return
            cust = row[0]

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.answer_callback_query(call.id)

            if action == "accept":
                # Internal implementation note: legacy behavior is preserved during modernization.
                phone    = cust.get("phone", "—")
                username = cust.get("username", "—")
                # Internal implementation note: legacy behavior is preserved during modernization.
                lines = [
                    f"👤 نام: {cust.get('name','—')}",
                    f"🌍 منطقه: {cust.get('region','—')}",
                    f"🕒 زمان درخواست: {cust.get('request_time','—')}",
                ]
                if cust.get("note"):
                    lines.append(f"📝 توضیحات: {cust['note']}")
                lines += [
                    f"📞 شماره تلفن: +{phone}",
                    f"🆔 یوزرنیم: @{username}"
                ]
                new_caption = "\n".join(lines)
                # Internal implementation note: legacy behavior is preserved during modernization.
                done_keyboard = InlineKeyboardMarkup(row_width=2)
                done_keyboard.add(
                    InlineKeyboardButton("✅ انجام شد", callback_data=f"request_drafts:done:{request_id}"),
                    InlineKeyboardButton("❌ کنسل شد", callback_data=f"request_drafts:cancel:{request_id}")
                )



                # Internal implementation note: legacy behavior is preserved during modernization.
                
                self.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    caption=new_caption,
                    parse_mode="HTML",
                    reply_markup=done_keyboard
                    
                )
            
                    

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.update(
                    "request_drafts",
                    {"status": "finalaized"},
                    "id = ?",
                    (request_id,)
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                user_id = cust.get("telegram_id")
                if user_id:
                    code = cust.get("staff_code", "—")
                    self.bots["client"].send_message(
                        user_id,
                        f"✅ درخواست شما برای کد پرسنل {code} پذیرفته شد.\n📞 منتظر تماس پرسنل با شماره‌ای که وارد کرده‌اید باشید."
                    )
                admin_text = (
                    f"📬 درخواست #{request_id} توسط پرسنل تایید شد ✅\n\n"
                    f"👤 مشتری: {cust.get('name', '—')}\n"
                    f"🌍 منطقه: {cust.get('region', '—')}\n"
                    f"📞 تلفن: +{cust.get('phone', '—')}\n"
                    f"🆔 یوزرنیم: @{cust.get('username', '—')}\n"
                    f"🕒 زمان درخواست: {cust.get('request_time', '—')}\n"
                    f"🔑 کد ارائه‌دهنده: {cust.get('staff_code', '—')}\n"
                    + (f"📝 توضیحات: {cust['note']}\n" if cust.get('note') else "")
                )
                self.message_to_admin(admin_text)



            elif action == "reject":
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.user_state[chat_id] = {"reject_request_id": request_id}
                self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)

                # Internal implementation note: legacy behavior is preserved during modernization.
                sent = self.bot.send_message(
                    chat_id,
                    "❌ لطفاً دلیل رد درخواست را وارد کنید:"
                )
                self.bot.register_next_step_handler(sent, self._process_reject_reason)
                
            elif action == "done":
                self.db.update("request_drafts", {"status": "done"}, "id = ?", (request_id,))
                self.bot.answer_callback_query(call.id, "✅ وضعیت انجام‌شده ثبت شد.")
                self.bot.send_message(chat_id, "🟢 وضعیت این درخواست به انجام‌شده تغییر یافت.")
                self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)

                # Internal implementation note: legacy behavior is preserved during modernization.
                admin_text = (
                    f"🎯 درخواست #{request_id} توسط پرسنل انجام شد 🟢\n\n"
                    f"👤 مشتری: {cust.get('name', '—')}\n"
                    f"🌍 منطقه: {cust.get('region', '—')}\n"
                    f"📞 تلفن: +{cust.get('phone', '—')}\n"
                    f"🆔 یوزرنیم: @{cust.get('username', '—')}\n"
                    f"🕒 زمان درخواست: {cust.get('request_time', '—')}\n"
                    f"🔑 کد ارائه‌دهنده: {cust.get('staff_code', '—')}\n"
                )
                self.message_to_admin(admin_text)

                # Internal implementation note: legacy behavior is preserved during modernization.
                user_id = cust.get("telegram_id")
                if user_id:
                    self.bots["client"].send_message(
                        user_id,
                        "✨ درخواست شما با موفقیت انجام شد.\n🙏 امیدواریم از سفارش خود لذت کافی را برده باشید."
                    )


            elif action == "cancel":
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.user_state[chat_id] = {"cancel_request_id": request_id}

                sent = self.bot.send_message(
                    chat_id,
                    "❌ لطفاً دلیل کنسل شدن این درخواست را وارد کنید:"
                )
                self.bot.register_next_step_handler(sent, self._process_cancel_reason)


    def _process_cancel_reason(self, message: types.Message):
        chat_id = message.chat.id
        state = self.user_state.get(chat_id, {})
        request_id = state.get("cancel_request_id")

        if not request_id:
            self.bot.send_message(chat_id, "⚠️ خطا: شناسه درخواست پیدا نشد.")
            return

        reason = message.text.strip()
        if not reason:
            self.bot.send_message(chat_id, "❗ لطفاً یک دلیل معتبر وارد کنید.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update(
            "request_drafts",
            {"status": "canceled", "cancel_reason": reason},
            "id = ?",
            (request_id,)
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        row = self.db.select_dict("request_drafts", "id = ?", (request_id,))
        if row:
            cust = row[0]
            admin_text = (
                f"🔻 درخواست #{request_id} توسط پرسنل کنسل شد ❌\n\n"
                f"👤 مشتری: {cust.get('name', '—')}\n"
                f"🌍 منطقه: {cust.get('region', '—')}\n"
                f"📞 تلفن: +{cust.get('phone', '—')}\n"
                f"🆔 یوزرنیم: @{cust.get('username', '—')}\n"
                f"🕒 زمان درخواست: {cust.get('request_time', '—')}\n"
                f"🔑 کد ارائه‌دهنده: {cust.get('staff_code', '—')}\n"
                f"📝 دلیل کنسلی: {reason}"
            )
            self.message_to_admin(admin_text)



        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, "✅ دلیل دریافت شد. وضعیت به حالت «کنسل‌شده» ثبت شد.")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state.pop(chat_id, None)


    @license_required
    def _on_activity(self, message: types.Message):
        self.prompt_start_time(message)
    
    
    def get_code_by_telegram(self, message: types.Message) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            telegram_id = message.from_user.id
            row = self.db.select_dict("codes", "telegram_id = ?", (telegram_id,))
            if row:
                row = row[0]
                
                return row.get("code")
            return None
        except Exception as exc:
            logger.exception("get_code_by_telegram failed · err=%s", exc)
            return None

    def validate_license(self, license_key: str) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            row = self.db.select_dict("codes", "license = ?", (license_key,))
            if row:
                row = row[0]
                return row.get("code")
            return None
        except Exception as exc:
            logger.exception("validate_license failed · err=%s", exc)
            return None

    def set_telegram_id(self, message: types.Message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            telegram_id = message.from_user.id
            license_key = message.text.strip()
            self.db.update("codes", {"telegram_id": telegram_id}, "license = ?", (license_key,))
            logger.info("Set telegram_id for license=%s", license_key)
            return True
        except Exception as exc:
            logger.exception("set_telegram_id failed · err=%s", exc)
            return False



    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _check_license(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            license_key = message.text.strip()
            code = self.validate_license(license_key)
            if code:
                self.set_telegram_id( message)
                self.bot.reply_to(message, "✅ کد ورود تأیید شد.")
                self.send_activity_button(message.chat.id)
            else:
                sent = self.bot.reply_to(message, "❌ کد ورود نامعتبر است، دوباره امتحان کنید:")
                self.bot.register_next_step_handler(sent, self._check_license)
        except Exception as exc:
            logger.exception("License check failed: %s", exc)
            self.bot.reply_to(message, "⚠️ خطا در بررسی کد ورود.")

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def send_activity_button(self, chat_id: int) -> None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(SUBMIT_TO_DAY_ACTIVITY)
        self.bot.send_message(chat_id, "برای ثبت فعالیت روزانه، دکمه زیر را بزنید.", reply_markup=markup)

    ## ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _compute_start_slots(self) -> List[_dt.datetime]:
        now = _dt.datetime.now()
        start_base = now + _dt.timedelta(minutes=MIN_DELAY_BEFORE_START)
        if ROUND_TO_NEAREST_HOUR:
            start_base = start_base.replace(minute=0, second=0, microsecond=0) + _dt.timedelta(hours=1)
        slots: List[_dt.datetime] = []
        limit_time = _dt.datetime.combine(now.date(), _dt.time.fromisoformat(LAST_START_TIME_LIMIT))
        while start_base <= limit_time:
            slots.append(start_base)
            start_base += _dt.timedelta(minutes=INTERVAL_BETWEEN_HOURS)
        return slots

    # ------------------------------------------------------------------
    def _compute_end_slots(self, start: datetime.datetime) -> List[datetime.datetime]:
        """Legacy-compatible behavior preserved for this callable."""
        end_slots: List[datetime.datetime] = []
        # Internal implementation note: legacy behavior is preserved during modernization.
        next_slot = start + datetime.timedelta(minutes=DURATION_AFTER_START)
        # Internal implementation note: legacy behavior is preserved during modernization.
        last_allowed = datetime.datetime.combine(
            start.date(),
            datetime.time.fromisoformat(LAST_START_TIME_LIMIT)
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        while next_slot <= last_allowed:
            end_slots.append(next_slot)
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_slot += datetime.timedelta(minutes=INTERVAL_BETWEEN_HOURS)
        return end_slots


    # Internal implementation note: legacy behavior is preserved during modernization.
    def _handle_start(self, message: types.Message):
        try:
            chat_id = message.chat.id
            selected = message.text.strip()
            start_time = _dt.datetime.combine(_dt.datetime.now().date(), _dt.time.fromisoformat(selected))

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state[chat_id] = {"start_time": start_time}

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.prompt_end_time(message, start_time)
        except Exception as exc:
            logger.exception("handle_start failed: %s", exc)
            self.bot.reply_to(message, "❌ ساعت شروع نامعتبر بود.")

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _handle_end(self, message: types.Message):
        try:
            chat_id = message.chat.id
            selected = message.text.strip()

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                end_time = _dt.datetime.combine(_dt.datetime.now().date(), _dt.time.fromisoformat(selected))
            except ValueError:
                self.bot.reply_to(message, "❌ فرمت ساعت نامعتبره. لطفاً از دکمه‌ها استفاده کن.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            start_time = self.user_state.get(chat_id, {}).get("start_time")
            if not start_time:
                self.bot.reply_to(message, "⛔ ساعت شروع پیدا نشد. لطفاً دوباره انتخاب کن.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            if end_time <= start_time:
                self.bot.reply_to(message, "⚠️ ساعت پایان باید بعد از ساعت شروع باشه.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            delta_minutes = int((end_time - start_time).total_seconds() / 60)
            if delta_minutes % INTERVAL_BETWEEN_HOURS != 0:
                self.bot.reply_to(message, f"⚠️ فاصله بین شروع و پایان باید مضرب {INTERVAL_BETWEEN_HOURS} دقیقه باشه.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            latest_allowed = _dt.datetime.combine(start_time.date(), _dt.time(23, 59)) - _dt.timedelta(minutes=MINUTES_BEFORE_MIDNIGHT)
            if end_time > latest_allowed:
                self.bot.reply_to(message, "❌ ساعت انتخاب‌شده خیلی دیره. لطفاً زودتر رو انتخاب کن.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            code = self.get_code_by_telegram(message)
            self.finalize_activity(chat_id, code, start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))

        except Exception as exc:
            logger.exception("handle_end failed: %s", exc)
            self.bot.reply_to(message, "❌ خطا در ثبت ساعت پایان.")


     # Internal implementation note: legacy behavior is preserved during modernization.
    def prompt_start_time(self, message) -> None:
        try:
            chat_id = message.chat.id
            slots = self._compute_start_slots()
            markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            buttons = [types.KeyboardButton(slot.strftime("%H:%M")) for slot in slots]
            markup.add(*buttons)
            sent = self.bot.send_message(chat_id, "ساعت شروع را انتخاب کنید:", reply_markup=markup)
            self.bot.register_next_step_handler(sent, self._handle_start)
        except Exception as exc:
            logger.exception("Failed to prompt start time: %s", exc)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def prompt_end_time(self, message, start_time: datetime.datetime) -> None:
        try:
            chat_id = message.chat.id
            slots = self._compute_end_slots(start_time)
            if not slots:
                self.bot.send_message(chat_id, "❌ متأسفانه هیچ گزینه‌ای برای پایان موجود نیست.")
                return
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            buttons = [types.KeyboardButton(s.strftime("%H:%M")) for s in slots]
            markup.add(*buttons)
            sent = self.bot.send_message(chat_id, "ساعت پایان را انتخاب کنید:", reply_markup=markup)
            self.bot.register_next_step_handler(sent, self._handle_end)
        except Exception as exc:
            logger.exception("Failed to prompt end time: %s", exc)



    # Internal implementation note: legacy behavior is preserved during modernization.
    def finalize_activity(self, chat_id: int, code: str, start: str, end: str) -> None:
        try:
            text_admin = f"کاربر با کد {code} امروز از ساعت {start} تا {end} فعالیت خود را ثبت کرد."
            self.message_to_admin(text_admin)
            self.bot.send_message(
                chat_id,
                "✅ فعالیت شما ثبت شد.",
                reply_markup=types.ReplyKeyboardRemove()
            )
        except Exception as exc:
            logger.exception("Failed to finalize activity: %s", exc)

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def schedule_function_daily(self, target_time: str, func: Callable) -> None:
        """Schedules a function to run daily at the given HH:MM time."""
        now = _dt.datetime.now()
        try:
            hour, minute = map(int, target_time.split(":"))
            notif_time = _dt.datetime.combine(now.date(), _dt.time(hour, minute))
        except ValueError:
            logger.error("Invalid time format. Use HH:MM.")
            return

        if now >= notif_time:
            notif_time += _dt.timedelta(days=1)

        delay = (notif_time - now).total_seconds()
        threading.Timer(delay, func).start()
        logger.info("Function scheduled in %s seconds for %s", delay, target_time)

    def _send_daily_notifications(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("codes")
            # Internal implementation note: legacy behavior is preserved during modernization.
            ids = [row["telegram_id"] for row in rows if row.get("telegram_id")]
            if not ids:
                logger.info("No telegram_id found for daily notifications")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            for chat_id in ids:
                try:
                    self.bot.send_message(chat_id, "لطفاً فعالیت امروز خود را ثبت کنید.")
                except Exception as send_exc:
                    logger.error("Failed sending daily notification to %s: %s", chat_id, send_exc)

            logger.info("Daily notifications sent to %d users", len(ids))
        except Exception as exc:
            logger.exception("Failed to send daily notifications: %s", exc)
        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.schedule_function_daily(DAILY_NOTIFICATION_TIME , self._send_daily_notifications)
    def _send_daily_alreat(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("codes")
            # Internal implementation note: legacy behavior is preserved during modernization.
            ids = [row["telegram_id"] for row in rows if row.get("telegram_id")]
            if not ids:
                logger.info("No telegram_id found for daily notifications")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            for chat_id in ids:
                try:
                    self.bot.send_message(chat_id, "لطفاً وضعیت سفارش های امروز خود را مشخص کنید.")
                except Exception as send_exc:
                    logger.error("Failed sending daily notification to %s: %s", chat_id, send_exc)

            logger.info("Daily notifications sent to %d users", len(ids))
        except Exception as exc:
            logger.exception("Failed to send daily notifications: %s", exc)
        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.schedule_function_daily(ALREATE_TIME , self._send_daily_alreat)

    def message_to_admin(self, text: str):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            admins = self.get_admins()
            if not admins:
                logger.warning("[ADMIN_MSG] No eligible admins to notify.")
                return

            for admin in admins:
                try:
                    self.bots["admin"].send_message(admin["telegram_id"], text)
                    logger.info(f"[ADMIN_MSG] Message sent to admin ID={admin['telegram_id']}")
                except Exception as send_exc:
                    logger.error(f"[ADMIN_MSG] Failed to send to admin ID={admin['telegram_id']}: {send_exc}")

        except Exception as exc:
            logger.exception(f"[ADMIN_MSG] Unexpected failure in admin messaging: {exc}")

    def get_admins(self):
        """Legacy-compatible behavior preserved for this callable."""
        import json
        try:
            admins = self.db.select_dict("admins")
            filtered_admins = []

            if admins:
                for admin in admins:
                    try:
                        permissions = json.loads(admin.get("permissions", "{}"))
                        if permissions.get("manage_requests"):
                            filtered_admins.append(admin)
                    except json.JSONDecodeError as json_err:
                        logger.warning(f"[ADMIN-PERMISSIONS] Invalid JSON for admin ID={admin.get('id')}: {json_err}")

            return filtered_admins

        except Exception as exc:
            logger.exception(f"[GET_ADMINS] Failed to fetch admins: {exc}")
            return []
    # Internal implementation note: legacy behavior is preserved during modernization.

    

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _process_reject_reason(self, message: types.Message):
        chat_id = message.chat.id
        state = self.user_state.get(chat_id, {})
        request_id = state.get("reject_request_id")
        reason = message.text.strip()

        if not request_id:
            self.bot.send_message(chat_id, "⚠️ خطا: شناسه درخواست پیدا نشد.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update(
            "request_drafts",
            {"status": "rejected", "reject_reason": reason},
            "id = ?",
            (request_id,)
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        row = self.db.select_dict("request_drafts", "id = ?", (request_id,))[0]
        user_id = row.get("telegram_id")
        if user_id:
            self.bots["client"].send_message(
                user_id,
                "❌ متاسفانه این پرسنل در حال حاضر قادر به ارائه خدمات نمی‌باشد.\nلطفاً کد دیگری را انتخاب و مجدد ثبت درخواست نمایید."
            )
            
        admin_text = (
            f"📪 درخواست #{request_id} توسط پرسنل *رد شد* ❌\n\n"
            f"👤 مشتری: {row.get('name', '—')}\n"
            f"🌍 منطقه: {row.get('region', '—')}\n"
            f"📞 تلفن: +{row.get('phone', '—')}\n"
            f"🆔 یوزرنیم: @{row.get('username', '—')}\n"
            f"🕒 زمان درخواست: {row.get('request_time', '—')}\n"
            f"🔑 کد ارائه‌دهنده: {row.get('staff_code', '—')}\n"
            f"📝 دلیل رد: {reason}"
        )

        self.message_to_admin(admin_text)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            "✅ درخواست رد شد و دلیل آن ارسال گردید."
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state.pop(chat_id, None)
 
    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def start(self) -> None:
        self.schedule_function_daily(DAILY_NOTIFICATION_TIME , self._send_daily_notifications)
        self.schedule_function_daily(ALREATE_TIME , self._send_daily_alreat)
        
        logger.info("Staff bot started …")
        self.bot.infinity_polling()





# ----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ----------------------------------------------------------------------------
def start_staff_bot() -> None:
    tokens = {
        "client": BOT_CLIENT_TOKEN,
        "admin": BOT_ADMIN_TOKEN,
        "staff": BOT_STAFF_TOKEN,
    }
    try:
        StaffBot(tokens).start()
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user (Ctrl-C)")
    except Exception as exc:
        logger.exception("Fatal error – bot crashed: %s", exc)


if __name__ == "__main__":
    start_staff_bot()