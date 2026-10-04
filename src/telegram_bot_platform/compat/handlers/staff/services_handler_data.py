from __future__ import annotations

from .services_handler_context import *


class ServicesHandlerDataMixin:
    def preview_custom_outfits(self, message):
        chat_id = message.chat.id
        items = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
        if self.is_back(message):
            return
        if not items:
            self.bot.send_message(chat_id, "❌ هیچ محصولی ثبت نشده است.")
            return self.handle_custom_outfit_service(message)
        for item in items:
            caption = f"👗 <b>{item['description']}</b>\n💰 {item['price']:,} تومان"
            self.bot.send_photo(
                chat_id, item["file_id"], caption=caption, parse_mode="HTML")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.handle_service_price_input(message)
        self.bot.send_message(
            chat_id, "پیش‌نمایش محصول‌های ثبت‌شده:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_custom_outfit_preview_confirmation)
    def handle_custom_outfit_preview_confirmation(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "💾 ذخیره تغییرات و بازگشت":
            self.handle_service_price_input(message)
            self.bot.send_message(chat_id, "✅ محصول‌ها ذخیره شدند.")
            return self.handle_services(message)
        self.bot.send_message(
            chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
        return self.preview_custom_outfits(message)
    def handle_social_service_service(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        is_enabled = premium_data.get("social_service", False)
        label = "🤝 غیرفعال کردن خدمات تعاملی" if is_enabled else "🤝 فعال‌سازی خدمات تعاملی"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(label)
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.bot.send_message(
            chat_id, "👫 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_social_service_toggle)
    def handle_social_service_toggle(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if self.is_back(message):
            return
        if "خدمات تعاملی" in text:
            current = premium_data.get("social_service", False)
            premium_data["social_service"] = not current
            status = "✅ فعال شد" if not current else "❌ غیرفعال شد"
            self.bot.send_message(chat_id, f"{status}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.handle_service_price_input2(chat_id)
            return self.handle_social_service_service(message)
        elif text == "💾 ذخیره تغییرات و بازگشت":
            self.handle_service_price_input(message)
            return self.handle_services(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های معتبر استفاده کنید.")
            return self.handle_social_service_service(message)
    def handle_massage_service(self, message):
        chat_id = message.chat.id
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        if self.is_back(message):
            return
        is_on = premium_data.get("massage", False)
        has_price = "massage_price" in premium_data
        toggle_label = "💅🏻 غیرفعال کردن خدمت ویژه" if is_on else "💅🏻 فعال‌سازی خدمت ویژه"
        price_label = "💰 ویرایش قیمت" if has_price else "💰 تعیین قیمت"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(toggle_label, price_label)
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.bot.send_message(
            chat_id,
            "💅🏻 لطفاً یک گزینه را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_massage_options)
    def handle_massage_options(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if self.is_back(message):
            return
        if "فعال‌سازی" in text or "غیرفعال کردن" in text:
            current = premium_data.get("massage", False)
            premium_data["massage"] = not current
            status = "✅ فعال شد" if not current else "❌ غیرفعال شد"
            self.bot.send_message(chat_id, f"{status}")
            self.handle_service_price_input2(chat_id)
            return self.handle_massage_service(message)
        elif "قیمت" in text:
            self._set_pending_service(chat_id, 'premium_services', 'massage', 'خدمت ویژه')
            self.bot.send_message(
                chat_id,
                "💰 لطفاً مبلغ را وارد کنید (۲۰۰,۰۰۰ تا ۷۰۰,۰۰۰ تومان):",
            )
            return self.bot.register_next_step_handler(message, self.receive_massage_price)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های معتبر را انتخاب کنید.")
            self.handle_massage_service(message)
    def receive_massage_price(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        if raw == "🔙 بازگشت":
            return self.handle_massage_service(message)
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            amount = self.parse_price(raw, min_amount=200_000, max_amount=700_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, self.receive_massage_price)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data.setdefault(chat_id, {}).setdefault("premium_services", {})["massage_price"] = amount
        short = self._format_price_short(amount)
        # Internal implementation note: legacy behavior is preserved during modernization.
        caption = (
            f"✅ قیمت خدمت ویژه {amount:,} تومان ({short}) ثبت شد.\n\n"
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:\n"
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, caption)
        log.info(f"[receive_massage_price] Saved massage_price={amount} for {chat_id}")
        return self._return_to_service_menu(message, 'massage')
    def handle_special_service(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔱 گزینه A را فعال می‌کنم", "🧷 گزینه B را فعال می‌کنم")
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.bot.send_message(
            chat_id,
            "⛓️ لطفاً نقش خود را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_special_service_role_selection)
    def handle_special_service_role_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if self.is_back(message):
            return
        if text == "🔱 گزینه A را فعال می‌کنم":
            return self.handle_service_subrole(message, role="option_a")
        elif text == "🧷 گزینه B را فعال می‌کنم":
            return self.handle_service_subrole(message, role="option_b")
        elif text == "💾 ذخیره تغییرات و بازگشت":
            self.handle_service_price_input(message)
            return self.handle_services(message)
        self.bot.send_message(chat_id, "❌ لطفاً یک گزینه معتبر انتخاب کنید.")
        return self.handle_special_service(message)
    def handle_service_subrole(self, message, role):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        config = services_config["special_service"]["sub_roles"][role]
        is_on = premium_data.get(f"special_service_{role}", False)
        has_price = f"special_service_{role}_price" in premium_data
        toggle_label = f"🔘 {'غیرفعال' if is_on else 'فعال‌سازی'} {config['title']}"
        price_label = f"💰 {'ویرایش قیمت' if has_price else 'تعیین قیمت'}"
        back_label = "🔙 بازگشت"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(toggle_label, price_label)
        markup.add(back_label)
        self.bot.send_message(
            chat_id,
            f"{config['title']}:\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, lambda m: self.handle_service_subrole_options(m, role))
    def handle_service_subrole_options(self, message, role):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        text = message.text.strip() if message.text else None
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        config = services_config["special_service"]["sub_roles"][role]
        title = config["title"]
        if "فعال‌سازی" in text or "غیرفعال" in text:
            current = premium_data.get(f"special_service_{role}", False)
            premium_data[f"special_service_{role}"] = not current
            msg = f"{'✅ فعال شد' if not current else '❌ غیرفعال شد'}"
            self.bot.send_message(chat_id, msg)
            self.handle_service_price_input2(chat_id)
            return self.handle_service_subrole(message, role)
        elif "قیمت" in text:
            self._set_pending_service( chat_id, 'premium_services', f'special_service_{role}', config['title'])           
            self.bot.send_message(
                chat_id,
                f"💰 لطفاً قیمت برای {title} را وارد کنید ({config['price_range'][0]:,} تا {config['price_range'][1]:,} تومان):",
            )
            return self.bot.register_next_step_handler(message, lambda m: self.receive_special_service_price(m, role))
        elif "بازگشت" in text:
            return self.handle_special_service(message)
        else:
            self.bot.send_message(chat_id, "❌ لطفاً گزینه معتبری انتخاب کنید.")
            self.handle_service_subrole(message, role)
    def receive_special_service_price(self, message, role):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        raw = (message.text or "").strip()
        cfg = services_config["special_service"]["sub_roles"][role]
        min_p, max_p = cfg["price_range"]
        if raw == "🔙 بازگشت":
            return self.handle_service_subrole(message, role)
        try:
            amount = self.parse_price(raw, min_amount=min_p, max_amount=max_p)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, lambda m: self.receive_special_service_price(m, role))
        key = f"special_service_{role}_price"
        self.data.setdefault(chat_id, {}).setdefault(
            "premium_services", {})[key] = amount
        short = self._format_price_short(amount)
        self.bot.send_message(chat_id, f"✅ قیمت برای {cfg['title']} ذخیره شد: {amount:,} تومان ({short})")
        self.handle_service_price_input(message)
        return self.handle_service_subrole(message, role)
    def save_premium_services_to_db(self, chat_id):
        U_code = self.get_u_code(chat_id)
        premium_data = self.data.get(chat_id, {}).get("premium_services", {})
        clothes = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
        # Build data row
        row = {"U_code": U_code}
        row.update(premium_data)
        if clothes:
            row["custom_clothes"] = json.dumps(clothes, ensure_ascii=False)
        # Save using DatabaseManage
        self.db.upsert("services", data=row, key="U_code")
    def handle_regular_service_choice(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        for key, cfg in regular_services_config.items():
            if text == cfg.get("title"):
                if key == "confirm":
                    return self.finalize_service_selection(message)
                elif key == "view":
                    return self.show_my_regular_services(message)
                elif key == "back":
                    return self.handle_back_service(message)
                elif key == "service_group":
                    return self.handle_service_group(message)
        self.bot.send_message(
            chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
        return self.handle_services(message)
    def show_my_all_services(self, message):
        chat_id = message.chat.id
        U_code = self.get_u_code(chat_id)
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        if user:
            price = user[0].get("service_price")
        else:
            price = None
        price_line = f"💰 <b>قیمت تک سرویس:</b> {int(price):,} تومان\n" if price else "💰 <b>قیمت تک سرویس:</b> تعیین نشده\n"
        # Internal implementation note: legacy behavior is preserved during modernization.
        row = self.db.select_dict("services", "U_code = ?", (U_code,))
        data = row[0] if row else {}
        lines = [price_line, "📝 <b>خدمات فعال شما:</b>"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if data.get("back"):
            price = data.get("back_price")
            lines.append(
                f"🧰 گزینه خدمات ۱ - {price:,} تومان" if price else "🧰 گزینه خدمات ۱")
        if data.get("group_option_b"):
            lines.append("🧩 گزینه خدمات B")
        if data.get("group_option_a"):
            participant = data.get("group_option_a_code", "نامشخص")
            lines.append(f"🧩 گزینه خدمات تعاملی\n👤 کد مشارکت‌کننده: {participant}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if data.get("candles_music"):
            lines.append("🕯️ روشن کردن شمع و موزیک")
            if data.get("candles_music_drinks"):
                price = data.get("candles_music_drinks_price")
                lines.append(
                    f"🍷 نوشیدنی - {price:,} تومان" if price else "🍷 نوشیدنی (بدون قیمت)")
        if data.get("social_service"):
            lines.append("🤝 خدمات تعاملی")
        if data.get("massage"):
            price = data.get("massage_price")
            lines.append(
                f"💅🏻 خدمت ویژه - {price:,} تومان" if price else "💅🏻 خدمت ویژه (بدون قیمت)")
        if data.get("special_service_option_a"):
            price = data.get("special_service_option_a_price")
            lines.append(
                f"🔱 گزینه A را فعال می‌کنم - {price:,} تومان" if price else "🔱 گزینه A را فعال می‌کنم (بدون قیمت)")
        if data.get("special_service_option_b"):
            price = data.get("special_service_option_b_price")
            lines.append(
                f"🧷 گزینه B را فعال می‌کنم - {price:,} تومان" if price else "🧷 گزینه B را فعال می‌کنم (بدون قیمت)")
        clothes = data.get("custom_clothes")
        if clothes:
            try:
                clothes_list = json.loads(clothes)
                lines.append("👗 محصول‌های سفارشی:")
                for item in clothes_list:
                    lines.append(
                        f"— {item['description']} ({item['price']:,} تومان)")
            except:
                lines.append("👗 محصول‌های سفارشی (خطا در خواندن)")
        if len(lines) == 2:  # Only price and header added, no services
            lines.append("هیچ خدمتی فعال نشده است.")
        self.bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")
        return self.handle_services(message)
    def handle_back_service(self, message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        service_data: dict = self.data.setdefault(chat_id, {}).setdefault(
            "regular_services", {}
        )
        amount: int | None = service_data.get("back_price")          # Internal implementation note: legacy behavior is preserved during modernization.
        is_active: bool = service_data.get("back", False)            # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        toggle_label = "🔁 غیرفعال کردن" if is_active else "🔁 فعال کردن"
        if amount:                                                # Internal implementation note: legacy behavior is preserved during modernization.
            short = self._format_price_short(int(amount))         # Internal implementation note: legacy behavior is preserved during modernization.
            price_label = f"✏️ ویرایش قیمت ({short})"
        else:
            price_label = "💰 تعیین قیمت"
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(price_label, toggle_label)
        markup.add(regular_services_config["confirm"]["title"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            "🧰 لطفاً گزینهٔ مورد نظر برای سرویس «گزینه خدمات ۱» را انتخاب کنید:",
            reply_markup=markup,
        )
        self.bot.register_next_step_handler(message, self.handle_back_options)
    def receive_back_price(self, message):
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        if self.is_back(message):
            return
        if raw == "🔙 بازگشت":
            return self.handle_back_service(message)
        try:
            amount = self.parse_price(raw, min_amount=300_000, max_amount=500_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, self.receive_back_price)
        self.data.setdefault(chat_id, {}).setdefault(
            "regular_services", {})["back_price"] = amount
        short = self._format_price_short(amount)
        self.bot.send_message(chat_id, f"✅ قیمت ثبت شد: {amount:,} تومان ({short})")
        self.handle_service_price_input(message)
        return self.handle_back_service(message)
