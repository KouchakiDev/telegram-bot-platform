"""Legacy-compatible behavior preserved for this callable."""

from __future__ import annotations

import logging
import json
from typing import Optional, Dict, List , Any
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
import telebot
from telebot.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
# Internal implementation note: legacy behavior is preserved during modernization.

BTN_BACK_MAIN     = "🏠 بازگشت به منوی اصلی"
BTN_BACK_PREV     = "🔙 بازگشت"
BTN_PANEL_TEXTS   = "📝 متن‌ها"
BTN_PANEL_MISSIONS= "⏰ مأموریت"
BTN_TOGGLE_BOT    = "🤖 ارسال در ربات"
BTN_TOGGLE_CHN    = "📢 ارسال در کانال"
INLINE_TOGGLE_BOT = "ارسال جدول دکمه شیشه ای🥂"
BTN_ADD           = "➕ افزودن"
BTN_LIST          = "📃 مشاهده"
BTN_EDIT          = "✏️ ویرایش"
BTN_DELETE        = "🗑 حذف"

KINDS             = {"text": "متن‌ تبلیغ", "button": "متنِ دکمه"}

ACTIVITIES        = {"photo": "محتوای تصویری",
                     "order": "ثبت سفارش",
                     "codes": "جدول شیشه ای کدها",  }

# -----------------------------------------------------------------------------


