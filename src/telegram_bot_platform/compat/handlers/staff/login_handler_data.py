from __future__ import annotations

from .login_handler_context import *


class LoginHandlerDataMixin:
    def handle_receipt_upload(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        if message.content_type == "photo":
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                file_id = self.save_media_to_channel(message, media_type="photo")
                # Internal implementation note: legacy behavior is preserved during modernization.
                staff = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
                if not staff:
                    self.bot.send_message(chat_id, "❗ کاربر یافت نشد")
                    return
                U_code = staff[0]["U_code"]
                method = self.data[chat_id].get("receipt_method", "نامشخص")
                # Internal implementation note: legacy behavior is preserved during modernization.
                method_translation = {
                    "rial": "واریز ریالی",
                    "crypto": "واریز کریپتویی"
                }
                method_fa = method_translation.get(method, "نامشخص")
                # Internal implementation note: legacy behavior is preserved during modernization.
                data = {
                    "U_code": U_code,
                    "receipt": file_id,
                    "status": "pending",
                    "receipt_method": method_fa,
                }
                self.db.insert("receipts", data)
                self.bot.send_message(chat_id, "✅ رسید شما با موفقیت ثبت شد.")
            except Exception as e:
                logger.exception(f"[handle_receipt_upload] Error occurred: {e}")
                self.bot.send_message(chat_id, "❌ مشکلی در ثبت رسید رخ داد. لطفاً دوباره تلاش کنید.")
            return self.show_accounting_menu(message)
        elif message.text == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        else:
            self.bot.send_message(chat_id, "❗ لطفاً فقط یک تصویر رسید ارسال کنید یا بازگردید.")
            self.bot.register_next_step_handler(message, self.handle_receipt_upload)
    def start_receipt_flow(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("💵 واریز ریالی", "🪙 واریز کریپتو")
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "لطفاً نوع واریز را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_receipt_method_selection)
    def handle_receipt_method_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        if text == "💵 واریز ریالی":
            method = "rial"
            result = self.db.select_dict("cards", "is_default = 1")
            if not result:
                self.bot.send_message(chat_id, "❗ هیچ کارت پیش‌فرضی یافت نشد.")
                return self.show_accounting_menu(message)
            row = result[0]
            info = f"💳 شماره کارت: {row.get('card_number', 'نامشخص')}\n👤 به نام: {row.get('cardholder_name', 'نامشخص')}"
            self.data[chat_id] = {
                "receipt_method": method,
                "receipt_account": row.get("card_number", "1نامشخص")
            }
        elif text == "🪙 واریز کریپتو":
            method = "crypto"
            result = self.db.select_dict("wallets", "is_default = 1")
            if not result:
                self.bot.send_message(
                    chat_id, "❗ هیچ کیف پول پیش‌فرضی یافت نشد.")
                return self.show_accounting_menu(message)
            row = result[0]
            info = f"🪙 ارز: {row.get('crypto', 'نامشخص')}\n🌐 شبکه: {row.get('network', 'نامشخص')}\n📬 آدرس: {row.get('address', 'نامشخص')}"
            self.data[chat_id] = {
                "receipt_method": method,
                "receipt_account": row.get("address", "نامشخص")
            }
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.start_receipt_flow(message)
        # Save method
        self.data[chat_id]["receipt_method"] = method
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, f"{info}\n\n💰 لطفاً مبلغ واریزی را وارد کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_receipt_amount_input)
    def handle_receipt_amount_input(self, message):
        chat_id = message.chat.id
        if not message.text:
            self.bot.send_message(chat_id, "❗ لطفاً فقط  مبلغ وارد کنید.")
            return self.bot.register_next_step_handler(message, self.handle_receipt_amount_input)
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.start_receipt_flow(message)
        if not text.isdigit():
            self.bot.send_message(chat_id, "❗ لطفاً فقط عدد وارد کنید.")
            return self.bot.register_next_step_handler(message, self.handle_receipt_amount_input)
        self.data[chat_id]["receipt_amount"] = int(text)
        self.bot.send_message(chat_id, "📸 لطفاً تصویر رسید خود را ارسال کنید:")
        self.bot.register_next_step_handler(
            message, self.handle_receipt_upload_final)
    def handle_receipt_upload_final(self, message):
        chat_id = message.chat.id
        if message.text == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        if not message.photo:
            self.bot.send_message(chat_id, "❌ لطفاً فقط عکس ارسال کنید:")
            return self.bot.register_next_step_handler(message, self.handle_receipt_upload_final)
        telegram_id = message.from_user.id
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        if staff:
            PU_code = staff[0].get("U_code", "")
        else:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return self.show_accounting_menu(message)
        method = self.data[chat_id].get("receipt_method", "نامشخص")
        amount = self.data[chat_id].get("receipt_amount", 0)
        account_number = self.data[chat_id].get("receipt_account", "2نامشخص")
        before_balace = 0
        if self.db.table_exists("balance"):
            before_balace = self.db.select_dict(
                "balance", "PU_code = ?", (PU_code,))
            if before_balace:
                if self.db.column_exists("balance", "balance"):
                    before_balace = before_balace[0]["balance"]
                else:
                    before_balace = 0
            else:
                before_balace = 0
        channel_id = STORAGE_CHANNEL
        if message.content_type == "photo":
            # file_id = message.photo[-1].file_id
            receipt_photo = message.photo[-1]
            sent_msg = self.bot.send_photo(channel_id, receipt_photo.file_id)
            new_file_id = sent_msg.photo[-1].file_id
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tarikh = now
        try:
            g_date = datetime.strptime(tarikh, "%Y-%m-%d %H:%M:%S.%f")
        except:
            g_date = datetime.strptime(tarikh, "%Y-%m-%d %H:%M:%S")
        tarikh_shamsi = jdatetime.date.fromgregorian(date=g_date.date())
        tarikh_shamsi_str = f"{tarikh_shamsi.year}/{tarikh_shamsi.month}/{tarikh_shamsi.day}"
        print(f"inja chi: {tarikh_shamsi}")
        print(f" inja bayad bashe: {tarikh_shamsi_str}")
        self.db.insert("transactions", {
            "PU_code": PU_code,
            "method": method,
            "amount": amount,
            "balance_before": before_balace,  # Optional: you can store 0 for deposits
            "account_number": account_number,
            "status": "pending",
            "transaction_type": "deposit",
            "receipt_photo": new_file_id,
            "created_at": now,
            "j_date": tarikh_shamsi_str
        })
        self.bot.send_message(chat_id, "✅ رسید شما با موفقیت ثبت شد.")
        return self.show_accounting_menu(message)
    def show_invoice_history_dates(self, message):
        chat_id = message.chat.id
        self.data[chat_id] = {"invoice_step": "select_month"}
        months = [
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "عضواد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for i in range(0, 12, 3):
            markup.row(*months[i:i+3])
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "📅 لطفاً ماه مورد نظر را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_invoice_date_selection)
    def handle_invoice_date_selection(self, message):
        chat_id = message.chat.id
        selected = message.text.strip() if message.text else None
        if selected == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        months = [
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "عضواد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]
        if self.data.get(chat_id, {}).get("invoice_step") == "select_month" and selected in months:
            self.data[chat_id] = {
                "invoice_step": "select_day", "month": selected}
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=5)
            for i in range(1, 32, 7):
                markup.row(*[str(d) for d in range(i, min(i+7, 32))])
            markup.add("🔙 بازگشت")
            self.bot.send_message(
                chat_id, f"📆 ماه انتخاب شده: {selected}\nلطفاً روز مورد نظر را انتخاب کنید:", reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.handle_invoice_day_selection)
    def handle_invoice_day_selection(self, message):
        chat_id = message.chat.id
        day = message.text.strip() if message.text else None
        if day == "🔙 بازگشت":
            return self.show_invoice_history_dates(message)
        if not day.isdigit() or not (1 <= int(day) <= 31):
            self.bot.send_message(chat_id, "❌ لطفاً یک روز معتبر انتخاب کنید.")
            return self.show_invoice_history_dates(message)
        day = int(day)
        month = self.data.get(chat_id, {}).get("month")
        if not month:
            return self.show_invoice_history_dates(message)
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not staff:
            self.bot.send_message(chat_id, "❌ حساب کاربری یافت نشد.")
            return self.show_accounting_menu(message)
        PU_code = staff[0]["U_code"]
        # Build j_date to match with invoice rows
        all_rows = self.db.select_dict(
            "invoice_history", "PU_code = ?", (PU_code,))
        matched_rows = []
        for r in all_rows:
            j_date = r.get("j_date", "")
            if j_date:
                parts = j_date.split("/")
                if len(parts) == 3 and parts[1] == str(self.persian_months.index(month)+1) and parts[2] == str(day):
                    matched_rows.append(r)
        if not matched_rows:
            self.bot.send_message(
                chat_id, "❌ هیچ صورتحسابی برای این روز ثبت نشده است.")
            return self.show_invoice_history_dates(message)
        ##########################################
        lines = [f"📅 تاریخ: {matched_rows[0].get('j_date')}"]
        total_balance = 0
        for row in matched_rows:
            def fmt(val):
                try:
                    return f"{int(val):,}"
                except:
                    return "نامشخص"
            ad_id = row.get("ad_id", "نامشخص")
            base_price = fmt(row.get("base_price"))
            base_share = fmt(row.get("base_share"))
            service_price = fmt(row.get("service_price"))
            service_share = fmt(row.get("service_share"))
            profit_total = fmt(row.get("profit_total"))
            payment_method = row.get("payment_method", "نامشخص")
            credit_total = int(row.get("credit_total") or 0)
            debit_total = int(row.get("debit_total") or 0)
            total_balance += (credit_total - debit_total)
            lines.append(f"➖➖➖➖➖➖➖➖")
            lines.append(f"🔹 آگهی: {ad_id}")
            lines.append(f"💵 مبلغ پایه: {base_price}")
            lines.append(f"  🧾 سهم شما: {base_share}")
            lines.append(f"💰 مبلغ خدمات: {service_price}")
            lines.append(f"💎 سهم شما از خدمات: {service_share}")
            lines.append(f"💸 سود کل: {profit_total}")
            lines.append(f"  نوع پرداخت: {payment_method}")
            lines.append(
                f"📊 بستانکار: {fmt(credit_total)}  |  بدهکار: {fmt(debit_total)}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        lines.append(f"\n➖➖➖➖➖➖")
        sum_profit = sum(int(r.get("profit_total") or 0) for r in matched_rows)
        sum_credit = sum(int(r.get("credit_total") or 0) for r in matched_rows)
        sum_debit = sum(int(r.get("debit_total") or 0) for r in matched_rows)
        status = "✅ بستانکار" if total_balance >= 0 else "🔻 بدهکار"
        lines.append(f"💰 مجموع سود آن روز: {sum_profit:,} تومان")
        lines.append(f"✅ مجموع بستانکار: {sum_credit:,} تومان")
        lines.append(f"🔻 مجموع بدهکار: {sum_debit:,} تومان")
        lines.append(f"\n📊 وضعیت کلی: {abs(total_balance):,} تومان {status}")
        transactions = self.db.select_dict(
            "transactions", "PU_code = ?", (PU_code,))
        day_transactions = []
        for row in transactions:
            j_date = row.get("j_date", "")
            if j_date:
                parts = j_date.split("/")
                if len(parts) == 3:
                    try:
                        year, month_num, day_num = int(
                            parts[0]), int(parts[1]), int(parts[2])
                        if month_num == self.persian_months.index(month) + 1 and day_num == day:
                            day_transactions.append(row)
                    except:
                        continue
        if day_transactions:
            lines.append(f"\n➖➖➖➖➖➖")
            lines.append("\n📥 تراکنش های این روز:\n")
            for row in day_transactions:
                method = row.get("method", "نامشخص")
                amount = int(row.get("amount", 0))
                status = row.get("status", "نامشخص")
                account = row.get("account_number", "نامشخص")
                transaction_type = row.get("transaction_type", "نامشخص")
                transaction_type_text = "🟢 واریز" if transaction_type == "deposit" else "🔴 برداشت" if transaction_type == "withdrawal" else "نامشخص"
                method_text = "💵 ریالی" if method == "rial" else "🪙 کریپتو" if method == "crypto" else "نامشخص"
                status_text = {
                    "pending": "⏳ در انتظار تأیید",
                    "approved": "✅ تأیید شده",
                    "rejected": "❌ رد شده"
                }.get(status, "نامشخص")
                lines.append(f"{transaction_type_text}")
                lines.append(f"🔸 {method_text} | مبلغ: {amount:,} ")
                lines.append(f"🏦 مقصد: {account}")
                lines.append(f"📌 وضعیت: {status_text}")
                lines.append("➖")
            # tarikh = row.get("j_date")
            # amount = row.get("amount")
            # transaction_type = transactions["transaction_type"]
            #
            # t_status = transactions["status"]
            # Internal implementation note: legacy behavior is preserved during modernization.
            # print(amount)
            # print(tarikh)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
        lines.append(f"\n➖➖➖➖➖➖")
        #############################################
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت")
        sent = self.bot.send_message(
            chat_id, "\n".join(lines), reply_markup=markup)
        self.bot.register_next_step_handler(
            sent, self.handle_invoice_details_back)
    def show_transaction_history(self, message):
        chat_id = message.chat.id
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not staff:
            self.bot.send_message(chat_id, "❌ حساب کاربری شما یافت نشد.")
            return self.show_accounting_menu(message)
        PU_code = staff[0]["U_code"]
        rows = self.db.select_dict("transactions", "PU_code = ?", (PU_code,))
        if not rows:
            self.bot.send_message(chat_id, "📜 شما هیچ تراکنشی ندارید.")
            return self.show_accounting_menu(message)
        lines = ["📜 لیست تراکنش‌های شما:\n"]
        for row in sorted(rows, key=lambda x: x.get("created_at", ""), reverse=True):
            created_at_raw = row.get("created_at", "")
            try:
                if "." in created_at_raw:
                    g_date = datetime.strptime(
                        created_at_raw, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    g_date = datetime.strptime(
                        created_at_raw, "%Y-%m-%d %H:%M:%S")
                j_date = jdatetime.date.fromgregorian(date=g_date.date())
                created_at = f"{j_date.year}/{j_date.month}/{j_date.day}"
            except:
                created_at = "نامشخص"
            amount = f"{int(row.get('amount', 0)):,}"
            account = row.get("account_number", "نامشخص")
            status_raw = row.get("status", "")
            status = {
                "pending": "در انتظار تأیید",
                "approved": "تأیید شده",
                "rejected": "رد شده"
            }.get(status_raw, "نامشخص")
            balance_before = row.get("balance_before", "نامشخص")
            # Internal implementation note: legacy behavior is preserved during modernization.
            tx_type = row.get("transaction_type", "")
            tx_type_text = "واریز" if tx_type == "deposit" else "برداشت" if tx_type == "withdrawal" else "نامشخص"
            method = row.get("method", "")
            method_text = "💵 ریالی" if method == "rial" else "🪙 کریپتو" if method == "crypto" else "نامشخص"
            lines.append("➖➖➖➖")
            lines.append(f"📅 تاریخ: {created_at}")
            lines.append(f"🔄 نوع تراکنش: {tx_type_text} ({method_text})")
            lines.append(f"💵 مبلغ: {amount} تومان")
            lines.append(f"🏦 شماره مقصد: {account}")
            lines.append(f"💲 موجودی پیش از تراکنش: {balance_before}")
            lines.append(f"📌 وضعیت: {status}")
        lines.append("\n➖➖➖➖")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به حسابداری")
        sent = self.bot.send_message(
            chat_id, "\n".join(lines), reply_markup=markup)
        self.bot.register_next_step_handler(
            sent, self.handle_invoice_details_back)
    def show_invoice_details(self, message):
        chat_id = message.chat.id
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not staff:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return self.show_accounting_menu(message)
        PU_code = staff[0]["U_code"]
        rows = self.db.select_dict(
            "client_accounting", "PU_code = ?", (PU_code,))
        today_j = jdatetime.date.fromgregorian(date=datetime.now().date())
        today_str = f"{today_j.year}/{today_j.month}/{today_j.day}"
        if not rows:
            self.bot.send_message(
                chat_id, "📄 صورتحسابی برای شما ثبت نشده است.")
            return self.show_accounting_menu(message)
        lines = []
        total_balance = 0  # Track net balance
        for row in rows:
            created_at_raw = row.get("created_at")
            try:
                g_date = datetime.strptime(
                    created_at_raw, "%Y-%m-%d %H:%M:%S.%f")
            except:
                try:
                    g_date = datetime.strptime(
                        created_at_raw, "%Y-%m-%d %H:%M:%S")
                except:
                    continue
            j_date = jdatetime.date.fromgregorian(date=g_date.date())
            j_date_str = f"{j_date.year}/{j_date.month}/{j_date.day}"
            if j_date_str != today_str:
                continue  # Skip if not today
            created_at = j_date_str
            slot_time = row.get("slot_time", "نامشخص")
            client_u_code = row.get("U_code", "نامشخص")
            ad_id = row.get("ad_id", "نامشخص")
            payment_method = row.get("payment_method", "نامشخص")
            def fmt(value):
                try:
                    return f"{int(value):,}"
                except:
                    return "نامشخص"
            base_price = fmt(row.get("base_price"))
            base_share = fmt(row.get("base_share"))
            service_price = fmt(row.get("service_price"))
            service_share = fmt(row.get("service_share"))
            profit_total = fmt(row.get("profit_total"))
            balance_status = row.get("balance_status", "نامشخص")
            balance_amount_raw = row.get("balance_amount", 0)
            balance_amount = fmt(balance_amount_raw)
            # Update total balance based on status
            try:
                if balance_status.strip() == "بستانکار":
                    total_balance += int(balance_amount_raw)
                elif balance_status.strip() == "بدهکار":
                    total_balance -= int(balance_amount_raw)
            except:
                pass
            lines.append(f"➖➖➖➖➖➖➖➖")
            lines.append(f"🔹 آگهی: {ad_id}   |   🕒 زمان: {slot_time}")
            lines.append(f"👤 کد مشتری: {client_u_code}")
            lines.append(f"📅 تاریخ: {created_at}")
            lines.append(f"💵 مبلغ پایه: {base_price}")
            lines.append(f"  🧾 سهم شما: {base_share}")
            lines.append(f"💰 مبلغ خدمات: {service_price}")
            lines.append(f"💎 سهم شما از خدمات: {service_share}")
            lines.append(f"💸 سود شما: {profit_total}")
            lines.append(f"  نوع پرداخت: {payment_method}")
            lines.append(f"📊 وضعیت مالی: {balance_status} ({balance_amount})")
        # Final total
        lines.append(f"\n➖➖➖➖➖➖➖➖")
        final_status = "بستانکار" if total_balance >= 0 else "بدهکار"
        formatted_total = f"{abs(total_balance):,}"
        lines.append(f"\nمجموع: {formatted_total} {final_status}")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به حسابداری")
        sent = self.bot.send_message(
            chat_id, "\n".join(lines), reply_markup=markup)
        self.bot.register_next_step_handler(
            sent, self.handle_invoice_details_back)
