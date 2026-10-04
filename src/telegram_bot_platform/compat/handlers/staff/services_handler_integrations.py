from __future__ import annotations

from .services_handler_context import *


class ServicesHandlerIntegrationsMixin:
    def handle_back_options(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        service_data = self.data.setdefault(
            chat_id, {}).setdefault("regular_services", {})
        if self.is_back(message):
            return
        if text == "🔁 فعال کردن":
            service_data["back"] = True
            self.bot.send_message(chat_id, "✅ سرویس «گزینه خدمات ۱» فعال شد.")
            self.handle_service_price_input2(chat_id)
            return self.handle_back_service(message)
        elif text == "🔁 غیرفعال کردن":
            service_data["back"] = False
            self.bot.send_message(chat_id, "❌ سرویس «گزینه خدمات ۱» غیرفعال شد.")
            self.handle_service_price_input2(chat_id)
            return self.handle_back_service(message)
        elif text in ["💰 تعیین قیمت", "✏️ ویرایش قیمت"]:
            self._set_pending_service(chat_id, 'regular_services', 'back', 'گزینه خدمات ۱')
            self.bot.send_message(
                chat_id,
                "💰 لطفاً قیمت این سرویس را وارد کنید (۳۰۰,۰۰۰ تا ۵۰۰,۰۰۰):",
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.handle_service_price_input2(chat_id)
            return self.bot.register_next_step_handler(message, self.receive_back_price)
        elif text == regular_services_config["confirm"]["title"]:
            return self.handle_services(message)
        elif text == "🔙 بازگشت":
            return self.handle_services(message)
        else:
            self.bot.send_message( 
                chat_id, "❌ لطفاً از گزینه‌های معتبر استفاده کنید.")
            self.handle_back_service(message)
    def handle_service_group(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🧩 تنظیم گزینه خدمات B", "🧩 تنظیم گزینه خدمات A")
        markup.add(regular_services_config["confirm"]["title"])
        if self.is_back(message):
            return
        self.bot.send_message(
            chat_id,
            "🧩 لطفاً یکی از حالت‌های گروه خدمات را برای تنظیم انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_service_group_mode_selection)
    def handle_service_group_mode_selection(self, message):
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "🧩 تنظیم گزینه خدمات B":
            return self.handle_group_option_b_service(message)
        elif text == "🧩 تنظیم گزینه خدمات A":
            return self.handle_group_option_a_service(message)
        elif text == regular_services_config["confirm"]["title"]:
            return self.handle_services(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً از گزینه‌های معتبر استفاده کنید.")
            return self.handle_service_group(message)
    def handle_group_option_b_service(self, message):
        chat_id = message.chat.id
        service_data = self.data.setdefault(
            chat_id, {}).setdefault("regular_services", {})
        if self.is_back(message):
            return
        is_active = service_data.get("group_option_b", False)
        has_price = "group_option_b_price" in service_data
        toggle_label = "🔁 غیرفعال کردن" if is_active else "🔁 فعال کردن"
        price_label = "✏️ ویرایش قیمت" if has_price else "💰 تعیین قیمت"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(price_label, toggle_label)
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id,
            "🧩 لطفاً گزینه مورد نظر برای سرویس «گزینه خدمات B» را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self.handle_group_option_b_options)
    def handle_group_option_b_options(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        service_data = self.data.setdefault(
            chat_id, {}).setdefault("regular_services", {})
        if self.is_back(message):
            return
        if text == "🔁 فعال کردن":
            if "group_option_b_price" not in service_data:
                self.bot.send_message(
                    chat_id, "❗ ابتدا باید قیمت این سرویس را وارد کنید.")
                return self.handle_group_option_b_service(message)
            service_data["group_option_b"] = True
            service_data["group_option_a"] = False
            service_data.pop("group_option_a_code", None)
            self.bot.send_message(chat_id, "✅ سرویس «گزینه خدمات B» فعال شد.")
            self.handle_service_price_input2(chat_id)
            return self.handle_group_option_b_service(message)
        elif text == "🔁 غیرفعال کردن":
            service_data["group_option_b"] = False
            self.bot.send_message(
                chat_id, "❌ سرویس «گزینه خدمات B» غیرفعال شد.")
            self.handle_service_price_input2(chat_id)
            return self.handle_group_option_b_service(message)
        elif text in ["💰 تعیین قیمت", "✏️ ویرایش قیمت"]:
            self._set_pending_service(chat_id, 'regular_services', 'group_option_b', 'گزینه خدمات B')
            self.bot.send_message(
                chat_id,
                "💰 لطفاً قیمت این سرویس را وارد کنید (۳۰۰,۰۰۰ تا ۵۰۰,۰۰۰):",
            )
            return self.bot.register_next_step_handler(message, self.receive_group_option_b_price)
        elif text == "🔙 بازگشت":
            return self.handle_service_group(message)
        else:
            self.bot.send_message(chat_id, "❌ لطفاً گزینه معتبر انتخاب کنید.")
            self.handle_group_option_b_service(message)
    def receive_group_option_b_price(self, message):
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        if self.is_back(message):
            return
        if raw == "🔙 بازگشت":
            return self.handle_group_option_b_service(message)
        try:
            amount = self.parse_price(raw, min_amount=300_000, max_amount=500_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, self.receive_group_option_b_price)
        self.data.setdefault(chat_id, {}).setdefault(
            "regular_services", {})["group_option_b_price"] = amount
        short = self._format_price_short(amount)
        self.bot.send_message(chat_id, f"✅ قیمت ثبت شد: {amount:,} تومان ({short})")
        self.handle_service_price_input(message)
        return self.handle_group_option_b_service(message)
    def handle_group_option_a_service(self, message):
        chat_id = message.chat.id
        service_data = self.data.setdefault(
            chat_id, {}).setdefault("regular_services", {})
        if self.is_back(message):
            return
        is_active = service_data.get("group_option_a", False)
        has_price = "group_option_a_price" in service_data
        has_code = "group_option_a_code" in service_data
        toggle_label = "🔁 غیرفعال کردن" if is_active else "🔁 فعال کردن"
        price_label = "✏️ ویرایش قیمت" if has_price else "💰 تعیین قیمت"
        code_label = "👤 وارد کردن کد مشارکت‌کننده" if not has_code else f"👤 ویرایش کد مشارکت‌کننده ({service_data['group_option_a_code']})"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(code_label)
        markup.add(price_label, toggle_label)
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id,
            "🧩 لطفاً گزینه مورد نظر برای سرویس «گزینه خدمات A» را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(message, self.handle_group_option_a_options)
    def handle_group_option_a_options(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        service_data = self.data.setdefault(
            chat_id, {}).setdefault("regular_services", {})
        if self.is_back(message):
            return
        if "کد مشارکت‌کننده" in text:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("🔙 بازگشت")
            self.bot.send_message(
                chat_id, "📨 لطفاً کد کاربری (U_code) نفر دوم را وارد کنید:", reply_markup=markup)
            return self.bot.register_next_step_handler(message, self.receive_group_option_a_code_and_return_here)
        elif text in ["💰 تعیین قیمت", "✏️ ویرایش قیمت"]:
            self._set_pending_service(chat_id, 'regular_services', 'group_option_a', 'گزینه خدمات A')
            self.bot.send_message(
                chat_id,
                "💰 لطفاً قیمت این سرویس را وارد کنید (۳۰۰,۰۰۰ تا ۵۰۰,۰۰۰):",
            )
            return self.bot.register_next_step_handler(message, self.receive_group_option_a_price)
        elif text == "🔁 فعال کردن":
            if "group_option_a_price" not in service_data or "group_option_a_code" not in service_data:
                self.bot.send_message(
                    chat_id, "❗ برای فعال‌سازی، ابتدا باید کد مشارکت‌کننده و قیمت را وارد کنید.")
                return self.handle_group_option_a_service(message)
            service_data["group_option_a"] = True
            service_data["group_option_b"] = False
            self.bot.send_message(chat_id, "✅ سرویس «گزینه خدمات A» فعال شد.")
            self.handle_service_price_input2(chat_id)
            return self.handle_group_option_a_service(message)
        elif text == "🔁 غیرفعال کردن":
            service_data["group_option_a"] = False
            self.bot.send_message(
                chat_id, "❌ سرویس «گزینه خدمات A» غیرفعال شد.")
            self.handle_service_price_input2(chat_id)
            return self.handle_group_option_a_service(message)
        elif text == "🔙 بازگشت":
            return self.handle_service_group(message)
        else:
            self.bot.send_message(chat_id, "❌ لطفاً گزینه معتبر انتخاب کنید.")
            self.handle_group_option_a_service(message)
    def receive_group_option_a_price(self, message):
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        if self.is_back(message):
            return
        if raw == "🔙 بازگشت":
            return self.handle_group_option_a_service(message)
        try:
            amount = self.parse_price(raw, min_amount=300_000, max_amount=500_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, self.receive_group_option_a_price)
        self.data.setdefault(chat_id, {}).setdefault(
            "regular_services", {})["group_option_a_price"] = amount
        short = self._format_price_short(amount)
        self.bot.send_message(chat_id, f"✅ قیمت ثبت شد: {amount:,} تومان ({short})")
        self.handle_service_price_input(message)
        return self.handle_group_option_a_service(message)
    def receive_group_option_a_code_and_return_here(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.handle_group_option_a_service(message)
        if self.is_back(message):
            return
        service_data = self.data.setdefault(
            chat_id, {}).setdefault("regular_services", {})
        user = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر شما یافت نشد.")
        sender = user[0]
        sender_code = sender.get("U_code")
        sender_name = sender.get("name", "کاربر")
        if text == sender_code:
            self.bot.send_message(
                chat_id, "❌ نمی‌توانید کد کاربری خودتان را وارد کنید.")
            return self.bot.register_next_step_handler(message, self.receive_group_option_a_code_and_return_here)
        target = self.db.select_dict("staff", "U_code = ?", (text,))
        if not target:
            self.bot.send_message(
                chat_id, "❌ کاربر با این کد پیدا نشد. لطفاً دوباره امتحان کنید یا دکمه بازگشت را بزنید.")
            return self.bot.register_next_step_handler(message, self.receive_group_option_a_code_and_return_here)
        # Internal implementation note: legacy behavior is preserved during modernization.
        price = service_data.get("group_option_a_price")
        if not price:
            self.bot.send_message(chat_id, "❗ لطفاً ابتدا قیمت را وارد کنید.")
            return self.handle_group_option_a_service(message)
        service_data["group_option_a_code"] = text
        existing = self.db.select_dict(
            "group_option_a_requests", "from_u = ? AND to_u = ?", (sender_code, text))
        if existing and existing[0]["p_status"] == "pending":
            self.bot.send_message(
                chat_id, "📨 درخواست قبلی شما در انتظار تأیید است.")
        else:
            self.db.insert("group_option_a_requests", {
                "from_u": sender_code,
                "to_u": text,
                "price": price,
                "p_status": "pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            self.parent.requests_handler.create_request(
                U_code=sender_code,
                telegram_id=sender.get("telegram_id"),
                request_type="Group Service Request",
                content=f"🔁 درخواست FMF از طرف {sender_name} با قیمت {price:,} تومان\nآیا مایل به پذیرش این درخواست هستید؟",
                target_U_code=text
            )
            participant = target[0]
            participant_chat_id = participant.get("telegram_id")
            if participant_chat_id:
                self.bot.send_message(
                    participant_chat_id,
                    f"📨 یک درخواست FMF جدید از طرف {sender_name} دریافت کرده‌اید. برای مشاهده و پاسخ دادن به درخواست، به بخش «📨 درخواست‌ها» در منوی حساب کاربری بروید."
                )
            self.bot.send_message(
                chat_id, f"✅ درخواست FMF برای {text} ارسال شد. منتظر پاسخ باشید.")
        self.bot.send_message(chat_id, f"👤 کد مشارکت‌کننده با موفقیت ثبت شد: {text}")
        self.handle_service_price_input(message)
        return self.handle_group_option_a_service(message)
    def finalize_service_selection(self, message):
        chat_id = message.chat.id
        user = self.db.select_dict(
            "staff", "telegram_id = ?", (chat_id,)
        )
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
        U_code = user[0]["U_code"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        reg_data = self.data.get(chat_id, {}).get("regular_services", {})
        reg_row = {"U_code": U_code}
        reg_row.update(reg_data)
        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_data = self.data.get(chat_id, {}).get("premium_services", {})
        premium_row = {"U_code": U_code}
        premium_row.update(premium_data)
        # Internal implementation note: legacy behavior is preserved during modernization.
        clothes = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
        if clothes:
            premium_row["custom_clothes"] = json.dumps(clothes, ensure_ascii=False)
        # Internal implementation note: legacy behavior is preserved during modernization.
        combined_row = {**reg_row, **premium_row}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.upsert("services", combined_row, key="U_code")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id, "✅ اطلاعات خدمات شما با موفقیت ذخیره شد.")
        return self.parent.login_handler.show_ads_menu(message)
    def parse_price(
        self,
        text: str,
        *,
        min_amount: int | None = None,
        max_amount: int | None = None
    ) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        if not isinstance(text, str):
            raise ValueError("input must be a string")
        # Internal implementation note: legacy behavior is preserved during modernization.
        raw = (
            text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
                .replace(",", "")
                .replace(" ", "")
                .strip()
        )
        if not raw:
            raise ValueError("empty input")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if "." in raw:
            amount = int(float(raw) * 1_000_000)
        else:
            val = int(raw)
            amount = val * 1_000 if (len(raw) <= 4 or val < 100_000) else val
        # Internal implementation note: legacy behavior is preserved during modernization.
        if max_amount:
            while amount > max_amount and amount % 10 == 0:
                amount //= 10
        # Internal implementation note: legacy behavior is preserved during modernization.
        if amount % 1_000 != 0:
            raise ValueError("amount must be a multiple of 1 000")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if min_amount and amount < min_amount:
            raise ValueError(f"amount must be ≥ {min_amount:,}")
        if max_amount and amount > max_amount:
            raise ValueError(f"amount must be ≤ {max_amount:,}")
        return amount
    def _format_price_short(self, amount: int) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if amount is None:
            return ""
        if amount >= 1_000_000:
            # Internal implementation note: legacy behavior is preserved during modernization.
            txt = f"{amount/1_000_000:.1f}".rstrip("0").rstrip(".")
            return f"{txt} میلیون"
        return f"{amount//1_000:,}".replace(",", "") + " هزار"
    def _set_pending_service(self, chat_id: int, category: str, key: str, title: str):
        """Legacy-compatible behavior preserved for this callable."""
        self.data.setdefault(chat_id, {})['pending_service'] = {
            'category': category,
            'key': key,
            'title': title
        }
    def handle_service_price_input2(self, chat_id: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            logger.info("[ServicesSave] start chat_id=%s", chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            u_code: str = self.get_u_code(chat_id)
            premium_data: dict   = self.data.get(chat_id, {}).get("premium_services", {})
            reg_data: dict   = self.data.get(chat_id, {}).get("regular_services", {})
            clothes:  list   = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not (premium_data or reg_data or clothes):
                return logger.info("[ServicesSave] nothing to save")
            # Internal implementation note: legacy behavior is preserved during modernization.
            row = {"U_code": u_code, **premium_data, **reg_data}
            if clothes:
                row["custom_clothes"] = json.dumps(clothes, ensure_ascii=False)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # self.db.ensure_table_and_columns("services", data=row, columns=column_types)  # :contentReference[oaicite:0]{index=0}
            self.db.upsert("services", row, key="U_code")      # :contentReference[oaicite:1]{index=1}
            logger.info("[ServicesSave] saved U_code=%s", u_code)
        except Exception as exc:
            logger.exception("[ServicesSave] failed chat_id=%s", chat_id)
    def upsert_service_field(self, chat_id: int, category: str, key: str, title: str, price: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            U_code = self.get_u_code(chat_id)
            if not U_code:
                log.error(f"[ServiceUpsert] Missing U_code for chat_id={chat_id}")
                return self.bot.send_message(chat_id, "❌ خطا: کد کاربری یافت نشد.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict("services", "U_code = ?", (U_code,))
            if rows:
                record = rows[0]
                reg_json = record.get("regular_services")
                premium_json = record.get("premium_services")
            else:
                reg_json, premium_json = "{}", "{}"
            # Internal implementation note: legacy behavior is preserved during modernization.
            reg_services = json.loads(reg_json or "{}")
            premium_services = json.loads(premium_json or "{}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if category == 'regular_services':
                reg_services[key] = {"title": title, "price": price}
            elif category == 'premium_services':
                premium_services[key] = {"title": title, "price": price}
            else:
                log.error(f"[ServiceUpsert] Unknown category: {category}")
                return self.bot.send_message(chat_id, "❌ دسته‌بندی سرویس نامعتبر است.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.upsert(
                table_name="services",
                data={
                    "U_code": U_code,
                    "regular_services": json.dumps(reg_services, ensure_ascii=False),
                    "premium_services": json.dumps(premium_services, ensure_ascii=False)
                },
                unique_column="U_code"
            )
            log.info(f"[ServiceUpsert] Upserted {category} '{key}'={price} for U_code={U_code}")
        except Exception as e:
            log.exception(f"[ServiceUpsert] Failed to upsert {category} '{key}' for chat_id={chat_id}: {e}")
            raise
    def handle_service_price_input(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            price = int(text)
        except ValueError:
            return self.bot.send_message(chat_id, "❌ مبلغ نامعتبر است. لطفاً فقط عدد وارد کنید.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        user_context = self.data.get(chat_id, {})
        pending = user_context.pop('pending_service', None)
        if not pending:
            return self.bot.send_message(chat_id, "⚠️ خطا: سرویس مورد نظر پیدا نشد.")
        category = pending['category']  # Internal implementation note: legacy behavior is preserved during modernization.
        key = pending['key']
        title = pending['title']
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.upsert_service_field(
            chat_id=chat_id,
            category=category,
            key=key,
            title=title,
            price=price
        )
        log.info(f"[Service] Upserted {category}.{key}={price} for {chat_id}")
