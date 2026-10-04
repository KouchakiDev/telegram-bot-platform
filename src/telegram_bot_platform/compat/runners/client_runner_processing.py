from __future__ import annotations

from .client_runner_context import *


class ClientRunnerProcessingMixin:
    def _has_pending_request(self, message: types.Message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            from datetime import datetime
            today = datetime.now().date().isoformat()
            telegram_id = message.from_user.id
            rows = self.db.select_dict(
                table="request_drafts",
                condition="telegram_id = ? AND date(created_at) = ? AND status = 'pending'",
                params=(telegram_id, today)
            )
            if rows:
                self.log.info(f"[CHECK_PENDING] chat={telegram_id} has pending request")
                return True
            else:
                return False
        except Exception as exc:
            self.log.exception(f"[CHECK_PENDING] failed: {exc}")
            return False
    def _pick_random_emoji(self, used: list[str]) -> str:   # noqa: D401
        import random
        pool = [e for e in HAND_VERFIY if e not in used] or list(HAND_VERFIY)
        return random.choice(pool)
    def _process_code_selection(self, chat_id: int, code: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        user_id = str(chat_id)
        try:
            self.log.debug("[DEEPLINK] start processing for user=%s code=%s", chat_id, code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if user_id not in self.engine._user_states:
                self.log.debug("[DEEPLINK] registering new user_state for user=%s", chat_id)
                self.engine._user_states[user_id] = {}
            else:
                self.log.debug("[DEEPLINK] resetting existing user_state for user=%s", chat_id)
                self.engine.reset_state(user_id)
                self.engine._user_states[user_id] = {}
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("codes", "code = ? AND activity = 1", (code,))
            if not rows:
                self.log.warning("[DEEPLINK] inactive or missing code=%s for user=%s", code, chat_id)
                self.bot.send_message(chat_id, "⚠️ این کد فعّال نیست یا وجود ندارد.")
                return
            dispatch_mode = rows[0]["dispatch_mode"]
            self.log.info("[DEEPLINK] code %s is active (dispatch_mode=%s)", code, dispatch_mode)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.log.debug("[DEEPLINK] engine state reset for user=%s", chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.engine._user_states[user_id].update({
                "dispatch_mode":  dispatch_mode,
                "staff_code": code,
            })
            self.log.debug("[DEEPLINK] set dispatch_mode=%s, staff_code=%s in user_state for user=%s",
                           dispatch_mode, code, chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            for step in ("choose_dispatch_mode", "select_staff_code"):
                try:
                    self.engine._skip_step(user_id, step_name=step, reason="deep-link")
                    self.log.debug("[DEEPLINK] skipped step=%s for user=%s", step, chat_id)
                except Exception as e:
                    self.log.error("[DEEPLINK] skip_step failed step=%s user=%s err=%s", step, chat_id, e)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.handle_confirm_staff_code(user_id, message=None)
            self.log.info("[DEEPLINK] jumped to confirm_staff_code for user=%s with code=%s", chat_id, code)
            # Internal implementation note: legacy behavior is preserved during modernization.
            def _forward_bio():
                try:
                    row = self.db.select_dict("codes", "code = ?", (code,))[0]
                    ch_id = row.get("photos_channel_id")
                    msg_id = row.get("photos_msg_id")
                    if ch_id and msg_id:
                        self.log.debug("[DEEPLINK] forwarding bio msg_id=%s from channel=%s to user=%s",
                                       msg_id, ch_id, chat_id)
                        self.bot.forward_message(chat_id, ch_id, int(msg_id))
                    else:
                        self.log.debug("[DEEPLINK] no bio msg/channel to forward for code=%s", code)
                except Exception as exc:
                    self.log.exception("[DEEPLINK] forward_bio failed for code=%s user=%s err=%s",
                                       code, chat_id, exc)
            threading.Timer(5, _forward_bio).start()
            self.log.debug("[DEEPLINK] scheduled bio forward in 5s for user=%s code=%s", chat_id, code)
        except Exception as exc:
            self.log.exception("[DEEPLINK] processing failed for user=%s code=%s err=%s", chat_id, code, exc)
            try:
                self.bot.send_message(chat_id, "❌ خطایی رخ داد؛ لطفاً دوباره تلاش کنید.")
            except Exception:
                self.log.error("[DEEPLINK] failed to send error message to user=%s", chat_id)
    def _pretty_state(self, state: dict) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        import re
        from typing import Any
        # Internal implementation note: legacy behavior is preserved during modernization.
        LABELS = {
            "dispatch_mode":      "نوع خدمات",
            "staff_code":     "کد پرسنل",
            "region":             "آدرس",
            "reserve_time":       "ساعت رزرو",
            "verification_photo_1_emoji":     "ایموجی سلفی ۱",
            "verification_photo_1_file_id":   "سلفی ۱",
            "verification_photo_2_emoji":     "ایموجی سلفی ۲",
            "verification_photo_2_file_id":   "سلفی ۲",
            "video_sentence":     "جملهٔ ویدیو",
            "video_file_id":      "ویدیوی احراز",
            "phone":              "شماره تماس",
            "note":               "توضیحات کاربر",
        }
        # Internal implementation note: legacy behavior is preserved during modernization.
        IGNORED_KEYS = {
            "step", "current_step",
            "verification_photo_1_timer", "verification_photo_2_timer", "video_timer", "contact_timer",
            "verification_photo_1_msg_id", "verification_photo_2_msg_id", "video_msg_id",
        }
        IGNORED_PREFIXES = ("_",)
        IGNORED_SUFFIXES = ("_timer", "_msg_id")
        def _skip(key: str) -> bool:
            return (
                key in IGNORED_KEYS
                or key.startswith(IGNORED_PREFIXES)
                or any(key.endswith(suf) for suf in IGNORED_SUFFIXES)
            )
        def _escape_md(text: str) -> str:
            """Escapes Telegram-Markdown-V2 special chars."""
            special = r"\`*_[]()~>#+-=|{}.! "
            return re.sub(f"([{re.escape(special)}])", r"\\\1", str(text))
        def _pretty_value(key: str, val: Any) -> str:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if key.endswith("_file_id") and val:
                return "✅ ذخیره شد"
            return str(val)
        # Internal implementation note: legacy behavior is preserved during modernization.
        ordered_keys = [k for k in LABELS if k in state and state[k] not in ("", None)]
        other_keys   = [k for k in state if k not in ordered_keys]
        lines = []
        for key in ordered_keys + other_keys:
            val = state.get(key)
            if val in ("", None) or _skip(key):
                continue
            label = LABELS.get(key, key)  # Internal implementation note: legacy behavior is preserved during modernization.
            lines.append(f"• *{_escape_md(label)}*: `{_escape_md(_pretty_value(key, val))}`")
        header = "🗒️ *مشخصات ثبت‌شدهٔ کاربر تا این لحظه*"
        return header + "\n" + "\n".join(line.replace("\\", "") for line in lines)
    def _show_photo_slide(self, chat_id: int, *, retry: bool = False) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        st = self._photo_play.get(chat_id)
        if not st:
            self.log.debug("[PHOTO] no playback state for chat=%s", chat_id)
            return
        photos: list[tuple[str, str]] = st["photos"]
        idx: int                      = st["idx"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not photos:
            self.bot.send_message(chat_id, "⚠️ هیچ عکسی برای نمایش باقی نمانده است.")
            return
        if idx < 0 or idx >= len(photos):
            self.log.warning("[PHOTO] idx out of range chat=%s idx=%s len=%s", chat_id, idx, len(photos))
            st["idx"] = 0
            return self._show_photo_slide(chat_id)
        code, fid = photos[idx]
        self.log.info("[PHOTO] chat=%s code=%s idx=%s retry=%s fid=%s", chat_id, code, idx, retry, fid)
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            row      = self.db.select_dict("codes", "code = ?", (code,))[0]
            caption  = (row.get("photos_caption") or row.get("bio") or "")[:1024]
            is_live  = bool(row.get("activity"))
        except Exception as e:
            self.log.error("[PHOTO] DB fetch failed code=%s : %s", code, e)
            caption, is_live = "", False
        # Internal implementation note: legacy behavior is preserved during modernization.
        def kb(show_retry:bool = False) -> InlineKeyboardMarkup:
            k = InlineKeyboardMarkup(row_width=3)
            # live-order button first
            # nav buttons
            buttons = []
            if idx > 0:
                buttons.append(InlineKeyboardButton("⬅️ قبلی", callback_data="photo_nav:prev"))
            if show_retry:
                buttons.append(InlineKeyboardButton("🔄 دوباره", callback_data="photo_nav:retry"))
            if idx < len(photos) - 1:
                buttons.append(InlineKeyboardButton("➡️ بعدی", callback_data="photo_nav:next"))
            k.add(*buttons)
            if is_live:
                k.add(InlineKeyboardButton("✅ سفارش این کد", callback_data=f"select_code:{code}"))
            return k
        # Internal implementation note: legacy behavior is preserved during modernization.
        def send_with(src):
            return self.bot.send_photo(
                chat_id,
                src,
                caption=caption,
                parse_mode="HTML",
                has_spoiler=True,
                reply_markup=kb()
            )
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            msg = send_with(fid)
        except Exception as e1:
            self.log.warning("[PHOTO] file_id send failed fid=%s : %s", fid, e1)
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                f_meta  = self.admin_bot.get_file(fid)
                f_bytes = self.admin_bot.download_file(f_meta.file_path)
                bio     = io.BytesIO(f_bytes); bio.name = "photo.jpg"
                msg     = send_with(bio)
                self.log.debug("[PHOTO] sent via admin-download bytes chat=%s", chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            except Exception as e2:
                self.log.error("[PHOTO] admin download failed fid=%s : %s", fid, e2)
                photos.pop(idx)
                if not photos:
                    self.bot.send_message(chat_id, "⚠️ متأسفانه هیچ عکس سالمی برای این گالری پیدا نشد.")
                    return
                # adjust idx within new bounds
                st["idx"] = min(idx, len(photos) - 1)
                return self._show_photo_slide(chat_id, retry=False)
        photo_msg_id = msg.message_id
        # Internal implementation note: legacy behavior is preserved during modernization.
        if (old := self._photo_timers.pop(chat_id, None)):
            try: old.cancel()
            except Exception: pass
        # Internal implementation note: legacy behavior is preserved during modernization.
        def _after_delay():
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.bot.delete_message(chat_id, photo_msg_id)
            except Exception:
                pass
            # Internal implementation note: legacy behavior is preserved during modernization.
            text_body =  "برای مشاهدهٔ عکس‌ها از دکمه‌های زیر استفاده کن:"
            try:
                self.bot.send_message(chat_id, text_body, parse_mode="HTML", reply_markup=kb(True))
            except Exception as e:
                self.log.warning("[PHOTO] send nav-text failed chat=%s : %s", chat_id, e)
        timer = threading.Timer(PHOTO_DELAY, _after_delay)
        self._photo_timers[chat_id] = timer
        timer.start()
        self.log.debug("[PHOTO] timer=%ss set chat=%s photo_msg_id=%s", PHOTO_DELAY, chat_id, photo_msg_id)
