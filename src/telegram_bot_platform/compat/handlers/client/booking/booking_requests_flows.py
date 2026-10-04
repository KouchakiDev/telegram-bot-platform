from __future__ import annotations

from .booking_requests_context import *


class BookingHandlerFlowsMixin:
    def send_service_selection_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        data = self.temp_data[chat_id]
        ad_row = data["ad_row"]
        services_dict = {}
        try:
            services_dict.update(json.loads(ad_row.get("services", "{}")))
        except Exception as ex:
            print("خطا در بارگذاری services:", ex)
        try:
            if ad_row.get("premium") == 1:
                services_dict.update(json.loads(
                    ad_row.get("premium_services", "{}")))
        except Exception as ex:
            print("خطا در بارگذاری premium_services:", ex)
        if not services_dict:
            self.check_slot_extension(message)
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        service_buttons = []
        button_map = {}       # Internal implementation note: legacy behavior is preserved during modernization.
        reverse_map = {}      # Internal implementation note: legacy behavior is preserved during modernization.
        for key, info in services_dict.items():
            price = info.get("price", 0)
            if not price or int(price) == 0:
                continue
            title = info.get("title", key)
            base_text = f"{title} {int(price):,} تومان"
            is_selected = self.current_request.get(chat_id, {}).get(
                "selected_services", {}).get(key, False)
            display_text = f"{'✅' if is_selected else '☑️'} {base_text}"
            button_map[base_text] = key
            reverse_map[key] = base_text
            service_buttons.append(KeyboardButton(display_text))
        self.temp_data[chat_id]["service_button_map"] = button_map
        self.temp_data[chat_id]["reverse_service_button_map"] = reverse_map
        for i in range(0, len(service_buttons), 2):
            markup.add(*service_buttons[i:i + 2])
        markup.add(KeyboardButton(BUTTONS["confirm_services"]))
        self.add_back_buttons(markup)
        self.bot.send_message(
            chat_id,
            "✅ لطفاً خدمات مورد نظر را انتخاب کن:\n(فقط خدماتی که قیمت دارند نمایش داده می‌شوند)",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_service_selection)
    def handle_service_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["confirm_services"]:
            return self.check_slot_extension(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text.startswith("✅ ") or text.startswith("☑️ "):
            text = text[2:].strip()
        button_map = self.temp_data[chat_id].get("service_button_map", {})
        service_key = button_map.get(text)
        if service_key:
            selected = self.current_request[chat_id]["selected_services"].get(
                service_key, False)
            self.current_request[chat_id]["selected_services"][service_key] = not selected
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های معتبر را انتخاب کن.")
        self.send_service_selection_menu(message)
    def check_slot_extension(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        data = self.temp_data[chat_id]
        current_slot = data.get("slot_time")
        slot_row = data.get("slot")[0]
        try:
            time_slots = json.loads(slot_row.get("time_slots", "{}"))
            times = sorted(time_slots.keys())
            index = times.index(current_slot)
            free_slots = []
            for next_time in times[index + 1:]:
                if time_slots[next_time] is True:
                    free_slots.append(next_time)
                else:
                    break
            if free_slots:
                self.temp_data[chat_id]["free_extra_slots"] = free_slots
                return self.ask_extra_slots(message, free_slots)
        except Exception as ex:
            print("❌ خطا در بررسی اسلات‌های اضافه:", ex)
        self.final_confirmation(message)
    def ask_extra_slots(self, message, free_slots):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        current_extras = self.current_request[chat_id].get("extra_times", [])
        base_price = self.temp_data[chat_id]["staff"].get(
            "service_price", 0)
        fmt = "%H:%M"
        try:
            start_time = self.temp_data[chat_id].get("slot_time")
            slot_row = self.temp_data[chat_id].get("slot")[0]
            time_slots = json.loads(slot_row.get("time_slots", "{}"))
            times = sorted(time_slots.keys())
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            last_slot = current_extras[-1] if current_extras else start_time
            try:
                index = times.index(last_slot)
                end_time = times[index + 1] if index + \
                    1 < len(times) else last_slot
            except:
                end_time = last_slot
            start = datetime.strptime(start_time, fmt)
            end = datetime.strptime(end_time, fmt)
            total_minutes = int((end - start).total_seconds() // 60)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if total_minutes <= 0:
                duration_text = "۰ دقیقه"
            elif total_minutes < 60:
                duration_text = f"{total_minutes} دقیقه"
            elif total_minutes % 60 == 0:
                duration_text = f"{total_minutes // 60} ساعت"
            else:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                duration_text = f"{hours} ساعت و {minutes} دقیقه"
        except Exception as e:
            print("❌ خطا در محاسبه فاصله بین اسلات‌ها:", e)
            duration_text = "۰ دقیقه"
        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons = []
        for slot in free_slots:
            selected = slot in current_extras
            emoji = "✅" if selected else "☑️"
            buttons.append(KeyboardButton(f"{emoji} {slot}"))
        markup.add(*buttons)
        markup.row(
            KeyboardButton(BUTTONS["confirm_extra_time"]),
            KeyboardButton(BUTTONS["reject_extra_time"])
        )
        self.add_back_buttons(markup)
        price_str = f"{int(base_price):,} تومان" if base_price else "نامشخص"
        msg = (
            f"⏱ مدت زمان سرویس فعلی: {duration_text}\n"
            "آیا نیاز به تایم بیشتری دارید؟\n"
            f"💸 مبلغ هر اسلات اضافه: {price_str}\n"
            "لطفاً در صورت نیاز، تایم‌های دلخواه را انتخاب و سپس تأیید نمایید:"
        )
        self.bot.send_message(chat_id, msg, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_extra_slots)
    def handle_extra_slots(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        text = message.text.strip()
        free_slots = self.temp_data[chat_id].get("free_extra_slots", [])
        current_extras = self.current_request[chat_id].get("extra_times", [])
        if text == BUTTONS["confirm_extra_time"]:
            return self.final_confirmation(message)
        if text == BUTTONS["reject_extra_time"]:
            self.current_request[chat_id]["extra_times"] = []
            return self.final_confirmation(message)
        if text.startswith("☑️") or text.startswith("✅"):
            clicked_slot = text[2:].strip()
            if clicked_slot not in free_slots:
                return self.bot.send_message(chat_id, "❌ گزینه نامعتبر است.")
            if clicked_slot not in current_extras:
                index = free_slots.index(clicked_slot)
                new_selection = free_slots[:index + 1]
                self.current_request[chat_id]["extra_times"] = new_selection
            else:
                index = free_slots.index(clicked_slot)
                new_selection = [
                    s for s in current_extras if free_slots.index(s) < index]
                self.current_request[chat_id]["extra_times"] = new_selection
            return self.ask_extra_slots(message, free_slots)
    def final_confirmation(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        data = self.temp_data[chat_id]
        current_req = self.current_request[chat_id]
        ad_row = data.get("ad_row")
        staff = data.get("staff")
        base_price = staff.get("service_price", 0)
        if isinstance(base_price, str) and base_price.isdigit():
            base_price = int(base_price)
        extra_times = current_req.get("extra_times", [])
        num_extra_slots = len(extra_times)
        extra_time_cost = base_price * num_extra_slots
        services_cost = 0
        services_dict = {}
        try:
            services_dict.update(json.loads(ad_row.get("services", "{}")))
        except Exception as ex:
            print("خطا در بارگذاری خدمات:", ex)
        try:
            services_dict.update(json.loads(ad_row.get("premium_services", "{}")))
        except Exception as ex:
            print("خطا در بارگذاری PREMIUM:", ex)
        selected_services = []
        for service_key, active in current_req.get("selected_services", {}).items():
            if active:
                selected_services.append(services_dict.get(
                    service_key, {}).get("title", service_key))
                services_cost += int(services_dict.get(service_key,
                                     {}).get("price", 0))
        services_str = ', '.join(
            selected_services) if selected_services else "❌ هیچ‌کدام"
        fmt = "%H:%M"
        try:
            start_time = data.get("slot_time")
            slot_row = data.get("slot")[0]
            time_slots = json.loads(slot_row.get("time_slots", "{}"))
            times = sorted(time_slots.keys())
            last_slot = extra_times[-1] if extra_times else start_time
            try:
                index = times.index(last_slot)
                end_time = times[index + 1] if index + \
                    1 < len(times) else last_slot
            except:
                end_time = last_slot
            start = datetime.strptime(start_time, fmt)
            end = datetime.strptime(end_time, fmt)
            total_minutes = int((end - start).total_seconds() // 60)
            if total_minutes <= 0:
                duration_str = "۰ دقیقه"
            elif total_minutes < 60:
                duration_str = f"{total_minutes} دقیقه"
            elif total_minutes % 60 == 0:
                duration_str = f"{total_minutes // 60} ساعت"
            else:
                h = total_minutes // 60
                m = total_minutes % 60
                duration_str = f"{h} ساعت و {m} دقیقه"
        except Exception as ex:
            print("خطا در محاسبه زمان سرویس:", ex)
            start_time = "-"
            end_time = "-"
            duration_str = "نامشخص"
        total_price = base_price + extra_time_cost + services_cost
        summary_msg = (
            "📋 خلاصه درخواست شما:\n"
            f"🔸 خدمات انتخابی: {services_str}\n"
            f"🕓 زمان شروع سرویس: {start_time}\n"
            f"🕔 زمان پایان سرویس: {end_time}\n"
            f"⏱ مجموع مدت‌زمان سرویس: {duration_str}\n"
            f"➕ تعداد اسلات‌های اضافه: {num_extra_slots} (هر اسلات: {base_price:,} تومان)\n"
            f"💰 هزینه خدمات: {services_cost:,} تومان\n"
            f"🧾 مبلغ کل: {total_price:,} تومان"
        )
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [KeyboardButton(BUTTONS["submit_order"]),]
        if selected_services or self.temp_data[chat_id]["free_extra_slots"]:
            buttons.append(KeyboardButton(BUTTONS["edit_services"]))
        markup.add(*buttons)
        self.add_back_buttons(markup)
        self.bot.send_message(chat_id, summary_msg, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.confirm_and_save)
    def confirm_and_save(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["edit_services"]:
            self.send_service_selection_menu(message)
            return
        if text == BUTTONS["submit_order"]:
            self.ask_payment_method(message)
            return
        self.bot.send_message(
            chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
        self.bot.register_next_step_handler(message, self.confirm_and_save)
