from __future__ import annotations
"""client_manager.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Admin‑side *ClientManager* handler for Telegram bots powered by **pyTelegramBotAPI**.

Features implemented
--------------------
1. **start_menu()** – main GUI with two single‑row actions (block‑all / unblock‑all) followed by a paged 3‑column list of clients.
2. **show_all_clients()** – utility method used by *start_menu* (and elsewhere) that fetches every row from *clients* and renders buttons.
3. **search_client()** – smart search accepting username/ID/full‑name or a forwarded message; if exactly one match ⇒ jumps straight to **show_client_details**.
4. **show_client_details()** – pretty print of *all* DB columns & dynamic inline button (*block* / *unblock*).
5. **toggle_block()** – flips *status* between ``blocked`` / ``approved``, edits inline‑keyboard in‑place **and** notifies the target user.

Implementation notes
-------------------
* **Dependency Injection** – *bot* & *db* objects are injected through ``__init__`` (same pattern as other handlers in the code‑base)
* All user‑facing strings are Persian (matching the rest of the project) while logs stay English.
* Universal "❌ Cancel" + */start* escape hatches work in every stage.
* Every public method includes a full doctring; private helpers are prefixed with ``_``.
* The handler auto‑registers *message* **and** *callback_query* listeners on construction – no need to fiddle with manual wiring.
"""

from typing import List, Dict, Callable, Any
import telebot
from telebot.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from typing import List, Dict, Callable, Any, Set
# Import shared utilities/constants from the project -------------------------
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger  # type: ignore
from telegram_bot_platform.compat.database.database_manager import DatabaseManager  # type: ignore
from telegram_bot_platform.compat.config.settings import BUTTONS, MESSAGES , field_labels # Internal implementation note: legacy behavior is preserved during modernization.
BACK_BTN = "❌ Cancel"

