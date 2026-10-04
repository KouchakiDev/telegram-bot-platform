from __future__ import annotations

from .codes_manager_context import *


class CodesManagerDataMixin:
    def _ask_photos_done(self, chat_id: int):
        """Legacy-compatible behavior preserved for this callable."""
        st = self._state.get(chat_id)
        if not st or "photos" not in st:
            return
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("بله", callback_data="photos_done"))
            msg = self.bot.send_message(chat_id, PHOTO_ASK_TEXT, reply_markup=kb)
            st["ask_msg_id"] = msg.message_id
            # Internal implementation note: legacy behavior is preserved during modernization.
            st.pop("timer", None)
        except Exception as exc:
            logger.exception("Ask photos done failed · %s", exc)
    def _on_photos_done(self, call: types.CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = call.message.chat.id
        st = self._state.get(chat_id)
        if not st or "photos" not in st:
            return self.bot.answer_callback_query(call.id)
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if st.get("timer"):
                st["timer"].cancel()
                st["timer"] = None
            if st.get("ask_msg_id"):
                try:
                    self.bot.delete_message(chat_id, st["ask_msg_id"])
                except Exception:
                    pass
            self.bot.answer_callback_query(call.id)
            self.bot.send_message(chat_id, "کپشن مدیا را بنویس (پیش‌فرض #{}):".format(st["code"]))
            self.bot.register_next_step_handler(call.message, self._finalize_add_with_photos)
        except Exception as exc:
            logger.exception("Photos done callback failed · %s", exc)
    def _finalize_add_with_photos(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            st = self._state.pop(chat_id, None)
            if not st:                                   # Internal implementation note: legacy behavior is preserved during modernization.
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            caption = (message.text or "").strip() or f"#{st['code']}"
            photos  = st["photos"]                       # Internal implementation note: legacy behavior is preserved during modernization.
            code    = st["code"]
            if st.get("edit_add"):
                old_row = self.db.select_dict("codes", "code = ?", (code,))[0]
                old_ids = json.loads(old_row.get("photos_msg_ids") or "[]")
                for mid in old_ids:
                    try:
                        self.bot.delete_message(PHOTOS_CHANNEL, mid)
                    except Exception:
                        logger.warning("Couldn't delete old photo msg=%s for code=%s", mid, code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            media         = [types.InputMediaPhoto(pid, has_spoiler=True) for pid in photos]
            media[0].caption = caption                  # Internal implementation note: legacy behavior is preserved during modernization.
            mg            = self.bot.send_media_group(PHOTOS_CHANNEL, media)
            msg_ids       = [m.message_id for m in mg]  # Internal implementation note: legacy behavior is preserved during modernization.
            caption_msg_id = msg_ids[0]                 # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            license_key = self._insert_code(
                code,
                st["dispatch_mode"],
                st["bio"],
                st["username"],
            )
            self.db.update(
                "codes",
                {
                    "photos"          : json.dumps(photos),
                    "photos_msg_ids"  : json.dumps(msg_ids),
                    "caption_msg_id"  : caption_msg_id,
                    "photos_caption"  : caption,
                },
                "code = ?",
                (code,),
            )
            logger.info("Add · code=%s saved with %d photos", code, len(photos))
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                f"✅ پرسنل افزوده شد.\n🔐 کد ورود:\n`{license_key}`",
                parse_mode="Markdown",
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.show_root_menu(message)#message)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Finalize add with photos failed · %s", exc)
            self.bot.reply_to(message, f"❌ خطا در ثبت نهایی عکس‌ها: {exc}")
    def _start_delete(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if self.is_back(message):
                return
            chat_id = message.chat.id
            self.user_state.setdefault(chat_id, {})["step"] = "delete"
            rows = self.db.select_dict("codes")
            if not rows:
                self.bot.send_message(chat_id, "هیچ کدی ثبت نشده است.")
                return
            markup = self._build_codes_keyboard(rows)
            markup.add(BACK_BTN)
            self.bot.send_message(chat_id, "🗑 کدی که می‌خوای حذف کنی رو انتخاب کن:", reply_markup=markup)
            self.bot.register_next_step_handler(message, self._delete_confirm)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Start delete failed · err=%s", exc)
    def _delete_confirm(self, message):
        try:
            chat_id = message.chat.id
            if self.is_back(message):
                return
            self.user_state.setdefault(chat_id, {})["step"] = "delete"
            code = message.text.strip()
            logger.info("Delete · chat=%s · code=%s", chat_id, code)
            if code not in self._list_codes():
                self.bot.send_message(chat_id, "❗ کد نامعتبره. دوباره انتخاب کن.")
                return self._start_delete(message)
            self._delete_code(code)
            self.bot.send_message(chat_id, f"✅ کد {code} حذف شد.")
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Delete failed · err=%s", exc)
            self.bot.send_message(chat_id, f"❌ خطا در حذف کد: {exc}")
        finally:
            self.show_root_menu(message)#message)
    def _start_edit(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if self.is_back(message):
                return
            chat_id = message.chat.id
            self.user_state.setdefault(chat_id, {})["step"] = "edit"
            rows = self.db.select_dict("codes")
            if not rows:
                self.bot.send_message(chat_id, "هیچ کدی ثبت نشده است.")
                return
            markup = self._build_codes_keyboard(rows)
            markup.add(BACK_BTN)
            self.bot.send_message(chat_id, "🔧 کدی که می‌خوای ویرایش کنی رو انتخاب کن:", reply_markup=markup)
            self.bot.register_next_step_handler(message, self._edit_choose_field)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Start edit failed · err=%s", exc)
    def _build_edit_photos_menu(self, file_ids: list[str]) -> tuple[str, types.InlineKeyboardMarkup]:
        """Legacy-compatible behavior preserved for this callable."""
        text = "برای تعویض هر عکس، روی دکمهٔ مربوطه کلیک کن."
        kb   = types.InlineKeyboardMarkup(row_width=3)
        for idx, fid in enumerate(file_ids, start=1):
            kb.add(types.InlineKeyboardButton(f"عکس {idx}", callback_data=f"edit_photo:{idx-1}"))
        return text, kb
    def _edit_choose_field(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            if self.is_back(message):
                return
            code = message.text.strip()
            if code not in self._list_codes():
                self.bot.send_message(chat_id, "⚠️ کد نامعتبره. لطفاً دوباره انتخاب کن.")
                return self._start_edit(message)
            row = self.db.select_dict("codes", "code = ?", (code,))
            if not row:
                self.bot.send_message(chat_id, "❌ کد نامعتبر است. از لیست انتخاب کنید.")
                return self._start_view(message)
            r = row[0]
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                f"📄 **بیو:** \n{r['bio'] or '–––'}\n",
                parse_mode="HTML"
            )
            details = (
                f"🔖 <b>کد:</b> <code>{escape(str(r['code']))}</code>\n"
                f"🚚 <b>نوع مراجعه:</b> {escape(r['dispatch_mode'])}\n"
                f"🔐 <b>کد ورود:</b> <code>{escape(r['license'] or '')}</code>\n"
                f"👤 <b>آی‌دی تلگرام ست شده؟</b> {'✅' if r['telegram_id'] else '❌'}\n"
                f"👤 <b>یوزرنیم تلگرام:</b> {escape(r['username'] or '–––')}\n"
                f"⚙️ <b>وضعیت فعال:</b> {'✅ فعال' if r['activity'] else '❌ غیرفعال'}"
            )
            self.bot.send_message(chat_id, details, parse_mode="HTML")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._state[chat_id] = {"edit_code": code}
            self.user_state[chat_id]["step"] = "edit"
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            markup.add("کد", "بیو", "نوع مراجعه", "یوزرنیم تلگرام", "کپشن عکس‌ها", "♻️ لغو کد ورود")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            file_ids = json.loads(r.get("photos") or "[]")
            buttons = []
            for idx, fid in enumerate(file_ids, start=1):
                btn_text = f"عکس {idx}"
                buttons.append(btn_text)
                try:
                    self.bot.send_photo(chat_id, fid, caption=btn_text)
                except Exception as exc:
                    logger.warning("Edit · photo preview failed idx=%s code=%s · err=%s", idx, code, exc)
                    self.bot.send_message(chat_id, f"{btn_text} – ❌ نتونستیم عکس رو بارگذاری کنیم.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            for i in range(0, len(buttons), 4):
                row = [types.KeyboardButton(text) for text in buttons[i:i + 4]]
                markup.row(*row)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add("افزودن عکس‌ها")
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add(BACK_BTN)
            self.bot.send_message(
                chat_id,
                "فیلدی که می‌خوای ویرایشش کنی رو انتخاب کن:",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self._edit_ask_new_value)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Edit choose field failed · err=%s", exc)
    def _edit_ask_new_value(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if self.is_back(message):
                return
            chat_id = message.chat.id
            selected = (message.text or "").strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            if selected.startswith("عکس "):
                try:
                    idx = int(selected.split()[1]) - 1  # Internal implementation note: legacy behavior is preserved during modernization.
                except (ValueError, IndexError):
                    self.bot.send_message(chat_id, "❗ شماره عکس نامعتبر است.")
                    return self.bot.register_next_step_handler(message, self._edit_ask_new_value)
                code = self._state[chat_id]["edit_code"]
                file_ids = json.loads(
                    self.db.select_dict("codes", "code = ?", (code,))[0].get("photos") or "[]"
                )
                if idx >= len(file_ids):
                    self.bot.send_message(chat_id, "❗ این شماره عکس وجود ندارد.")
                    return self.bot.register_next_step_handler(message, self._edit_ask_new_value)
                # Internal implementation note: legacy behavior is preserved during modernization.
                self._state[chat_id].update(
                    replace_photo_idx=idx,
                    replace_photo_code=code,
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                kb.add("❌ حذف عکس")
                kb.add(BACK_BTN)
                self.bot.send_message(
                    chat_id,
                    "📥 عکسِ جدید را ارسال کن یا «❌ حذف عکس» را بزن:",
                    reply_markup=kb,
                )
                self.bot.register_next_step_handler(message, self._handle_replace_photo)
                return
    # Internal implementation note: legacy behavior is preserved during modernization.
             # Internal implementation note: legacy behavior is preserved during modernization.
            if selected == "افزودن عکس‌ها":
    # Internal implementation note: legacy behavior is preserved during modernization.
                code = self._state[chat_id]["edit_code"]
                row  = self.db.select_dict("codes", "code = ?", (code,))[0]
                # Internal implementation note: legacy behavior is preserved during modernization.
                existing_photos = json.loads(row.get("photos") or "[]")
                st = self._state[chat_id]
                st.update({
                    "code":          code,
                    "dispatch_mode": row["dispatch_mode"],
                    "bio":           row["bio"] or "",
                    "username":      row["username"],    # Internal implementation note: legacy behavior is preserved during modernization.
                    "photos":        existing_photos,    # Internal implementation note: legacy behavior is preserved during modernization.
                    "edit_add":      True                # Internal implementation note: legacy behavior is preserved during modernization.
                })
                # Internal implementation note: legacy behavior is preserved during modernization.
                st.pop("ask_msg_id", None)
                if t := st.pop("timer", None):
                    t.cancel()
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(
                    chat_id,
                    "لطفاً تمامی عکس‌های پرسنل را ارسال کنید.\n"
                    "عکس‌های جدید به فهرست قبلی اضافه می‌شوند.",
                    reply_markup=types.ReplyKeyboardRemove()
                )
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            field_map = {
                "کد": "code",
                "بیو": "bio",
                "نوع مراجعه": "dispatch_mode",
                "یوزرنیم تلگرام": "username",
                "کپشن عکس‌ها": "__photos_caption__",   # Internal implementation note: legacy behavior is preserved during modernization.
                "♻️ لغو کد ورود": "__revoke__",
            }
            if selected not in field_map:
                self.bot.send_message(chat_id, "❗ گزینه نامعتبره. فقط از بین دکمه‌ها انتخاب کن.")
                return self.bot.register_next_step_handler(message, self._edit_ask_new_value)
            field = field_map[selected]
            self._state[chat_id]["edit_field"] = field
            # Internal implementation note: legacy behavior is preserved during modernization.
            if field == "__revoke__":
                code = self._state[chat_id]["edit_code"]
                try:
                    new_license = self._revoke_license(code)
                    self.bot.send_message(
                        chat_id,
                        f"✅ کد ورود قبلی حذف و کد ورود جدید صادر شد:\n\n`{new_license}`",
                        parse_mode="Markdown",
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                except Exception as exc:
                    logger.exception("Revoke license failed · code=%s | err=%s", code, exc)
                    self.bot.send_message(chat_id, "❌ خطا در لغو کد ورود.")
                return self._start_edit(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if field == "dispatch_mode":
                markup.add("ارائه در محل مشتری", "مکان دار")
            if field == "username":
                markup.add(NO_USERNAME_BTN)
            markup.add(BACK_BTN)
            self.bot.send_message(chat_id, f"مقدار جدید برای «{selected}» رو وارد کن:", reply_markup=markup)
            self.bot.register_next_step_handler(message, self._save_new_value)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Edit ask new value failed · err=%s", exc)
    def _handle_replace_photo(self, message: types.Message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
                return
        chat_id = message.chat.id
        st      = self._state.get(chat_id, {})
        idx     = st.get("replace_photo_idx")
        code    = st.get("replace_photo_code")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if idx is None or code is None:
            return self.bot.send_message(chat_id, "❌ خطا: عملیات جایگزینی نامشخص است.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message.text and message.text.strip() == BACK_BTN:
            self._state.pop(chat_id, None)
            return self.show_root_menu(message)#chat_id, code)
        # Internal implementation note: legacy behavior is preserved during modernization.
        row = self.db.select_dict("codes", "code = ?", (code,))[0]
        photos         = json.loads(row.get("photos") or "[]")
        old_msg_ids    = json.loads(row.get("photos_msg_ids") or "[]")
        caption        = row.get("photos_caption") or f"#{code}"
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message.text and message.text.strip() == "❌ حذف عکس":
            # Internal implementation note: legacy behavior is preserved during modernization.
            if idx >= len(photos):
                return self.bot.send_message(chat_id, "❗ اندیس عکس خارج از محدوده است.")
            photos.pop(idx)
            # Internal implementation note: legacy behavior is preserved during modernization.
            for mid in old_msg_ids:
                try: self.bot.delete_message(PHOTOS_CHANNEL, mid)
                except Exception: pass
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not photos:
                self.db.update(
                    "codes",
                    {
                        "photos"          : None,
                        "photos_msg_ids"  : None,
                        "caption_msg_id"  : None,
                        "photos_caption"  : None,
                    },
                    "code = ?", (code,),
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                clean_bio = self._inject_photo_link(row["bio"], "")
                self._update_code(code, bio=clean_bio)
                self.bot.send_message(chat_id, "✅ عکس حذف شد. هیچ عکسی باقی نمانده است.")
                self._state.pop(chat_id, None)
                return self.show_root_menu(message)#chat_id, code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            media          = [types.InputMediaPhoto(fid, has_spoiler=True) for fid in photos]
            media[0].caption = caption
            mg              = self.bot.send_media_group(PHOTOS_CHANNEL, media)
            new_msg_ids     = [m.message_id for m in mg]
            caption_msg_id  = new_msg_ids[0]
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(
                "codes",
                {
                    "photos"          : json.dumps(photos),
                    "photos_msg_ids"  : json.dumps(new_msg_ids),
                    "caption_msg_id"  : caption_msg_id,
                },
                "code = ?", (code,),
            )
            self.bot.send_message(chat_id, "✅ عکس مورد نظر حذف و مجموعه به‌روزرسانی شد.")
            self._state.pop(chat_id, None)
            return self.show_root_menu(message)#chat_id, code)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not message.photo:
            self.bot.send_message(chat_id, "⚠️ لطفاً یک عکس بفرست یا «❌ حذف عکس» را بزن.")
            return self.bot.register_next_step_handler(message, self._handle_replace_photo)
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            # fwd     = self.bot.forward_message(STORAGE_CHANNEL, chat_id, message.message_id)
            # new_fid = fwd.photo[-1].file_id
            # Internal implementation note: legacy behavior is preserved during modernization.
            file_info   = self.bot.get_file(message.photo[-1].file_id)
            orig_bytes  = self.bot.download_file(file_info.file_path)
            wm_buf      = watermark_image(orig_bytes, WATERMARK_PATH)
            wm_buf.name = "photo.jpg"
            sent        = self.bot.send_photo(STORAGE_CHANNEL, wm_buf)
            new_fid     = sent.photo[-1].file_id
        except Exception as exc:
            logger.exception("Replace forward failed · %s", exc)
            return self.bot.send_message(chat_id, "❌ خطا در دریافت عکس جدید.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if idx >= len(photos):
            return self.bot.send_message(chat_id, "❗ اندیس عکس خارج از محدوده است.")
        photos[idx] = new_fid
        # Internal implementation note: legacy behavior is preserved during modernization.
        for mid in old_msg_ids:
            try: self.bot.delete_message(PHOTOS_CHANNEL, mid)
            except Exception: pass
        # Internal implementation note: legacy behavior is preserved during modernization.
        media          = [types.InputMediaPhoto(fid, has_spoiler=True) for fid in photos]
        media[0].caption = caption
        mg              = self.bot.send_media_group(PHOTOS_CHANNEL, media)
        new_msg_ids     = [m.message_id for m in mg]
        caption_msg_id  = new_msg_ids[0]
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update(
            "codes",
            {
                "photos"          : json.dumps(photos),
                "photos_msg_ids"  : json.dumps(new_msg_ids),
                "caption_msg_id"  : caption_msg_id,
            },
            "code = ?", (code,),
        )
        logger.info("Photo replaced · code=%s idx=%s", code, idx + 1)
        self.bot.send_message(chat_id, f"✅ عکس {idx + 1} جایگزین شد.")
        self._state.pop(chat_id, None)
        self.show_root_menu(message)#chat_id, code)
    def _ask_new_value(self, msg, code: str, field: str):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if self.is_back(msg):
                return
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if field == "dispatch_mode":
                markup.add("ارائه در محل مشتری", "مکان دار")
            markup.add(BACK_BTN)
            field_fa = {"code": "کد", "bio": "بیو", "dispatch_mode": "نوع مراجعه"}[field]
            self.bot.send_message(msg.chat.id, f"مقدار جدید برای «{field_fa}» را وارد کنید:", reply_markup=markup)
            self._state[msg.chat.id] = {"edit_code": code, "edit_field": field}
            self.bot.register_next_step_handler(msg, self._save_new_value)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Ask new value failed · err=%s", exc)
    def _save_new_value(self, message: types.Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if self.is_back(message):
                return
            chat_id = message.chat.id
            st      = self._state.pop(chat_id, {})
            code    = st.get("edit_code")           # Internal implementation note: legacy behavior is preserved during modernization.
            field   = st.get("edit_field")          # Internal implementation note: legacy behavior is preserved during modernization.
            if code is None or field is None:
                return self.bot.reply_to(message, "❌ خطای داخلی: دادهٔ ویرایش یافت نشد.")
            new_val_raw = (message.text or "").strip()
            logger.info(
                "Edit save · chat=%s · code=%s · field=%s · raw='%s'",
                chat_id, code, field, new_val_raw
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            if field == "code":
                if new_val_raw in self._list_codes():
                    self.bot.reply_to(message, "⚠️ این کد قبلاً ثبت شده است.")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    return self._ask_new_value(message, code, field)
            if field == "username":
                if new_val_raw == NO_USERNAME_BTN:
                    new_val = None
                else:
                    if not new_val_raw.startswith("@"):
                        new_val_raw = "@" + new_val_raw
                    if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}", new_val_raw):
                        self.bot.send_message(chat_id, "⚠️ یوزرنیم نامعتبر است.")
                        return self._ask_new_value(message, code, field)
                    new_val = new_val_raw
            else:
                new_val = new_val_raw
            # Internal implementation note: legacy behavior is preserved during modernization.
            if field == "__photos_caption__":
                row = self.db.select_dict("codes", "code = ?", (code,))[0]
                caption_msg_id  = int(row.get("caption_msg_id") or 0)
                photos_msg_ids  = json.loads(row.get("photos_msg_ids") or "[]")
                photos_file_ids = json.loads(row.get("photos") or "[]")
                new_caption     = new_val or f"#{code}"
                # Internal implementation note: legacy behavior is preserved during modernization.
                edited_ok = False
                if caption_msg_id:
                    try:
                        self.bot.edit_message_caption(
                            chat_id=PHOTOS_CHANNEL,
                            message_id=caption_msg_id,
                            caption=new_caption
                        )
                        edited_ok = True
                    except Exception:
                        edited_ok = False
                # Internal implementation note: legacy behavior is preserved during modernization.
                if not edited_ok:
                    for mid in photos_msg_ids:
                        try:
                            self.bot.delete_message(PHOTOS_CHANNEL, mid)
                        except Exception:
                            pass
                    media            = [types.InputMediaPhoto(fid, has_spoiler=True) for fid in photos_file_ids]
                    media[0].caption = new_caption
                    mg               = self.bot.send_media_group(PHOTOS_CHANNEL, media)
                    photos_msg_ids   = [m.message_id for m in mg]
                    caption_msg_id   = photos_msg_ids[0]
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.update(
                    "codes",
                    {
                        "photos_caption" : new_caption,
                        "photos_msg_ids" : json.dumps(photos_msg_ids),
                        "caption_msg_id" : caption_msg_id,
                    },
                    "code = ?", (code,)
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                link    = f"https://t.me/c/{str(PHOTOS_CHANNEL).lstrip('-100')}/{caption_msg_id}"
                new_bio = self._inject_photo_link(row.get("bio") or "", link)
                self._update_code(code, bio=new_bio)
                self.bot.reply_to(message, "✅ کپشن عکس‌ها به‌روزرسانی شد.")
                # Internal implementation note: legacy behavior is preserved during modernization.
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            if field == "code":
                row = self.db.select_dict("codes", "code = ?", (code,))[0]
                old_code = code           # Internal implementation note: legacy behavior is preserved during modernization.
                new_code = new_val_raw    # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                row["code"] = new_code
                self.db.delete("codes", "code = ?", (old_code,))
                self.db.insert("codes", row)
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.reply_to(message, "✅ کد با موفقیت به‌روزرسانی شد.")
                code = new_code           # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            if field not in {"__photos_caption__", "code"}:
                self._update_code(code, **{field: new_val})
                self.bot.reply_to(message, "✅ با موفقیت ویرایش شد.")
        except Exception as exc:           # pylint: disable=broad-except
            logger.exception("Save new value failed · err=%s", exc)
            self.bot.reply_to(message, f"❌ خطا: {exc}")
        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.show_root_menu(message)
