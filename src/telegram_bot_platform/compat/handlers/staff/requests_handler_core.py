from __future__ import annotations

from .requests_handler_context import *


class RequestsHandlerCoreMixin:
    def create_request(self, U_code, telegram_id, request_type, content="", target_U_code=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "U_code": U_code,
            "telegram_id": telegram_id,
            "target_U_code": target_U_code,
            "request_type": request_type,
            "content": content,
            "R_status": "pending",
            "timestamp": now,
            "created_at": now,
            "last_updated": now
        }
        self.db.insert("Requests", data)
        return True
    def insert_into_accounting(self, message, client_id, status):
        telegram_id = message.from_user.id
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        if staff:
            PU_code = staff[0]["U_code"]
            credit_rows = self.db.select_dict(
                "client_accounting",
                "PU_code = ? AND balance_status = 'بستانکار' AND settlement_status = 'open'",
                (PU_code,)
            )
            debit_rows = self.db.select_dict(
                "client_accounting",
                "PU_code = ? AND balance_status = 'بدهکار' AND settlement_status = 'open'",
                (PU_code,)
            )
            total_credit = sum(int(row.get("balance_amount") or 0)
                               for row in credit_rows)
            total_debit = sum(int(row.get("balance_amount") or 0)
                              for row in debit_rows)
            stock = total_credit - total_debit
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing = self.db.select_dict(
                "balance", "PU_code = ?", (PU_code,))
            if existing:
                old_balance = int(existing[0].get("balance") or 0)
                new_balance = old_balance + stock  # Internal implementation note: legacy behavior is preserved during modernization.
                data = {
                    "balance": new_balance,
                    "created_at": now
                }
                self.db.update("balance", data, "PU_code = ?", (PU_code,))
            else:
                data = {
                    "telegram_id": telegram_id,
                    "PU_code": PU_code,
                    "balance": stock,
                    "created_at": now
                }
                self.db.insert("balance", data)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(
                "client_accounting",
                {"settlement_status": "calculated"},
                "PU_code = ? AND settlement_status = 'open'",
                (PU_code,)
            )
        # Get today's finalized rows from client_accounting
        all_today_rows = self.db.select_dict(
            "client_accounting",
            "PU_code = ? AND settlement_status = 'calculated'",
            (PU_code,)
        )
        for row in all_today_rows:
            created_at_raw = row.get("created_at")
            try:
                g_date = datetime.strptime(
                    created_at_raw, "%Y-%m-%d %H:%M:%S.%f")
            except:
                g_date = datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M:%S")
            j_date = jdatetime.date.fromgregorian(date=g_date.date())
            j_date_str = f"{j_date.year}/{j_date.month}/{j_date.day}"
            ad_id = row.get("ad_id")
            base_share = int(row.get("base_share") or 0)
            service_share = int(row.get("service_share") or 0)
            base_price = int(row.get("base_price") or 0)
            service_price = int(row.get("service_price") or 0)
            profit_total = int(row.get("profit_total") or 0)
            client_req_id = row.get("client_rad_id")
            # Get today's all calculated rows (again) to compute totals by date
            daily_rows = [
                r for r in all_today_rows
                if jdatetime.date.fromgregorian(date=datetime.strptime(r.get("created_at", ""), "%Y-%m-%d %H:%M:%S.%f").date()
                                                if "." in r.get("created_at", "") else
                                                datetime.strptime(
                                                    r.get("created_at", ""), "%Y-%m-%d %H:%M:%S").date()
                                                ) == g_date.date()
            ]
            # Calculate daily credit and debit totals
            credit_total = sum(int(r.get("balance_amount") or 0) for r in daily_rows if r.get(
                "balance_status") == "بستانکار" and r.get("client_rad_id") == client_req_id)
            debit_total = sum(int(r.get("balance_amount") or 0) for r in daily_rows if r.get(
                "balance_status") == "بدهکار" and r.get("client_rad_id") == client_req_id)
            payment_method = row.get("payment_method", "نامشخص")
            data = {
                "PU_code": PU_code,
                "ad_id": ad_id,
                "j_date": j_date_str,     # Internal implementation note: legacy behavior is preserved during modernization.
                "base_share": base_share,
                "service_share": service_share,
                "base_price": base_price,
                "service_price": service_price,
                "credit_total": credit_total,
                "debit_total": debit_total,
                "profit_total": profit_total,
                "payment_method": payment_method,
                "created_at": now,
                "last_updated": now
            }
            self.db.insert("invoice_history", data)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = self.db.select_dict("service_requests", "id = ?", (client_id,))
        if not row:
            return
        row = row[0]
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            invoice = eval(row.get("invoice", "{}"))
        except:
            invoice = {}
        total_price = invoice.get("total_price", 0)
        base_price = invoice.get("base_price", 0)
        service_price = int(invoice.get("services_price"))
        # or invoice.get("service_price", 0))
        # Internal implementation note: legacy behavior is preserved during modernization.
        BASE_CUT = 400_000
        SERVICE_PERCENT = 0.20  # 20%
        # Internal implementation note: legacy behavior is preserved during modernization.
        base_share = max(base_price - BASE_CUT, 0)
        service_share = int(service_price * (1 - SERVICE_PERCENT))
        profit_total = base_share + service_share
        payment_method = str(row.get("payment_method") or "").strip()
        prepayment_amount = int(row.get("prepayment_amount") or 0)
        if payment_method == "پرداخت کامل قبل از شروع":
            balance_amount = profit_total
            balance_status = "بستانکار"
        elif payment_method == "پرداخت در محل":
            balance_amount = total_price - profit_total
            balance_status = "بدهکار"
        elif payment_method == "پیش‌پرداخت + مابقی در محل":
            user_received = total_price - prepayment_amount
            balance_amount = user_received - profit_total
            balance_status = "بدهکار" if balance_amount > 0 else "بستانکار"
        else:
            balance_amount = 0
            balance_status = "نامشخص"
        data = {
            "client_rad_id": client_id,
            "U_code": row.get("U_code"),
            "PU_code": row.get("PU_code"),
            "ad_id": row.get("ad_id"),
            "status": status,
            "total_price": total_price,
            "payment_method": row.get("payment_method"),
            "prepayment_amount": row.get("prepayment_amount"),
            "slot_time": row.get("slot_time"),
            "cancel_paid": row.get("cancel_paid") if status == "cancelled" else None,
            "created_at": now,
            "video_note": row.get("video_note"),
            "balance_status": balance_status,
            "balance_amount": balance_amount,
            "settled_amount": 0,
            "settlement_status": "open",
            # Internal implementation note: legacy behavior is preserved during modernization.
            "base_price": base_price,
            "base_share": base_share,
            "service_price": service_price,
            "service_share": service_share,
            "profit_total": profit_total
        }
        data["balance_status"] = balance_status
        data["balance_amount"] = balance_amount
        self.db.insert("client_accounting", data)
    def show_requests_category_menu(self, message):
        chat_id = message.chat.id
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
        U_code = user[0]["U_code"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        pending_requests = [r for r in self.get_requests_for_user(
            U_code) if r["R_status"] == "pending"]
        client_pending = self.get_pending_client_requests(U_code)
        pending_count = len(pending_requests) + len(client_pending)
        waiting_service_requests = self.get_client_requests_by_status(
            U_code, "finalized")
        waiting_count = len(waiting_service_requests)
        buttons = []
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        if pending_count:
            buttons.append(f"🕒 در انتظار پاسخ ({pending_count})")
        else:
            buttons.append("🕒 در انتظار پاسخ")
        if waiting_count:
            buttons.append(f"✅ در انتظار سرویس ({waiting_count})")
        else:
            buttons.append("✅ در انتظار سرویس")
        markup.add(*buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "📂 لطفاً دسته‌بندی درخواست‌ها را انتخاب کنید:", reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_category_selection)
    def handle_category_selection(self, message):
        text = message.text.strip() if message.text else None
        chat_id = message.chat.id
        if "🕒 در انتظار پاسخ" in text:
            return self.show_pending_requests_menu(message)
        elif text.startswith("✅ در انتظار سرویس"):
            return self.show_requests_by_status(message, "finalized")
        elif text == "❌ رد شده":
            return self.show_requests_by_status(message, "rejected")
        elif text == "🚫 لغو شده":
            return self.show_requests_by_status(message, "cancelled")
        elif text == "✔️ انجام شده":
            return self.show_requests_by_status(message, "done")
        elif text == "🔙 بازگشت":
            return self.parent.login_handler.show_work_panel(message)
        else:
            self.bot.send_message(chat_id, "❌ گزینه نامعتبر است.")
            return self.show_requests_category_menu(message)
    def get_client_requests_by_status(self, U_code, status):
        return self.db.select_dict(
            "service_requests",
            "status = ? AND PU_code = ?",
            (status, U_code)
        )
    def show_requests_by_status(self, message, status):
        chat_id = message.chat.id
        user = self.db.select_dict("staff", "telegram_id = ?", (chat_id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
        U_code = user[0]["U_code"]
        all_requests = self.get_requests_for_user(U_code)
        matching = [r for r in all_requests if r["R_status"] == status]
        client_requests = self.get_client_requests_by_status(
            U_code, status)
        if not matching and not client_requests:
            self.bot.send_message(chat_id, "📭 موردی با این وضعیت یافت نشد.")
            return self.show_requests_category_menu(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        label_map = {}
        for req in matching:
            sender_info = self.db.select_dict(
                "staff", "U_code = ?", (req["U_code"],))
            sender_name = sender_info[0]["name"] if sender_info else "کاربر ناشناس"
            req_type_label = "🔁 FMF" if req['request_type'] == "Group Service Request" else "📄 دیگر"
            label = f"{req_type_label} | از: {sender_name}"
            label_map[label] = req["id"]
            markup.add(label)
        status_lbl = STATUS_INFO[status]["title"]
        for creq in client_requests:
            requester_info = self.db.select_dict(
                "staff", "U_code = ?", (creq["U_code"],))
            requester_name = requester_info[0]["name"] if requester_info else "کاربر ناشناس"
            slot_time = creq.get("slot_time", "نامشخص")
            reserve_id = creq["id"]
            label = f"👤 مشتری (رزرو {status_lbl}) | 🕒 زمان: {slot_time} | شماره سفارش: {reserve_id}"
            label_map[label] = f"client_rad_{reserve_id}"
            markup.add(label)
        markup.add("🔙 بازگشت")
        self.data.setdefault(chat_id, {})["label_map"] = label_map
        self.bot.send_message(
            chat_id, f"📄 درخواست‌های با وضعیت: {status_lbl}", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_request_selection)
    def get_pending_client_requests(self, U_code):
        return self.db.select_dict(
            "service_requests",
            "status = ? AND PU_code = ?",
            ("approved", U_code)
        )
