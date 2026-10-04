from __future__ import annotations

from .requests_handler_context import *


class RequestsHandlerFlowsMixin:
    def convert_selected_services_from_client_rad(self, selected_dict):
        titles_map = {
            "custom_outfit": "📦 محصول سفارشی",
            "candles_music": "🕯️🎶 شمع و موزیک و نوشیدنی",
            "drinks": "🥂 نوشیدنی",
            "social_service": "🤝 خدمات تعاملی",
            "special_service": "⛓️ گزینهٔ سفارشی ویژه",
            "special_service_option_a": "🔱 گزینه A را فعال می‌کنم",
            "special_service_option_b": "🧷 گزینه B را فعال می‌کنم",
            "back": "🧰 گزینه خدمات ۱",
            "service_group": "🧩 گروه خدمات",
            "group_option_b": "🧩 گزینه خدمات B",
            "group_option_a": "🧩 گزینه خدمات A"
        }
        result = []
        for key, value in selected_dict.items():
            if isinstance(value, bool) and value:
                title = titles_map.get(key)
                if title:
                    result.append(title)
            elif isinstance(value, dict):
                for subkey, subval in value.items():
                    if subval is True:
                        title = titles_map.get(subkey)
                        if title:
                            result.append(title)
        return "، ".join(result) if result else "ندارد"
    def show_pending_requests_menu(self, message):
        chat_id = message.chat.id
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
        U_code = user[0]["U_code"]
        all_requests = self.get_requests_for_user(U_code)
        pending_requests = [
            r for r in all_requests if r["R_status"] == "pending"]
        client_requests = self.get_pending_client_requests(U_code)
        if not pending_requests and not client_requests:
            self.bot.send_message(
                chat_id, "📭 شما هیچ درخواست باز و تأیید نشده‌ای ندارید.")
            return self.parent.login_handler.show_work_panel(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        label_map = {}  # to map each label to its request ID
        for req in pending_requests:
            sender_info = self.db.select_dict(
                "staff", "U_code = ?", (req["U_code"],))
            sender_name = sender_info[0]["name"] if sender_info else "کاربر ناشناس"
            req_type_label = "🔁 FMF" if req['request_type'] == "Group Service Request" else "📄 دیگر"
            label = f"{req_type_label} | از: {sender_name}"
            label_map[label] = req["id"]
            markup.add(label)
        for creq in client_requests:
            requester_info = self.db.select_dict(
                "staff", "U_code = ?", (creq["U_code"],)
            )
            requester_name = requester_info[0]["name"] if requester_info else "کاربر ناشناس"
            slot_time = creq.get("slot_time", "نامشخص")
            reserve_id = creq["id"]
            label = f"👤 مشتری (رزرو فعال) | 🕒 زمان: {slot_time} | کد رزرو: {reserve_id}"
            label_map[label] = f"client_rad_{reserve_id}"
            markup.add(label)
        # Save label mapping in memory so we know which label maps to which request
        self.data.setdefault(chat_id, {})["label_map"] = label_map
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "📨 درخواست‌های دریافتی شما:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_request_selection)
    def process_request_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.show_requests_category_menu(message)
        label_map = self.data.get(chat_id, {}).get("label_map", {})
        req_id = label_map.get(text)
        if isinstance(req_id, str) and req_id.startswith("client_rad_"):
            parts = req_id.split("_")
            if len(parts) == 3 and parts[2].isdigit():
                client_id = int(parts[2])
                status_row = self.db.select_dict(
                    "service_requests", "id = ?", (client_id,))
                if status_row and status_row[0].get("status") == "finalized":
                    return self.handle_finalized_client_rad_selection(message, client_id)
                elif status_row and status_row[0]["status"] == "rejected":
                    return self.show_rejected_request_summary(message, client_id)
                elif status_row and status_row[0]["status"] == "cancelled":
                    return self.show_cancelled_request_summary(message, client_id)
                elif status_row and status_row[0]["status"] == "done":
                    return self.show_done_request_summary(message, client_id)
                else:
                    return self.process_client_rad_request(message, client_id)
        if not req_id:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
            return self.show_requests_category_menu(message)
        request = self.get_request_by_id(req_id)
        if not request or request["R_status"] != "pending":
            self.bot.send_message(chat_id, "❌ درخواست معتبر یا باز یافت نشد.")
            return self.show_requests_category_menu(message)
        if request["request_type"] == "Group Service Request":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("✅ تایید درخواست", "❌ رد درخواست", "🔙 بازگشت")
            self.bot.send_message(
                chat_id, request["content"], reply_markup=markup)
            self.data[chat_id]["active_request_id"] = req_id
            return self.bot.register_next_step_handler(message, self.handle_group_option_a_response)
        self.bot.send_message(
            chat_id, "ℹ️ این نوع درخواست هنوز پشتیبانی نمی‌شود.")
        return self.show_requests_category_menu(message)
    def show_done_request_summary(self, message, client_id):
        chat_id = message.chat.id
        info = self.db.select_dict("service_requests", "id = ?", (client_id,))
        if not info:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
            return self.show_requests_by_status(message, "done")
        info = info[0]
        slot_time = info.get("slot_time", "نامشخص")
        video_note_id = info.get("video_note")
        ad_id = info.get("ad_id")
        # Internal implementation note: legacy behavior is preserved during modernization.
        payment_method = info.get("payment_method", "-")
        # Internal implementation note: legacy behavior is preserved during modernization.
        ad_info = self.db.select_dict("ads", "id = ?", (ad_id,))
        prepayment_amount = "-"
        if ad_info:
            ad_info = ad_info[0]
            prepayment_amount = ad_info.get("prepayment_amount", "-")
        try:
            invoice = eval(info.get("invoice", "{}"))
            total_price = invoice.get("total_price", "نامشخص")
        except:
            total_price = "نامشخص"
        try:
            raw_value = info.get("selected_services", "{}")
            selected_dict = json.loads(raw_value)
            selected_services = self.convert_selected_services_from_client_rad(
                selected_dict)
        except:
            selected_services = "نامشخص"
        text = f"✔️ این رزرو با موفقیت انجام شده است.\n\n" \
            f"🕒 زمان شروع سرویس: {slot_time}\n" \
            f"🔧 سرویس‌ها: {selected_services}\n" \
            f"💰 قیمت نهایی آگهی: {total_price} تومان\n" \
            f"💳 روش پرداخت: {payment_method}\n" \
            f"💵 مبلغ پیش‌پرداخت: {prepayment_amount} تومان"
        if video_note_id:
            try:
                self.bot.send_video_note(chat_id, video_note_id)
            except:
                self.bot.send_message(chat_id, "⚠️ ارسال ویدیو ناموفق بود.")
        self.bot.send_message(chat_id, text)
        self.show_requests_by_status(message, "done")
    def show_rejected_request_summary(self, message, client_id):
        chat_id = message.chat.id
        info = self.db.select_dict("service_requests", "id = ?", (client_id,))
        self.db.ensure_table_and_columns("service_requests", {
            "reject_reason": "TEXT",
            "cancel_reason": "TEXT",
            "cancel_paid": "TEXT"
        })
        if not info:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
            return self.show_requests_by_status(message, "rejected")
        info = info[0]
        slot_time = info.get("slot_time", "نامشخص")
        reason = info.get("reject_reason", "نامشخص")
        video_note_id = info.get("video_note")
        text = f"❌ این درخواست توسط شما رد شده است.\n\n" \
            f"🕒 زمان درخواستی: {slot_time}\n" \
            f"📄 دلیل رد: {reason}"
        if video_note_id:
            try:
                self.bot.send_video_note(chat_id, video_note_id)
            except:
                self.bot.send_message(chat_id, "⚠️ ارسال ویدیو ناموفق بود.")
        self.bot.send_message(chat_id, text)
        self.show_requests_by_status(message, "rejected")
    def show_cancelled_request_summary(self, message, client_id):
        chat_id = message.chat.id
        info = self.db.select_dict("service_requests", "id = ?", (client_id,))
        self.db.ensure_table_and_columns("service_requests", {
            "reject_reason": "TEXT",
            "cancel_reason": "TEXT",
            "cancel_paid": "TEXT"
        })
        if not info:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
            return self.show_requests_by_status(message, "cancelled")
        info = info[0]
        slot_time = info.get("slot_time", "نامشخص")
        reason = info.get("cancel_reason", "نامشخص")
        paid = info.get("cancel_paid", "نامشخص")
        video_note_id = info.get("video_note")
        text = f"🚫 این رزرو لغو شده است.\n\n" \
            f"🕒 زمان درخواستی: {slot_time}\n" \
            f"📄 دلیل لغو: {reason}\n" \
            f"💸 هزینه لغو پرداخت شده؟ {paid}"
        if video_note_id:
            try:
                self.bot.send_video_note(chat_id, video_note_id)
            except:
                self.bot.send_message(chat_id, "⚠️ ارسال ویدیو ناموفق بود.")
        self.bot.send_message(chat_id, text)
        self.show_requests_by_status(message, "cancelled")
    def process_client_rad_request(self, message, client_id):
        chat_id = message.chat.id
        row = self.db.select_dict("service_requests", "id = ?", (client_id,))
        if not row:
            self.bot.send_message(chat_id, "❌ درخواست مشتری یافت نشد.")
            return self.show_pending_requests_menu(message)
        info = row[0]
        # Extract Persian-labeled data from the table
        ad_id = info.get("ad_id", "نامشخص")
        slot_time = info.get("slot_time", "نامشخص")
        extra_times = info.get("extra_times", "ندارد")
        try:
            raw_value = info.get("selected_services", "{}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            selected_dict = json.loads(raw_value)
            selected_services = self.convert_selected_services_from_client_rad(
                selected_dict)
        except Exception as e:
            selected_services = "نامشخص"
        # invoice is a dictionary, parse and get total_price
        try:
            invoice = eval(info.get("invoice", "{}"))
            total_price = invoice.get("total_price", "نامشخص")
        except Exception:
            total_price = "نامشخص"
        video_note_id = info.get("video_note")
        # Internal implementation note: legacy behavior is preserved during modernization.
        text = f"📩 یک رزرو جدید:\n\n" \
            f"🆔 آگهی: {ad_id}\n" \
            f"🕒 زمان درخواستی: {slot_time}\n" \
            f"➕ زمان‌های اضافه: {extra_times}\n" \
            f"🔧 سرویس‌ها: {selected_services}\n" \
            f"💰 قیمت نهایی: {total_price} تومان"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ تایید رزرو", "❌ رد رزرو", "🔙 بازگشت")
        self.data[chat_id]["active_client_rad_id"] = client_id
        # Send video (if exists), then the text
        if video_note_id:
            try:
                self.bot.send_video_note(chat_id, video_note_id)
            except Exception as e:
                self.bot.send_message(
                    chat_id, "⚠️ ارسال ویدیو مسیج ناموفق بود.")
        else:
            self.bot.send_message(
                chat_id, "⚠️ ویدیو مسیجی برای این درخواست ثبت نشده است.")
        self.bot.send_message(chat_id, text, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_client_rad_response)
