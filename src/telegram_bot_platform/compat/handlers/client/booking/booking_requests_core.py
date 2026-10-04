from __future__ import annotations

from .booking_requests_context import *


class BookingHandlerCoreMixin:
    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text
        if text:
            if text == BUTTONS["back_to_main_menu"]:
                self.back_main(message)
                return True
            elif "start" in text:
                self.start(message)
                return True
            elif text == BUTTONS["back_to_pervious_menu"]:
                self.back_previous(message)
                return True
        return False
    def add_back_buttons(self, markup):
        """Legacy-compatible behavior preserved for this callable."""
        markup.add(KeyboardButton(BUTTONS["back_to_main_menu"]))
        return markup
    def _has_order_today(self, telegram_id: int) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()  # Internal implementation note: legacy behavior is preserved during modernization.
            client = {}
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                normcus = self.db.select_dict("clients", "telegram_id = ?", (telegram_id,))
                if normcus:
                    client.update(normcus[0])
            except Exception as e:
                log.warning(f"[DailyOrder] Failed to fetch normal client {telegram_id}: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                premiumcus = self.db.select_dict("premium_clients", "telegram_id = ?", (telegram_id,))
                if premiumcus:
                    client.update(premiumcus[0])
            except Exception as e:
                log.warning(f"[DailyOrder] Failed to fetch PREMIUM client {telegram_id}: {e}")
            if not client:
                log.debug(f"[DailyOrder] No client found for telegram_id={telegram_id}")
                return False
            U_code = client.get("U_code")
            if not U_code:
                log.debug(f"[DailyOrder] Client has no U_code for telegram_id={telegram_id}")
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            condition = (
                "U_code = ? AND DATE(created_at) = ? "
                "AND status IN ('pending', 'approved', 'finalized')"
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            result = self.db.select_dict(table="service_requests", condition=condition, params=(U_code, today))
            count = len(result) if result else 0
            log.debug(f"[DailyOrder] Found {count} active orders today for U_code={U_code}")
            return count > 0
        except Exception as exc:
            log.exception(f"[DailyOrder] Failed to check orders for telegram_id={telegram_id}: {exc}")
            return False
    def start_menu(self, message, data: dict):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
                # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            if self._has_order_today(message.from_user.id):
                self.bot.send_message(
                    chat_id,
                    "🚫 شما امروز یک سفارش ثبت کرده‌اید لطفا پیگیری سفارش خود را انجام دهید یا تا فردا نمی‌توانید سفارش جدیدی بدهید."
                )
                return self.back_main(message)
        except Exception as exc:
            log.exception(f"[DailyOrder] guard failed: {exc}")
            self.bot.send_message(
                chat_id,
                "❌ خطایی رخ داد؛ لطفاً بعداً دوباره امتحان کنید."
            )
            return self.back_main(message)
        self.temp_data[chat_id] = data
        self.current_request[chat_id] = {
            "selected_services": {},
            "extra_times": [],
            "payment_method": "",
            "phone": "",
            "photo_id": "",
            "video_message": ""
        }
        self.temp_data[chat_id]["slot_time"] = data.get("slot_time", "")
        self.temp_data[chat_id]["free_extra_slots"] = []
        ad_row = data.get("ad_row", {})
        if ad_row.get("dispatch_mode") == "اعزام":
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.ask_region_selection(message)
        self.send_service_selection_menu(message)
    def ask_region_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        ad_row = self.temp_data[chat_id].get("ad_row", {})
        raw_regions = ad_row.get("region", "")
        regions = [r.strip() for r in raw_regions.split(",") if r.strip()]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not regions:
            return self.send_service_selection_menu(message)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons = []
        for region in regions:
            buttons.append(KeyboardButton(region))
        markup.add(*buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.add_back_buttons(markup)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            MESSAGES["select_region_prompt"],
            reply_markup=markup
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(
            message, self.handle_region_selection)
    def handle_region_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        text = message.text.strip()
        ad_row = self.temp_data[chat_id].get("ad_row", {})
        raw_regions = ad_row.get("region", "")
        regions = [r.strip() for r in raw_regions.split(",") if r.strip()]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text not in regions:
            self.bot.send_message(
                chat_id,
                MESSAGES["invalid_region_selection"]
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.ask_region_selection(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request[chat_id]["selected_region"] = text
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.send_service_selection_menu(message)
