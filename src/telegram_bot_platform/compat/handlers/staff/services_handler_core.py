from __future__ import annotations

from .services_handler_context import *


class ServicesHandlerCoreMixin:
    def is_back(self, message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            txt: str = (message.text or "").strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not txt:
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            def _goto(target_callable):
                """Legacy-compatible behavior preserved for this callable."""
                try:
                    self.bot.clear_step_handler_by_chat_id(chat_id)
                except Exception:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    logger.debug("[is_back] step-handler not found | chat_id=%s", chat_id)
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.data.get(chat_id, {}).pop("_back_target", None)
                # Internal implementation note: legacy behavior is preserved during modernization.
                target_callable(message)
            if txt == "✔️ ذخیره و بازگشت":
                message.text = "تنظیمات آکهی ⚙️"
                self.handle_services(message ,_bypass_back=True)
                return True
            # Internal implementation note: legacy behavior is preserved during modernization.
            if txt == "/start":
                logger.info("[is_back] /start → show_ads_menu | chat_id=%s", chat_id)
                _goto(self.parent.login_handler.show_ads_menu)
                return True
            # Internal implementation note: legacy behavior is preserved during modernization.
            if txt.startswith(START_CMD_PREFIXES):
                logger.info("[is_back] deep-link → work_panel | chat_id=%s", chat_id)
                _goto(self.parent.login_handler.show_work_panel)
                return True
            # Internal implementation note: legacy behavior is preserved during modernization.
            if txt == BACK_TO_PANEL:
                logger.info("[is_back] BACK_TO_PANEL → work_panel | chat_id=%s", chat_id)
                _goto(self.parent.login_handler.show_work_panel)
                return True
            # Internal implementation note: legacy behavior is preserved during modernization.
            if txt == BACK_GENERIC:
                logger.info("[is_back] BACK_GENERIC pressed | chat_id=%s", chat_id)
                target = self.data.get(chat_id, {}).get("_back_target")
                if callable(target):
                    _goto(target)                     # Internal implementation note: legacy behavior is preserved during modernization.
                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    _goto(lambda m: self.show_ad_settings(m, _bypass_back=True))
                return True
            # Internal implementation note: legacy behavior is preserved during modernization.
            return False
        except Exception as exc:
            logger.exception("[is_back] unexpected error | chat_id=%s | err=%s", chat_id, exc)
            return False
    def add_back_button(self,markup, label="🔙 بازگشت"):
        """Legacy-compatible behavior preserved for this callable."""
        for row in markup.keyboard:
            if label in row:          # Internal implementation note: legacy behavior is preserved during modernization.
                return markup
        markup.add(label)
        return markup
    def get_u_code(self, chat_id):
        result = self.db.select_dict(
            "staff", condition="telegram_id = ?", params=(chat_id,))
        if result:
            return result[0]["U_code"]
        else:
            raise ValueError(
                "❌ کاربر در جدول staff با telegram_id یافت نشد.")
    def show_ad_settings(self, message, *, _bypass_back=False):
        """Legacy-compatible behavior preserved for this callable."""
        return self.handle_services(message, _bypass_back=_bypass_back)
    def process_ad_settings(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "🔙 بازگشت به پنل":
            self.parent.login_handler.show_work_panel(message)
            return
        elif text == "خدمات ♨️":
            self.handle_services(message)
        elif text == "تعیین قیمت💲":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("🔙 بازگشت به پنل")
            self.bot.send_message(
                chat_id,  "مبلغ خود را وارد کنید", reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.get_service_price)
        elif text == "ویرایش قیمت💲":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("🔙 بازگشت به پنل")
            self.bot.send_message(
                chat_id,  "مبلغ خود را وارد کنید", reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.get_service_price)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید ")
            self.bot.register_next_step_handler(message, self.show_ad_settings)
    def get_service_price(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        raw_text = message.text.strip()
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if raw_text == "🔙 بازگشت به پنل":
            return self.show_ad_settings(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        raw_text = raw_text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        raw_text = raw_text.replace(" ", "")
        # Internal implementation note: legacy behavior is preserved during modernization.
        raw_text = raw_text.replace(",", "")
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if "." in raw_text:                           # Internal implementation note: legacy behavior is preserved during modernization.
                amount = int(float(raw_text) * 1_000_000)
            else:
                value = int(raw_text)
                amount = value * 1_000 if value < 100_000 else value  # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not (min(BASE_PRICE_FILTER) <= amount <= max(BASE_PRICE_FILTER)) or amount % 1_000 != 0:
                self.bot.send_message(
                    chat_id,
                    MESSAGES["invalid_price"].format(min_price = min(BASE_PRICE_FILTER), max_price=max(BASE_PRICE_FILTER))
                    # (MESSAGES["pleace_enter_base_price"].format(min_price = min(BASE_PRICE_FILTER), max_price=max(BASE_PRICE_FILTER))
                )
                return self.bot.register_next_step_handler(message, self.get_service_price)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(
                "staff",
                {"service_price": amount},
                "telegram_id = ? AND status = 'approved'",
                (message.from_user.id,)
            )
            short = self._format_price_short(amount)           # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                f"✅ قیمت ثبت شد: {amount:,} تومان ({short})"   # Internal implementation note: legacy behavior is preserved during modernization.
            )
            logger.info(f"Service price set for user {message.from_user.id}: {amount}")
        except ValueError:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "❌ لطفاً فقط عدد معتبر وارد کنید.")
            return self.bot.register_next_step_handler(message, self.get_service_price)
        except Exception as e:
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.exception(f"Error when saving service price: {e}")
            self.bot.send_message(chat_id, "⚠️ خطا در ثبت مبلغ. لطفاً بعداً دوباره تلاش کنید.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.show_ad_settings(message)
    def handle_services(self, message, *, _bypass_back=False):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if not _bypass_back and self.is_back(message):
            return
        # Check if user is PREMIUM
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
        ucode = user[0]["U_code"]
        # Default: not PREMIUM
        is_premium = False
        if self.dev_mode_premium_access:
            is_premium = True
        elif user[0]["is_premium"] == 'approved':
            is_premium = True
        elif self.db.table_exists("premium_staff"):
            premium_data = self.db.select_dict(
                "premium_staff", "U_code = ? AND telegram_id = ?", (ucode, chat_id))
            if premium_data and premium_data[0].get("status", "").lower() == "approved":
                is_premium = True
                if not self.db.column_exists("staff", "is_premium"):
                    self.db.add_column("staff", "is_premium", "TEXT")
                self.db.update(
                    "staff", {"is_premium": "approved"}, "U_code = ?", (ucode,))
        return self.show_combined_services(message, is_premium)
    def show_combined_services(self, message, is_premium: bool) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        staff_row = self.db.select_dict(
            "staff", "telegram_id = ?", (chat_id,)
        )
        staff = staff_row[0] if staff_row else {}
        ucode = staff.get("U_code")
        service_row = {}
        if ucode:
            rows = self.db.select_dict("services", "U_code = ?", (ucode,))
            if rows:
                service_row = rows[0]
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons: list[str] = []
        # Internal implementation note: legacy behavior is preserved during modernization.
        for key, cfg in regular_services_config.items():
            if key in ("confirm", "view"):
                continue
            title = cfg["title"]
            # Internal implementation note: legacy behavior is preserved during modernization.
            price_field = f"{key}_price"
            price = int(service_row.get(price_field, 0) or 0)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if key == "service_group":
                group_option_b_price = int(service_row.get("group_option_b_price", 0) or 0)
                group_option_a_price = int(service_row.get("group_option_a_price", 0) or 0)
                price     = group_option_b_price or group_option_a_price
            if price:
                title += f" ({self._format_price_short(price)})"
            buttons.append(title)
        # Internal implementation note: legacy behavior is preserved during modernization.
        for key, cfg in services_config.items():
            if cfg.get("category") != "premium" or key == "confirm":
                continue
            title = cfg["title"]
            price = int(service_row.get(f"{key}_price", 0) or 0)
            if not is_premium:
                title = f"🚫 {title}"
            if price:
                title += f" ({self._format_price_short(price)})"
            buttons.append(title)
        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons.append(regular_services_config["view"]["title"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        base_price = int(staff.get("service_price", 0) or 0)
        price_btn  = "قیمت تک سرویس💲"
        if base_price:
            price_btn += f" ({self._format_price_short(base_price)})"
        markup.add(price_btn)
        # Internal implementation note: legacy behavior is preserved during modernization.
        for i in range(0, len(buttons), 2):
            markup.add(*buttons[i : i + 2])
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(regular_services_config["confirm"]["title"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            "لطفاً خدمات مورد نظر را انتخاب کنید:",
            reply_markup=markup,
        )
        self.bot.register_next_step_handler(
            message, lambda msg: self.handle_combined_choice(msg, is_premium)
        )
    def handle_combined_choice(self, message: Message, is_premium: bool) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text or ""
        chat_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        raw = text.lstrip("🚫 ").strip()
        base_title = re.sub(r"\s*\(.*\)$", "", raw)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if base_title == "بازگشت به پنل":
            return self.parent.login_handler.show_work_panel(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if base_title.startswith("قیمت تک سرویس"):
            return self._prompt_base_service_price(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        for key, cfg in regular_services_config.items():
            if key in ("confirm", "view"): continue
            if base_title == cfg["title"]:
                handler_map = {
                    "back": self.handle_back_service,
                    "service_group": self.handle_service_group,
                    "confirm": self.finalize_service_selection,
                    "view": self.show_my_all_services,
                }
                return handler_map.get(key, self._unknown_service)(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if base_title == regular_services_config["view"]["title"]:
            return self.show_my_all_services(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        for key, cfg in services_config.items():
            if cfg.get("category") != "premium" or key == "confirm": continue
            if base_title == cfg["title"]:
                if not is_premium:
                    return self.show_premium_access_denied(message)
                handler = getattr(self, f"handle_{key}_service", None)
                if handler:
                    return handler(message)
                return self._unknown_service(message)
        if text == "✔️ ذخیره و بازگشت":
            message.text = "آگهی ها 📢"
            self.parent.login_handler.show_ads_menu(message)
            return 
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
        return self.show_combined_services(message, is_premium)
    def _prompt_base_service_price(self, message: Message) -> None:
        chat_id = message.chat.id
        staff = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        price = int((staff[0].get("service_price") if staff else 0) or 0)
        caption = (
            (f"💲 قیمت فعلی: {price:,} تومان\n\n") if price else ""
        ) + MESSAGES["pleace_enter_base_price"].format(
            min_price=min(BASE_PRICE_FILTER), max_price=max(BASE_PRICE_FILTER)
        )
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(chat_id, caption, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.get_service_price)
    def _unknown_service(self, message: Message) -> None:
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "❌ این سرویس هنوز پیاده‌سازی نشده است.")
    def show_premium_access_denied(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔐 درخواست عضویت PREMIUM", "🔙 بازگشت")
        self.bot.send_message(
            chat_id,
            "🚫 برای استفاده از «خدمات PREMIUM» باید ابتدا عضو PREMIUM شوید.\n\n"
            "در صورت تمایل می‌توانید درخواست عضویت PREMIUM ثبت کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_premium_request_flow)
    def _return_to_service_menu(self, message, service_key: str):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.handle_service_price_input(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        handler = getattr(self, f"handle_{service_key}_service", None)
        if handler:
            return handler(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        return self.handle_services(message)
    def handle_premium_request_flow(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "🔙 بازگشت":
            self.handle_services(message)
            return 
        if self.is_back(message):
            return
        if text == "🔐 درخواست عضویت PREMIUM":
            user = self.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if not user:
                self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
                return 
            user = user[0]
            ucode = user["U_code"]
            telegram_id = user["telegram_id"]
            # Step 1: Create premium_staff table if needed
            self.db.create_table("premium_staff", {
                "U_code": "TEXT UNIQUE",
                "telegram_id": "INTEGER",
                "status": "TEXT"
            })
            # Step 2: Insert or update PREMIUM row
            existing = self.parent.db.select_dict(
                "premium_staff", "U_code = ? AND telegram_id = ?", (ucode, telegram_id))
            if existing and existing[0].get("status", "").lower() == "pending":
                self.bot.send_message(chat_id, "⏳ درخواست شما برای عضویت PREMIUM در حال بررسی است.\n"
                                               "پس از تایید می‌توانید آگهی PREMIUM ایجاد کنید.")
                return self.handle_services(message)
            # Step 3: Insert or update PREMIUM entry
            self.parent.db.upsert("premium_staff", {
                "U_code": ucode,
                "telegram_id": telegram_id,
                "status": "pending"
            }, key="U_code")
            # Step 3: Add 'is_premium' column to staff if needed
            if not self.db.column_exists("staff", "is_premium"):
                self.db.add_column("staff", "is_premium", "TEXT")
            # Step 4: Update is_premium status in staff
            self.db.update(
                "staff", {"is_premium": "requested"}, "U_code = ?", (ucode,))
            # Step 5: Notify user
            self.bot.send_message(
                chat_id, "✅ درخواست شما برای عضویت PREMIUM ثبت شد. منتظر بررسی ادمین باشید.")
            return self.handle_services(message)
    def handle_premium_service_choice(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        for key, config in services_config.items():
            if text == config["title"]:
                if key == "confirm":
                    self.handle_service_price_input(message)
                    self.bot.send_message(chat_id, "✅ تغییرات ذخیره شدند.")
                    return self.handle_services(message)
                else:
                    handler_name = f"handle_{key}_service"
                    if hasattr(self, handler_name):
                        return getattr(self, handler_name)(message)
                    else:
                        self.bot.send_message(
                            chat_id, "❌ این سرویس هنوز پیاده‌سازی نشده است.")
                        return self.handle_services(message)
        if text == "📝 مشاهده خدمات من":
            return self.show_my_premium_services(message)
        self.bot.send_message(
            chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
        return self.handle_services(message)
    def handle_candles_music_service(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        is_candles_music_on = premium_data.get("candles_music", False)
        candles_label = "🕯️🎶 روشن کردن شمع و موزیک (فعال)" if is_candles_music_on else "🕯️🎶 روشن کردن شمع و موزیک"
        drinks_label = "🍷 نوشیدنی‌ها"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(candles_label, drinks_label)
        # markup.add()
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.bot.send_message(
            chat_id,
            "لطفاً یک گزینه را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_candles_music_options)
