from __future__ import annotations

from .services_handler_context import *


class ServicesHandlerFlowsMixin:
    def handle_candles_music_options(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        if self.is_back(message):
            return
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if "شمع و موزیک" in text:
            current = premium_data.get("candles_music", False)
            premium_data["candles_music"] = not current
            status = "✅ فعال شد" if not current else "❌ غیرفعال شد"
            self.bot.send_message(
                chat_id,
                f"{status}.\nبا فعالسازی این گزینه، ۱۰۰,۰۰۰ تومان به مبلغ خدمات شما افزوده خواهد شد."
            )
            self.handle_service_price_input2(chat_id)
            return self.handle_candles_music_service(message)
        elif text == "🍷 نوشیدنی‌ها":
            return self.handle_drinks_submenu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            self.handle_candles_music_service(message)
    def handle_drinks_submenu(self, message):
        chat_id = message.chat.id
        text = message.text
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        is_drink_on = premium_data.get("candles_music_drinks", False)
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if self.is_back(message):
            return
        toggle_label = "🍷 غیرفعال کردن نوشیدنی" if is_drink_on else "🍷 فعال‌سازی نوشیدنی"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(toggle_label, "💰 تعیین قیمت نوشیدنی")
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.bot.send_message(
            chat_id,
            "🍷 لطفاً تنظیمات مربوط به نوشیدنی را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_drinks_options)
    def handle_drinks_options(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        premium_data = self.data.setdefault(
            chat_id, {}).setdefault("premium_services", {})
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if self.is_back(message):
            return
        if "فعال‌سازی نوشیدنی" in text:
            premium_data["candles_music_drinks"] = True
            self.bot.send_message(chat_id, "✅ نوشیدنی‌ها فعال شدند.")
            self.handle_service_price_input2(chat_id)
            return self.handle_drinks_submenu(message)
        elif "غیرفعال کردن نوشیدنی" in text:
            premium_data["candles_music_drinks"] = False
            self.bot.send_message(chat_id, "❌ نوشیدنی‌ها غیرفعال شدند.")
            self.handle_service_price_input2(chat_id)
            return self.handle_drinks_submenu(message)
        elif text == "💰 تعیین قیمت نوشیدنی":
            self._set_pending_service(chat_id, 'premium_services', 'candles_music_drinks', 'نوشیدنی')
            self.bot.send_message(
                chat_id,
                "💰 لطفاً مبلغ نوشیدنی را وارد کنید (بین ۱۰۰,۰۰۰ تا ۴۰۰,۰۰۰ تومان):",
            )
            return self.bot.register_next_step_handler(message, self.receive_drink_price)
        else:
            self.bot.send_message(chat_id, "❌ گزینه نامعتبر است.")
            self.handle_drinks_submenu(message)
    def receive_drink_price(self, message):
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        if raw == "🔙 بازگشت":
            return self.handle_drinks_submenu(message)
        if self.is_back(message):
            return
        try:
            amount = self.parse_price(raw, min_amount=100_000, max_amount=400_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, self.receive_drink_price)
        self.data.setdefault(chat_id, {}).setdefault(
            "premium_services", {})["candles_music_drinks_price"] = amount
        short = self._format_price_short(amount)
        self.bot.send_message(chat_id, f"✅ قیمت نوشیدنی ذخیره شد: {amount:,} تومان ({short})")
        self.handle_service_price_input(message)
        return self.handle_drinks_submenu(message)
    def single_back_button_markup(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت")
        return markup
    def handle_custom_outfit_service(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        user_code = user[0]["U_code"]
        srvc = self.db.select_dict("services", "U_code = ?", (user_code,))
        active = srvc[0].get("custom_outfit", 0) if srvc else 0
        print(f"inja {active} print shod")
        if not active:
            toggle_btn = "✅ فعال کردن محصول"
        else:
            toggle_btn = "🚫 غیرفعال کردن محصول"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("➕ افزودن محصول سفارشی")
        markup.add("📦 مشاهده محصول‌ها", toggle_btn)
        markup.add("💾 ذخیره تغییرات و بازگشت")
        self.bot.send_message(
            chat_id,
            "👗 لطفاً یکی از گزینه‌های مربوط به محصول سفارشی را انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.custom_outfit_menu_handler)
    def custom_outfit_menu_handler(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "💾 ذخیره تغییرات و بازگشت":
            return self.handle_services(message ,_bypass_back=True)
        if self.is_back(message):
            return
        if text == "➕ افزودن محصول سفارشی":
            self.bot.send_message(
                chat_id,
                "📸 لطفاً عکس محصول را ارسال کنید:",
                reply_markup=self.single_back_button_markup()
            )
            return self.bot.register_next_step_handler(message, self.receive_custom_outfit_photo)
        elif text == "✅ فعال کردن محصول" or text == "🚫 غیرفعال کردن محصول":
            return self.custom_outfit_service_toggle(message)
        elif text == "📦 مشاهده محصول‌ها":
            return self.show_outfit_list(message)
        elif text == "💾 ذخیره تغییرات و بازگشت":
            self.handle_service_price_input(message)
            return self.handle_services(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.handle_custom_outfit_service(message)
    def custom_outfit_service_toggle(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        user_code = user[0]["U_code"]
        toggle = self.db.select_dict("services", "U_code = ?", (user_code,))
        current = toggle[0].get("custom_outfit", 0) if toggle else 0
        new_status = not bool(current)
        self.db.update("services", {"custom_outfit": int(
            new_status)}, "U_code = ?", (user_code,))
        if new_status:
            self.bot.send_message(chat_id, "✅ محصول سفارشی فعال شد.")
        else:
            self.bot.send_message(chat_id, "🚫 محصول سفارشی غیرفعال شد.")
        return self.handle_custom_outfit_service(message)
    def receive_custom_outfit_photo(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.handle_custom_outfit_service(message)
        if self.is_back(message):
            return
        if not message.photo:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط عکس ارسال کنید:", reply_markup=self.single_back_button_markup()
            )
            return self.bot.register_next_step_handler(message, self.receive_custom_outfit_photo)
        # Forward photo to channel
        photo = message.photo[-1]
        forwarded = self.bot.forward_message(STORAGE_CHANNEL,
                                             chat_id, message.message_id)
        file_id = forwarded.photo[-1].file_id
        # Store
        entry = {"file_id": file_id}
        self.data.setdefault(chat_id, {}).setdefault(
            "premium_custom_clothes", []).append(entry)
        self.bot.send_message(
            chat_id, "📝 لطفاً توضیحی برای این محصول وارد کنید:", reply_markup=self.single_back_button_markup()
        )
        self.handle_service_price_input(message)
        self.bot.register_next_step_handler(
            message, self.receive_custom_outfit_description)
    def receive_custom_outfit_description(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            # Remove incomplete entry
            self.data[chat_id]["premium_custom_clothes"].pop()
            return self.handle_custom_outfit_service(message)
        if self.is_back(message):
            return
        desc = message.text.strip() if message.text else None
        self.data[chat_id]["premium_custom_clothes"][-1]["description"] = desc
        self.bot.send_message(
            chat_id, "💰 لطفاً قیمت محصول را وارد کنید (۲۰۰,۰۰۰ تا ۵۰۰,۰۰۰):", reply_markup=self.single_back_button_markup()
        )
        self.handle_service_price_input(message)
        self.bot.register_next_step_handler(
            message, self.receive_custom_outfit_price)
    def receive_custom_outfit_price(self, message):
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        if raw == "🔙 بازگشت":
            self.data[chat_id]["premium_custom_clothes"].pop()
            return self.handle_custom_outfit_service(message)
        if self.is_back(message):
            return
        try:
            amount = self.parse_price(raw, min_amount=200_000, max_amount=500_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}", reply_markup=self.single_back_button_markup())
            return self.bot.register_next_step_handler(message, self.receive_custom_outfit_price)
        self.data[chat_id]["premium_custom_clothes"][-1]["price"] = amount
        short = self._format_price_short(amount)
        self.bot.send_message(chat_id, f"✅ محصول با قیمت {amount:,} تومان ({short}) ذخیره شد.")
        self.handle_service_price_input(message)
        return self.handle_custom_outfit_service(message)
    def show_outfit_list(self, message):
        chat_id = message.chat.id
        clothes = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
        if not clothes:
            self.bot.send_message(
                chat_id, "❌ شما هنوز محصولی اضافه نکرده‌اید.\nاز دکمه افزودن محصول استفاده کنید.")
            return self.handle_custom_outfit_service(message)
        if self.is_back(message):
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for item in clothes:
            markup.add(item["description"])
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "👗 لطفاً یکی از محصول‌های زیر را برای مشاهده انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.view_selected_outfit)
    def view_selected_outfit(self, message):
        chat_id = message.chat.id
        desc = message.text.strip() if message.text else None
        if desc == "🔙 بازگشت":
            return self.handle_custom_outfit_service(message)
        if self.is_back(message):
            return
        clothes = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
        for item in clothes:
            if item["description"] == desc:
                caption = f"👗 <b>{item['description']}</b>\n💰 {item['price']:,} تومان"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("✏️ ویرایش این محصول", "🗑️ حذف این محصول")
                markup.add("🔙 بازگشت")
                self.bot.send_photo(
                    chat_id, item["file_id"], caption=caption, reply_markup=markup, parse_mode="HTML")
                return self.bot.register_next_step_handler(message, lambda m: self.handle_outfit_action(m, item))
        self.bot.send_message(chat_id, "❌ محصول مورد نظر یافت نشد.")
        return self.show_outfit_list(message)
    def handle_outfit_action(self, message, item):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "✏️ ویرایش این محصول":
            self.data[chat_id]["_edit_target"] = item
            self.bot.send_message(chat_id,
                                  "📸 لطفاً عکس جدید این محصول را ارسال کنید:",
                                  reply_markup=self.single_back_button_markup())
            return self.bot.register_next_step_handler(message, self.edit_outfit_photo)
        elif text == "🗑️ حذف این محصول":
            clothes = self.data.get(chat_id, {}).get("premium_custom_clothes", [])
            self.data[chat_id]["premium_custom_clothes"] = [
                c for c in clothes if c != item]
            self.bot.send_message(chat_id, "🗑️ محصول با موفقیت حذف شد.")
            if not self.data[chat_id]["premium_custom_clothes"]:
                return self.handle_custom_outfit_service(message)
            return self.show_outfit_list(message)
        elif text == "🔙 بازگشت":
            return self.show_outfit_list(message)
        self.bot.send_message(
            chat_id, "❌ لطفاً فقط از گزینه‌های معتبر استفاده کنید.")
        return self.view_selected_outfit(message)
    def edit_outfit_photo(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        if message.text == "🔙 بازگشت":
            return self.handle_custom_outfit_service(message)
        if not message.photo:
            self.bot.send_message(chat_id, "❌ لطفاً فقط عکس ارسال کنید.")
            return self.bot.register_next_step_handler(message, self.edit_outfit_photo)
        photo = message.photo[-1]
        forwarded = self.bot.forward_message(STORAGE_CHANNEL,
                                             chat_id, message.message_id)
        file_id = forwarded.photo[-1].file_id
        self.data[chat_id]["_edit_target"]["file_id"] = file_id
        self.bot.send_message(
            chat_id, "📝 لطفاً توضیح جدید برای این محصول وارد کنید:")
        self.bot.register_next_step_handler(
            message, self.edit_outfit_description)
    def edit_outfit_description(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return
        if message.text == "🔙 بازگشت":
            return self.handle_custom_outfit_service(message)
        desc = message.text.strip() if message.text else None
        self.data[chat_id]["_edit_target"]["description"] = desc
        self.bot.send_message(
            chat_id, "💰 لطفاً قیمت جدید محصول را وارد کنید (۲۰۰,۰۰۰ تا ۵۰۰,۰۰۰):")
        self.bot.register_next_step_handler(message, self.edit_outfit_price)
    def edit_outfit_price(self, message):
        chat_id = message.chat.id
        raw = (message.text or "").strip()
        if self.is_back(message):
            return
        if raw == "🔙 بازگشت":
            return self.handle_custom_outfit_service(message)
        try:
            amount = self.parse_price(raw, min_amount=200_000, max_amount=500_000)
        except ValueError as err:
            self.bot.send_message(chat_id, f"❌ {err}")
            return self.bot.register_next_step_handler(message, self.edit_outfit_price)
        self.data[chat_id]["_edit_target"]["price"] = amount
        self.data[chat_id].pop("_edit_target", None)
        self.bot.send_message(chat_id, "✅ محصول با موفقیت ویرایش شد.")
        self.handle_service_price_input(message)
        self.handle_custom_outfit_service(message)
