from __future__ import annotations

from .requests_handler_context import *


class RequestsHandlerIntegrationsMixin:
    def handle_group_option_a_response(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        req_id = self.data.get(chat_id, {}).pop("active_request_id", None)
        request = self.get_request_by_id(req_id)
        if not request:
            self.bot.send_message(chat_id, "❌ درخواست یافت نشد.")
            return self.show_requests_category_menu(message)
        sender_u_code = request["U_code"]
        sender = self.db.select_dict(
            "staff", "U_code = ?", (sender_u_code,))
        if not sender:
            self.bot.send_message(chat_id, "❌ ارسال‌کننده درخواست یافت نشد.")
            return self.show_requests_category_menu(message)
        sender_chat_id = sender[0]["telegram_id"]
        if text == "✅ تایید درخواست":
            self.update_request_R_status(req_id, "approved")
            self.bot.send_message(chat_id, "✅ درخواست تایید شد.")
            self.parent.messages_handler.send_message(
                from_u_code=request["target_U_code"],
                to_u_code=request["U_code"],
                message_text="✅ درخواست FMF شما توسط کاربر دوم تایید شد."
            )
        elif text == "❌ رد درخواست":
            self.update_request_R_status(req_id, "rejected")
            self.bot.send_message(chat_id, "❌ درخواست رد شد.")
            self.parent.messages_handler.send_message(
                from_u_code=request["target_U_code"],
                to_u_code=request["U_code"],
                message_text="❌ درخواست FMF شما توسط کاربر دوم رد شد."
            )
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً از دکمه‌های موجود استفاده کنید.")
            return self.bot.register_next_step_handler(message, self.handle_group_option_a_response)
        return self.show_requests_category_menu(message)
    def get_requests_pending_count(self, U_code):
        return len([
            r for r in self.get_requests_for_user(U_code)
            if r["R_status"] == "pending"
        ])
    def get_requests_button_label(self, U_code):
        count = len(self.get_requests_for_user(U_code))
        pending = [r for r in self.get_requests_for_user(
            U_code) if r["R_status"] == "pending"]
        return f"📨 درخواست‌ها ({len(pending)})" if pending else "📨 درخواست‌ها"
    def get_user_requests(self, U_code):
        return self.db.select_dict("Requests", "U_code = ?", (U_code,))
    def get_requests_for_user(self, target_U_code):
        return self.db.select_dict("Requests", "target_U_code = ?", (target_U_code,))
    def get_request_by_id(self, request_id):
        rows = self.db.select_dict("Requests", "id = ?", (request_id,))
        return rows[0] if rows else None
    def update_request_R_status(self, request_id, new_status):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update("Requests", {
            "R_status": new_status,
            "last_updated": now
        }, "id = ?", (request_id,))
