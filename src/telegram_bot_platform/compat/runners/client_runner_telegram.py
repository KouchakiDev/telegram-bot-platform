from __future__ import annotations

from .client_runner_context import *
from telegram_bot_platform.compat.miniapp import send_mini_app


class ClientRunnerTelegramMixin:
    def _register_telegram_handlers(self) -> None:
        @self.bot.message_handler(commands=["app"])
        def _cmd_app(message: types.Message):
            send_mini_app(self.bot, message)

        """Single universal message handler that pipes updates into the engine."""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("photo_nav:"))
        def _on_photo_nav( call: types.CallbackQuery) -> None:
            """Legacy-compatible behavior preserved for this callable."""
            chat_id = call.message.chat.id
            callback_id = call.id
            action = None
            if self.user_blocked(call.message):
                self.bot.send_message(chat_id,
                    "❌ حساب شما مسدود است؛ برای رفع مشکل با ادمین تماس بگیرید.")
                return          # Internal implementation note: legacy behavior is preserved during modernization.
            if self._has_pending_request(call.message):
                kb = ReplyKeyboardMarkup(resize_keyboard=True)
                kb.add("از درخواست خود منصرف شدم 🚫")
                self.bot.send_message(
                    chat_id,
                    "⚠️ شما یک سفارش در وضعیت *در انتظار تأیید* دارید.\n"
                    "اگر منصرف شدی، می‌توانی با دکمه زیر آن را لغو کنی.",
                    parse_mode="Markdown",
                    reply_markup=kb,
                )
                return  
            try:
                action = call.data.split(":", 1)[1]  # prev|retry|next
                self.log.debug("[PHOTO_NAV] user=%s action=%s", chat_id, action)
            except Exception as e:
                self.log.error("[PHOTO_NAV] malformed callback_data=%s · err=%s", call.data, e)
                # Internal implementation note: legacy behavior is preserved during modernization.
                try: self.bot.answer_callback_query(callback_id)
                except: pass
                return
            st = self._photo_play.get(chat_id)
            if not st:
                self.log.warning("[PHOTO_NAV] no slide state for user=%s", chat_id)
                try: self.bot.answer_callback_query(callback_id)
                except: pass
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            timer = self._photo_timers.pop(chat_id, None)
            if timer:
                try:
                    timer.cancel()
                    self.log.debug("[PHOTO_NAV] cancelled existing timer for user=%s", chat_id)
                except Exception as e:
                    self.log.error("[PHOTO_NAV] failed to cancel timer for user=%s · err=%s", chat_id, e)
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.bot.delete_message(chat_id, call.message.message_id)
                self.log.debug("[PHOTO_NAV] deleted message %s for user=%s", call.message.message_id, chat_id)
            except Exception as e:
                self.log.warning("[PHOTO_NAV] could not delete message %s for user=%s · err=%s",
                                 call.message.message_id, chat_id, e)
            # Internal implementation note: legacy behavior is preserved during modernization.
            old_idx = st["idx"]
            max_idx = len(st.get("photos", [])) - 1
            if action == "prev":
                if old_idx > 0:
                    st["idx"] -= 1
            elif action == "next":
                if old_idx < max_idx:
                    st["idx"] += 1
            elif action == "retry":
                # Internal implementation note: legacy behavior is preserved during modernization.
                pass
            else:
                self.log.warning("[PHOTO_NAV] unknown action '%s' for user=%s", action, chat_id)
            new_idx = st["idx"]
            self.log.info("[PHOTO_NAV] user=%s idx changed %s → %s", chat_id, old_idx, new_idx)
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self._show_photo_slide(chat_id, retry=(action == "retry"))
                self.log.debug("[PHOTO_NAV] called _show_photo_slide for user=%s retry=%s", chat_id, action == "retry")
            except Exception as e:
                self.log.exception("[PHOTO_NAV] _show_photo_slide failed for user=%s action=%s err=%s", chat_id, action, e)
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.bot.answer_callback_query(callback_id)
                self.log.debug("[PHOTO_NAV] answered callback_query %s for user=%s", callback_id, chat_id)
            except Exception as e:
                self.log.error("[PHOTO_NAV] answer_callback_query failed for user=%s callback=%s · err=%s",
                               chat_id, callback_id, e)
                # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("select_code:"))
        def _on_select_code(call: types.CallbackQuery) -> None:
            try:
                if self.user_blocked(call.message):
                    self.bot.send_message(call.message.chat.id,
                        "❌ حساب شما مسدود است؛ برای رفع مشکل با ادمین تماس بگیرید.")
                    return   
                if self._has_pending_request(call.message):
                    kb = ReplyKeyboardMarkup(resize_keyboard=True)
                    kb.add("از درخواست خود منصرف شدم 🚫")
                    self.bot.send_message(
                        call.message.chat.id,
                        "⚠️ شما یک سفارش در وضعیت *در انتظار تأیید* دارید.\n"
                        "اگر منصرف شدی، می‌توانی با دکمه زیر آن را لغو کنی.",
                        parse_mode="Markdown",
                        reply_markup=kb,
                    )
                    return  
                code = call.data.split(":", 1)[1]
                self._process_code_selection(call.from_user.id, code)
                self.bot.answer_callback_query(call.id)         # Internal implementation note: legacy behavior is preserved during modernization.
            except Exception as exc:
                self.log.exception("[CALLBACK] select_code failed · %s", exc)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.message_handler(commands=["play_photos"])
        def _cmd_play_photos(msg: types.Message):
            chat_id = msg.chat.id
            try:
                if self.user_blocked(msg):
                    self.bot.send_message(chat_id,
                        "❌ حساب شما مسدود است؛ برای رفع مشکل با ادمین تماس بگیرید.")
                    return 
                if self._has_pending_request(msg):
                    kb = ReplyKeyboardMarkup(resize_keyboard=True)
                    kb.add("از درخواست خود منصرف شدم 🚫")
                    self.bot.send_message(
                        chat_id,
                        "⚠️ شما یک سفارش در وضعیت *در انتظار تأیید* دارید.\n"
                        "اگر منصرف شدی، می‌توانی با دکمه زیر آن را لغو کنی.",
                        parse_mode="Markdown",
                        reply_markup=kb,
                    )
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                rows = self.db.select_dict("codes", "photos IS NOT NULL AND photos <> ''")
                photos_all: list[tuple[str, str]] = []
                for r in rows:
                    try:
                        lst = json.loads(r["photos"] or "[]")
                        photos_all.extend([(r["code"], fid) for fid in lst])
                    except Exception:
                        continue
                for photo in photos_all:
                    self.log.debug(f"{photo}")
                if not photos_all:
                    self.bot.send_message(chat_id, "⚠️ فعلاً عکسی برای نمایش نداریم.")
                    return
                # random.shuffle(photos_all)  
                self._photo_play[chat_id] = {"photos": photos_all, "idx": 0}
                self._show_photo_slide(chat_id)   # Internal implementation note: legacy behavior is preserved during modernization.
            except Exception as exc:
                self.log.exception("[PLAY_PHOTOS] failed chat=%s : %s", chat_id, exc)
                self.bot.send_message(chat_id, "❌ خطا در فراخوانی گالری.")
        @self.bot.message_handler(content_types=[
            "text", "photo", "contact", "document",
            "audio", "voice", "video", "video_note"
        ])
        def _router(message: types.Message) -> None:
            chat_id_key = str(message.chat.id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.user_blocked(message):
                self.bot.send_message(message.chat.id,
                    "❌ حساب شما مسدود است؛ برای رفع مشکل با ادمین تماس بگیرید.")
                return 
             # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                # -----------------------------------------------------
                # Internal implementation note: legacy behavior is preserved during modernization.
                # -----------------------------------------------------
                # Internal implementation note: legacy behavior is preserved during modernization.
                if message.text and message.text.startswith("/start"):
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    parts = message.text.split(maxsplit=1)
                    if len(parts) == 2 and parts[1].startswith("code_"):
                        code = parts[1].replace("code_", "").strip()
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        self._process_code_selection(message.chat.id, code)
                        return
                    if len(parts) == 2 and parts[1] == "play_photos":
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        _cmd_play_photos(message)
                        return
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if message.text.strip() == "/start" or (len(parts) == 2 and parts[1] == "start"):
                        if not self.user_blocked(message):
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            if self._has_pending_request(message):
                                kb = ReplyKeyboardMarkup(resize_keyboard=True)
                                kb.add("از درخواست خود منصرف شدم 🚫")
                                self.bot.send_message(
                                    message.chat.id,
                                    "⚠️ شما یک سفارش در وضعیت *در انتظار تأیید* دارید.\n"
                                    "اگر منصرف شدی، می‌توانی با دکمه زیر آن را لغو کنی.",
                                    parse_mode="Markdown",
                                    reply_markup=kb,
                                )
                                return  # Internal implementation note: legacy behavior is preserved during modernization.
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            self.starter.store_user_info(message)
                            self.engine.reset_state(chat_id_key)
                            self.engine.on_start(chat_id_key)
                            self.engine.execute_next(chat_id_key, message=None)
                            return
                        else:
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            return
                # Internal implementation note: legacy behavior is preserved during modernization.
                if message.text and message.text.strip() == BACK_BTN:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.engine.execute_prev(chat_id_key, message=None)
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                if message.text and message.text.strip() == "از درخواست خود منصرف شدم 🚫":
                    return self.handle_cancel_request(message)
                if self._has_pending_request(message):
                    kb = ReplyKeyboardMarkup(resize_keyboard=True)
                    kb.add("از درخواست خود منصرف شدم 🚫")
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ شما یک سفارش در وضعیت *در انتظار تأیید* دارید.\n"
                        "اگر منصرف شدی، می‌توانی با دکمه زیر آن را لغو کنی.",
                        parse_mode="Markdown",
                        reply_markup=kb,
                    )
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                result = self.engine.execute_next(chat_id_key, message)
                # Internal implementation note: legacy behavior is preserved during modernization.
                iteration = 0
                while result is not None and iteration < 10:
                    iteration += 1
                    result = self.engine.execute_next(chat_id_key, message=None)
            except StepExecutionError as ste:
                self.log.warning("Recoverable step error for chat=%s : %s", chat_id_key, ste)
                self.bot.send_message(message.chat.id, "⚠️ خطا در پردازش مرحله. لطفاً دوباره تلاش کنید.")
            except Exception as exc:  # noqa: BLE001
                self.log.exception("Fatal error while routing message: %s", exc)
                self.bot.send_message(message.chat.id, "❌ خطای غیرمنتظره. بعداً دوباره امتحان کنید.")
    def log_pre_hook(self, user_id: str, step: str, message: Any, response: Any | None) -> None:  # noqa: D401
        self.log.debug("[PRE] step=%s user=%s message_type=%s", step, user_id, getattr(message, "content_type", None))
    def log_post_hook(self, user_id: str, step: str, message: Any, response: Any | None) -> None:  # noqa: D401
        self.log.debug("[POST] step=%s user=%s response=%s", step, user_id, response)
