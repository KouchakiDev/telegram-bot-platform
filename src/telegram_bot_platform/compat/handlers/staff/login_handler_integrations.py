from __future__ import annotations

from .login_handler_context import *


class LoginHandlerIntegrationsMixin:
    def handle_invoice_details_back(self, message):
        if message.text == "🔙 بازگشت به حسابداری":
            return self.show_accounting_menu(message)
        elif message.text == "🔙 بازگشت":
            return self.show_invoice_history_dates(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً فقط از دکمه بازگشت استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_invoice_details_back)
    def show_invoice_summary(self, message):
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
        total_balance = 0
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
                continue  # Skip rows not from today
            try:
                amount = int(row.get("balance_amount", 0))
                status = row.get("balance_status", "").strip()
                if status == "بستانکار":
                    total_balance += amount
                elif status == "بدهکار":
                    total_balance -= amount
            except:
                pass
        status = "✅ بستانکار" if total_balance >= 0 else "🔻 بدهکار"
        formatted_total = f"{abs(total_balance):,}"
        text = (
            f"📊 وضعیت کلی حساب شما:\n\n"
            f"وضعیت: {status}\n"
            f"مبلغ: {formatted_total} تومان"
        )
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔍 مشاهده جزئیات", "🔙 بازگشت")
        sent = self.bot.send_message(chat_id, text, reply_markup=markup)
        self.bot.register_next_step_handler(sent, self.handle_invoice_buttons)
    def handle_invoice_buttons(self, message):
        chat_id = message.chat.id
        text = message.text
        if text == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        elif text == "🔍 مشاهده جزئیات":
            return self.show_invoice_details(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_invoice_buttons)
    def save_media_to_channel(self, message, media_type="photo") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            forwarded = self.bot.forward_message(
                STORAGE_CHANNEL,  # Internal implementation note: legacy behavior is preserved during modernization.
                message.chat.id,
                message.message_id
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            if media_type == "photo" and forwarded.photo:
                return forwarded.photo[-1].file_id
            elif media_type == "video_note" and hasattr(forwarded, 'video_note'):
                return forwarded.video_note.file_id
            elif media_type == "document" and forwarded.document:
                return forwarded.document.file_id
            elif media_type == "video" and forwarded.video:
                return forwarded.video.file_id
            else:
                raise Exception("❌ مدیا معتبر یافت نشد.")
        except Exception as e:
            print(f"❌ خطا در ذخیره مدیا: {e}")
            return ""
    def handle_settlement_type(self, message):
        chat_id = message.chat.id
        # Get financial info from DB
        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ حساب کاربری شما یافت نشد.")
            return self.show_accounting_menu(message)
        user = result[0]
        PU_code = user.get("U_code")
        # Get card and wallet info
        card_number = (user.get("card_number") or "").strip()
        card_info = (user.get("card_number_info") or "").strip()
        wallet = (user.get("wallet") or "").strip()
        wallet_network = (user.get("wallet_network") or "").strip()
        card_button = None
        wallet_button = None
        buttons = []
        # Get financial data for this user
        balance_row = self.db.select_dict("balance", "PU_code = ?", (PU_code,))
        withdrawable_balance = int(balance_row[0].get(
            "balance", 0)) if balance_row else 0
        # Masked card number
        if card_number and card_info and len(card_number) >= 8:
            masked_card = f"{card_number[:4]} **** **** {card_number[-4:]}"
            card_button = f"💳 واریز به کارت: {masked_card} به نام {card_info}"
            buttons.append(card_button)
        # Masked wallet
        if wallet and wallet_network and len(wallet) >= 10:
            masked_wallet = f"{wallet[:5]}...{wallet[-5:]}"
            wallet_button = f"🪙 واریز به کیف: {masked_wallet} ({wallet_network})"
            buttons.append(wallet_button)
        # No card or wallet registered
        if not buttons:
            self.bot.send_message(
                chat_id,
                "❗ برای ثبت درخواست تسویه، ابتدا باید اطلاعات کارت بانکی یا کیف پول خود را در بخش «حساب کاربری» ثبت کنید."
            )
            return self.show_accounting_menu(message)
        if withdrawable_balance < 0:
            debt = (
                f"شما مبلغ {abs(withdrawable_balance)} به کانال بدهکار هستید. لطفا جهت تسویه از بخش ارسال رسید اقدام کنید")
            self.bot.send_message(chat_id, debt)
            self.show_accounting_menu(message)
            return
        # Add withdrawable balance info
        info_text = (
            f"💰 موجودی قابل برداشت شما: {withdrawable_balance:,} تومان\n\n"
            f"لطفاً روش دریافت تسویه را انتخاب کنید:"
        )
        buttons.append("🔙 بازگشت")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for btn in buttons:
            markup.add(btn)
        self.bot.send_message(chat_id, info_text, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, lambda m: self.process_settlement_method(m, card_button, wallet_button))
    def process_settlement_method(self, message, card_button, wallet_button):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        if text == card_button:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.data[chat_id] = {
                "settlement_method": "rial",
                "selected_account": self.get_user_account_number(message.from_user.id, "rial")
            }
            self.bot.send_message(chat_id, "💵 مبلغ تسویه ریالی را وارد کنید:")
            self.bot.register_next_step_handler(
                message, lambda m: self.process_settlement_amount(m))
        elif text == wallet_button:
            self.data[chat_id] = {
                "settlement_method": "crypto",
                "selected_account": self.get_user_account_number(message.from_user.id, "crypto")
            }
            self.bot.send_message(chat_id, "🪙 مبلغ تسویه کریپتو را وارد کنید:")
            self.bot.register_next_step_handler(
                message, lambda m: self.process_settlement_amount(m))
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از دکمه‌های موجود را انتخاب کنید.")
            self.bot.register_next_step_handler(
                message, lambda m: self.process_settlement_method(m, card_button, wallet_button))
    def get_user_account_number(self, telegram_id, method):
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (telegram_id,))
        if not staff:
            return ""
        user = staff[0]
        if method == "rial":
            return (user.get("card_number") or "").strip()
        else:
            return (user.get("wallet") or "").strip()
    def process_settlement_amount(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.show_accounting_menu(message)
        if not text.isdigit():
            self.bot.send_message(chat_id, "❗ لطفاً فقط عدد وارد کنید.")
            return self.bot.register_next_step_handler(message, self.process_settlement_amount)
        amount = int(text)
        # Get user info
        staff = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not staff:
            self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            return self.show_accounting_menu(message)
        PU_code = staff[0]["U_code"]
        # Get current withdrawable balance
        balance_row = self.db.select_dict("balance", "PU_code = ?", (PU_code,))
        withdrawable_balance = int(balance_row[0].get(
            "balance", 0)) if balance_row else 0
        if amount > withdrawable_balance:
            self.bot.send_message(
                chat_id, f"❗ مبلغ وارد شده بیشتر از موجودی قابل برداشت ({withdrawable_balance:,} تومان) است.")
            return self.bot.register_next_step_handler(message, self.process_settlement_amount)
        # Internal implementation note: legacy behavior is preserved during modernization.
        method = self.data.get(chat_id, {}).get("settlement_method", "")
        account_number = self.data.get(chat_id, {}).get("selected_account", "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.insert("transactions", {
            "PU_code": PU_code,
            "method": method,
            "amount": amount,
            "balance_before": withdrawable_balance,
            "status": "pending",
            "account_number": account_number,
            "transaction_type": "withdrawal",
            "created_at": now
        })
        self.bot.send_message(
            chat_id, f"✅ درخواست تسویه ({'ریالی' if method == 'rial' else 'کریپتو'}) به مبلغ {amount:,} تومان ثبت شد.")
        return self.show_accounting_menu(message)
    def show_help_menu(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("راهنمای پنل کاری", "راهنمای حساب کاربری")
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "لطفاً یک بخش را برای دریافت راهنما انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_help_selection)
    def process_help_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        help_texts = {
            "راهنمای پنل کاری": (
                "📎 *راهنمای پنل کاری:*\n"
                "در این بخش شما آگهی میسازید و اطلاعات مربوط به کار را تنظیم میکنید"
            ),
            "راهنمای حساب کاربری": (
                "🛎️ *راهنمای حساب کاربری:*\n"
                "در این بخش شما اطلاعات شخصی خود را وارد میکنید"
            )
        }
        if text == "🔙 بازگشت به پنل":
            self.login_menu(message)
            return
        if text in help_texts:
            self.bot.send_message(chat_id, help_texts[text])
            # Show help menu again for more selections
            self.show_help_menu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_help_selection)
    def wait_for_back_to_panel(self, message):
        if message.text.strip() if message.text else None == "🔙 بازگشت به پنل":
            self.login_menu(message)  # Internal implementation note: legacy behavior is preserved during modernization.
        else:
            self.bot.send_message(
                message.chat.id, "لطفاً فقط از دکمه موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.wait_for_back_to_panel)
