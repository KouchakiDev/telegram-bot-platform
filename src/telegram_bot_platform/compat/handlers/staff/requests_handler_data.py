from __future__ import annotations

from .requests_handler_context import *


class RequestsHandlerDataMixin:
    def normalize_phone_number(self , number , with_plus: bool = True) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        log.debug("normalize_phone_number called with number=%r, with_plus=%s", number, with_plus)
        # 1) Validate None
        if number is None:
            log.error("Input number is None")
            raise TypeError("شماره نمی‌تواند None باشد")
        # 2) Convert to string
        if isinstance(number, bytes):
            try:
                number_str = number.decode('utf-8')
                log.debug("Decoded bytes to string: %r", number_str)
            except UnicodeDecodeError as e:
                log.exception("UTF-8 decoding error")
                raise ValueError("خطا در رمزگشایی شماره") from e
        else:
            number_str = str(number)
            log.debug("Converted input to string: %r", number_str)
        # 3) Normalize digits and remove separators
        cleaned = number_str.translate(_P2E)
        log.debug("After Persian->English digits: %r", cleaned)
        for sep in (' ', '-', '(', ')', '.'):
            cleaned = cleaned.replace(sep, '')
        log.debug("After removing separators: %r", cleaned)
        cleaned = cleaned.lstrip()
        log.debug("After stripping leading whitespace: %r", cleaned)
        # 4) Remove international prefixes: '+', '00', '98', '0'
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
            log.debug("Removed '+': %r", cleaned)
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
            log.debug("Removed '00': %r", cleaned)
        if cleaned.startswith('98'):
            cleaned = cleaned[2:]
            log.debug("Removed '98': %r", cleaned)
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
            log.debug("Removed leading '0': %r", cleaned)
        # 5) Validate final pattern: exactly 10 digits starting with '9'
        if not re.fullmatch(r"9\d{9}", cleaned):
            log.error("Validation failed for cleaned number: %r", cleaned)
            raise ValueError(f"{number!r} یک شمارهٔ موبایل معتبر نیست")
        # 6) Prepend country code and return
        normalized = f"98{cleaned}"
        result = f"+{normalized}" if with_plus else normalized
        log.info("Normalized phone number: %r", result)
        return result
    def handle_client_rad_response(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        client_id = self.data.get(chat_id, {}).pop("active_client_rad_id", None)
        if not client_id:
            self.bot.send_message(chat_id, "❌ درخواست معتبر یافت نشد.")
            return self.show_pending_requests_menu(message)
        mosh_id = None
        mosh_phone = None
        mosh_U_code = None
        try:
            row = self.db.select_dict("service_requests", "id = ?", (client_id,))
            info = row[0]
            mosh_U_code = info["U_code"]
            ad_id = info["ad_id"]
            slot_time = info["slot_time"]
            extra_times = json.loads(info.get("extra_times", "[]"))
            # Internal implementation note: legacy behavior is preserved during modernization.
            mosh_data = dict(info)
            # Internal implementation note: legacy behavior is preserved during modernization.
            premium_data = self.db.select_dict("premium_clients", "U_code = ?", (mosh_U_code,))
            if premium_data:
                mosh_data.update(premium_data[0])
            else:
                normal_data = self.db.select_dict("clients", "U_code = ?", (mosh_U_code,))
                if normal_data:
                    mosh_data.update(normal_data[0])
            # Internal implementation note: legacy behavior is preserved during modernization.
            mosh_id = mosh_data.get("telegram_id")
            mosh_phone = mosh_data.get("phone", "نامشخص")
            mosh_username = mosh_data.get("username", "")
        except Exception as e:
            logger.exception("[handle_client_rad_response] Error fetching client info")
        admins_id = [row["telegram_id"] for row in self.db.select_dict("admins")]
        if text == "✅ تایید رزرو":
            self.db.update("service_requests", {
                "status": "finalized"
            }, "id = ?", (client_id,))
            self.bot.send_message(chat_id, "✅ رزرو تأیید شد.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if mosh_phone or mosh_username:
                username_text = f"\n🆔 تلگرام: @{mosh_username}" if mosh_username else ""
                self.bot.send_message(
                    chat_id,
                    f"📞 شماره مشتری: {mosh_phone or 'نامشخص'}{username_text}\n📣 لطفاً جهت هماهنگی تماس حاصل کنید."
                )
            for admin in self.db.select_dict("admins", "id = ?",(1,)):
                perms = json.loads(admin.get("permissions", ""))
                if not perms.get("manage_requests"):
                    continue
                try:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    client = self.db.select_dict("clients", "U_code = ?", (mosh_U_code,))
                    if not client:
                        client = self.db.select_dict("premium_clients", "U_code = ?", (mosh_U_code,))
                    client = client[0] if client else {}
                    rad_row = self.db.select_dict("service_requests", "id = ?", (client_id,))
                    rad_row = rad_row[0] if rad_row else {}
                    ad_id = rad_row.get("ad_id")
                    slot_time = rad_row.get("slot_time")
                    extra_times = rad_row.get("extra_times")
                    ad_row = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
                    ad_row = ad_row[0] if ad_row else {}
                    pu_code = rad_row.get("PU_code")
                    staff = self.db.select_dict("staff", "U_code = ?", (pu_code,))
                    staff = staff[0] if staff else {}
                    msg = (
                        "📢 یک رزرو توسط پرسنل تأیید شد\n"
                        "👤 مشتری: {} | {}\n".format(client.get("name", "نامشخص"), self.normalize_phone_number(mosh_phone)) +
                        "📞 تلگرام: @{}\n".format(client.get("username", "نامشخص")) +
                        "🧑‍💼 ارائه‌دهنده: {} | سطح تجربه: {} | کد: {}\n".format(
                            staff.get("name", "نامشخص"),
                            staff.get("age", "-"),
                            staff.get("U_code", "---")
                        ) +
                        "📞 تلفن ارائه‌دهنده: {}\n".format(self.normalize_phone_number(staff.get("phone_number", "---"))) +
                        "📍 منطقه: {} | شهر: {}\n".format(
                            staff.get("region", "---"),
                            staff.get("city", "---")
                        ) +
                        "📅 آگهی: آیدی {}, تایم شروع: {}, تایم پایانی: {}\n".format(
                            ad_id,
                            ad_row.get("start_time", "-"),
                            ad_row.get("end_time", "-")
                        ) +
                        "🕒 تاریخ ثبت: {}".format(
                            RequestManager.convert_to_shamsi(rad_row.get("created_at", "-"))
                        )
                    )
                    self.bots["admin"].send_message(admin["telegram_id"], msg)
                except Exception as e:
                    logger.exception(f"[AdminNotify] Failed to send detailed booking approval to admin {admin.get('telegram_id')}: {e}")
            if mosh_id:
                self.bots["moshtari"].send_message(
                    mosh_id,
                    "درخواست شما توسط پرسنل تأیید شد، جهت اطلاع از راه ارتباطی به بخش نتیجه درخواست‌ها مراجعه کنید"
                )
        elif text == "❌ رد رزرو":
            """
            بخش مدیریت رد رزرو توسط ارائه‌دهنده:
            - درخواست دلیل رد از پرسنل دریافت می‌شود و در دیتای ویژه ذخیره می‌گردد.
            - تایم‌های رزرو شده (اصلی و اضافه) در جدول live_ads آزاد می‌شوند.
            - پیام کامل و مودبانه به ادمین‌ها و مشتری ارسال می‌شود.
            - پس از دریافت دلیل رد، متد save_client_reject_reason فراخوانی می‌شود.
            """
            # Internal implementation note: legacy behavior is preserved during modernization.
            if chat_id not in self.data:
                self.data[chat_id] = {}
            self.data[chat_id]["awaiting_rejection_reason"] = client_id
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "📄 لطفاً دلیل رد این رزرو را وارد کنید:")
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                ad_data = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
                if ad_data:
                    time_slots = json.loads(ad_data[0]["time_slots"])
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if slot_time in time_slots:
                        time_slots[slot_time] = True
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    for extra_time in extra_times:
                        if extra_time in time_slots:
                            time_slots[extra_time] = True
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.update("live_ads", {
                        "time_slots": json.dumps(time_slots)
                    }, "ad_id = ?", (ad_id,))
                    logger.info(f"[Reject] Freed slots {slot_time}, extras: {extra_times} for ad_id={ad_id}")
            except Exception as e:
                logger.exception(f"[Reject] Error freeing time slots for ad_id={ad_id}: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            for admin_id in admins_id:
                try:
                    self.bots["admin"].send_message(admin_id, 
                        f"❗ درخواست رزرو شماره {client_id} توسط پرسنل رد شد.\n"
                        f"⏰ تایم اصلی: {slot_time}\n"
                        f"⏰ تایم‌های اضافه: {', '.join(extra_times) if extra_times else '-'}\n"
                        f"📣 لطفاً برای اطلاعات بیشتر منتظر دلیل رد باشید."
                    )
                except Exception as e:
                    logger.exception(f"[Reject] Failed to notify admin {admin_id}: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if mosh_id:
                try:
                    self.bots["moshtari"].send_message(
                        mosh_id,
                        "❌ درخواست شما توسط پرسنل رد شد.\n"
                        "لطفاً دلیل رد را در بخش نتیجه درخواست‌ها مشاهده کنید و در صورت تمایل آگهی دیگری انتخاب نمایید."
                    )
                except Exception as e:
                    logger.exception(f"[Reject] Failed to notify client {mosh_id}: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.bot.register_next_step_handler(message, self.save_client_reject_reason)
        elif text == "🔙 بازگشت":
            return self.show_pending_requests_menu(message)
        else:
            self.bot.send_message(chat_id, "❌ لطفاً از دکمه‌های موجود استفاده کنید.")
            return self.bot.register_next_step_handler(message, self.handle_client_rad_response)
        return self.show_pending_requests_menu(message)
    def save_client_reject_reason(self, message):
        chat_id = message.chat.id
        reason = message.text.strip() if message.text else None
        client_id = self.data.get(chat_id, {}).pop(
            "awaiting_rejection_reason", None)
        if not client_id:
            self.bot.send_message(chat_id, "❌ درخواست معتبر یافت نشد.")
            return self.show_pending_requests_menu(message)
        self.db.update("service_requests", {
            "status": "rejected",
            "reject_reason": reason
        }, "id = ?", (client_id,))
        self.bot.send_message(chat_id, "❌ رزرو رد شد و دلیل ذخیره شد.")
        return self.show_pending_requests_menu(message)
    def handle_finalized_client_rad_selection(self, message, client_id):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        row = self.db.select_dict("service_requests", "id = ?", (client_id,))
        if not row:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
            return self.show_requests_by_status(message, "finalized")
        info = row[0]
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            invoice = eval(info.get("invoice", "{}"))
            total_price = invoice.get("total_price", "نامشخص")
        except:
            total_price = "نامشخص"
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            raw_value = info.get("selected_services", "{}")
            selected_dict = json.loads(raw_value)
            selected_services = self.convert_selected_services_from_client_rad(selected_dict)
        except:
            selected_services = "نامشخص"
        slot_time = info.get("slot_time", "نامشخص")
        extra_times = json.loads(info.get("extra_times", "[]"))
        extra_display = "، ".join(extra_times) if extra_times else "ندارد"
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            client_data = dict(info)  # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            premium_rows = self.db.select_dict("premium_clients", "U_code = ?", (info["U_code"],)) 
            if premium_rows:
                client_data.update(premium_rows[0])
            else:
                client_rows = self.db.select_dict("clients", "U_code = ?", (info["U_code"],))
                if client_rows:
                    client_data.update(client_rows[0])
        except Exception as e:
            log.exception(f"[FinalizedSelection] Failed to load client data: {e}")
            client_data = {}
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            staff_data = self.db.select_dict("staff", "U_code = ?", (info["PU_code"],))
            staff_data = staff_data[0] if staff_data else {}
        except:
            staff_data = {}
        client_name = client_data.get("name", "نامشخص")
        client_code = client_data.get("U_code", "---")
        client_phone = client_data.get("phone", "نامشخص")
        staff_name = staff_data.get("name", "نامشخص")
        staff_code = staff_data.get("U_code", "---")
        payment_method = info.get("payment_method", "نامشخص")
        cancel_paid = info.get("cancel_paid", "نامشخص")
        selected_region = info.get("selected_region", "نامشخص")
        text = (
            f"📌 <b>جزئیات رزرو نهایی‌شده:</b>\n"
            f"👤 مشتری: {client_name}\n"
            f"📞 شماره تماس: {self.normalize_phone_number(client_phone)}\n"
            f"📍 منطقه انتخابی: {selected_region}\n"
            f"🕒 ساعت: {slot_time}\n"
            f"➕ تایم اضافه: {extra_display}\n"
            f"🔧 سرویس‌ها: {selected_services}\n"
            f"💳 روش پرداخت: {payment_method}\n"
            f"💰 قیمت نهایی: {total_price} تومان\n"
        )
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✔️ سرویس ارائه شد", "🚫 لغو شد")
        markup.add("🔙 بازگشت")
        self.data.setdefault(chat_id, {})["finalized_client_id"] = client_id
        video_note_id = info.get("video_note")
        if video_note_id:
            try:
                self.bot.send_video_note(chat_id, video_note_id)
            except:
                self.bot.send_message(chat_id, "⚠️ ارسال ویدیو ناموفق بود.")
        self.bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        self.bot.register_next_step_handler(message, self.handle_service_or_cancel)
    def handle_service_or_cancel(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        client_id = self.data.get(chat_id, {}).get("finalized_client_id")
        if text == "✔️ سرویس ارائه شد":
            self.db.update("service_requests", {
                           "status": "done"}, "id = ?", (client_id,))
            self.bot.send_message(
                chat_id, "✔️ وضعیت به «سرویس ارائه شد» تغییر کرد.")
            self.insert_into_accounting(message, client_id, "done")
            return self.show_requests_by_status(message, "finalized")
        elif text == "🚫 لغو شد":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("✅ بله", "❌ خیر")
            self.bot.send_message(
                chat_id, "❓ آیا مشتری هزینه لغو را پرداخت کرده است؟", reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.handle_cancellation_payment)
        elif text == "🔙 بازگشت":
            return self.show_requests_by_status(message, "finalized")
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌ها را انتخاب کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_service_or_cancel)
    def handle_cancellation_payment(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        client_id = self.data.get(chat_id, {}).get("finalized_client_id")
        if text == "✅ بله":
            cancel_paid = "yes"
            note = "✔️ دریافت شد. لطفاً دلیل لغو را وارد کنید:"
        elif text == "❌ خیر":
            note = "❗ بدون پرداخت لغو شد. لطفاً دلیل را وارد کنید:"
            cancel_paid = "no"
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً از دکمه‌های موجود استفاده کنید.")
            return self.bot.register_next_step_handler(message, self.handle_cancellation_payment)
        self.data.setdefault(chat_id, {})["cancel_paid_value"] = cancel_paid
        self.bot.send_message(chat_id, note)
        self.bot.register_next_step_handler(
            message, self.save_cancellation_reason)
    def save_cancellation_reason(self, message):
        chat_id = message.chat.id
        reason = message.text.strip() if message.text else None
        client_id = self.data.get(chat_id, {}).pop(
            "finalized_client_id", None)
        if client_id:
            cancel_paid_value = self.data.get(
                chat_id, {}).pop("cancel_paid_value", None)
            self.db.update("service_requests", {
                "status": "cancelled",
                "cancel_reason": reason,
                "cancel_paid": cancel_paid_value
            }, "id = ?", (client_id,))
            self.db.update("client_accounting", {
                "cancel_paid": cancel_paid_value
            }, "client_rad_id = ?", (client_id,))
            self.insert_into_accounting(message, client_id, "cancelled")
            self.bot.send_message(chat_id, "🚫 وضعیت لغو شد و دلیل ذخیره شد.")
        else:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
        return self.show_requests_by_status(message, "finalized")
