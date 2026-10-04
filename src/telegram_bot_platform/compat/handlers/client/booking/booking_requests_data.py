from __future__ import annotations

from .booking_requests_context import *


class BookingHandlerDataMixin:
    def ask_payment_method(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        data = self.temp_data[chat_id]
        ad_row = data.get("ad_row", {})
        raw_payment_methods = ad_row.get("payment_method", "")
        payment_methods = [pm.strip()
                           for pm in raw_payment_methods.split(",") if pm.strip()]
        if not payment_methods:
            self.bot.send_message(
                chat_id, "❌ روش پرداختی برای این آگهی ثبت نشده است.")
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        buttons = []
        for method in payment_methods:
            buttons.append(KeyboardButton(method))
        markup.add(*buttons)
        self.add_back_buttons(markup)
        msg = "💳 لطفاً روش پرداخت مورد نظر را انتخاب کن:"
        self.bot.send_message(chat_id, msg, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_payment_method)
    def handle_payment_method(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        text = message.text.strip()
        ad_row = self.temp_data[chat_id].get("ad_row", {})
        valid_methods = [pm.strip() for pm in ad_row.get(
            "payment_method", "").split(",") if pm.strip()]
        if text in valid_methods:
            self.current_request[chat_id]["payment_method"] = text
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.start_identity_verification(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را از بین دکمه‌ها انتخاب کن.")
            self.bot.register_next_step_handler(
                message, self.handle_payment_method)
    def start_identity_verification(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        self.identity_verification_service = IDENTITY_VERIFICATIONService(self.db)
        user_id = message.from_user.id
        status, completed = self.identity_verification_service.get_status(chat_id)
        if self.is_back(message):
            return
        if status == 'not_premium':
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(
                KeyboardButton(BUTTONS["submit_premium_request"]),
                KeyboardButton(BUTTONS["continue_without_premium"])
            )
            self.bot.send_message(
                chat_id, MESSAGES["premium_required_prompt"], reply_markup=markup)
            self.bot.register_next_step_handler(message, self.handle_non_premium)
        elif status == 'premium_no_identity_verification':
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(KeyboardButton(
                BUTTONS["yes"]), KeyboardButton(BUTTONS["identity_verification_later"]))
            self.bot.send_message(
                chat_id, MESSAGES["identity_verification_now_prompt"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.handle_premium_no_identity_verification_choice)
        elif status == 'identity_verification_incomplete':
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(KeyboardButton(
                BUTTONS["yes"]), KeyboardButton(BUTTONS["identity_verification_later"]))
            self.bot.send_message(
                chat_id, MESSAGES["identity_verification_incomplete_prompt"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.handle_premium_incomplete_choice)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            identity_verification_data = self.identity_verification_service.get_identity_verification_data(chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.current_request[chat_id]['identity_verification_snapshot'] = identity_verification_data.copy()
            # Internal implementation note: legacy behavior is preserved during modernization.
            row = self.db.select_dict(
                "premium_clients",
                "telegram_id = ?",
                (chat_id,)
            )[0]
            self.current_request[chat_id]["phone"] = row.get("phone")
            identity_verification_rows = self.db.select_dict(
                "identity_verification_requests",
                "telegram_id = ?",
                (user_id,)
            )[0]
            for field in identity_verification_fields:
                self.current_request[chat_id][field] = identity_verification_rows.get(field)
            self.finalize_booking(message)
    def handle_non_premium(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if self.is_back(message):
            return
        if text == BUTTONS["submit_premium_request"]:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.premiumr.start_registration(message)
            return
        if text == BUTTONS["continue_without_premium"]:
            # Internal implementation note: legacy behavior is preserved during modernization.
            missing = ['name', 'phone', 'photo_id', 'video_message']
            self._start_identity_verification_steps(message, missing)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, MESSAGES["invalid_option"])
        self.start_identity_verification(message)
    def ensure_identity_verification_table(self):
        if not self.db.table_exists("identity_verification_requests"):
            schema = {
                "telegram_id":  "BIGINT UNIQUE",
                "U_code":       "VARCHAR(32)",
                "identity_verification_docs":     "JSON",
                "status":       "VARCHAR(32)",
            }
            self.db.create_table("identity_verification_requests", schema)
            print("info[init] identity_verification_requests table created.")
    def handle_premium_no_identity_verification_choice(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_id = message.from_user.id
        text    = (message.text or "").strip()
        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == BUTTONS["yes"]:
            self.profile.identity_verification_verification(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == BUTTONS["identity_verification_later"]:
            # Internal implementation note: legacy behavior is preserved during modernization.
                                             # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                premium_rows = self.db.select_dict(
                    "premium_clients",
                    "telegram_id = ?",
                    (user_id,)
                )
                premium_row = premium_rows[0] if premium_rows else {}
            except Exception as e:
                log.error(f"[PREMIUM-later] premium_clients query failed: {e}")
                premium_row = {}
            premium_phone = premium_row.get("phone")
            premium_name  = (premium_row.get("name") or "").strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.current_request.setdefault(chat_id, {})
            if premium_phone:
                self.current_request[chat_id]["phone"] = premium_phone
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.ensure_identity_verification_table()
            try:
                rows = self.db.select_dict(
                    "identity_verification_requests",
                    "telegram_id = ?",
                    (user_id,)
                )
                user_data      = rows[0] if rows else {}
                identity_verification_status_map = json.loads(user_data.get("identity_verification_docs", "{}") or "{}")
            except Exception as e:
                log.error(f"[PREMIUM-later] identity_verification_requests query/parse failed: {e}")
                identity_verification_status_map = {}
            # Internal implementation note: legacy behavior is preserved during modernization.
            required_fields = ["name", "photo_id", "video_message"]
            missing = []
            for field in required_fields:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if identity_verification_status_map.get(field) is True:
                    continue
                # Internal implementation note: legacy behavior is preserved during modernization.
                if field == "name" and premium_name:
                    continue
                # Internal implementation note: legacy behavior is preserved during modernization.
                missing.append(field)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if missing:
                self._start_identity_verification_steps(message, missing)
                # Internal implementation note: legacy behavior is preserved during modernization.
            else:
                self.finalize_booking(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, MESSAGES["invalid_option"])
        self.start_identity_verification(message)
    def handle_premium_incomplete_choice(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        user_id = message.from_user.id
        if self.is_back(message):
            return
        if text == BUTTONS["yes"]:
            self.profile.identity_verification_verification(message)
            return
        if text == BUTTONS["identity_verification_later"]:
            snapshot = self.identity_verification_service.get_identity_verification_data(chat_id)
            self.current_request[chat_id]['identity_verification_snapshot'] = snapshot
            row = self.db.select_dict(
                "premium_clients",
                "telegram_id = ?",
                (chat_id,)
            )[0]
            self.current_request[chat_id]["phone"] = row.get("phone")
            user_data = None
            res = self.db.select_dict(
                "identity_verification_requests", "telegram_id = ?", (user_id,))
            if res:
                user_data = res[0]
            # identity_verification_docs = json.loads(user_data.get("identity_verification_docs", "{}") or "{}")
            identity_verification_status_map = json.loads(
                user_data.get("identity_verification_docs", "{}") or "{}")
            missing = []
            for field in identity_verification_fields:
                label = identity_verification_field_labels.get(field, field)
                status = identity_verification_status_map.get(field, None)
                if not status is True and field in ['name', 'photo_id', 'video_message']:
                    missing.append(field)
            self._start_identity_verification_steps(message, missing)
            return
        self.bot.send_message(chat_id, MESSAGES["invalid_option"])
        self.start_identity_verification(message)