class PromoManager:
    """Legacy-compatible behavior preserved for this callable."""

    # Internal implementation note: legacy behavior is preserved during modernization.
    def __init__(
        self,
        bot: telebot.TeleBot,
        db : DatabaseManager,                                   # Internal implementation note: legacy behavior is preserved during modernization.
        back_to_main,                         # Internal implementation note: legacy behavior is preserved during modernization.
        back_to_settings,            
        on_interval_update,  # Internal implementation note: legacy behavior is preserved during modernization.
        storage_table: str = "promo_settings",
        texts_table: str = "promo_texts",
        logger: Optional[logging.Logger] = None
    ):
        self.bot             = bot
        self.db              = db
        
        self.back_to_main    = back_to_main
        self.back_to_settings= back_to_settings
        self.on_interval_update = on_interval_update 
        self.storage_table   = storage_table
        self.texts_table     = texts_table
        self.log             = logger or CustomLogger("promo_manager")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._ensure_tables()

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._state: Dict[int, Dict] = {}   # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    
    def _ensure_tables(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.ensure_table_and_columns(
                self.storage_table,
                data={
                    "id": 1,
                    "channel_enabled": 0,
                    "bot_enabled": 0,
                    "inline_table_enabled": 0,
                    "channel_interval": 180,
                    "bot_interval": 180,
                    "last_channel_promo_at": 0,
                    "last_bot_promo_at": 0
                },
                column_types={
                    "id": "INT PRIMARY KEY",
                    "channel_enabled": "TINYINT(1)",
                    "bot_enabled": "TINYINT(1)",
                    "inline_table_enabled": "TINYINT(1)",
                    "channel_interval": "INT",
                    "bot_interval": "INT",
                    "last_channel_promo_at": "BIGINT",
                    "last_bot_promo_at": "BIGINT"
                }
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.ensure_table_and_columns(
                self.texts_table,
                data={
                    "activity": "",
                    "kind": "",
                    "content": "",
                    "inline_enabled": 0,
                },
                column_types={
                    "id": "INT PRIMARY KEY AUTO_INCREMENT",
                    "activity": "VARCHAR(16)",
                    "kind": "VARCHAR(16)",
                    "content": "TEXT",
                    "inline_enabled": "TINYINT(1)",
                }
            )

            self.log.info("[DB] promo tables ensured successfully")

        except Exception as exc:
            self.log.exception("[DB] Failed to ensure promo tables: %s", exc)

    
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def show_root_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            settings = self._get_settings()

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

            chn_lbl = f"{BTN_TOGGLE_CHN} {'✅' if settings['channel_enabled'] else '☑'}"
            bot_lbl = f"{BTN_TOGGLE_BOT} {'✅' if settings['bot_enabled'] else '☑'}"
            inline_lbl = f"{INLINE_TOGGLE_BOT} {'✅' if settings['inline_table_enabled'] else '☑'}"
            
            markup.add(KeyboardButton(chn_lbl), KeyboardButton(bot_lbl))
            if inline_lbl:
                markup.add(KeyboardButton(inline_lbl))
            markup.add(KeyboardButton(BTN_PANEL_MISSIONS),
                       KeyboardButton(BTN_PANEL_TEXTS))
            markup.add(KeyboardButton(BTN_BACK_MAIN))

            self.bot.send_message(
                chat_id,
                "👋 لطفاً یکی از گزینه‌های مدیریت تبلیغات را انتخاب کنید:",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self._handle_root_selection)

        except Exception as exc:
            self.log.exception("[ROOT_MENU] failed: %s", exc)

    def _handle_root_selection(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        text = (message.text or "").strip()

        if text == BTN_BACK_MAIN:
            return self.back_to_main(message)

        if BTN_PANEL_MISSIONS in text:
            return self._show_mission_menu(message)

        if BTN_PANEL_TEXTS in text:
            return self._texts_root_menu(message)

        if BTN_TOGGLE_CHN.split()[0] in text:
            self._toggle_setting("channel_enabled", message)
            return

        if BTN_TOGGLE_BOT.split()[0] in text:
            self._toggle_setting("bot_enabled", message)
            return
        
        if INLINE_TOGGLE_BOT.split()[0] in text:
            self._toggle_setting("inline_table_enabled", message)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(message.chat.id, "❗ گزینه نامعتبر است.")
        self.show_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _toggle_setting(self, key: str, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            settings = self._get_settings()  # returns dict including 'id'

            # Internal implementation note: legacy behavior is preserved during modernization.
            current = bool(settings.get(key, 0))
            settings[key] = 0 if current else 1

            # Internal implementation note: legacy behavior is preserved during modernization.
            settings.pop("id", None)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(
                self.storage_table,
                settings,
                "id = ?",
                (1,)
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            new_state = settings[key]
            self.log.info("[TOGGLE] %s set to %s", key, new_state)

        except Exception as exc:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.log.exception("[TOGGLE] failed to toggle %s: %s", key, exc)
            self.bot.send_message(
                message.chat.id,
                f"❌ خطا در تغییر وضعیت «{key}». لطفاً مجدداً تلاش کنید."
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.show_root_menu(message)


    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _show_mission_menu(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        settings = self._get_settings()
        txt = (
            "⏰ <b>فواصل زمانی فعلی:</b>\n"
            f"• کانال: <code>{settings['channel_interval']}</code> دقیقه\n"
            f"• ربات:  <code>{settings['bot_interval']}</code> دقیقه\n\n"
            "یکی از مقاصد زیر را انتخاب کنید تا مقدار جدید وارد نمایید:"
        )
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("کانال"),
            KeyboardButton("ربات")
        )
        markup.add(KeyboardButton(BTN_BACK_PREV), KeyboardButton(BTN_BACK_MAIN))
        self.bot.send_message(
            message.chat.id, txt, parse_mode="HTML", reply_markup=markup)
        self.bot.register_next_step_handler(message, self._mission_destination_selected)

    def _mission_destination_selected(self, message: Message):
            dest = message.text.strip()
            if dest == BTN_BACK_PREV:
                return self.show_root_menu(message)
            if dest == BTN_BACK_MAIN:
                return self.back_to_main(message)

            if dest not in ("کانال", "ربات"):
                self.bot.send_message(message.chat.id, "❌ ورودی نامعتبر.")
                return self._show_mission_menu(message)

            self._state[message.chat.id] = {"dest": dest}
            self.bot.send_message(
                message.chat.id,
                f"🔢 فاصلهٔ زمانی جدید برای {dest} (به دقیقه) را وارد کنید:"
            )
            self.bot.register_next_step_handler(message, self._mission_save_interval)

    def _mission_save_interval(self, message: Message) -> None:
        chat_id = message.chat.id
        st = self._state.pop(chat_id, {})
        dest = st.get("dest")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if message.text in (BTN_BACK_PREV, BTN_BACK_MAIN):
            return self._show_mission_menu(message)

        try:
            minutes = int(message.text.strip())
            if not (1 <= minutes <= 1440):
                raise ValueError

            # Internal implementation note: legacy behavior is preserved during modernization.
            col = "channel_interval" if dest == "کانال" else "bot_interval"

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(self.storage_table, {col: minutes}, "id = %s", (1,))
            self.log.info("[MISSION] %s set to %d minutes", col, minutes)

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.on_interval_update(dest, minutes)
            except Exception as exc:
                self.log.exception("[MISSION] interval callback failed: %s", exc)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, f"✅ فاصلهٔ زمانی «{dest}» روی {minutes} دقیقه تنظیم شد.")

        except ValueError:
            self.bot.send_message(chat_id, "❌ لطفاً یک عدد صحیح بین ۱ تا ۱۴۴۰ وارد کنید.")
        except Exception as exc:
            self.log.exception("[MISSION] unexpected error: %s", exc)
            self.bot.send_message(chat_id, "❌ خطا در ذخیرهٔ تنظیمات.")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._show_mission_menu(message)



    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _texts_root_menu(self, message: Message):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton(BTN_ADD),
            KeyboardButton(BTN_LIST),
            KeyboardButton(BTN_EDIT),
            KeyboardButton(BTN_DELETE)
        )
        markup.add(KeyboardButton(BTN_BACK_PREV), KeyboardButton(BTN_BACK_MAIN))
        self.bot.send_message(
            message.chat.id,
            "📝 یک گزینه را برای مدیریت متن‌ها انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self._texts_handle_action)

    def _texts_handle_action(self, message: Message):
        act = message.text.strip()
        if act == BTN_BACK_PREV:
            return self.show_root_menu(message)
        if act == BTN_BACK_MAIN:
            return self.back_to_main(message)

        if act == BTN_ADD:
            return self._texts_add_step1(message)
        if act == BTN_LIST:
            return self._texts_show_all(message)
        if act == BTN_EDIT:
            return self._texts_select_for_edit(message)
        if act == BTN_DELETE:
            return self._texts_select_for_delete(message)

        self.bot.send_message(message.chat.id, "❗ گزینه نامعتبر.")
        self._texts_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _texts_add_step1(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*(KeyboardButton(v) for v in ACTIVITIES.values()))
        markup.add(KeyboardButton(BTN_BACK_PREV))
        self.bot.send_message(
            message.chat.id,
            "🔸 ابتدا نوع فعالیت را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self._texts_add_step2)

    def _texts_add_step2(self, message: Message):
        if message.text == BTN_BACK_PREV:
            return self._texts_root_menu(message)

        activity_key = self._activity_key(message.text)
        if not activity_key:
            self.bot.send_message(message.chat.id, "❌ گزینه نامعتبر.")
            return self._texts_add_step1(message)

        self._state[message.chat.id] = {"activity": activity_key}
        # Internal implementation note: legacy behavior is preserved during modernization.
        allowed_kinds = ["text"] if activity_key == "codes" else KINDS.keys()
        self._state[message.chat.id] = {"activity": activity_key}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*(KeyboardButton(KINDS[k]) for k in allowed_kinds))
        markup.add(KeyboardButton(BTN_BACK_PREV))
        self.bot.send_message(
            message.chat.id,
            "🔸 حالا نوع محتوا را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self._texts_add_step3)

    def _texts_add_step3(self, message: Message):
        if message.text == BTN_BACK_PREV:
            return self._texts_add_step1(message)

        kind_key = self._kind_key(message.text)
        if not kind_key:
            self.bot.send_message(message.chat.id, "❌ گزینه نامعتبر.")
            return self._texts_add_step2(message)

        self._state[message.chat.id]["kind"] = kind_key
        self.bot.send_message(
            message.chat.id,
            f"✍️ متن {KINDS[kind_key]} را ارسال کنید:"
        )
        self.bot.register_next_step_handler(message, self._texts_add_finalize)

    def _texts_add_finalize(self, message: Message):
        chat_id = message.chat.id
        st = self._state.pop(chat_id, {})
        content = message.text.strip()
        inline_code_stat = 0
            # Internal implementation note: legacy behavior is preserved during modernization.
        if message.text in (BTN_BACK_PREV, BTN_BACK_MAIN):
            return self._texts_root_menu(message)

        try:
            if st["activity"] == "codes" and st["kind"] != "text":
                self.bot.send_message(chat_id, "❌ برای این بخش فقط «متن تبلیغ» مجاز است.")
                return self._texts_root_menu(message)
            if st["activity"] == "codes":
                inline_code_stat = 1
            self.db.insert(
                self.texts_table,
                {
                    "activity": st["activity"],
                    "kind": st["kind"],
                    "content": content ,
                    "inline_enabled" : inline_code_stat
                }
            )
            self.bot.send_message(chat_id, "✅ با موفقیت ذخیره شد.")
            self.log.info("[TEXT_ADD] (%s/%s) added.", st["activity"], st["kind"])
        except Exception as exc:
            self.bot.send_message(chat_id, "❌ خطا در ذخیره‌سازی.")
            self.log.exception("[TEXT_ADD] failed: %s", exc)

        self._texts_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _texts_show_all(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        MAX_LENGTH = 4000

        try:
            rows = self.db.select_dict(self.texts_table, None)
        except Exception as exc:
            self.log.exception("[TEXTS] DB fetch failed: %s", exc)
            self.bot.send_message(chat_id, "❌ خطا در دریافت متون.")
            return self._texts_root_menu(message)

        if not rows:
            self.bot.send_message(chat_id, "هیچ متنی ثبت نشده است.")
            return self._texts_root_menu(message)

        buffer = ""
        send_buffer = lambda buf: (
            self.bot.send_message(chat_id, buf, parse_mode="HTML")
            if buf.strip() else None
        )

        for r in rows:
            activity_label = ACTIVITIES.get(r["activity"], r["activity"])
            kind_label     = KINDS.get(r["kind"], r["kind"])
            entry_header   = f"<b>ID:</b> <code>{r['id']}</code> | " \
                             f"<b>{activity_label}</b> | {kind_label}:\n"
            content        = r["content"].strip() + "\n\n"

            # Internal implementation note: legacy behavior is preserved during modernization.
            full_entry = entry_header + content
            if len(full_entry) > MAX_LENGTH:
                # Internal implementation note: legacy behavior is preserved during modernization.
                lines = content.splitlines(keepends=True)
                chunk = entry_header
                for line in lines:
                    if len(chunk) + len(line) > MAX_LENGTH:
                        try:
                            send_buffer(chunk)
                        except Exception as exc:
                            self.log.exception("[TEXTS] failed to send oversized chunk: %s", exc)
                        chunk = ""
                    chunk += line
                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    send_buffer(chunk)
                except Exception as exc:
                    self.log.exception("[TEXTS] failed to send final oversized chunk: %s", exc)
                continue

            # Internal implementation note: legacy behavior is preserved during modernization.
            if len(buffer) + len(full_entry) > MAX_LENGTH:
                try:
                    send_buffer(buffer)
                except Exception as exc:
                    self.log.exception("[TEXTS] failed to send chunk: %s", exc)
                buffer = ""

            buffer += full_entry

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            send_buffer(buffer)
        except Exception as exc:
            self.log.exception("[TEXTS] failed to send final chunk: %s", exc)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._texts_root_menu(message)



    # Internal implementation note: legacy behavior is preserved during modernization.
    def _texts_select_for_edit(self, message: Message):
        self._texts_select_common(message, mode="edit")

    def _texts_select_for_delete(self, message: Message):
        self._texts_select_common(message, mode="delete")

    def _texts_select_common(self, message: Message, mode: str):
        rows = self.db.select_dict(self.texts_table, None)
        if not rows:
            self.bot.send_message(message.chat.id, "هیچ متنی وجود ندارد.")
            return self._texts_root_menu(message)

        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for r in rows:
            lbl = f"{r['id']} · {ACTIVITIES[r['activity']]} · {KINDS[r['kind']]}"
            markup.add(KeyboardButton(lbl))
        markup.add(KeyboardButton(BTN_BACK_PREV))
        self.bot.send_message(
            message.chat.id,
            "یک مورد را انتخاب کنید:",
            reply_markup=markup
        )
        nxt = self._texts_edit_step if mode == "edit" else self._texts_delete_confirm
        self.bot.register_next_step_handler(message, nxt)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _texts_edit_step(self, message: Message):
        if message.text == BTN_BACK_PREV:
            return self._texts_root_menu(message)

        try:
            rec_id = int(message.text.split()[0])
            row = self.db.select_dict(
                self.texts_table, "id = ?", (rec_id,))
            if not row:
                raise ValueError
            self._state[message.chat.id] = {"rec_id": rec_id}
            self.bot.send_message(
                message.chat.id,
                "✏️ متن جدید را ارسال کنید:"
            )
            self.bot.register_next_step_handler(message, self._texts_edit_finalize)
        except Exception:
            self.bot.send_message(message.chat.id, "❌ انتخاب نامعتبر.")
            self._texts_select_for_edit(message)

    def _texts_edit_finalize(self, message: Message):
        chat_id = message.chat.id
        st = self._state.pop(chat_id, {})
        new_content = message.text.strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
        if message.text in (BTN_BACK_PREV, BTN_BACK_MAIN):
            return self._texts_root_menu(message)

        try:
            self.db.update(
                self.texts_table,
                {"content": new_content},
                "id = ?", (st["rec_id"],)
            )
            self.bot.send_message(chat_id, "✅ متن ویرایش شد.")
            self.log.info("[TEXT_EDIT] id=%s edited.", st["rec_id"])
        except Exception as exc:
            self.bot.send_message(chat_id, "❌ خطا در ویرایش.")
            self.log.exception("[TEXT_EDIT] failed: %s", exc)
        self._texts_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _texts_delete_confirm(self, message: Message):
        if message.text == BTN_BACK_PREV:
            return self._texts_root_menu(message)
        try:
            rec_id = int(message.text.split()[0])
            row = self.db.select_dict(self.texts_table, "id = ?", (rec_id,))
            if not row:
                raise ValueError
            self.db.delete(self.texts_table, "id = ?", (rec_id,))
            self.bot.send_message(
                message.chat.id,
                "🗑 حذف شد."
            )
            self.log.info("[TEXT_DEL] id=%s deleted.", rec_id)
        except Exception:
            self.bot.send_message(message.chat.id, "❌ خطا در حذف.")
        self._texts_root_menu(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _get_settings(self) -> Dict[str, Any]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            rows = self.db.select_dict(self.storage_table, "id = %s", (1,))
        except Exception as exc:
            self.log.exception("[GET_SETTINGS] DB query failed: %s", exc)
            # Internal implementation note: legacy behavior is preserved during modernization.
            return {
                "id": 1,
                "channel_enabled": 1,
                "bot_enabled": 1,
                "channel_interval": 180,
                "bot_interval": 180,
                "last_channel_promo_at": 0,
                "last_bot_promo_at": 0
            }

        if not rows:
            # Internal implementation note: legacy behavior is preserved during modernization.
            default = {
                "id": 1,
                "channel_enabled": 1,
                "bot_enabled": 1,
                "channel_interval": 180,
                "bot_interval": 180,
                "last_channel_promo_at": 0,
                "last_bot_promo_at": 0
            }
            try:
                self.db.insert(self.storage_table, default)
            except Exception as exc:
                self.log.exception("[GET_SETTINGS] failed to insert default: %s", exc)
            return default

        # Internal implementation note: legacy behavior is preserved during modernization.
        return rows[0]


    @staticmethod
    def _activity_key(label: str) -> Optional[str]:
        for k, v in ACTIVITIES.items():
            if v == label:
                return k
        return None

    @staticmethod
    def _kind_key(label: str) -> Optional[str]:
        for k, v in KINDS.items():
            if v == label:
                return k
        return None
