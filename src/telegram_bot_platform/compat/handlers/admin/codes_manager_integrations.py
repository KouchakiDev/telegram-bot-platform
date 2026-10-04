from __future__ import annotations

from .codes_manager_context import *


class CodesManagerIntegrationsMixin:
    def _revoke_license(self, code: str):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            new_license = self._generate_license()
            self._update_code(code, license=new_license, telegram_id=None)
            logger.info("License revoked · code=%s", code)
            return new_license
        except Exception as exc:
            logger.exception("Revoke license failed · err=%s", exc)
            raise
    def _start_activity(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return
            chat_id = message.chat.id
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state.setdefault(chat_id, {})["step"] = "activity"
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("codes")
            if not rows:
                self.bot.send_message(chat_id, "هیچ کدی موجود نیست.")
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = self._build_codes_keyboard(rows, show_activity_icon=True)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add("تایید", BACK_BTN, row_width=1)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                "کدی که می‌خوای وضعیتش رو تغییر بدی انتخاب کن:",
                reply_markup=markup,
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.register_next_step_handler(message, self._handle_activity_toggle)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Start activity failed · err=%s", exc)
    def _strip_hours_line(self, bio: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        return re.sub(_HOURS_LINE_RE, "", bio).strip()
    def _handle_activity_toggle(self, message):
        try:
            chat_id   = message.chat.id
            text      = (message.text or "").strip()
            prev_code = self._state.get(chat_id, {}).get("pending_code")  # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "تایید" and prev_code:
                self._state.pop(chat_id, None)
                self._activate_without_hours(chat_id, prev_code)
                return self._start_activity(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "تایید":
                self.bot.send_message(chat_id, "✅ تغییرات ذخیره شد.")
                return self.show_root_menu(message)#message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            m = re.match(r"^(✅|☑️)\s+(\d+)$", text)
            if not m:
                self.bot.send_message(chat_id, "❗ لطفاً فقط از دکمه‌ها استفاده کنید.")
                return self._start_activity(message)
            new_code = m.group(2)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if prev_code and prev_code != new_code:
                self._activate_without_hours(chat_id, prev_code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            row = self.db.select_dict("codes", "code = ?", (new_code,))
            if not row:
                self.bot.send_message(chat_id, "❗ کد یافت نشد.")
                return self._start_activity(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if row[0]["activity"]:
                self._remove_bio_from_channel(new_code)
                self.bot.send_message(chat_id, "🚫 پرسنل غیرفعال شد و از کانال حذف شد.")
                return self._start_activity(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._state[chat_id] = {"pending_code": new_code}
            self.bot.send_message(
                chat_id,
                "⏰ ساعت فعالیت پرسنل را وارد کنید (مثلاً «17 تا 24») یا «تایید» را بزنید:",
            )
            self.bot.register_next_step_handler(message, self._handle_activity_hours)
        except Exception as exc:
            logger.exception("Handle activity toggle failed · err=%s", exc)
    def _handle_activity_hours(self, message):
        try:
            chat_id = message.chat.id
            if self.is_back(message):
                return
            text        = (message.text or "").strip()
            pending_row = self._state.pop(chat_id, {})
            code        = pending_row.get("pending_code")
            if not code:                               # Internal implementation note: legacy behavior is preserved during modernization.
                return self._start_activity(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "تایید":
                self._activate_without_hours(chat_id, code)
                return self._start_activity(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            m = re.match(r"^(✅|☑️)\s+(\d+)$", text)
            if m:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self._activate_without_hours(chat_id, code)
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self._handle_activity_toggle(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            hours = text
            self._post_bio_to_channel(code, hours)    # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "✅ پرسنل فعال شد و بیو با ساعت در کانال منتشر گردید.")
            self._start_activity(message)
        except Exception as exc:
            logger.exception("Save activity hours failed · err=%s", exc)
            self.bot.send_message(chat_id, "❌ خطایی رخ داد.")
            self._start_activity(message)
    def _activate_without_hours(self, chat_id: int, code: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        row = self.db.select_dict("codes", "code = ?", (code,))
        if not row:
            self.bot.send_message(chat_id, "❗ کد یافت نشد.")
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._update_code(code, activity=True)
        # Internal implementation note: legacy behavior is preserved during modernization.
        bio_clean = self._strip_hours_line(row[0]["bio"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        msg = self.bot.send_message(
            chat_id=CHANNEL_ID,
            text=bio_clean,
            disable_web_page_preview=True,
            parse_mode="HTML"
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.db.upsert(
                table_name="bios",
                data={
                    "code":       code,
                    "message_id": msg.message_id,
                    "channel_id": CHANNEL_ID,
                },
                key="code",
                column_types={
                    "code":       "varchar(10) UNIQUE",
                    "message_id": "varchar(50)",
                    "channel_id": "varchar(50)",
                },
                unique_column="code",
            )
        except Exception as exc:
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.exception("Upsert bios failed · code=%s · err=%s", code, exc)
            try:
                self.bot.delete_message(CHANNEL_ID, msg.message_id)
            finally:
                self._update_code(code, activity=False)
            self.bot.send_message(chat_id, "❌ خطا در ذخیره‌سازی. عملیات لغو شد.")
            return
        self.bot.send_message(chat_id, "✅ پرسنل فعال شد و بیو بدون ساعت در کانال منتشر گردید.")
    def _set_meta(self, key: str, value: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        self.db.upsert(
            table_name="bot_meta",
            data={"key": key, "value": value},
            key="key",
            column_types={"key": "varchar(50) UNIQUE",
                          "value": "varchar(255)"},
            unique_column="key",
        )
    def _get_meta(self, key: str, *, default: Optional[str] = None) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            row = self.db.select_dict(
                table="bot_meta",
                condition="`key` = ?",     # Internal implementation note: legacy behavior is preserved during modernization.
                params=(key,),
            )
            return row[0]["value"] if row else default
        except Exception as exc:
            logger.error("get_meta failed · key=%s · err=%s", key, exc, exc_info=True)
            return default
    def _build_codes_inline_keyboard(self, rows: list[dict]) -> types.InlineKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        EMOJIS = ["😍", "🥰", "🤩", "🛎", "🧰", "⭐", "⭐", "🧰", "🧩", "✅", "✅", "🎯", "💼", "✨", "📌", "🛡️", "✨"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        active = [r for r in rows if r.get("activity")]
        # Internal implementation note: legacy behavior is preserved during modernization.
        active.sort(key=lambda r: int(r["code"]))
        kb = types.InlineKeyboardMarkup(row_width=3)
        btns = []
        for r in active:
            code = r["code"]
            # Internal implementation note: legacy behavior is preserved during modernization.
            num_emojis = random.randint(1, 2)
            chosen = random.choices(EMOJIS, k=num_emojis)
            emoji_str = "".join(chosen)
            btn = types.InlineKeyboardButton(
                text=f"کد {code} {emoji_str}",
                url=f"https://t.me/{CLIENT_BOT_ID}?start=code_{code}"
            )
            btns.append(btn)
        kb.add(*btns)
        logger.debug("Inline keyboard built · %s active codes", len(active))
        return kb
    def _delete_codes_keyboard(self) -> None:
        msg_id = self._get_meta("codes_kb_msg_id")
        if not msg_id:
            return
        try:
            self.bot.delete_message(CHANNEL_ID, int(msg_id))
            logger.debug("Old codes keyboard cleared · msg_id=%s", msg_id)
        except Exception as exc:
            logger.warning("Clear keyboard failed · msg_id=%s · err=%s", msg_id, exc)
        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._set_meta("codes_kb_msg_id", "")
    def _post_codes_keyboard(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            code_rows = self.db.select_dict("codes", "activity = 1")
            if not code_rows:
                logger.info("No active codes found · skipping keyboard post")
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                settings = self.db.select_dict("promo_settings", "id = ?", (1,))[0]
                if not bool(settings.get("inline_table_enabled")):
                    logger.debug("Inline codes table is disabled · skipping")
                    return
            except Exception as exc:
                logger.exception("Cannot read inline_table_enabled: %s", exc)
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            DEFAULT_PROMPTS = [
                "📞 همین الان زیر ۵ دقیقه یکی از گزینه‌های زیر رو انتخاب کن و سفارش بده!",
                "⏰ الان جون می‌ده؛ یکی از گزینه‌های زیر رو بردار قبل از پر شدن وقت‌شون!",
                "⚡️  عجله کن؛ یک گزینه را انتخاب کن و کار رو تموم کن!",
                "🚀 خدمت موردنظر رو بردار و امروز حالشو ببر!",
                "🎯 وقت طلاییه؛ یک خدمت رو انتخاب کن و خوش باش!",
                "🔥 الان داغه؛ یک خدمت حرفه‌ای سفارش بده!",
                "🌟 یک گزینهٔ حرفه‌ای را انتخاب کنید.",
                "💥 گزینه‌های فعال را همین حالا بررسی کنید.",
                "🌈 در چند دقیقه سفارش خود را ثبت کنید و شروع کنید.",
                "🎉 سریع سفارش خود را ثبت و کار را شروع کنید.",
                "⚡️ ظرفیت محدود است؛ سفارش خود را به‌موقع ثبت کنید.",
                "🥳 از خدمات ویژهٔ این مجموعه استفاده کنید."
            ]
            try:
                promo_rows = self.db.select_dict(
                    "promo_texts",
                    "activity = 'codes' AND kind = 'text' AND inline_enabled = 1"
                )
                prompts = [r["content"] for r in promo_rows]
            except Exception as exc:
                logger.exception("DB fetch codes prompts failed: %s", exc)
                prompts = []
            if not prompts:
                prompts = DEFAULT_PROMPTS
            msg_text = random.choice(prompts)
            logger.debug("Selected random prompt for keyboard: %s", msg_text)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = self._build_codes_inline_keyboard(code_rows)
            sent = self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=msg_text,
                reply_markup=markup
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._set_meta("codes_kb_msg_id", str(sent.message_id))
            logger.info("Codes keyboard posted · msg_id=%s", sent.message_id)
        except Exception as exc: 
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.exception("Failed to post codes keyboard: %s", exc)
    def _schedule_codes_keyboard_refresh(self, delay: int = 30) -> None:
        import threading
        self._delete_codes_keyboard()
        # Internal implementation note: legacy behavior is preserved during modernization.
        if self._kb_timer and self._kb_timer.is_alive():
            self._kb_timer.cancel()
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._kb_timer = threading.Timer(delay, self._post_codes_keyboard)
        self._kb_timer.start()
        logger.debug("Codes keyboard refresh scheduled in %ss", delay)
