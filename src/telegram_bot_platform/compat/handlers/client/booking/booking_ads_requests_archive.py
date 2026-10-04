# booking_ads_requests.py

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import json
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.
from datetime import datetime ,timedelta 
from telegram_bot_platform.compat.handlers.client.verification.identity_verification import *
import re
from telebot import types , TeleBot
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
# services/identity_verification_service.py
# from database.DataBaseManager import DatabaseManager
import json
# from telegram_bot_platform.compat.handlers.client.premium.premium_profile import PREMIUMProfileH
from telegram_bot_platform.compat.handlers.client.premium.premium_registeration import PREMIUMRegistration
from telegram_bot_platform.compat.handlers.client.premium.premium_profile import PREMIUMProfile
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
log = CustomLogger("booking_ads")
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# from telegram_bot_platform.compat.config.settings import CLIENT_BOT_ID, CHANNEL_ID, BUTTONS
# from datetime import datetime
import html
class BookingHandler:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot : TeleBot, db: DatabaseManager, back_main, back_previous, start):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.db = db
        self.back_main = back_main
        self.back_previous = back_previous
        self.start = start
        self.premiumr = PREMIUMRegistration(bot, db, back_main, back_previous)
        self.profile = PREMIUMProfile(bot, db, back_main, back_previous, start)
        self.settings = REQUEST_SETTINGS
        self.admin_bot = TeleBot(BOT_ADMIN_TOKEN)
        self.staff_bot = TeleBot(BOT_STAFF_TOKEN)
        
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_data = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.identity_verification_manager = None
        self.identity_verification_user = None

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

    def _start_identity_verification_steps(self, message, missing_fields: list):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        manager = AuthenticationManager()
        # Internal implementation note: legacy behavior is preserved during modernization.
        manager.skip_step = True
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        for field in missing_fields:
            prompt = IDENTITY_VERIFICATION_PROMPTS[field]
            if field == "name":
                manager.add_step(TextAuthStep(field, prompt))
            elif field == "phone":
                manager.add_step(ContactAuthStep(field, prompt))
            elif field == "photo_id":
                manager.add_step(PhotoAuthStep(field, prompt))
            elif field == "video_message":
                manager.add_step(VideoAuthStep(field, prompt))

        # Internal implementation note: legacy behavior is preserved during modernization.
        manager.on_complete(self._on_identity_verification_complete)
        self.identity_verification_manager = manager
        self.identity_verification_user = chat_id
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.run_next_identity_verification_step(message)

    def run_next_identity_verification_step(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        for step in self.identity_verification_manager.steps:
            if step.enabled and step.response is None:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)

                if step.step_type == "contact":
                    contact_button = KeyboardButton(
                        text="📱 ارسال شماره من", request_contact=True)
                    markup.add(contact_button)
                markup = self.add_back_buttons(markup)

                self.bot.send_message(
                    chat_id, step.prompt, reply_markup=markup)

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.register_next_step_handler(
                    message, lambda msg, current_step=step: self.handle_identity_verification_response(msg, current_step))
                return
        # Internal implementation note: legacy behavior is preserved during modernization.
        results = {
            s.name: s.response for s in self.identity_verification_manager.steps if s.enabled}
        self.current_request[chat_id].update(results)
        self.finalize_booking(message)

    def handle_identity_verification_response(self, message, step):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        if step.step_type == "contact" and message.contact and message.contact.phone_number:
            step.response = message.contact.phone_number
        elif step.name == "name":
            if message.text:
                text = message.text.strip()
                if len(text) > 72:
                    self.bot.send_message(
                        chat_id, "❌ نام وارد شده بیش از ۷۲ کاراکتر است.")
                    return self.run_next_identity_verification_step(message)

                # Internal implementation note: legacy behavior is preserved during modernization.
                valid_name_regex = r'^([a-zA-Z\u0600-\u06FF]{2,})(\s[a-zA-Z\u0600-\u06FF]{2,}){0,3}$'

                if not re.match(valid_name_regex, text):
                    self.bot.send_message(
                        chat_id,
                        "❌ نام باید فقط شامل حروف فارسی یا انگلیسی باشد، بدون عدد یا علامت، و حداکثر ۴ بخش."
                    )
                    return self.run_next_identity_verification_step(message)

                step.response = text
            else:

                self.bot.send_message(
                    chat_id, "❌ لطفاً اطلاعات معتبر وارد کنید.")
                return self.run_next_identity_verification_step(message)
        elif step.step_type == "photo" and message.photo:
            step.response = self.save_media_to_channel(message, "photo")
        elif step.step_type == "video" and hasattr(message, 'video_note') and message.video_note:

            step.response = self.save_media_to_channel(message, "video_note")
        else:
            self.bot.send_message(chat_id, "❌ لطفاً اطلاعات معتبر وارد کنید.")
            return self.run_next_identity_verification_step(message)
        self.run_next_identity_verification_step(message)

    def _on_identity_verification_complete(self, results: dict):
        """Legacy-compatible behavior preserved for this callable."""
        telegram_id = self.identity_verification_user
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.identity_verification_service.save_identity_verification_data(telegram_id, results)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update(
            "premium_clients",
            {"identity_verification_status": "completed"},
            "telegram_id = ?",
            (telegram_id,)
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request[telegram_id]['identity_verification_snapshot'] = results.copy()
        # Internal implementation note: legacy behavior is preserved during modernization.
        fake_message = types.Message()  # Internal implementation note: legacy behavior is preserved during modernization.
        fake_message.chat = types.SimpleNamespace(id=telegram_id)
        self.finalize_booking(fake_message)

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

    def finalize_booking(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id
        username = user.username or ""
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        ad_row = self.temp_data[chat_id].get("ad_row", {})
        staff = self.temp_data[chat_id].get("staff", {})
        slot_row = self.temp_data[chat_id].get("slot", [{}])[0]
        slot_time = self.temp_data[chat_id].get("slot_time", "")
        extra_times = self.current_request[chat_id].get("extra_times", [])
        selected_svcs = self.current_request[chat_id].get(
            "selected_services", {})
        payment_meth = self.current_request[chat_id].get("payment_method", "")
        phone = self.current_request[chat_id].get("phone", "")
        photo_id = self.current_request[chat_id].get("photo_id", "")
        video_note = self.current_request[chat_id].get("video_message", "")
        selected_region = self.current_request[chat_id].get(
            "selected_region", "درمحل")
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            time_slots = json.loads(slot_row.get("time_slots", "{}"))
            times = sorted(time_slots.keys())
            last_slot = extra_times[-1] if extra_times else slot_time
            idx = times.index(last_slot)
            end_time = times[idx + 1] if idx + 1 < len(times) else last_slot
        except Exception:
            end_time = slot_time

        # Internal implementation note: legacy behavior is preserved during modernization.
        base_price = int(staff.get("service_price", 0) or 0)
        svc_defs = {}
        svc_defs.update(json.loads(ad_row.get("services", "{}")))
        svc_defs.update(json.loads(ad_row.get("premium_services", "{}")))
        services_price = sum(
            int(svc_defs.get(k, {}).get("price", 0) or 0)
            for k, v in selected_svcs.items() if v
        )
        extra_cost = len(extra_times) * base_price
        total_price = base_price + services_price + extra_cost

        # Internal implementation note: legacy behavior is preserved during modernization.
        invoice = {
            "base_price":      base_price,
            "services_price":  services_price,
            "extra_time_cost": extra_cost,
            "total_price":     total_price
        }
        print(invoice)

        # Internal implementation note: legacy behavior is preserved during modernization.
        user_exists = self.db.select_dict(
            "clients", "telegram_id = ?", (user_id,)
        )
        if not user_exists:
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_idx = self.db.count_rows(
                "clients") if self.db.table_exists("clients") else 0
            U_code = f"c{next_idx + 1 + 3420}"
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.insert("clients", {
                "telegram_id": user_id,
                "U_code":      U_code,
                "name":        self.current_request[chat_id].get("name", "")
            })
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            U_code = user_exists[0].get("U_code")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # current_name = user_exists[0].get("name", "")
            new_name = self.current_request[chat_id].get("name", "")
            # if not current_name and new_name:
            #     self.db.update("clients", {"name": new_name},
            #                    "telegram_id = ?", (user_id,))
            self.db.update("clients", {"name": new_name},
                           "telegram_id = ?", (user_id,))
        # Internal implementation note: legacy behavior is preserved during modernization.
        status_code, _ = self.identity_verification_service.get_status(chat_id)
        AutoApproval = status_code == "identity_verification_complete"

        # status_code, _ = self.identity_verification_service.get_status(chat_id)
        # status = "approved" if status_code == "identity_verification_complete" and AutoApproval else "pending"
        created_at = datetime.now()
        # Internal implementation note: legacy behavior is preserved during modernization.
        
        def format_time(val):
            if isinstance(val, datetime):
                return val.strftime("%H:%M")
            elif isinstance(val, timedelta):
                return (datetime.min + val).strftime("%H:%M")
            elif isinstance(val, str) and ":" in val:
                return val[:5]
            return str(val)

        final_data = {
            "created_at":         created_at,
            "U_code":             U_code,
            "PU_code":            staff.get("U_code", ""),
            "ad_id":              ad_row.get("id"),

            # Internal implementation note: legacy behavior is preserved during modernization.
            "slot_time":          format_time(slot_time),
            "start_time":         format_time(slot_time),
            "end_time":           format_time(end_time),

            # Internal implementation note: legacy behavior is preserved during modernization.
            "extra_times":        json.dumps([
                format_time(t) for t in extra_times
            ]),
            "selected_services":  json.dumps(selected_svcs),
            "invoice":            json.dumps(invoice),

            # Internal implementation note: legacy behavior is preserved during modernization.
            "payment_method":     payment_meth,
            "phone":              phone,
            "photo_id":           photo_id,
            "video_note":         video_note,
            "selected_region":    selected_region,
            "status":             "pending"
        }
        log.debug(final_data)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.insert("service_requests", final_data)

        # Internal implementation note: legacy behavior is preserved during modernization.
        


        # Internal implementation note: legacy behavior is preserved during modernization.
        summary = (
            "✅ رزرو شما با موفقیت ثبت شد!\n"
            f"🧾 مبلغ کل: {total_price:,} تومان\n"
            "در اسرع وقت با شما تماس خواهیم گرفت."
        )
        self.bot.send_message(chat_id, summary)
        if AutoApproval:
            
            try:
                condition = (
                    "U_code = %s AND "
                    "PU_code = %s AND "
                    "ad_id = %s AND "
                    "slot_time = %s AND "
                    "start_time = %s AND "
                    "end_time = %s AND "
                    "status = %s"
                )
                params = (
                    final_data["U_code"],
                    final_data["PU_code"],
                    final_data["ad_id"],
                    final_data["slot_time"],
                    final_data["start_time"],
                    final_data["end_time"],
                    final_data["status"],
                )

                log.debug(f"[AutoType5] SELECT condition:\n{condition}")
                log.debug("[AutoType5] Parameters:")
                for key, value in zip(
                    ["U_code", "PU_code", "ad_id", "slot_time", "start_time", "end_time", "status"],
                    params
                ):
                    log.debug(f"    {key} = {value}")

                result = self.db.select_dict("service_requests", condition, params)
                log.debug(f"[AutoType5] Query result: {result}")

                if not result:
                    raise ValueError("Record not found for auto-approval")

                last_id = result[0]["id"]
                log.info(f"[AutoType5] Auto-approval record found → ID = {last_id}")
                try:
                    log.info(f"[AutoType5] Trying auto_accept_premium_client for request ID: {last_id}")
                    self.auto_accept_premium_client(message, last_id)
                    log.info(f"[AutoType5] auto_accept_premium_client executed successfully for request ID: {last_id}")
                except Exception as ex:
                    log.warning(f"[AutoType5] auto_accept_premium_client FAILED for request ID: {last_id} | Error: {ex}")

                    
                self.bot.send_message(
                    chat_id,
                    "🌟 به دلیل ویژه بودن حساب شما و تکمیل احراز هویت، درخواستتان به‌صورت خودکار تأیید و برای پرسنل ارسال شد. لطفاً منتظر پاسخ از سمت پرسنل باشید."
                )
            except Exception as ex:
                log.warning(f"[AutoType5] Error in automatic approval: {ex}")

            

            # Internal implementation note: legacy behavior is preserved during modernization.
        self.back_main(message)   
       
    def auto_accept_premium_client(self, message, request_id):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        log.info(f"[TYPE5] Start auto_accept_premium_client | request_id={request_id}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            table = "service_requests"
            status_column = self.settings.get(table, {}).get("status_column", "status")
            rows = self.db.select_dict(table, "id = ?", (request_id,))
            if not rows:
                log.warning(f"[TYPE5] Request id={request_id} not found.")
                return
            req = rows[0]
            U_code = req.get("U_code")
            PU_code = req.get("PU_code")
            ad_id = req.get("ad_id")
            def normalize_time(val):
                if isinstance(val, timedelta):
                    return (datetime.min + val).strftime("%H:%M")
                if isinstance(val, datetime):
                    return val.strftime("%H:%M")
                if isinstance(val, str):
                    return val[:5] if ":" in val else val
                return str(val)
            
            slot_time = normalize_time(req.get("slot_time"))
            extra_times = [normalize_time(t) for t in json.loads(req.get("extra_times") or "[]")]


            log.debug(f"[TYPE5] Loaded request data | U_code={U_code}, PU_code={PU_code}, ad_id={ad_id}, slot={slot_time}, extra={extra_times}")
            ad_row = self.db.select_dict("ads", "id = ?", (ad_id,))
            ad_row = ad_row[0] if ad_row else {}
        except Exception as e:
            log.error(f"[TYPE5] Failed to fetch request/ad data: {e}")
            return
        
        
        # Internal implementation note: legacy behavior is preserved during modernization.
        
        try:
            def normalize_time(val):
                if isinstance(val, timedelta):
                    return (datetime.min + val).strftime("%H:%M")
                elif isinstance(val, datetime):
                    return val.strftime("%H:%M")
                elif isinstance(val, str) and ":" in val:
                    return val[:5]  # Internal implementation note: legacy behavior is preserved during modernization.
                return str(val)

            # Internal implementation note: legacy behavior is preserved during modernization.
            slot_time = normalize_time(req.get("slot_time"))
            extra_times_raw = req.get("extra_times") or "[]"
            extra_times = [normalize_time(t) for t in json.loads(extra_times_raw)]

            all_times = list(set([slot_time] + extra_times))  # Internal implementation note: legacy behavior is preserved during modernization.
            placeholders = ",".join("?" for _ in all_times)
            query = f"U_code != ? AND ad_id = ? AND slot_time IN ({placeholders})"
            params = (U_code, ad_id, *all_times)

            log.debug(f"[TYPE5] Looking for conflicts with times: {all_times}")

            conflicts = self.db.select_dict(table, query, params)
            user_map = {r["U_code"]: r.get("telegram_id") for r in conflicts if r.get("telegram_id")}
            ucodes = list(user_map.keys())

            if ucodes:
                ph = ",".join("?" for _ in ucodes)
                self.db.update(table, {status_column: "expired"}, f"U_code IN ({ph})", ucodes)
                for tg_id in user_map.values():
                    self.bot.send_message(tg_id, "❌ درخواست شما برای این تایم لغو شد؛ ظرفیت پر شده است.")
            log.info(f"[TYPE5] Expired duplicate requests: {ucodes}")
        except Exception as e:
            log.warning(f"[TYPE5] Failed to expire duplicates: {e}")


        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            admins = self.db.select_dict("admins")
            notified = []
            for admin in admins:
                perms = json.loads(admin.get("permissions") or "{}")
                if perms.get("manage_requests") and admin.get("telegram_id"):
                    notified.append(admin["telegram_id"])
                    
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    start_time = datetime.strptime(slot_time, "%H:%M")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    end_time = start_time + timedelta(minutes=BETWIN_TIME)
                    end_time_str = end_time.strftime("%H:%M")  # Internal implementation note: legacy behavior is preserved during modernization.
                    
                    self.admin_bot.send_message(
                        admin["telegram_id"],
                        f"<b>درخواست یک مشتری ویژه به صورت خودکار تایید شد ✅</b>\n\n"
                        f"<b>جزئیات:</b> 📝\n"
                        f"<b>کد ارائه‌دهنده:</b> /{PU_code} 🧑‍💼\n"
                        f"<b>کد مشتری:</b> {U_code} 👤\n"
                        f"<b>زمان شروع:</b> {slot_time} ⏰\n"
                        f"<b>زمان پایان:</b> {end_time_str} 🕒\n\n",
                        parse_mode="HTML"
                    )
            log.info(f"[TYPE5] Sent admin notifications: {notified}")
        except Exception as e:
            log.error(f"[TYPE5] Failed to notify admins: {e}")




        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.bot.send_message(chat_id, MESSAGES["request_approved_clients"])
            staff = self.db.select_dict("staff", "U_code = ?", (PU_code,))
            if staff:
                self.staff_bot.send_message(
                    staff[0]["telegram_id"],
                    MESSAGES["request_approved_staff"]
                )
            log.info(f"[TYPE5] Sent confirmation messages to client and staff")
        except Exception as e:
            log.error(f"[TYPE5] Failed to notify client/staff: {e}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            live = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
            if not live:
                log.warning(f"[TYPE5] live_ads entry not found for ad_id={ad_id}.")
                return
            live = live[0]
            msg_id = live.get("channel_message_id")
            slots = json.loads(live.get("time_slots") or "{}")
            log.debug(f"Slots of live ads takeed ==== {slots}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            normalized_slots = {normalize_time(k): v for k, v in slots.items()}
            slot_time = normalize_time(slot_time)
            extra_times = [normalize_time(t) for t in extra_times]
            
            if slot_time in normalized_slots:
                normalized_slots[slot_time] = False
            for t in extra_times:
                if t in normalized_slots:
                    normalized_slots[t] = False
            slots = normalized_slots
            log.debug(f"Slots of live ads takeed after change ==== {slots}")

            log.debug(f"Slots of live ads takeed after change ==== {slots}")
            
            # Internal implementation note: legacy behavior is preserved during modernization.
            keyboard = InlineKeyboardMarkup()
            link_base = f"https://t.me/{html.escape(CLIENT_BOT_ID)}?start"
            buttons = []
            for s, available in slots.items():
                log.debug(f"slot = {s} | status {available}")
                if available:
                    log.debug(f"status  = {available} And this slot avalabel")
                    
                    fmt = datetime.strptime(s, "%H:%M").strftime("%H_%M")
                    buttons.append(InlineKeyboardButton(s, url=f"{link_base}=reserve_ads_{ad_id}_{fmt}"))
                else:
                    log.debug(f"status  = {available} And this slot not avalabel")
                    
                    buttons.append(InlineKeyboardButton("رزرو شده 🕰", url=f"{link_base}=ShowAvalabelCodes"))
            rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
            if len(rows) >= 2 and len(rows[-1]) == 1:
                flat = sum(rows, [])
                rows = [flat[i:i+3] for i in range(0, len(flat), 3)]
            rows.append([
                InlineKeyboardButton(BUTTONS["Goto_Cutsomer_bot"], url=f"https://t.me/{CLIENT_BOT_ID}?start"),
                InlineKeyboardButton(BUTTONS["Add_toFavoris"], callback_data=f"AddToFavorits_{ad_row['U_code']}")
            ])
            for r in rows:
                log.debug(f"[TYPE5] Adding row: {[b.text for b in r]}")
                keyboard.row(*r)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.edit_message_reply_markup(chat_id=CHANNEL_ID, message_id=msg_id, reply_markup=keyboard)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update("live_ads", {"time_slots": json.dumps(slots, ensure_ascii=False)}, "id = ?", (live["id"],))
            self.db.update(table, {status_column: "approved"}, "id = ?", (request_id,))
            log.info(f"[TYPE5] Request {request_id} approved and live_ads updated.")
        except Exception as e:
            log.warning(f"[TYPE5] Failed to update channel or live_ads: {e}")

        log.info(f"[TYPE5] Finished auto_accept_premium_client for request_id={request_id}")
