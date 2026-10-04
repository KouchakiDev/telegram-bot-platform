from __future__ import annotations

from .codes_manager_context import *


class CodesManagerCoreMixin:
    def _on_new_photo(self, msg: types.Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = msg.chat.id
        st = self._state.get(chat_id)
        if not st or "photos" not in st:
            return
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # fwd = self.bot.forward_message(STORAGE_CHANNEL, chat_id, msg.message_id)
            # file_id = fwd.photo[-1].file_id
            # Internal implementation note: legacy behavior is preserved during modernization.
            file_info   = self.bot.get_file(msg.photo[-1].file_id)
            orig_bytes  = self.bot.download_file(file_info.file_path)
            wm_buf      = watermark_image(orig_bytes, WATERMARK_PATH)   # Internal implementation note: legacy behavior is preserved during modernization.
            wm_buf.name = "photo.jpg"                                   # Internal implementation note: legacy behavior is preserved during modernization.
            sent        = self.bot.send_photo(STORAGE_CHANNEL, wm_buf)
            file_id     = sent.photo[-1].file_id
            st["photos"].append(file_id)
            self.db.insert("photos", {"code": st["code"], "file_id": file_id})
            logger.debug("Photo stored · code=%s · total=%s", st["code"], len(st["photos"]))
            # Internal implementation note: legacy behavior is preserved during modernization.
            if t := st.pop("timer", None):
                t.cancel()
            if mid := st.pop("ask_msg_id", None):
                try:
                    self.bot.delete_message(chat_id, mid)
                except Exception:
                    pass
            # Internal implementation note: legacy behavior is preserved during modernization.
            t = threading.Timer(2, lambda: self._ask_photos_done(chat_id))
            st["timer"] = t
            t.start()
        except Exception as exc:
            logger.exception("New photo handler failed · %s", exc)
    def is_back(self, message) -> bool:  # Internal implementation note: legacy behavior is preserved during modernization.
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if not message or not getattr(message, "text", None):
                return False
            if message.text.startswith("/start"):
                self.start_callback(message)
                return True
            if message.text.strip() != BACK_BTN:
                return False  # Internal implementation note: legacy behavior is preserved during modernization.
            chat_id = message.chat.id
            current_step: str | None = self.user_state.get(chat_id, {}).get("step")
            logger.info("Back button pressed · chat=%s · step=%s", chat_id, current_step)
            text = message.text 
            if text and "start" in text:
                return self.start_callback(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            elif current_step == "root":
                target_handler = self.back_callback
                next_step = "root"  # Internal implementation note: legacy behavior is preserved during modernization.
            elif current_step == "start":
                target_handler = self.start_callback
                next_step = "start"
            else:  # Internal implementation note: legacy behavior is preserved during modernization.
                target_handler = self.show_root_menu
                next_step = "root"
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                target_handler(message)
            finally:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.user_state.setdefault(chat_id, {})["step"] = next_step
                logger.info(
                    "State updated · chat=%s · new_step=%s", chat_id, next_step
                )
            return True
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error while handling back · err=%s", exc)
            return False
    def _inject_hours_into_bio(self, bio: str, hours: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        clock_regex = re.compile(
            r'^\s*(?:[🕑⏰⌚🕰]\s*)?(?:فعال(?:یت)?|ساعت(?:‌ها| ها)?)(?=[\s:：])',
            re.IGNORECASE
        )
        lines = [ln for ln in bio.splitlines() if not clock_regex.match(ln.strip())]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not hours:
            return "\n".join(lines).strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        activity_line = f"🕑فعال: {hours}"
        # Internal implementation note: legacy behavior is preserved during modernization.
        insert_idx = None
        # Internal implementation note: legacy behavior is preserved during modernization.
        for i, ln in enumerate(lines):
            if "💵" in ln:
                insert_idx = i + 1
                break
        # Internal implementation note: legacy behavior is preserved during modernization.
        if insert_idx is None:
            for i, ln in enumerate(lines):
                if any(token in ln for token in ("👤", "👤", "📍")):
                    insert_idx = i + 1
                    break
        # Internal implementation note: legacy behavior is preserved during modernization.
        if insert_idx is None:
            insert_idx = len(lines) // 2
        # Internal implementation note: legacy behavior is preserved during modernization.
        lines.insert(insert_idx, activity_line)
        return "\n".join(lines).strip()
    def _inject_photo_link(self, bio: str, link: str | None) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        raw_lines = bio.splitlines()
        cleaned: list[str] = []
        skip_old_photo_block = False
        # Internal implementation note: legacy behavior is preserved during modernization.
        for ln in raw_lines:
            stripped = ln.strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            if stripped.startswith("🖼"):
                continue
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not skip_old_photo_block and (
                stripped.startswith("📸")
                or re.search(r'\b(تصاویر|عکس)\b', stripped)
            ):
                skip_old_photo_block = True
                continue
            # Internal implementation note: legacy behavior is preserved during modernization.
            if skip_old_photo_block:
                if stripped.startswith("http") or stripped == "":
                    continue          # Internal implementation note: legacy behavior is preserved during modernization.
                skip_old_photo_block = False  # Internal implementation note: legacy behavior is preserved during modernization.
            cleaned.append(ln)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not link:
            return "\n".join(cleaned).strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        new_photo_line = f'🖼 <a href="{link}">عکس\u200cها</a>'
        # Internal implementation note: legacy behavior is preserved during modernization.
        insert_idx = None
        # Internal implementation note: legacy behavior is preserved during modernization.
        hour_regex = re.compile(r'^(?:[🕑⏰⌚🕰]\s*)?.*?(فعال|ساعت)', re.IGNORECASE)
        for i, ln in enumerate(cleaned):
            if hour_regex.search(ln):
                insert_idx = i + 1
                break
        # Internal implementation note: legacy behavior is preserved during modernization.
        if insert_idx is None:
            for i, ln in enumerate(cleaned):
                if "💵" in ln:
                    insert_idx = i + 1
                    break
        # Internal implementation note: legacy behavior is preserved during modernization.
        if insert_idx is None:
            insert_idx = len(cleaned)
        cleaned.insert(insert_idx, new_photo_line)
        return "\n".join(cleaned).strip()
    def _post_bio_to_channel(self, code: str, hours: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        msg: Optional["telebot.types.Message"] = None
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("codes", "code = ?", (code,))
            if not rows:
                logger.error("[post_bio] Code=%s not found in table codes", code)
                return
            row          = rows[0]
            raw_bio      = row.get("bio") or ""
            formatted    = self._inject_hours_into_bio(raw_bio, hours)
            caption_id   = row.get("caption_msg_id")
            if caption_id:
                link      = f"https://t.me/c/{str(PHOTOS_CHANNEL).lstrip("-100")}/{caption_id}"
                formatted = self._inject_photo_link(formatted, link)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._update_code(code, bio=formatted, activity=True)
            logger.debug("[post_bio] Code=%s marked active=True, bio updated", code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            msg = self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=formatted,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            logger.info("[post_bio] Sent message_id=%s for code=%s", msg.message_id, code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.upsert(
                table_name="bios",
                data={
                    "code"       : code,
                    "message_id" : str(msg.message_id),
                    "channel_id" : str(CHANNEL_ID),
                },
                key="code",
                column_types={
                    "code"       : "varchar(10) UNIQUE",
                    "message_id" : "varchar(50)",
                    "channel_id" : "varchar(50)",
                },
                unique_column="code",
            )
            logger.info("[post_bio] Upsert completed for code=%s", code)
        # Internal implementation note: legacy behavior is preserved during modernization.
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("[post_bio] Failure for code=%s → %s", code, exc)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if msg:
                try:
                    self.bot.delete_message(chat_id=CHANNEL_ID, message_id=msg.message_id)
                    logger.warning("[post_bio] Deleted message_id=%s due to failure", msg.message_id)
                except Exception:
                    logger.exception("[post_bio] Could NOT delete message_id=%s after failure", msg.message_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self._update_code(code, activity=False)
                logger.info("[post_bio] Reverted activity flag for code=%s", code)
            except Exception:
                logger.exception("[post_bio] Could NOT revert activity flag for code=%s", code)
    def _remove_bio_from_channel(self, code: str) -> None:
        rows = self.db.select_dict("bios", "code = ?", (code,))
        if rows:
            ch_id, msg_id = rows[0]["channel_id"], rows[0]["message_id"]
            try:
                self.bot.delete_message(ch_id, msg_id)
            except Exception as exc:
                logger.warning("Delete message failed · code=%s · err=%s", code, exc)
            self.db.delete("bios", "code = ?", (code,))
        self._update_code(code, activity=False)
    def _start_view(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if self.is_back(message):
                return
            chat_id = message.chat.id
            self.user_state.setdefault(chat_id, {})["step"] = "view"
            codes = self.db.select_dict("codes")
            if not codes:
                self.bot.send_message(chat_id, "هیچ کدی ثبت نشده است.")
                return
            markup = self._build_codes_keyboard(codes)    
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(EXPORT_BTN)
            markup.add(BACK_BTN)
            self.bot.send_message(
                chat_id,
                "🔍 یک کد را انتخاب کنید تا جزئیات نمایش داده شود:",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self._view_handle_selection)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Start view failed · err=%s", exc)
    def _view_handle_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            if self.is_back(message):
                return
            self.user_state[chat_id]["step"] = "view"
            text = message.text.strip()
            logger.info("View selection · chat=%s · text=%s", chat_id, text)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == EXPORT_BTN:
                return self._export_excel(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            row = self.db.select_dict("codes", "code = ?", (text,))
            if not row:
                self.bot.send_message(chat_id, "❌ کد نامعتبر است. از لیست انتخاب کنید.")
                return self._start_view(message)
            r = row[0]
            self.bot.send_message(chat_id,  f"📄 **بیو:** {r['bio'] or '–––'}\n" , parse_mode="HTML")
            details = (
                f"🔖 <b>کد:</b> <code>{escape(str(r['code']))}</code>\n"
                f"🚚 <b>نوع مراجعه:</b> {escape(r['dispatch_mode'])}\n"
                f"🔐 <b>کد ورود:</b> <code>{escape(r['license']  or '')}</code>\n"
                f"👤 <b>آی‌دی تلگرام ست شده؟</b> {'✅' if r['telegram_id'] else '❌'}\n"
                f"👤 <b>یوزرنیم تلگرام:</b> {escape(r['username'] or '–––')}\n"
                f"⚙️ <b>وضعیت فعال:</b> {'✅ فعال' if r['activity'] else '❌ غیرفعال'}"
            )
            self.bot.send_message(chat_id, details, parse_mode="HTML")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._start_view(message)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("View handle selection failed · err=%s", exc)
    def _export_excel(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            data = self.db.select_dict("codes")
            if not data:
                self.bot.send_message(chat_id, "⚠️ دیتابیس خالی است.")
                return self._start_view(message)
            df = pd.DataFrame(data)
            buffer = BytesIO()
            buffer.name = "codes.xlsx"  # Internal implementation note: legacy behavior is preserved during modernization.
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            self.bot.send_document(chat_id, buffer)
            logger.info("Excel exported and sent · chat=%s", chat_id)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Excel export failed · err=%s", exc)
            self.bot.send_message(message.chat.id, "❌ خطا در تولید خروجی اکسل.")
        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._start_view(message)
    def show_root_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            markup.add(
                types.KeyboardButton("➕ افزودن"),
                types.KeyboardButton("📝 ویرایش"),
                types.KeyboardButton("🗑 حذف"),
                types.KeyboardButton(VIEW_BTN),  # Internal implementation note: legacy behavior is preserved during modernization.
                types.KeyboardButton("✅ تعیین فعالیت"),
            )
            markup.add(types.KeyboardButton(BACK_BTN))
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state[chat_id] = {"step": "root"}
            logger.info("Show root menu · chat=%s", chat_id)
            self.bot.send_message(chat_id, "🔹 عملیات کدها را انتخاب کنید:", reply_markup=markup)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.register_next_step_handler_by_chat_id(chat_id, self.handle_root_menu)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to show root menu · err=%s", exc)
    def _generate_license(self) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        return f"{secrets.randbelow(10**6):06d}"
