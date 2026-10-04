from __future__ import annotations

from .login_handler_context import *


class LoginHandlerFlowsMixin:
    def show_work_panel(self, message):
        chat_id = message.chat.id
        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ حساب کاربری شما یافت نشد.")
            return self.parent.send_welcome(message)
        U_code = result[0]["U_code"]
        requests_label = self.parent.requests_handler.get_requests_button_label(
            U_code)
        messages_count = self.parent.messages_handler.get_unread_count(U_code)
        messages_label = f"📬 پیام‌ها ({messages_count})" if messages_count else "📬 پیام‌ها"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("آگهی ها 📢", "حسابداری 💵")
        markup.add(messages_label, requests_label)
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "لطفاً بخش مورد نظر را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_work_panel)
    def process_work_panel(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت به پنل":
            self.login_menu(message)
        elif text == "آگهی ها 📢":
            return self.show_ads_menu(message)
        elif text == "حسابداری 💵":
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.show_accounting_menu(message) #self.show_work_panel(message) 
        elif text.startswith("📬 پیام"):
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.parent.messages_handler.show_messages_menu(message) #self.show_work_panel(message) #
        elif text.startswith("📨 درخواست‌ها"):
            return self.parent.requests_handler.show_requests_category_menu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(message, self.show_work_panel)
    def show_ads_menu(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add("📢 ساخت آگهی" , "تنظیمات آکهی ⚙️")
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "📢 لطفاً یکی از گزینه‌های آگهی را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_ad_menu_selection)
    def handle_ad_menu_selection(self, message):
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.show_work_panel(message)
        elif text == "📢 ساخت آگهی":
            return self.parent.ad_creation_handler.start_featured_ad(message)
        elif text == "📂 آگهی‌های من":
            return self.parent.ad_creation_handler.show_my_ads_menu(message)
        elif text == "تنظیمات آکهی ⚙️":
            return self.parent.services_handler.show_ad_settings(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_ad_menu_selection)
    def show_accounting_menu(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🧾 نمایش صورتحساب", "📜 تاریخچه تراکنش‌ها")
        markup.add("📆 تاریخچه صورتحساب", "🖼 ارسال رسید")
        markup.add("💸 درخواست تسویه")
        markup.add("🔙 بازگشت به پنل")
        self.bot.send_message(
            chat_id, "لطفاً یکی از گزینه‌های حسابداری را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_accounting_menu)
    def handle_accounting_menu(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🧾 نمایش صورتحساب":
            self.bot.send_message(chat_id,"بزودی...")
            return self.show_accounting_menu(message) #self.show_invoice_summary(message)
        elif text == "📜 تاریخچه تراکنش‌ها":
            self.bot.send_message(chat_id,"بزودی...")
            return self.show_accounting_menu(message) #self.show_transaction_history(message)
        elif text == "🖼 ارسال رسید":
            return self.handle_receipt_menu(message) #self.start_receipt_flow(message)
        elif text == "💸 درخواست تسویه":
            self.bot.send_message(chat_id,"بزودی...")
            return self.show_accounting_menu(message) #self.handle_settlement_type(message)
        elif text == "📆 تاریخچه صورتحساب":
            self.bot.send_message(chat_id,"بزودی...")
            return self.show_accounting_menu(message)  #self.show_invoice_history_dates(message)
        elif text == "🔙 بازگشت به پنل":
            return self.show_work_panel(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            return self.show_accounting_menu(message)
    def handle_receipt_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            # Internal implementation note: legacy behavior is preserved during modernization.
            admin_enabled_wallet = True
            admin_enabled_card =  False
            # Internal implementation note: legacy behavior is preserved during modernization.
            has_card = bool(self.db.select_dict("cards", "is_default = 1"))
            has_wallet = bool(self.db.select_dict("wallets", "is_default = 1"))
            can_use_card = admin_enabled_card and has_card
            can_use_wallet = admin_enabled_wallet and has_wallet
            logger.info(f"[handle_receipt_menu] can_use_card={can_use_card}, can_use_wallet={can_use_wallet} | chat_id={chat_id}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not can_use_card and not can_use_wallet:
                self.bot.send_message(chat_id, "ℹ️ در حال حاضر امکان انتخاب روش پرداخت فعال نیست. لطفاً رسید را به‌صورت دستی ارسال کنید.")
                return self.handle_receipt_photo_taker_menu(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True , row_width=2)
            buttons = []
            if can_use_card:
                buttons.append("💵 واریز ریالی")
            if can_use_wallet:
                buttons.append("🪙 واریز کریپتو")
            markup.add(*buttons)
            markup.add("🔙 بازگشت")
            self.bot.send_message(
                chat_id, "لطفاً نوع واریز را انتخاب کنید:", reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self.handle_receipt__selection)
        except Exception as e:
            logger.exception(f"[handle_receipt_menu] Error occurred: {e}")
            self.bot.send_message(message.chat.id, "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
            return self.show_accounting_menu(message)
    def load_video_directory(self, folder_path: str, allowed_exts=("mp4", "mov", "gif", "mkv")) -> dict:
        """Legacy-compatible behavior preserved for this callable."""
        video_map = {}
        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    name, ext = os.path.splitext(filename)
                    if ext.lower().lstrip(".") in allowed_exts:
                        key = f"Train_{name}"
                        video_map[key] = file_path
                        logger.debug(f"[load_video_directory] Added video key={key} → path={file_path}")
        except Exception as e:
            logger.exception(f"[load_video_directory] Error reading directory: {e}")
        return video_map
    def callBack_handler(self):
        """Legacy-compatible behavior preserved for this callable."""
        TID = "@EasyTether"
        try:
            video_dir = os.path.join(os.path.dirname(__file__), "..", "..", "Data", "Train")
            self.training_sources = self.load_video_directory(video_dir)
            logger.info(
                f"[callBack_handler] Training video sources loaded → total={len(self.training_sources)}"
            )
            for k, p in self.training_sources.items():
                logger.debug(f"[callBack_handler] Loaded video key={k} → path={p}")
            @self.bot.callback_query_handler(func=lambda c: c.data.startswith("Train_"))
            def handle_training_video_callback(call: CallbackQuery):
                chat_id = call.message.chat.id
                cb = call.data
                logger.info(f"[callback] Received callback={cb} | chat_id={chat_id}")
                try:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.bot.answer_callback_query(call.id)
                except Exception as ack_err:
                    logger.warning(f"[callback] ACK failed: {ack_err}")
                # Internal implementation note: legacy behavior is preserved during modernization.
                if cb == "Train_Help":
                    logger.debug("[callback] Sending text help …")
                    self.bot.send_message(
                        chat_id,
                        (
                            "<b>💼 راهنمای پرداخت:</b>\n\n"
                            "لطفاً طبق یکی از ویدیوهای آموزشی بالا، مبلغ مورد نظر را به آدرس ولت مشخص‌شده <u>واریز</u> نمایید.\n"
                            "پس از انجام واریز، <b>تصویر رسید</b> خود را همین‌جا ارسال کنید تا بررسی و تأیید شود.\n\n"
                            "⏱ <i>پردازش و تأیید رسیدها معمولاً ظرف چند دقیقه انجام خواهد شد.</i>\n"
                            "در صورت هرگونه سؤال، از طریق بخش <b>پیام‌ها</b> در ربات اقدام به ارسال تیکت نمایید.\n\n"
                            f"<b>📌 آیدی تلگرامی برای خرید آسان تتر:</b> "
                            f"<a href='https://t.me/{TID.strip('@')}'>{TID}</a>\n\n"
                            "✅ <b>در صورت خرید از آیدی فوق، کارمزد خرید و هزینه انتقال کاملاً بر عهده کانال بوده</b> "
                            "و شما <u>هیچ مبلغ اضافه‌ای</u> پرداخت نخواهید کرد."
                        ),
                        parse_mode="HTML",
                    )
                    logger.info(f"[callback] Help text sent | chat_id={chat_id}")
                    return  # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                source_path = self.training_sources.get(cb)
                if not source_path:
                    logger.error(f"[callback] Unknown callback key: {cb}")
                    self.bot.send_message(chat_id, "❌ ویدیوی درخواستی یافت نشد.")
                    return
                logger.debug(f"[callback] Mapped video path={source_path}")
                try:
                    with open(source_path, "rb") as f:
                        self.bot.send_video(
                            chat_id,
                            f,
                            supports_streaming=True,
                            caption="🎬 ویدیوی آموزشی",
                        )
                    logger.info(f"[callback] Video sent | file={source_path} | chat_id={chat_id}")
                except Exception as e:
                    logger.exception(f"[callback] Failed to send video | file={source_path} | chat_id={chat_id} | err={e}")
                    self.bot.send_message(chat_id, "❌ ارسال ویدیو با مشکل مواجه شد.")
        except Exception as e:
            logger.exception(f"[callBack_handler] Error initializing callback handler: {e}")
    def handle_receipt__selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip() if message.text else ""
        training_labels = {
            "🎬 خرید تتر از والکس": "ExChangeVideoTrain",
            "🎥 خرید تتر از تلگرام": "TID_videoTrain"
        }
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == "🔙 بازگشت":
            logger.info(f"[handle_receipt__selection] Back pressed | chat_id={chat_id}")
            return self.show_accounting_menu(message)
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if text == "💵 واریز ریالی":
                method = "rial"
                rows = self.db.select_dict("cards", "is_default = 1")
                if not rows:
                    self.bot.send_message(chat_id, "❗ هیچ کارت پیش‌فرضی یافت نشد.")
                    return self.show_accounting_menu(message)
                card = rows[0]
                info = (
                    f"💳 شماره کارت: `{card.get('card_number','نامشخص')}`\n"
                    f"👤 به نام: {card.get('cardholder_name','نامشخص')}"
                )
                account = card.get("card_number", "")
            elif text == "🪙 واریز کریپتو":
                method = "crypto"
                rows = self.db.select_dict("wallets", "is_default = 1")
                if not rows:
                    self.bot.send_message(chat_id, "❗ هیچ کیف پول پیش‌فرضی یافت نشد.")
                    return self.show_accounting_menu(message)
                wallet = rows[0]
                info = (
                    f"🪙 ارز: {wallet.get('crypto','نامشخص')}\n"
                    f"🌐 شبکه: {wallet.get('network','نامشخص')}\n"
                    f"📬 آدرس: `{wallet.get('address','نامشخص')}`"
                )
                account = wallet.get("address", "")
            else:
                logger.warning(f"[handle_receipt__selection] Invalid choice: {text} | chat_id={chat_id}")
                self.bot.send_message(chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
                return self.start_receipt_flow(message)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.data.setdefault(chat_id, {})["receipt_method"] = method
            self.data[chat_id]["receipt_account"] = account
            logger.info(f"[handle_receipt__selection] Method={method}, Account={account} | chat_id={chat_id}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            prompt = info
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="راهنمای پرداخت", callback_data = "Train_Help"))
            callbacks = []
            for label, id  in training_labels.items():
                callback_id = f"Train_{id}"
                callbacks.append(callback_id)
                markup.add(types.InlineKeyboardButton(text=label, callback_data=callback_id))
            logger.debug(callbacks)
            self.bot.send_message(chat_id, prompt, parse_mode="Markdown", reply_markup=markup)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.handle_receipt_photo_taker_menu(message)
        except Exception as e:
            logger.exception(f"[handle_receipt__selection] Exception: {e} | chat_id={chat_id}")
            self.bot.send_message(chat_id, "⚠️ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
            return self.show_accounting_menu(message)
    def handle_receipt_photo_taker_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            # Internal implementation note: legacy behavior is preserved during modernization.
            # TID_TRAIN_VIDEO = r"./Data/TID_videoTrain.mp4"
            # EXCHANGE_TRAIN = r"./Data/ExChangeVideoTrain.mp4"
            TID = "@EasyTether"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("🔙 بازگشت")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # with open(TID_TRAIN_VIDEO, "rb") as video1:
            #     self.bot.send_animation(chat_id, video1)
            # with open(EXCHANGE_TRAIN, "rb") as video2:
            #     self.bot.send_animation(chat_id, video2)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "📸 لطفاً تصویر رسید واریزی خود را ارسال کنید:",reply_markup=markup,)
            self.bot.register_next_step_handler(message, self.handle_receipt_upload)
        except Exception as e:
            logger.exception(f"[handle_receipt_photo_taker_menu] Exception occurred: {e}")
            self.bot.send_message(chat_id, "❌ در ارسال آموزش مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
