from __future__ import annotations

from .codes_manager_context import *


class CodesManagerFlowsMixin:
    def handle_root_menu(self, message):
        try:
            chat_id = message.chat.id
            text = message.text.strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state.setdefault(chat_id, {})["step"] = "root"
            logger.info("Root menu selection · chat=%s · text=%s", chat_id, text)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "➕ افزودن":
                return self._start_add(message)
            elif text == "📝 ویرایش":
                return self._start_edit(message)
            elif text == "🗑 حذف":
                return self._start_delete(message)
            elif text == "✅ تعیین فعالیت":
                return self._start_activity(message)
            elif text == VIEW_BTN:  # Internal implementation note: legacy behavior is preserved during modernization.
                return self._start_view(message)
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(chat_id, "❗ گزینه نامعتبر است.")
                return self.show_root_menu(message)#message)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error in handle_root_menu · err=%s", exc)
    def _insert_code(self, code: str, dispatch_mode: str, bio: str, username: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            license_key = self._generate_license()
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.upsert(
                table_name="codes",
                data={
                    "code"           : int(code),
                    "dispatch_mode"  : dispatch_mode,
                    "bio"            : bio,
                    "activity"       : False,
                    "license"        : license_key,
                    "username"       : username,
                    "telegram_id"    : None,
                    "photos"         : None,
                    "photos_msg_ids" : None,
                    "caption_msg_id" : None,
                    "photos_caption" : f"#{code}",
                },
                key="code",
                column_types={
                    "code"            : "SMALLINT UNSIGNED UNIQUE",
                    "dispatch_mode"   : "VARCHAR(50)",
                    "bio"             : "TEXT",
                    "license"         : "TEXT",
                    "telegram_id"     : "VARCHAR(50)",
                    "username"        : "VARCHAR(100)",
                    "photos"          : "JSON",
                    "photos_msg_ids"  : "JSON",
                    "caption_msg_id"  : "TEXT",
                    "photos_caption"  : "TEXT",
                },
                unique_column="code"
            )
            try:
                self.db.execute_query("ALTER TABLE codes MODIFY COLUMN code SMALLINT UNSIGNED UNIQUE NOT NULL")
            except Exception as exc:
                logger.warning("Could not alter code column type: %s", exc)
            logger.info("Inserted code=%s with license", code)
            return license_key
        except Exception as exc:
            logger.exception("DB insert failed · code=%s | err=%s", code, exc)
            raise  # Internal implementation note: legacy behavior is preserved during modernization.
    def _update_code(self, code: str, **fields) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update("codes", fields, "code = ?", (code,))
            logger.info("Updated code=%s · fields=%s", code, fields)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if "activity" in fields:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self._schedule_codes_keyboard_refresh()
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("DB update failed · err=%s", exc)
            raise
    def _delete_code(self, code: str) -> None:
        try:
            self.db.delete("codes", "code = ?", (code,))
            logger.info("Deleted code=%s", code)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("DB delete failed · err=%s", exc)
            raise
    def _list_codes(self) -> list[str]:
        try:
            rows = self.db.select_dict("codes")
            # Internal implementation note: legacy behavior is preserved during modernization.
            return [str(row["code"]) for row in rows]   # Internal implementation note: legacy behavior is preserved during modernization.
        except Exception as exc:
            logger.exception("DB list failed · err=%s", exc)
            return []
    def _build_codes_keyboard(
        self,
        rows: list[dict],
        *,
        show_activity_icon: bool = False,
    ) -> types.ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
        groups = (("ارائه در محل مشتری", "📦 ارائه در محل مشتری‌ها"), ("مکان دار", "🏠 مکان‌دارها"))
        for mode, header in groups:
            mode_rows = sorted(
                (r for r in rows if r["dispatch_mode"] == mode),
                key=lambda r: (-bool(r["activity"]), int(r["code"])),
            )
            if not mode_rows:
                continue  # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(header)  # Internal implementation note: legacy behavior is preserved during modernization.
            buttons: list[str] = []
            for r in mode_rows:
                if show_activity_icon:
                    icon = "✅" if r["activity"] else "☑️"
                    buttons.append(f"{icon} {r['code']}")
                else:
                    buttons.append(str(r["code"]))
            # Internal implementation note: legacy behavior is preserved during modernization.
            for i in range(0, len(buttons), 5):
                markup.add(*buttons[i : i + 5])
        return markup
    def _start_add(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state.setdefault(chat_id, {})["step"] = "add"
            self.bot.send_message(chat_id, "کد پرسنل را وارد کنید:")
            self.bot.register_next_step_handler(message, self._add_get_code)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Start add failed · err=%s", exc)
    def _add_get_code(self, message):
        try:
            chat_id = message.chat.id
            if self.is_back(message):
                return
            code = message.text.strip()
            self.user_state.setdefault(chat_id, {})["step"] = "add"
            logger.info("Add · chat=%s · code_input=%s", chat_id, code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not re.fullmatch(r"\d{3,}", code):
                self.bot.send_message(chat_id, "⚠️ کد نامعتبر است! حداقل سه رقم.")
                return self._start_add(message)
            if code in self._list_codes():
                self.bot.send_message(chat_id, "⚠️ این کد قبلاً ثبت شده.")
                return self._start_add(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._state[chat_id] = {"code": code}
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add("ارائه در محل مشتری", "مکان دار")
            markup.add(BACK_BTN)
            self.bot.send_message(chat_id, "نوع مراجعه را انتخاب کنید:", reply_markup=markup)
            self.bot.register_next_step_handler(message, self._add_get_dispatch_mode)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Add get code failed · err=%s", exc)
    def _add_get_dispatch_mode(self, message):
        try:
            chat_id = message.chat.id
            if self.is_back(message):
                return  # Internal implementation note: legacy behavior is preserved during modernization.
            text = message.text.strip()
            logger.info("Add · dispatch_mode_input=%s", text)
            if text not in ["ارائه در محل مشتری", "مکان دار"]:
                self.bot.send_message(chat_id, "❗ فقط بین گزینه‌های داده‌شده انتخاب کنید.")
                return self.bot.register_next_step_handler(message, self._add_get_dispatch_mode)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._state[chat_id]["dispatch_mode"] = text
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(BACK_BTN)
            self.bot.send_message(chat_id, "لطفاً بیو پرسنل را وارد کنید:", reply_markup=markup)
            self.bot.register_next_step_handler(message, self._add_get_bio)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Add get dispatch mode failed · err=%s", exc)
    def _add_get_bio(self, message):
        try:
            chat_id = message.chat.id
            bio = message.text.strip()
            self._state[chat_id]["bio"] = bio  # Internal implementation note: legacy behavior is preserved during modernization.
            st = self._state.get(chat_id, {})
            logger.info("Add · bio_input_len=%s", len(bio))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(NO_USERNAME_BTN)
            markup.add(BACK_BTN)
            self.bot.send_message(
            chat_id,
            "یوزرنیم تلگرام را وارد کنید (با @). اگر ندارد، دکمهٔ «🚫 ندارم» را بزنید:",
            reply_markup=markup,
            )
            self.bot.register_next_step_handler(message, self._add_get_username)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Add save failed · err=%s", exc)
            self.bot.reply_to(message, f"❌ خطا در افزودن: {exc}")
    def _add_get_username(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        try:
            chat_id = message.chat.id
            txt = (message.text or "").strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            if txt == NO_USERNAME_BTN:
                username = None
            else:
                if not txt.startswith("@"):
                    txt = "@" + txt
                if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}", txt):
                    self.bot.send_message(
                        chat_id,
                        "⚠️ یوزرنیم نامعتبر است. دوباره وارد کنید یا «🚫 ندارم» را بزنید."
                    )
                    return self.bot.register_next_step_handler(message, self._add_get_username)
                username = txt
            # Internal implementation note: legacy behavior is preserved during modernization.
            st = self._state.get(chat_id, {})
            st["username"] = username
            self._state[chat_id] = st
            logger.info("Add · username set for code=%s", st.get("code"))
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add("بله", "خیر")
            markup.add(BACK_BTN)
            self.bot.send_message(
                chat_id,
                "آیا این کد عکس دارد؟",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self._add_has_photos)
        except Exception as exc:
            logger.exception("Add get username failed · err=%s", exc)
            self.bot.reply_to(message, f"❌ خطا در دریافت یوزرنیم: {exc}")
    def _add_has_photos(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            txt = (message.text or "").strip()
            if self.is_back(message):
                return
            if txt not in ("بله", "خیر"):
                self.bot.send_message(chat_id, "فقط دکمهٔ «بله» یا «خیر» را بزن دوست عزیز.")
                return self.bot.register_next_step_handler(message, self._add_has_photos)
            st = self._state.get(chat_id, {})
            code       = st.get("code")
            bio        = st.get("bio")
            username   = st.get("username")
            disp_mode  = st.get("dispatch_mode")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)   # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(BACK_BTN)     
            # Internal implementation note: legacy behavior is preserved during modernization.
            if txt == "خیر":
                license_key = self._insert_code(code, disp_mode, bio, username)
                logger.info("Add · code=%s saved (no photos)", code)
                self.bot.send_message(
                    chat_id,
                    f"✅ پرسنل افزوده شد.\n\n🔐 کد ورود:\n`{license_key}`",
                    parse_mode="Markdown",
                    reply_markup= markup
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                self._state.pop(chat_id, None)
                return self.show_root_menu(message)#message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.info("Add · collecting photos for code=%s", code)
            st["photos"] = []           # Internal implementation note: legacy behavior is preserved during modernization.
            self._state[chat_id] = st
            self.bot.send_message(chat_id,
                                  "لطفاً تمامی عکس‌های پرسنل را ارسال کنید.",
                                  reply_markup=markup)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
        except Exception as exc:
            logger.exception("Add has photos failed · err=%s", exc)
            self.bot.reply_to(message, f"❌ خطا در پردازش عکس‌ها: {exc}")
