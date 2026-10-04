from __future__ import annotations

from .client_runner_context import *


class ClientRunnerRequestFlowMixin:
    @step_handler("choose_dispatch_mode")
    def handle_choose_dispatch_mode(                               # noqa: D401
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        dispatch_options = ("ارائه در محل مشتری", "مکان دار")
        msg_txt = (message.text or "").strip() if message else ""
        # ask-phase
        if not msg_txt:
            kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            kb.add(*dispatch_options)
            text = (
                "✨ خوش اومدی به Telegram Platform 📅\n"
                "لطفاً مشخص کن نوع خدمات رو چطور می‌خوای 👇🏻\n\n"
                "📌 ارائه در محل مشتری یعنی کد میاد سمت شما\n"
                "📌 مکان‌دار یعنی شما میری پیش کد\n\n"
                "یکی از گزینه‌های زیر رو انتخاب کن ❤️‍🔥"
            )
            self.bot.send_message(
                int(user_id),text,
                reply_markup=kb,
            )
            self.log.debug("[choose_dispatch_mode][ASK] user=%s", user_id)
            return None
        # handle-phase
        if msg_txt in dispatch_options:
            st = self.engine._user_states[user_id]
    # Internal implementation note: legacy behavior is preserved during modernization.
            if "intro_msg_id" not in st and message.content_type == "text":
                st["intro_msg_id"] = message.message_id 
            self.engine._memory_persistence(user_id, "dispatch_mode", msg_txt)
            self.log.info("[choose_dispatch_mode] user=%s choice=%s", user_id, msg_txt)
            return msg_txt
        # invalid
        self.log.warning("[choose_dispatch_mode][INVALID] user=%s text=%s", user_id, msg_txt)
        self.bot.send_message(message.chat.id, "❗ فقط از دکمه‌های زیر استفاده کن.")
        return None
    @step_handler("select_staff_code")
    def handle_select_staff_code(                              # noqa: D401
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        dispatch_mode = self.engine._user_states[user_id].get("dispatch_mode")
        if not dispatch_mode:
            self.log.error("[select_staff_code] dispatch_mode missing for user=%s", user_id)
            self.engine.execute_prev(user_id, None)
            return None
        # fetch codes
        try:
            rows = self.db.select_dict(
                "codes", "dispatch_mode=? AND activity=1", (dispatch_mode,)
            )
            active_codes = [str(r["code"]) for r in rows]
        except Exception as exc:
            self.log.exception("[select_staff_code] DB error user=%s : %s", user_id, exc)
            self.bot.send_message(int(user_id), "❌ خطا در ارتباط با پایگاه‌داده. بعداً تلاش کن.")
            return None
        if not active_codes:
            self.log.info("[select_staff_code] no active codes user=%s mode=%s", user_id, dispatch_mode)
            self.bot.send_message(int(user_id), "⚠️ فعلاً کدی برای این نوع خدمات فعال نیست.")
            return None
        msg_txt = (message.text or "").strip() if message else ""
        # ask
        if not msg_txt:
            kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            kb.add(*active_codes)
            kb.add(BACK_BTN)
            text = (
                "🧚‍♀️ حالا لطفاً کد مورد نظرت رو انتخاب کن ⭐\n"
                "همه کدها تاییدشده، خوش‌برخورد و آماده‌ی هماهنگی هستن ✨\n\n"
                "هر کد که چشم‌تو گرفت رو بزن 😌👇🏻"
            )
            self.bot.send_message(
                int(user_id),text,
                reply_markup=kb,
            )
            self.log.debug("[select_staff_code][ASK] user=%s", user_id)
            return None
        # back
        if msg_txt == BACK_BTN:
            self.log.debug("[select_staff_code][BACK] user=%s", user_id)
            self.engine.execute_prev(user_id, None)
            return None
        # handle
        if msg_txt in active_codes:
            self.engine._memory_persistence(user_id, "staff_code", msg_txt)
            self.log.info("[select_staff_code] user=%s selected=%s", user_id, msg_txt)
            return msg_txt
        # invalid
        self.log.warning("[select_staff_code][INVALID] user=%s text=%s", user_id, msg_txt)
        self.bot.send_message(message.chat.id, "❗ لطفاً یکی از کدهای لیست را انتخاب کن.")
        return None
    @step_handler("confirm_staff_code")
    def handle_confirm_staff_code(                             # noqa: D401
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.log.debug("[confirm_staff_code] ENTER user=%s raw_msg=%s", user_id, message)
        # ------------------------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # # ------------------------------------------------------------------
        # chat_id = message.chat.id if message else int(user_id)
        # self.log.debug("[confirm_staff_code] chat_id=%s user=%s", chat_id, user_id)
        # ------------------------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # ------------------------------------------------------------------
        # code = self.engine._user_states[user_id].get("staff_code")
        code = self.engine._user_states[user_id].get("staff_code")
        self.log.debug("[confirm_staff_code] staff_code=%s user=%s", code, user_id)
        if not code:
            self.log.error("[confirm_staff_code] selected_code missing user=%s", user_id)
            self.engine.execute_prev(user_id, None)
            return None
        msg_txt = (message.text or "").strip() if message else ""
        # ------------------------------------------------------------------    
        # Internal implementation note: legacy behavior is preserved during modernization.
        # ------------------------------------------------------------------    
        # msg_txt = (message.text or "").strip() if message else ""
        # self.log.debug("[confirm_staff_code] msg_txt='%s' user=%s", msg_txt, user_id)
        # CONFIRM_VARIANTS = {
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # }
        # ------------------------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # ------------------------------------------------------------------
        if not msg_txt:
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.log.debug("[confirm_staff_code] DB select codes.code=%s", code)
                row = self.db.select_dict("codes", "code = ?", (code,))[0]
                bio        = row.get("bio") or "—"
                files_json = row.get("photos") or "[]"
                self.log.debug(
                    "[confirm_staff_code] DB ok · user=%s code=%s bio_len=%s", user_id, code, len(bio)
                )
            except Exception as exc:
                self.log.exception("[confirm_staff_code] DB error · user=%s code=%s err=%s", user_id, code, exc)
                bio, files_json = "—", "[]"
            # 4-B) Parse photos JSON
            try:
                photos: list[str] = json.loads(files_json)
                self.log.debug("[confirm_staff_code] photos_json parsed · count=%s user=%s", len(photos), user_id)
            except Exception as jerr:
                self.log.warning("[confirm_staff_code] photos_json invalid · user=%s err=%s", user_id, jerr)
                photos = []
            # Internal implementation note: legacy behavior is preserved during modernization.
            kb_confirm = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            kb_confirm.add(CONFIRM_BTN, OTHER_CODES_BTN)
            # Internal implementation note: legacy behavior is preserved during modernization.
            sent_media = False
            # Internal implementation note: legacy behavior is preserved during modernization.
            if photos:
                # Internal implementation note: legacy behavior is preserved during modernization.
                def _build_media(user_id: int, code: str,
                                 fids: list[str],
                                 caption_html: str) -> list[types.InputMediaPhoto]:
                    """Legacy-compatible behavior preserved for this callable."""
                    media: list[types.InputMediaPhoto] = []
                    for idx, fid in enumerate(fids):
                        try:
                            item = types.InputMediaPhoto(fid)
                            if idx == 0:
                                item.caption     = caption_html
                                item.parse_mode  = "HTML"
                            media.append(item)
                            self.log.debug(
                                "[confirm_staff_code] media_item OK · user=%s code=%s idx=%s",
                                user_id, code, idx
                            )
                        except Exception as ex:
                            self.log.warning(
                                "[confirm_staff_code] bad_media skipped · user=%s code=%s idx=%s err=%s",
                                user_id, code, idx, ex
                            )
                    self.log.info(
                        "[confirm_staff_code] build_media finished · user=%s code=%s valid=%s",
                        user_id, code, len(media)
                    )
                    return media
                # Internal implementation note: legacy behavior is preserved during modernization.
                fids          = photos             # Internal implementation note: legacy behavior is preserved during modernization.
                caption_html  = bio[:1024]         # Internal implementation note: legacy behavior is preserved during modernization.
                media         = _build_media(user_id, code, fids, caption_html)
                if media:
                    try:
                        self.bot.send_media_group(int(user_id), media)
                        sent_media = True
                        self.log.info("[confirm_staff_code] media_group sent (client bot) · user=%s code=%s", user_id, code)
                    except Exception as e1:
                        self.log.warning("[confirm_staff_code] media_group failed (client bot) · user=%s code=%s err=%s",
                                         user_id, code, e1)
                else:
                    self.log.error("[confirm_staff_code] no valid media built · user=%s code=%s", user_id, code)
                # Internal implementation note: legacy behavior is preserved during modernization.
                if not sent_media:
                    fallback_media: list[types.InputMediaPhoto] = []
                    for i, fid in enumerate(photos):
                        try:
                            f_info  = self.admin_bot.get_file(fid)
                            f_bytes = self.admin_bot.download_file(f_info.file_path)
                            bio_io         = io.BytesIO(f_bytes)
                            bio_io.name    = f"photo_{i}.jpg"
                            im             = types.InputMediaPhoto(bio_io)
                            if i == 0:
                                im.caption    = caption_html
                                im.parse_mode = "HTML"
                            fallback_media.append(im)
                            self.log.debug("[confirm_staff_code] admin_bot download OK idx=%s user=%s", i, user_id)
                        except Exception as e2:
                            self.log.warning(
                                "[confirm_staff_code] admin_bot download failed idx=%s user=%s err=%s",
                                i, user_id, e2
                            )
                    if fallback_media:
                        try:
                            self.bot.send_media_group(int(user_id), fallback_media)
                            sent_media = True
                            self.log.info("[confirm_staff_code] media_group sent (admin bytes) · user=%s code=%s", user_id, code)
                        except Exception as e3:
                            self.log.error("[confirm_staff_code] media_group failed (admin bytes) · user=%s code=%s err=%s",
                                           user_id, code, e3)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not sent_media:
                self.bot.send_message(int(user_id), bio, reply_markup=kb_confirm)
                self.log.debug("[confirm_staff_code] bio text sent (no media) · user=%s", user_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            text = (
                "✨ این کد همونه که مد نظرته؟ 😌💭\n"
                "اگه اوکی هست، بریم مرحله بعد\n"
                "اگه خواستی عوضش کنی، برگرد و یکی دیگه انتخاب کن 💅🏻⭐"
            )
            self.bot.send_message(int(user_id), text, reply_markup=kb_confirm)
            self.log.debug("[confirm_staff_code] ASK message sent · user=%s code=%s", user_id, code)
            return None     # Internal implementation note: legacy behavior is preserved during modernization.
        # ------------------------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # ------------------------------------------------------------------
        # handle
        if msg_txt == CONFIRM_BTN:
            self.log.info("[confirm_staff_code] user=%s confirmed code=%s", user_id, code)
            return code
        if msg_txt in (OTHER_CODES_BTN, BACK_BTN):
            self.log.debug("[confirm_staff_code][BACK] user=%s", user_id)
            self.engine.execute_prev(user_id, None)
            return None
        self.log.warning("[confirm_staff_code][INVALID] user=%s text=%s", user_id, msg_txt)
        self.bot.send_message(int(user_id), "❗ از دکمه‌های زیر استفاده کن.")
        return None
    @step_handler("enter_address")
    def handle_enter_address(
        self, user_id: str, message: Optional[types.Message]
    ) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        state         = self.engine._user_states.get(user_id, {})
        dispatch_mode = state.get("dispatch_mode")
        text          = (message.text or "").strip() if message else ""
        # Internal implementation note: legacy behavior is preserved during modernization.
        if dispatch_mode == "مکان دار":
            self.log.debug("[enter_address][SKIP] user=%s (mekan-dar)", user_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.engine._memory_persistence(user_id, "region", "")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.engine._skip_step(user_id, step_name="enter_address", reason="non-dispatch")
            # Internal implementation note: legacy behavior is preserved during modernization.
            return "SKIPPED"        # Internal implementation note: legacy behavior is preserved during modernization.
             # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not text:
            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(BACK_BTN)
            text = (
                "🚗 کدی که انتخاب کردی ارائه در محل مشتریه\n"
                "لطفاً آدرسی که می‌خوای کد بیاد اونجا رو برامون بنویس ✍🏻💌\n\n"
                "هرچی دقیق‌تر باشه، هماهنگی راحت‌تر انجام می‌شه 😇⭐"
            )
            self.bot.send_message(
                int(user_id),
                text,
                reply_markup=kb,
            )
            self.log.debug("[enter_address][ASK] user=%s", user_id)
            return None               # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == BACK_BTN:
            self.engine.execute_prev(user_id, None)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.engine._memory_persistence(user_id, "region", text)
        self.bot.send_message(message.chat.id, "✅ آدرس ثبت شد.")
        self.log.info("[enter_address] user=%s address=%s", user_id, text)
        return text                  # Internal implementation note: legacy behavior is preserved during modernization.
    @step_handler("select_reserve_time")
    def handle_select_reserve_time(                                 # noqa: D401
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        msg_txt = "" if message is None else (message.text or "").strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not msg_txt or msg_txt == CONFIRM_BTN:
            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(BACK_BTN)
            text = (
                "⏰ حالا لطفاً بگو چه ساعتی مد نظرت هست؟\n"
                "توجه: سفارش شما نیاز به ۱ ساعت زمان جهت هماهنگی با پرسنل دارد.\n"
                "نکته بعدی: اگر در ساعت درخواستی، کد انتخابی پذیرای شما نبود، مجدد نیاز به ثبت درخواست دارید.\n"
                "کدو برای چه زمانی می‌خوای رزرو کنیم؟ ⭐\n\n"
                "ترجیحاً دقیق بنویس که هماهنگی سریع انجام بشه 😇✨"
            )
            self.bot.send_message(
                int(user_id),text,
                reply_markup=kb,
            )
            self.log.debug("[select_reserve_time][ASK] user=%s", user_id)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if msg_txt == BACK_BTN:
            self.log.debug("[select_reserve_time][BACK] user=%s", user_id)
            self.engine.execute_prev(user_id, None)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if  msg_txt:
            self.engine._memory_persistence(user_id, "reserve_time", msg_txt)
            self.bot.send_message(message.chat.id, f"✅ ساعت {msg_txt} ثبت شد.🙏")
            self.log.info("[select_reserve_time] user=%s time=%s", user_id, msg_txt)
            return msg_txt
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.log.warning("[select_reserve_time][INVALID] user=%s text=%s", user_id, msg_txt)
        self.bot.send_message(
            message.chat.id,
            "❗ ساعت باید در قالب HH:MM باشد (مثال 18:45). دوباره امتحان کن.",
        )
        return None
    @step_handler("verification_photo_1")
    def handle_verification_photo_1(self, user_id: str, message: Optional[types.Message]) -> Optional[str]:
        return self._handle_request_verification_photo(user_id, message)          # Internal implementation note: legacy behavior is preserved during modernization.
    @step_handler("verification_photo_2")
    def handle_verification_photo_2(self, user_id: str, message: Optional[types.Message]) -> Optional[str]:
        return self._handle_request_verification_photo(user_id, message)          # Internal implementation note: legacy behavior is preserved during modernization.
    @step_handler("request_verification_photo_generic")
    def _handle_request_verification_photo(
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        import re, os, threading, random
        chat_id = int(user_id)
        st      = self.engine._user_states[user_id]
        # Internal implementation note: legacy behavior is preserved during modernization.
        step = st.get("current_step", "verification_photo_1")
        idx  = int(re.search(r"(\d+)$", step).group(1))
        emoji_k = f"verification_photo_{idx}_emoji"
        file_k  = f"verification_photo_{idx}_file_id"
        timer_k = f"verification_photo_{idx}_timer"
        global emtaked
        # Internal implementation note: legacy behavior is preserved during modernization.
        def _send_request(retry: bool = False , perv_emj = None) -> str:
            # Internal implementation note: legacy behavior is preserved during modernization.
            used = [st.get("verification_photo_1_emoji"), st.get("verification_photo_2_emoji")]
            # Internal implementation note: legacy behavior is preserved during modernization.
    # pool = random.shuffle([e for e in HAND_VERFIY if e not in used] or list(HAND_VERFIY))
            # Internal implementation note: legacy behavior is preserved during modernization.
            choices = [e for e in HAND_VERFIY if e not in used] or list(HAND_VERFIY)
            random.shuffle(choices)
            pool = choices
            emoji = random.choice(pool)
            while  emoji == perv_emj:
                emoji = random.choice(pool)
            emtaked = emoji
            st[emoji_k] = emoji
            # Internal implementation note: legacy behavior is preserved during modernization.
            if idx == 1:
                caption = (
                    f"📸 برای هماهنگی با عضو، لطفاً یه سلفی با این ایموجی بفرست: {emoji}\n\n"
                    "ساده و واضح باشه دوست عزیز 😇"
                )
            else:
                caption = (
                    "سوال 6\n\n"
                    f"عالی بود! حالا لطفاً یه سلفی دیگه با این ایموجی بفرست: {emoji}\n"
                    "مرسی از همکاری قشنگت ⭐"
                )
            if retry:
                caption = f"⏰ زمان شما به پایان رسید!\n{caption}"
            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(BACK_BTN)
            sample_path = os.path.join(IMAGES_DIR, f"{HAND_VERFIY[emoji]}.jpg")
            try:
                with open(sample_path, "rb") as img:
                    msg = self.bot.send_photo(chat_id, img, caption=caption, reply_markup=kb)
            except Exception:
                msg = self.bot.send_message(chat_id, caption, reply_markup=kb)
            st[f"verification_photo_{idx}_msg_id"]   = msg.message_id
            st[f"verification_photo_{idx}_photo_path"] = sample_path if os.path.exists(sample_path) else None
            # Internal implementation note: legacy behavior is preserved during modernization.
            if timer_k in st:
                st[timer_k].cancel()
                st.pop(timer_k, None)
            # Internal implementation note: legacy behavior is preserved during modernization.
            t = threading.Timer(180, _on_timeout)
            st[timer_k] = t
            t.start()
            return emtaked
        # Internal implementation note: legacy behavior is preserved during modernization.
        def _on_timeout() -> None:
            try:
                self.log.info("[TIMEOUT] chat=%s step=%s", chat_id, step)
                prev_id = st.get(f"verification_photo_{idx}_msg_id")
                if prev_id:
                    try:
                        self.bot.delete_message(chat_id, prev_id)
                    except Exception:
                        pass
                emtaked = _send_request(retry=True , perv_emj = emtaked)
            except Exception as exc:
                self.log.exception("[VERIFICATION_PHOTO_TIMEOUT] %s", exc)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message and message.text and message.text.strip() == BACK_BTN:
            if timer_k in st:
                st[timer_k].cancel()
                st.pop(timer_k, None)
            self.engine.execute_prev(user_id, None)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not (message and message.photo):
            emtaked = _send_request()
            self.log.debug("[verification_photo_%s][ASK] user=%s", idx, user_id)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not message.photo:
            self.bot.send_message(chat_id, "❌ لطفاً یک عکس معتبر ارسال کنید.")
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            if timer_k in st:
                st[timer_k].cancel()
                st.pop(timer_k, None)
            fwd = self.bot.forward_message(STORAGE_CHANNEL, chat_id, message.message_id)
            try:
                dump = self._pretty_state(st)
                mg = self.bot.send_message(
                    STORAGE_CHANNEL,
                    dump,
                    reply_to_message_id=fwd.message_id,
                    parse_mode="Markdown"
                )
                self.log.debug(dump)
                self.log.debug(mg)
            except Exception as e:
                self.log.warning("[STATE_DUMP] failed to send: %s", e)
            # Internal implementation note: legacy behavior is preserved during modernization.
            fid: str | None = None
            if fwd.photo:
                fid = fwd.photo[-1].file_id
            elif getattr(fwd, "document", None):
                fid = fwd.document.file_id
            if not fid:
                self.log.warning("[VERIFICATION_PHOTO] No valid file_id found for user=%s", user_id)
                self.bot.send_message(
                    chat_id,
                    "❌ تلگرام نتوانست عکس را پردازش کند. لطفاً یک عکس جدید بفرست.",
                )
                return None  # Internal implementation note: legacy behavior is preserved during modernization.
            st[file_k] = fid
            st["step"] = step
            self.log.info("[verification_photo_%s] user=%s stored file_id=%s", idx, user_id, fid)
                # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            if idx == 2:
                for k in list(st):
                    if k.startswith("verification_photo_"):
                        st.pop(k, None)
            return fid
      # Internal implementation note: legacy behavior is preserved during modernization.
        except Exception as exc:
            self.log.exception("[verification_photo_%s] forward failed: %s", idx, exc)
            self.bot.send_message(chat_id, "❌ خطا در ذخیره‌سازی. دوباره عکس بفرست.")
            return None
    @step_handler("video_note")
    def handle_video_note(
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        import threading, random, textwrap, logging
        from typing import List, Dict
        from telebot.types import ReplyKeyboardMarkup
        # Internal implementation note: legacy behavior is preserved during modernization.
        chat_id: int      = int(user_id)
        st: dict          = self.engine._user_states[user_id]
        timer_k: str      = "video_timer"      # Internal implementation note: legacy behavior is preserved during modernization.
        file_k: str       = "video_file_id"    # Internal implementation note: legacy behavior is preserved during modernization.
        text_k: str       = "video_sentence"   # Internal implementation note: legacy behavior is preserved during modernization.
        msg_k: str        = "video_msg_id"     # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        NUMBERS: List[str] = ["یک", "دو", "سه", "چهار", "پنج", "شش",
                              "هفت", "هشت", "نه", "ده", "یازده"]
        TEMPLATES: List[Dict] = [
            {
                "template": "من امروز {} {} {} خریدم",
                "allowed_units": ["کیلو", "بسته"],
                "allowed_items": ["برنج", "پیاز", "گوجه", "سیب", "گردو", "پسته"],
            },
            {
                "template": "می‌خواهم {} {} {} بخرم",
                "allowed_units": ["عدد", "تا"],
                "allowed_items": ["کتاب", "دفتر", "ماست", "شیر"],
            },
            {
                "template": "اگر وقت داشتم {} {} {} می‌پختم",
                "allowed_units": ["کیلو"],
                "allowed_items": ["برنج", "رب", "مربا"],
            },
        ]
        USED_SENTENCES: set[str] = set()      # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        def _rnd_sentence(max_retry: int = 20) -> str:
            logger = logging.getLogger(__name__)
            sentence: str = ""
            try:
                for _ in range(max_retry):
                    tpl = random.choice(TEMPLATES)
                    sentence = tpl["template"].format(
                        random.choice(NUMBERS),
                        random.choice(tpl["allowed_units"]),
                        random.choice(tpl["allowed_items"]),
                    )
                    if sentence not in USED_SENTENCES:
                        USED_SENTENCES.add(sentence)
                        logger.debug("[RND_SENTENCE] new=%s", sentence)
                        return sentence
                logger.warning("[RND_SENTENCE] duplicate fallback=%s", sentence)
                return sentence
            except Exception as exc:                 # Internal implementation note: legacy behavior is preserved during modernization.
                logger.exception("[RND_SENTENCE] error: %s", exc)
                return "من امروز یک بسته چای خریدم"
        # Internal implementation note: legacy behavior is preserved during modernization.
        def _ask(retry: bool = False) -> None:
            """Legacy-compatible behavior preserved for this callable."""
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                sentence = _rnd_sentence()
                st[text_k] = sentence
                # Internal implementation note: legacy behavior is preserved during modernization.
                vntcap = \
                    "با زدن روی دکمهٔ میکروفون، پایینِ سمت راستِ گوشی، می‌توانید ویدیو مسیج ارسال کنید.\n" \
                    "یک بار روی میکروفون بزنید تا آیکونش تغییر کند؛ سپس انگشت خود را نگه دارید و\n" \
                    "متنی را که از شما خواسته شده با صدای واضح بخوانید."
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(BACK_BTN)
                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    with open(VNT, "rb") as vid:
                        self.bot.send_video(
                            chat_id,
                            vid,
                            caption=vntcap,
                            reply_markup=keyboard,
                            parse_mode="Markdown"
                        )
                except FileNotFoundError:
                    self.log.warning("[VIDEO_ASK] VNT file not found → sending text only")
                    self.bot.send_message(
                        chat_id,
                        vntcap,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                # Internal implementation note: legacy behavior is preserved during modernization.
                caption = textwrap.dedent(f"""
                    📹 لطفاً یک *ویدیو مسیج* ۳–۱۰ ثانیه‌ای بگیر و دقیقاً همین جمله را بخوان 👇
                    « {sentence} »
                    { '⏰ زمانت تموم شد! دوباره امتحان کن.' if retry else '' }
                """).strip()
                msg = self.bot.send_message(
                    chat_id,
                    caption,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                st[msg_k] = msg.message_id  # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                if timer_k in st:
                    st[timer_k].cancel()
                t = threading.Timer(180, _on_timeout)
                st[timer_k] = t
                t.start()
            except Exception as exc:
                self.log.exception("[VIDEO_ASK] %s", exc)
        # Internal implementation note: legacy behavior is preserved during modernization.
        def _on_timeout() -> None:
            """Legacy-compatible behavior preserved for this callable."""
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if st.get("step") != "video_note" or st.get(file_k):
                    return
                self.log.info("[VIDEO_TIMEOUT] resend ask user=%s", user_id)
                # Internal implementation note: legacy behavior is preserved during modernization.
                if (mid := st.get(msg_k)):
                    try:
                        self.bot.delete_message(chat_id, mid)
                    except Exception:
                        pass
                _ask(retry=True)
            except Exception as exc:
                self.log.exception("[VIDEO_TIMEOUT] %s", exc)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message and message.text == BACK_BTN:
            if timer_k in st:
                st[timer_k].cancel()
                st.pop(timer_k, None)
            self.engine.execute_prev(user_id, None)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not (message and (message.video_note or message.video)):
            _ask()
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if timer_k in st:
            st[timer_k].cancel()
            st.pop(timer_k, None)
        try:
            fwd = self.bot.forward_message(STORAGE_CHANNEL,
                                           chat_id,
                                           message.message_id)
            try:
                dump = self._pretty_state(st)
                self.bot.send_message(
                    STORAGE_CHANNEL,
                    dump,
                    reply_to_message_id=fwd.message_id,
                    parse_mode="Markdown"
                )
            except Exception as e:
                self.log.warning("[STATE_DUMP][skip] %s", e)
            fid: Optional[str] = None
            if getattr(fwd, "video_note", None):
                fid = fwd.video_note.file_id
            if not fid:
                raise ValueError("empty file_id")
            st[file_k] = fid
            self.log.info("[VIDEO_NOTE] user=%s stored file_id=%s", user_id, fid)
            return fid                            # Internal implementation note: legacy behavior is preserved during modernization.
        except Exception as exc:
            self.log.exception("[VIDEO_NOTE] forward failed: %s", exc)
            self.bot.send_message(chat_id,
                                  "❌ خطا در ذخیره‌سازی. دوباره ویدیو بفرست.")
            return None
    @step_handler("get_contact")
    def _handle_request_contact(
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        import types
        chat_id = int(user_id)
        st      = self.engine._user_states[user_id]
        timer_k = "contact_timer"
        # Internal implementation note: legacy behavior is preserved during modernization.
        ASK_TEXT = (
            "📞 حالا لطفاً شماره‌ت رو با دکمه زیر بفرست 💬\n"
            "فقط با همون شماره‌ای که تو تلگرام وارد شدی می‌تونی ادامه بدی ✨\n\n"
            "اون شماره باید حتماً در دسترس باشه برای هماهنگی بعدی 📲⭐\n\n"
            "دکمه رو بزن دوست عزیز 😇👇🏻"
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message and message.text and message.text.strip() == BACK_BTN:
            if timer_k in st:
                st[timer_k].cancel()
                st.pop(timer_k, None)
            self.engine.execute_prev(user_id, None)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not (message and message.contact):
            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(KeyboardButton("📱 ارسال شماره من", request_contact=True))
            kb.add(BACK_BTN)
            self.bot.send_message(chat_id, ASK_TEXT, reply_markup=kb)
            self.log.debug("[get_contact][ASK] user=%s", user_id)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            c = message.contact
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            phone = c.phone_number
            st["phone"] = phone
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                "✅ شماره ثبت شد.",
                reply_markup=ReplyKeyboardRemove(),
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            for k in list(st):
                if k.startswith("contact_"):
                    st.pop(k, None)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            return phone
        except Exception as exc:
            self.log.warning("[get_contact] invalid contact: %s", exc)
            self.bot.send_message(
                chat_id,
                "❌ لطفاً فقط از دکمه «📱 ارسال شماره من» استفاده کن و شماره رو فوروارد نکن.",
            )
            return None
    @step_handler("collect_note")
    def _handle_collect_note(
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        import types
        chat_id = int(user_id)
        st      = self.engine._user_states[user_id]
        # Internal implementation note: legacy behavior is preserved during modernization.
        SKIP_BTN  = "⏭ رد میشم"
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(SKIP_BTN)
        kb.add(BACK_BTN)
        ASK_TEXT = (
            "📝 اگه توضیح خاصی داری یا نکته‌ای هست که لازمه بدونیم، همین‌جا برامون بنویس دوست عزیز ⭐\n"
            "(اگه چیزی نیاز نداری، می‌تونی بزنی رد شدن  😌 😌)"
        )
        # try:
        #     dump = self._pretty_state(st)
        #     self.bot.send_message(
        #         STORAGE_CHANNEL,
        #         dump,
        #         parse_mode="Markdown"
        #     )
        # except Exception as e:
        #     self.log.warning("[STATE_DUMP][skip] %s", e)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message and message.text and message.text.strip() == BACK_BTN:
            self.engine.execute_prev(user_id, None)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        if message and message.text and message.text.strip() == SKIP_BTN:
            st["note"] = ""                    # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "✅ باشه، مورد خاصی ثبت نشد.", reply_markup=ReplyKeyboardRemove())
            # Internal implementation note: legacy behavior is preserved during modernization.
            return SKIP_BTN                        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not (message and message.text):
            self.bot.send_message(chat_id, ASK_TEXT, reply_markup=kb)
            self.log.debug("[collect_note][ASK] user=%s", user_id)
            return None
        # Internal implementation note: legacy behavior is preserved during modernization.
        note_text = message.text.strip()
        st["note"] = note_text
        self.bot.send_message(chat_id, "✅ ممنون! یادداشتت ثبت شد. 🌟", reply_markup=ReplyKeyboardRemove())
        return note_text            # Internal implementation note: legacy behavior is preserved during modernization.
    @step_handler("finish_booking")
    def _handle_finish_booking(
        self,
        user_id: str,
        message: Optional[types.Message],
    ) -> Optional[str]:
        from datetime import datetime
        import json
        chat_id = int(user_id)
        st      = self.engine._user_states[user_id]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if st.get("_finished"):
            return None
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if message is not None:
                first_name = message.from_user.first_name or ""
                username   = message.from_user.username or ""
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    user_chat = self.bot.get_chat(chat_id)
                    first_name = user_chat.first_name or ""
                    username   = user_chat.username or ""
                except Exception:
                    first_name = ""
                    username   = ""
            code = st.get("staff_code") or st.get("selected_code", "")
            # Internal implementation note: legacy behavior is preserved during modernization.
            record = {
                "name":             first_name,
                "telegram_id":      chat_id,
                "username":         username,
                "staff_code":   code,
                "region":           st.get("region", ""),
                "phone":            st.get("phone", ""),
                "verification_photo_1_emoji":   st.get("verification_photo_1_emoji", ""),
                "verification_photo_1_file_id": st.get("verification_photo_1_file_id", ""),
                "video_sentence": st.get("video_sentence", ""),
                "video_file_id":  st.get("video_file_id", ""),
                "verification_photo_2_emoji":   st.get("verification_photo_2_emoji", ""),
                "verification_photo_2_file_id": st.get("verification_photo_2_file_id", ""),
                "note":             st.get("note", ""),
                "status":           "pending",
                "request_time":     st.get("reserve_time") or datetime.now().strftime("%H:%M") + datetime.minute(30),
                "intro_msg_id": st.get("intro_msg_id"),
            }
            # Internal implementation note: legacy behavior is preserved during modernization.
            client_data = {
                "telegram_id": chat_id,
                "name":        first_name,
                "username":    username,
                "phone":       record["phone"],
                "status" : "approved",
                "last_order":  datetime.now().isoformat(sep=" ", timespec="seconds"),
            }
              # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.upsert(
                table_name   = "clients",
                data         = client_data,
                key          = "telegram_id", 
                column_types = {                      # Internal implementation note: legacy behavior is preserved during modernization.
                    "telegram_id": "varchar(50) UNIQUE",
                    "name":        "varchar(100)",
                    "username":    "varchar(100)",
                    "phone":       "varchar(50)",
                    "note" : "TEXT",
                    "status":      "varchar(30)",
                    "last_order":  "datetime",
                },
                unique_column          = "telegram_id",          # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
            )
            self.log.info("[UPSERT] clients record upserted for chat %s", chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.db.execute_query(
                    "ALTER TABLE request_drafts MODIFY COLUMN rejection_reason JSON;"
                )
                self.db.execute_query(
                    "ALTER TABLE request_drafts MODIFY COLUMN note TEXT;"
                )
            except Exception:
                # Internal implementation note: legacy behavior is preserved during modernization.
                pass
            self.db.insert(
                table_name="request_drafts",
                data=record,
                column_types={"telegram_id": "varchar(50)", "rejection_reason": "JSON"},
            )
            self.log.info(f"[SAVE] request_drafts record inserted for chat {chat_id}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(CANCEL_BTN)
            # Internal implementation note: legacy behavior is preserved during modernization.
            info_text = (
                "✅ سفارشت با موفقیت ثبت شد دوست عزیز! 🎉\n\n"
                "📌 اگه اطلاعات اشتباه باشه، متأسفانه درخواستت لغو میشه.\n"
                "⏰ بعد از تأیید، پرسنل سریع باهات تماس می‌گیرن—پس گوشیت همیشه دم دست باشه! 📞"
            )
            self.bot.send_message(
                chat_id=int(user_id),
                text=info_text,
                reply_markup=kb
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            admin_text = (
                f"<b>🔔 یادت نره برای پیگیری فوری، کد انتخابی‌ت رو به"
                f"<a href=\"https://t.me/{admin_username.replace('@', '')}\">👤 ادمین</a> زیر بفرستی:</b>\n"
            )
            admin_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="💬 ارسال پیام به ادمین",
                    url=f"https://t.me/{admin_username.replace('@', '')}"
                )
            ]])
            self.bot.send_message(
                chat_id=int(user_id),
                text=admin_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=admin_kb
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            admin_msg = (
                "📥 *سفارش جدید:*\n\n"
                f"👤 نام: {first_name or '—'}\n"
                f"🔗 یوزرنیم: @{username or '—'}\n"
                f"🆔 آیدی عددی: {chat_id}\n"
                f"🧾 کد ارائه‌دهنده: {record['staff_code'] or '—'}\n"
                f"🕒 ساعت درخواستی: {record['request_time']}\n"
                f"📞 شماره تماس: {record['phone'] or '—'}"
            )
            self.message_to_admin(admin_msg)
            # Internal implementation note: legacy behavior is preserved during modernization.
            st["_finished"] = True
            return None
        except Exception as exc:
            self.log.exception(f"[FINISH_BOOKING] failed: {exc}")
            self.bot.send_message(chat_id, "❌ خطایی رخ داد. لطفاً بعداً دوباره تلاش کنید.")
            return None
    def _collect_step_handlers(self) -> Dict[str, Dict[str, Any]]:
        """Scan *self* for @step_handler decorated methods and build contract."""
        contract: Dict[str, Dict[str, Any]] = {}
        for _name, fn in inspect.getmembers(self, predicate=inspect.ismethod):
            step_name = getattr(fn, "_step_name", None)
            if not step_name:
                continue
            contract[step_name] = {
                "handler": fn,
                "input_type": getattr(fn, "_input_type", "text"),
                "description": (fn.__doc__ or "").strip(),
            }
        if not contract:
            raise RuntimeError("No @step_handler decorated methods found!")
        return contract
    def message_to_admin(self, text: str):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            admins = self.get_admins()
            if not admins:
                self.log.warning("[ADMIN_MSG] No eligible admins to notify.")
                return
            for admin in admins:
                try:
                    self.admin_bot.send_message(admin["telegram_id"], text)
                    self.log.info(f"[ADMIN_MSG] Message sent to admin ID={admin['telegram_id']}")
                except Exception as send_exc:
                    self.log.error(f"[ADMIN_MSG] Failed to send to admin ID={admin['telegram_id']}: {send_exc}")
        except Exception as exc:
            self.log.exception(f"[ADMIN_MSG] Unexpected failure in admin messaging: {exc}")
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
                        self.log.warning(f"[ADMIN-PERMISSIONS] Invalid JSON for admin ID={admin.get('id')}: {json_err}")
            return filtered_admins
        except Exception as exc:
            self.log.exception(f"[GET_ADMINS] Failed to fetch admins: {exc}")
            return []
    def handle_cancel_request(self, message):
        from datetime import datetime
        import types
        chat_id = message.chat.id
        today   = datetime.now().date().isoformat()
        try:
            pending = self.db.select_dict(
                "request_drafts",
                "telegram_id = ? AND date(created_at) = ? AND status IN ('pending', 'approved')",
                (message.from_user.id, today)
            )
            if not pending:
                self.bot.send_message(chat_id, "⚠️ شما سفارش جاری در امروز ندارید.", reply_markup=ReplyKeyboardRemove())
                return
            latest = pending[-1]
            status = latest["status"]
            # Internal implementation note: legacy behavior is preserved during modernization.
            if status == "approved":
                reserved = latest.get("request_time", "—")
                phone    = latest.get("phone", "—")
                self.bot.send_message(
                    chat_id,
                    f"✅ سفارش شما برای ساعت <b>{reserved}</b> با موفقیت رزرو شد.\n"
                    f"برای کنسلی فقط در صورت ضرورت، به <a href='https://t.me/{admin_username.lstrip(chr(64))}'>ادمین</a> پیام بدید 👇\n\n"
                    f"اگه شماره رو خودتون وارد کردین، منتظر تماس نباشید؛ در غیر این صورت منتظر تماس با شماره <b>{phone}</b> بمونید. 🙏",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("پیام به ادمین", url=f"https://t.me/{admin_username.lstrip(chr(64))}")
                    ]])
                )
                self.message_to_admin(
                    "⚠️ کاربر تأییدشده قصد کنسل دارد:\n"
                    f"👤 {latest['name']} (@{latest['username'] or '—'})\n"
                    f"🧾 کد: {latest['staff_code'] or '—'}\n"
                    f"📞 {phone}\n"
                    f"🕒 {reserved}"
                )
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update("request_drafts", {"status": "canceled"}, "id = ?", (latest["id"],))
            self.bot.send_message(chat_id, "❌ سفارش شما کنسل شد.", reply_markup=ReplyKeyboardRemove())
            self.message_to_admin(
                "❌ سفارش لغو شد توسط کاربر:\n"
                f"👤 {latest['name']} (@{latest['username'] or '—'})\n"
                f"🧾 کد: {latest['staff_code'] or '—'}\n"
                f"🕒 {latest['request_time'] or '—'}"
            )
        except Exception as exc:
            self.log.exception("[CANCEL_REQUEST] failed: %s", exc)
            self.bot.send_message(chat_id, "⚠️ خطایی رخ داد؛ لطفاً دوباره سعی کن.", reply_markup=ReplyKeyboardRemove())
