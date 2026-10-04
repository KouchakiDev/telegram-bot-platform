from __future__ import annotations

from .login_handler_context import *


class LoginHandlerCoreMixin:
    def start_login(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📱 فراموشی رمز عبور", "❌ بازگشت به منوی اصلی")
        self.bot.send_message(
            chat_id, "لطفاً کد ورود خود را وارد کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_U_code)
    def process_U_code(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        elif text == "📱 فراموشی رمز عبور":
            self.ask_for_phone_number(message)
            return
        U_code = text
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not self.db.table_exists("staff"):
            self.bot.send_message(chat_id, "❌ شما هنوز ثبت‌نام نکرده‌اید.")
            self.parent.send_welcome(message)
            return
        results = self.db.select_dict(
            "staff", "U_code = ? AND telegram_id = ?", (U_code, message.from_user.id))
        if results:
            user = results[0]
            if user.get("status") == "approved":
                self.bot.send_message(chat_id, "✅ ورود موفقیت‌آمیز بود.")
                self.login_menu(message)
            elif user.get("status") == "pending":
                self.bot.send_message(
                    chat_id, "⏳ حساب شما هنوز توسط مدیر تأیید نشده است.")
                self.parent.send_welcome(message)
            elif user.get("status") == "blocked":
                self.bot.send_message(chat_id, "⛔️ حساب شما مسدود شده است.")
                self.parent.send_welcome(message)
            else:
                self.bot.send_message(chat_id, "❌ وضعیت حساب شما نامشخص است.")
                self.parent.send_welcome(message)
        else:
            self.bot.send_message(
                chat_id, "❌ کد ورود نادرست است. لطفاً مجدداً امتحان کنید.")
            self.bot.register_next_step_handler(message, self.process_U_code)
    def ask_for_phone_number(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(
            "📞 ارسال شماره تلفن", request_contact=True)
        cancel = types.KeyboardButton("❌ بازگشت به منوی اصلی")
        markup.add(button, cancel)
        self.bot.send_message(
            chat_id, "لطفاً شماره تلفن خود را با دکمه زیر ارسال کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_forgotten_phone_number)
    def process_forgotten_phone_number(self, message):
        chat_id = message.chat.id
        if message.text == "❌ بازگشت به منوی اصلی":
            self.parent.send_welcome(message)
            return
        if not message.contact:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه ارسال شماره تلفن استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_forgotten_phone_number)
            return
        phone = message.contact.phone_number[-10:]
        if not self.db.table_exists("staff"):
            self.bot.send_message(
                chat_id, "❌ شماره‌ای با این مشخصات یافت نشد.")
            self.parent.send_welcome(message)
            return
        results = self.db.select_dict(
            "staff", "phone_number = ?", (phone,))
        if results:
            code = results[0].get("U_code", "نامشخص")
            self.bot.send_message(
                chat_id, f"🔑 کد ورود شما: `{code}`", parse_mode="Markdown")
            self.parent.send_welcome(message)
        else:
            self.bot.send_message(
                chat_id, "❌ شماره‌ای با این مشخصات یافت نشد.")
            self.parent.send_welcome(message)
    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            text = message.text
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not text:
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "/start":
                logger.info(f"[LoginHandler.is_back] /start command received → returning to login_menu | chat_id={chat_id}")
                self.login_menu(message)
                return True
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text in ["🔙 بازگشت", "🔙 بازگشت به پنل"]:
                logger.info(f"[LoginHandler.is_back] Back button pressed → returning to login_menu | chat_id={chat_id}")
                self.login_menu(message)
                return True
            return False
        except Exception as e:
            logger.exception(f"[LoginHandler.is_back] Exception occurred: {e}")
            return False
    def add_back_buttons(self, markup):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            markup.add("🔙 بازگشت")
            logger.debug("[LoginHandler.add_back_buttons] '🔙 بازگشت' button added to markup.")
            return markup
        except Exception as e:
            logger.exception(f"[LoginHandler.add_back_buttons] Failed to add back button: {e}")
            return markup
    def login_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            telegram_id = message.from_user.id
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not message.text:
                logger.warning(f"[login_menu] Non-text message received → skipping menu update | chat_id={chat_id}")
                return
            logger.info(f"[login_menu] Showing main login menu → chat_id={chat_id}")
            logger.info(
                f"🔔 Entering login_menu for telegram_id={telegram_id}, chat_id={chat_id}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            premium_info = self.db.select_dict(
                "premium_staff", "telegram_id = ? AND status = 'approved'", (
                    telegram_id,)
            )
            logger.debug(f"📦 PREMIUM info fetched: {premium_info}")
            if premium_info:
                logger.info(
                    f"✅ User {telegram_id} is PREMIUM. Upsocial_service staff table.")
                self.db.update(
                    "staff", {
                        "is_premium": "approved"}, "telegram_id = ?", (telegram_id,)
                )
            else:
                logger.info(f"ℹ️ User {telegram_id} is NOT PREMIUM.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            user = self.db.select_dict(
                "staff", "telegram_id = ?", (telegram_id,))
            logger.debug(f"👤 Staff info fetched: {user}")
            if not user:
                logger.warning(
                    f"❌ No staff found for telegram_id={telegram_id}.")
                self.bot.send_message(
                    chat_id, "❌ اطلاعات شما یافت نشد. لطفاً ثبت‌نام را دوباره انجام دهید.")
                return
            user_code = user[0]["U_code"]
            logger.info(
                f"✅ Retrieved U_code={user_code} for telegram_id={telegram_id}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                reqs = self.db.select_dict("service_requests", "PU_code = ? AND status IN ('approved','finalized')", (user_code,))
                logger.debug(f"[login_menu] Found {len(reqs)} pending requests for user {telegram_id}")
            except Exception as e:
                logger.exception(f"[login_menu] Failed to load pending requests → telegram_id={telegram_id}")
                reqs = []
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = "📨 درخواست‌ها"
            # Internal implementation note: legacy behavior is preserved during modernization.
            if reqs:
                pending_count = len(reqs)
                button = f"📨 درخواست‌ها ({pending_count})"
                # markup.add(button)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add("📢 ساخت آگهی", button)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup.add("⚙️ تنظیمات بیشتر")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                "لطفا بخش مورد نظر را انتخاب کنید:",
                reply_markup=markup
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.register_next_step_handler(message, self.process_login_selection)
        except Exception as e:
            logger.exception(f"[login_menu] Failed to show login menu → error: {e}")
    def login_menu2(self, message):
        chat_id = message.chat.id
        telegram_id = message.from_user.id
        logger.info(
            f"🔔 Entering login_menu for telegram_id={telegram_id}, chat_id={chat_id}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_info = self.db.select_dict(
            "premium_staff", "telegram_id = ? AND status = 'approved'", (
                telegram_id,)
        )
        logger.debug(f"📦 PREMIUM info fetched: {premium_info}")
        if premium_info:
            logger.info(
                f"✅ User {telegram_id} is PREMIUM. Upsocial_service staff table.")
            self.db.update(
                "staff", {
                    "is_premium": "approved"}, "telegram_id = ?", (telegram_id,)
            )
        else:
            logger.info(f"ℹ️ User {telegram_id} is NOT PREMIUM.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        user = self.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        logger.debug(f"👤 Staff info fetched: {user}")
        if not user:
            logger.warning(
                f"❌ No staff found for telegram_id={telegram_id}.")
            self.bot.send_message(
                chat_id, "❌ اطلاعات شما یافت نشد. لطفاً ثبت‌نام را دوباره انجام دهید.")
            return
        user_code = user[0]["U_code"]
        logger.info(
            f"✅ Retrieved U_code={user_code} for telegram_id={telegram_id}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        reqs = self.db.select_dict(
            "service_requests", "PU_code = ? AND status = 'approved'", (user_code,))
        logger.debug(f"📥 Pending requests fetched: count={len(reqs)}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if reqs:
            pending_count = len(reqs)
            button = f"🔔 درخواست‌های در انتظار پاسخ({pending_count})"
            markup.add(button)
            logger.info(f"🔔 Added pending requests button: {button}")
        else:
            logger.info("ℹ️ No pending requests to show.")
        markup.add("پنل کاری", "حساب کاربری")
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = self.add_back_buttons(markup)
        logger.debug("✅ Final menu markup constructed.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id, "لطفا بخش مورد نظر را انتخاب کنید:", reply_markup=markup
        )
        logger.info(f"📤 Sent login menu to chat_id={chat_id}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(
            message, self.process_login_selection2
        )
        logger.debug("🔄 Registered next step handler: process_login_selection")
    def process_login_selection2(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None if message.text else None
        if self.is_back(message):
                return
        if self.parent.it_work_any_time(message):
            return
        if text == "پنل کاری":
            self.show_work_panel(message)
        elif text == "راهنما":
            self.show_help_menu(message)
        elif text == "حساب کاربری":
            self.parent.user_account_handler.show_account_menu(message)
        elif text and text.startswith("🔔 درخواست‌های در انتظار پاسخ"):
            return self.parent.requests_handler.show_pending_requests_menu(message)
            # come
        else:
            self.bot.send_message(
                chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_login_selection)
    def process_login_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            telegram_id = message.from_user.id
            text = message.text.strip() if message.text else None
            logger.debug(f"[process_login_selection] Received message → chat_id={chat_id}, telegram_id={telegram_id}, text={repr(text)}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                logger.info(f"[process_login_selection] Detected BACK command → returning to main menu | chat_id={chat_id}")
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not text:
                logger.warning(f"[process_login_selection] Empty or invalid message received → chat_id={chat_id}")
                self.bot.send_message(chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
                return self.bot.register_next_step_handler(message, self.process_login_selection)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text.endswith(")") and "(" in text:
                original = text
                text = text[:text.rfind('(')].strip()
                logger.debug(f"[process_login_selection] Cleaned text from {original} → {text}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.parent.it_work_any_time(message):
                logger.debug(f"[process_login_selection] Global function handled message → chat_id={chat_id}")
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text.startswith("🔔 درخواست‌های در انتظار پاسخ"):
                logger.info(f"[process_login_selection] Selected → Pending Requests | chat_id={chat_id}")
                return self.parent.requests_handler.show_pending_requests_menu(message)
            elif text == "📢 ساخت آگهی":
                logger.info(f"[process_login_selection] Selected → Ad Creation | chat_id={chat_id}")
                return self.parent.ad_creation_handler.start_featured_ad(message)
            elif text.startswith("📨 درخواست‌ها"):
                logger.info(f"[process_login_selection] Selected → Requests | chat_id={chat_id}")
                return self.parent.requests_handler.show_requests_category_menu(message)
            elif text == "⚙️ تنظیمات بیشتر":
                logger.info(f"[process_login_selection] Selected → More Settings | chat_id={chat_id}")
                return self.login_menu2(message)
            elif text == "پنل کاری":
                logger.info(f"[process_login_selection] Selected → Work Panel | chat_id={chat_id}")
                return self.show_work_panel(message)
            elif text == "راهنما":
                logger.info(f"[process_login_selection] Selected → Help | chat_id={chat_id}")
                return self.show_help_menu(message)
            elif text == "حساب کاربری":
                logger.info(f"[process_login_selection] Selected → User Account | chat_id={chat_id}")
                return self.parent.user_account_handler.show_account_menu(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.warning(f"[process_login_selection] Invalid selection received → text={text} | chat_id={chat_id}")
            self.bot.send_message(chat_id, "❌ لطفا فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(message, self.process_login_selection)
        except Exception as e:
            logger.exception(f"[process_login_selection] Unexpected error occurred → chat_id={message.chat.id} | error: {e}")
            self.bot.send_message(message.chat.id, "⚠️ خطایی رخ داده است. لطفا دوباره تلاش کنید.")
            self.bot.register_next_step_handler(message, self.process_login_selection)