class ClientManager:
    """Legacy-compatible behavior preserved for this callable."""

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def __init__(
        self,
        bot: telebot.TeleBot,
        db: DatabaseManager,
        back_to_main_cb: Callable[[Message], Any],
        back_to_previous_cb: Callable[[Message], Any],
    ) -> None:
        self.bot = bot
        self.db = db
        self.back_to_main = back_to_main_cb
        self.back_to_previous = back_to_previous_cb
        self.log = CustomLogger("ClientManager")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._client_index: Dict[int, Dict[str, Any]] = {}
        self._active_sessions: Set[int] = set()  # Internal implementation note: legacy behavior is preserved during modernization.

        self._register_handlers()

    # --- - - - ---------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # --- - - - ---------------------------------------------------------------
    def _register_handlers(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        CANCEL = BUTTONS.get("CANCEL", "❌ Cancel")
        FILTER_ACTIVE = BUTTONS.get("FILTER_ACTIVE", "کاربران فعال")
        FILTER_BLOCKED = BUTTONS.get("FILTER_BLOCKED", "کاربران مسدود شده")
        BULK_BLOCK = BUTTONS.get("BLOCK_ALL", "🚫 مسدود کردن همه")
        BULK_UNBLOCK = BUTTONS.get("UNBLOCK_ALL", "✅ رفع مسدودیت همه")

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(commands=["start"])
        def _cmd_start(m: Message):
            self._active_sessions.discard(m.chat.id)
            self.back_to_main(m)

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(func=lambda m: m.text == "بازگشت")
        def _btn_cancel(m: Message):
            self._active_sessions.discard(m.chat.id)
            self.back_to_previous(m)

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(func=lambda m: m.chat.id in self._active_sessions and m.text == BULK_BLOCK)
        def _bulk_block(m: Message):
            self._bulk_toggle(block=True, message=m)

        @self.bot.message_handler(func=lambda m: m.chat.id in self._active_sessions and m.text == BULK_UNBLOCK)
        def _bulk_unblock(m: Message):
            self._bulk_toggle(block=False, message=m)

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(func=lambda m: m.chat.id in self._active_sessions and m.text == FILTER_ACTIVE)
        def _filter_active(m: Message):
            self._show_filtered("approved", m)

        @self.bot.message_handler(func=lambda m: m.chat.id in self._active_sessions and m.text == FILTER_BLOCKED)
        def _filter_blocked(m: Message):
            self._show_filtered("blocked", m)

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(func=lambda m: m.chat.id in self._active_sessions and " – " in (m.text or ""))
        def _client_selected(m: Message):
            try:
                key_part = (m.text or "").split(" – ")[0].lstrip("@")
                if not key_part:
                    return self.bot.reply_to(m, "کاربر یافت نشد.")
        
                tg_id = None
                if key_part.isdigit():
                    num = int(key_part)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    rows = self.db.select_dict("clients", "telegram_id = ?", (num,))
                    if rows:
                        tg_id = num
                    else:
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        rows = self.db.select_dict("clients", "id = ?", (num,))
                        if rows:
                            tg_id = int(rows[0]["telegram_id"])
                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    rows = self.db.select_dict("clients", "username = ?", (key_part,))
                    if rows:
                        tg_id = int(rows[0]["telegram_id"])
        
                if not tg_id:
                    return self.bot.reply_to(m, "❌ کاربر پیدا نشد.")
        
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.show_client_details(tg_id, reply_to=m)
        
            except Exception as exc:
                self.log.exception("[SELECT_CLIENT] failed: %s", exc)
                self.bot.reply_to(m, "❌ خطا در پردازش انتخاب.")


        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(func=lambda m: m.chat.id in self._active_sessions and m.content_type == "text")
        def _search_router(m: Message):
            if m.chat.id not in self._active_sessions:
                return  # Internal implementation note: legacy behavior is preserved during modernization.
            txt = m.text or ""
            if txt.startswith("/") or txt in (CANCEL, BULK_BLOCK, BULK_UNBLOCK, FILTER_ACTIVE, FILTER_BLOCKED) or " – " in txt:
                return
            self.search_client(m)

        # callback toggle
        @self.bot.callback_query_handler(func=lambda cq: cq.data.startswith("toggle_"))
        def _callback_toggle(cq: CallbackQuery):
            _, raw = cq.data.split("_", 1)
            self.toggle_block(int(raw), cq) 
                  
    def _show_filtered(self, status: str, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(
            "clients",
            "status = ?",
            (status,),
        )

        rows = sorted(rows, key=lambda row: row.get("last_updated") or "", reverse=True)
        if not rows:
            text = "❌ کاربری با این وضعیت یافت نشد."
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("بازگشت"))
            self.bot.send_message(chat_id, text, reply_markup=markup)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons: List[KeyboardButton] = []
        for r in rows:
            label = (
                f"@{r['username']} – {r['name']}"
                if r.get("username")
                else f"{r['id']} – {r['name']}"
            )
            buttons.append(KeyboardButton(label))

        
        markup.add(*buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.row(
            KeyboardButton("بازگشت"),
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        header = "📋 مشتریان "
        header += "مسدود شده" if status == "blocked" else "فعال"
        self.bot.send_message(chat_id, header, reply_markup=markup)
        
    def convert_to_shamsi(self, date_str: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        def normalize_to_datetime_str(date_input: any) -> str:
            """Legacy-compatible behavior preserved for this callable."""
            from datetime import datetime

            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(date_input, datetime):
                    return date_input.strftime('%Y-%m-%d %H:%M:%S')

                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(date_input, (float, int)):
                    dt = datetime.fromtimestamp(date_input)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')

                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(date_input, str):
                    date_str = date_input.replace("⏰", "").strip()
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    return date_str.replace("/", "-")

                # Internal implementation note: legacy behavior is preserved during modernization.
                return str(date_input)

            except Exception:
                return str(date_input)  # Internal implementation note: legacy behavior is preserved during modernization.

        from datetime import datetime
        from persiantools.jdatetime import JalaliDateTime
        
        if not date_str:
            return "نامشخص"
        try :
            date_str = normalize_to_datetime_str(date_str)
        except:
            return "نامشخص"
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            date_str = date_str.replace("⏰", "").strip()

            # Internal implementation note: legacy behavior is preserved during modernization.
            if '.' in date_str:
                date_str = date_str.split('.')[0]

            # Internal implementation note: legacy behavior is preserved during modernization.
            normalized = date_str.replace("/", "-")

            # Internal implementation note: legacy behavior is preserved during modernization.
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(normalized, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_str  # Internal implementation note: legacy behavior is preserved during modernization.

            jdt = JalaliDateTime(dt)

            formatted = f"\n  📅 {jdt.strftime('%Y/%m/%d')} تاریخ\n  " \
                f"🗓 {jdt.strftime('%A')} {jdt.day} {jdt.strftime('%B')}\n  " \
                f"⏰ ساعت : {jdt.strftime('%H:%M')}"

            # Internal implementation note: legacy behavior is preserved during modernization.
            days = {
                'Shanbeh': 'شنبه', 'Yekshanbeh': 'یک‌شنبه', 'Doshanbeh': 'دوشنبه',
                'Seshanbeh': 'سه‌شنبه', 'Chaharshanbeh': 'چهارشنبه',
                'Panjshanbeh': 'پنج‌شنبه', 'Jomeh': 'جمعه'
            }
            months = {
                'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
                'Tir': 'تیر', 'Mordad': 'عضواد', 'Shahrivar': 'شهریور',
                'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
                'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند'
            }

            for en, fa in days.items():
                formatted = formatted.replace(en, fa)
            for en, fa in months.items():
                formatted = formatted.replace(en, fa)

            return formatted

        except Exception:
            return date_str
    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def start_menu(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            self._active_sessions.add(chat_id)
            markup =  self._build_client_buttons()
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.row(
                KeyboardButton("🚫 مسدود کردن همه"),
                KeyboardButton("✅ رفع مسدودیت همه"),
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
           

            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(KeyboardButton("بازگشت"))

            self.bot.send_message(chat_id, "لیست مشتریان 👇", reply_markup=markup)
        except Exception as exc:
            self.log.exception("[START_MENU] failed: %s", exc)
            self.bot.reply_to(message, "❌ خطا در بارگذاری منو.")

    # ------------------------------------------------------------------
    # 2) Data->UI helpers
    # ------------------------------------------------------------------
    def _build_client_buttons(self, *, chunk_size: int = 3) -> ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict("clients")
        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = sorted(rows, key=lambda row: row.get("last_updated") or "", reverse=True)

        # Internal implementation note: legacy behavior is preserved during modernization.
        active_rows = [r for r in rows if r.get("status") != "blocked"]
        blocked_rows = [r for r in rows if r.get("status") == "blocked"]

        # Internal implementation note: legacy behavior is preserved during modernization.
        def _label(r: Dict[str, Any]) -> str:
            return (
                f"@{r['username']} – {r['name']}"
                if r.get('username')
                else f"{r['id']} – {r['name']}"
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=chunk_size)
        # Internal implementation note: legacy behavior is preserved during modernization.
        groups = [
            (active_rows, "کاربران فعال"),
            (blocked_rows, "کاربران مسدود شده"),
        ]

        for bucket, header in groups:
            if not bucket:
                continue
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.row(KeyboardButton(header))
            # Internal implementation note: legacy behavior is preserved during modernization.
            for i in range(0, len(bucket), chunk_size):
                chunk = bucket[i : i + chunk_size]
                buttons = [KeyboardButton(_label(r)) for r in chunk]
                markup.row(*buttons)

        return markup



    # ------------------------------------------------------------------
    # 3) show_all_clients utility (exposed publicly)
    # ------------------------------------------------------------------
    def show_all_clients(self, message: Message | None = None) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if message is None:
            raise ValueError("show_all_clients requires a Message context to reply to.")
        self.start_menu(message)  # Internal implementation note: legacy behavior is preserved during modernization.

    # ------------------------------------------------------------------
    # 4) Smart search
    # ------------------------------------------------------------------
    def search_client(self, message: Message) -> None:
        """Search *clients* table by @username, full name, Telegram ID or internal ID."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if message.forward_from:
                query = str(message.forward_from.id)
            else:
                query = (message.text or "").strip()

            rows: List[Dict[str, Any]] = []

            # Internal implementation note: legacy behavior is preserved during modernization.
            if query.startswith("@"):
                username = query[1:]
                rows = self.db.select_dict(
                    "clients",
                    "username = ?",
                    (username,),
                )

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif query.isdigit():
                num = int(query)
                # Internal implementation note: legacy behavior is preserved during modernization.
                rows = self.db.select_dict(
                    "clients",
                    "id = ?",
                    (num,),
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                if not rows:
                    rows = self.db.select_dict(
                        "clients",
                        "telegram_id = ?",
                        (num,),
                    )

            # Internal implementation note: legacy behavior is preserved during modernization.
            else:
                tokens = [t for t in query.split() if t]
                pattern = "%" + "%".join(tokens) + "%"
                rows = self.db.select_dict(
                    "clients",
                    "name LIKE ?",
                    (pattern,),
                )

            # Internal implementation note: legacy behavior is preserved during modernization.
            if not rows:
                return self.bot.reply_to(message, "❌ مشتری‌ای یافت نشد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            if len(rows) == 1:
                client = rows[0]
                self.show_client_details(client["telegram_id"], reply_to=message)
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            chat_id = message.chat.id
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            for i, r in enumerate(rows):
                label = (
                    f"@{r['username']} – {r['name']}" if r.get("username")
                    else f"{r['telegram_id']} – {r['name']}"
                )
                if i % 3 == 0:
                    markup.row(KeyboardButton(label))
                else:
                    markup.add(KeyboardButton(label))
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(KeyboardButton(BUTTONS.get("CANCEL", "بازگشت")))
            self.bot.send_message(chat_id, "نتایج جستجو 🔍", reply_markup=markup)

        except Exception as exc:
            self.log.exception("[SEARCH] failed: %s", exc)
            self.bot.reply_to(message, "⚠️ خطا در جستجو.")


   # ------------------------------------------------------------------
    # 5) Detail view
    # ------------------------------------------------------------------
    def show_client_details(self, tg_id: int, *, reply_to: Message | None = None) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("clients", "telegram_id = ?", (tg_id,))
            if not rows:
                if reply_to:
                    self.bot.reply_to(reply_to, "❌ کاربر پیدا نشد.")
                return
            row = rows[0]

            # Internal implementation note: legacy behavior is preserved during modernization.
            lines: list[str] = []
            for key, val in row.items():
                if key in ("created_at", "last_updated"):
                    continue
                label = field_labels.get(key, key)
                value = val or "—"
                lines.append(f"<b>{label}</b> : {value}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            created = row.get("created_at")
            updated = row.get("last_updated")
            ordered = row.get("last_order")
             
            if created:
                lines.append(self.convert_to_shamsi(created))
            if updated:
                lines.append(self.convert_to_shamsi(updated))
            if ordered:
                lines.append(self.convert_to_shamsi(ordered))
                

            caption = "\n".join(lines)

            # Internal implementation note: legacy behavior is preserved during modernization.
            status = row.get("status", "approved")
            btn_text = "✅ آنبلاک" if status == "blocked" else "🚫 مسدود"
            toggle_cb = f"toggle_{tg_id}"
            inline_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton(btn_text, callback_data=toggle_cb)
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            dest_chat = reply_to.chat.id if reply_to else tg_id
            self.bot.send_message(dest_chat, caption, reply_markup=inline_kb, parse_mode="HTML")

        except Exception as exc:
            self.log.exception("[DETAILS] failed: %s", exc)
            if reply_to:
                self.bot.reply_to(reply_to, "⚠️ خطا در نمایش جزئیات مشتری.")


    # ------------------------------------------------------------------
    # 6) Toggle helpers
    # ------------------------------------------------------------------
    def toggle_block(self, tg_id: int, cq: CallbackQuery | None = None) -> None:
        """Switch ``status`` between *blocked* / *approved* + inform user."""
        try:
            row = self.db.select_dict("clients", "telegram_id = ?", (tg_id,))
            if not row:
                return self.bot.answer_callback_query(cq.id, "نامعتبر.") if cq else None
            row = row[0]
            new_status = "approved" if row.get("status") == "blocked" else "blocked"
            self.db.update("clients", {"status": new_status}, "telegram_id = ?", (tg_id,))

            # Edit inline button text
            btn_text = "✅ آنبلاک" if new_status == "blocked" else "🚫 مسدود"
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton(btn_text, callback_data=f"toggle_{tg_id}")
            )
            if cq:
                self.bot.edit_message_reply_markup(
                    chat_id=cq.message.chat.id,
                    message_id=cq.message.message_id,
                    reply_markup=markup,
                )
                self.bot.answer_callback_query(cq.id, "بروزرسانی شد ✅")
            # Notify client directly (if we are not already in their chat)
            notice = (
                "❌ حسابت توسط ادمین مسدود شد." if new_status == "blocked" else "✅ حسابت آزاد شد، می‌توانی ادامه دهی."
            )
            try:
                self.bot.send_message(tg_id, notice)
            except Exception:
                # Internal implementation note: legacy behavior is preserved during modernization.
                pass
        except Exception as exc:
            self.log.exception("[TOGGLE] failed: %s", exc)
            if cq:
                self.bot.answer_callback_query(cq.id, "⚠️ خطا")

    # ------------------------------------------------------------------
    # 7) Bulk helpers
    # ------------------------------------------------------------------
    def _bulk_toggle(self, *, block: bool, message: Message) -> None:
        """Mass (un)block every client in the DB then reload menu."""
        try:
            new_status = "blocked" if block else "approved"
            self.db.execute_query(
                "UPDATE clients SET status = ?",
                (new_status,)
            )
            self.bot.reply_to(
                message,
                "همه‌ی کاربران «مسدود» شدند." if block else "همه‌ی کاربران آزاد شدند.",
            )
            self.start_menu(message)
        except Exception as exc:
            self.log.exception("[BULK_TOGGLE] failed: %s", exc)
            self.bot.reply_to(message, "⚠️ خطا در عملیات گروهی.")

