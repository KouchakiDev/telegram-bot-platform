from telegram_bot_platform.compat.config.settings import *
import re
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from datetime import datetime, timedelta
from telebot import types
import json
import jdatetime
from math import ceil
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

logger = CustomLogger("ad_creation")

# Internal implementation note: legacy behavior is preserved during modernization.
     # Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
BACK_TO_PANEL      = BUTTONS["back_to_pannel"]
BACK_GENERIC       = BUTTONS["back"]
BACK_TO_MAIN       = BUTTONS["back_to_main"]    # Internal implementation note: legacy behavior is preserved during modernization.
START_CMD_PREFIXES = ("/start",)  
class AdCreationHandler(StepHandlerMixin):
    def __init__(self, bot, data, parent):
        self.bot = bot
        self.data = data
        self.parent = parent
        self.ad_creation_steps = ad_creation_steps  # add this
        self.service_key_map = {
            "گزینه خدمات ۱": "back",
            "گروه خدمات": "group_option_b",
            "گزینه خدمات A": "group_option_a",
            "گزینه خدمات ۲": "service_option_2",
            "گزینه خدمات ۳": "service_option_3",
            "گزینه خدمات ۴": "service_option_4"
        }

    ADS_TABLE_SCHEMA = {
        "U_code": "TEXT",
        "creation_date": "TEXT",
        "start_time": "TEXT",
        "end_time": "TEXT",
        "service_count": "INTEGER",
        "status": "TEXT",
        "payment_method": "TEXT",
        "ad_photo": "TEXT",
        "region": "TEXT",
        "premium": "BOOLEAN",
        "premium_services": "TEXT",
        "services": "TEXT",
        "regular_services": "TEXT",
        "publish_time": "TEXT",
        "base_price": "INTEGER",
        "regular_services_price": "INTEGER",
        "premium_services_price": "INTEGER",
        "ad_price": "INTEGER",
        "dispatch_mode": "TEXT",
        "prepayment_amount": "INTEGER"


    }
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ----------------------------------------------------------------
    def is_back(self, message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        if not (message and message.text):
            return False

        txt = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if txt.startswith(START_CMD_PREFIXES):
            self.parent.login_handler.show_work_panel(message)
            return True

        # Internal implementation note: legacy behavior is preserved during modernization.
        if txt == BACK_TO_PANEL:
            self.parent.login_handler.show_ads_menu(message)
            return True

        # Internal implementation note: legacy behavior is preserved during modernization.
        if txt == BACK_GENERIC:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.parent.login_handler.show_ads_menu(message)
            return True

        return False
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ----------------------------------------------------------------
    def add_back_button(self, markup: types.ReplyKeyboardMarkup,
                        *, to_panel: bool = True) -> types.ReplyKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        back_txt = BACK_TO_PANEL if to_panel else BACK_GENERIC
        markup.add(back_txt)
        return markup
    def cancel_markup(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به پنل")
        return markup

    def show_premium_ad_access_denied(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔐 درخواست عضویت PREMIUM", "🔙 بازگشت")
        self.bot.send_message(
            chat_id,
            "🚫 برای ساخت آگهی PREMIUM باید ابتدا عضو PREMIUM شوید.\n\n"
            "در صورت تمایل می‌توانید درخواست عضویت PREMIUM ثبت کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_premium_ad_request)

    def handle_premium_ad_request(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت":
            return self.parent.login_handler.show_work_panel(message)

        if text == "🔐 درخواست عضویت PREMIUM":
            user = self.parent.db.select_dict(
                "staff", "telegram_id = ?", (message.from_user.id,))
            if not user:
                return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")
            user = user[0]
            ucode = user["U_code"]
            telegram_id = user["telegram_id"]

            # Step 1: Create premium_staff if needed
            self.parent.db.create_table("premium_staff", {
                "U_code": "TEXT UNIQUE",
                "telegram_id": "INTEGER",
                "status": "TEXT"
            })

            # Step 2: Insert or update PREMIUM entry
           # Step 2: Check if already pending
            existing = self.parent.db.select_dict(
                "premium_staff", "U_code = ? AND telegram_id = ?", (ucode, telegram_id))
            if existing and existing[0].get("status", "").lower() == "pending":
                self.bot.send_message(chat_id, "⏳ درخواست شما برای عضویت PREMIUM در حال بررسی است.\n"
                                               "پس از تایید می‌توانید آگهی PREMIUM ایجاد کنید.")
                return self.parent.login_handler.show_work_panel(message)

            # Step 3: Insert or update PREMIUM entry
            self.parent.db.upsert("premium_staff", {
                "U_code": ucode,
                "telegram_id": telegram_id,
                "status": "pending"
            }, key="U_code")

            # Step 3: Add 'is_premium' column to staff if missing
            if not self.parent.db.column_exists("staff", "is_premium"):
                self.parent.db.add_column("staff", "is_premium", "TEXT")

            # Step 4: Update 'is_premium' flag in staff
            self.parent.db.update(
                "staff", {"is_premium": "requested"}, "U_code = ?", (ucode,))

            # Step 5: Notify user
            self.bot.send_message(
                chat_id, "✅ درخواست شما برای عضویت PREMIUM ثبت شد. منتظر بررسی ادمین باشید.")
            return self.parent.login_handler.show_work_panel(message)

    def start_premium_ad_creation(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id, "💎 شروع ساخت آگهی PREMIUM... (در حال توسعه)")

    def is_premium_staff(self, message):
        user = self.parent.db.select_dict(
            "premium_staff", "telegram_id = ? AND status = ?", (message.from_user.id, "approved"))
        return bool(user)
    def _has_posted_today(self, u_code: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()  # yyyy-mm-dd
            rows = self.parent.db.select_dict(
                "ads",
                "U_code = ? AND date(created_at) = ? AND status IN ('pending','approved')",
                (u_code, today)
            )
            logger.debug("Daily-ad check for %s ➜ %d row(s) found", u_code, len(rows))
            return bool(rows)
        except Exception as exc:
            logger.exception("Error while checking daily-ad limit: %s", exc)
            return True  # Internal implementation note: legacy behavior is preserved during modernization.

    def start_featured_ad(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        staff = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (user_id,))
        
        if not staff or not staff[0].get("service_price") or str(staff[0]["service_price"]).strip() in ["", "0"]:
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("🔙 بازگشت به پنل")
            self.bot.send_message(
                chat_id,
                "⚠️ <b>قیمت پایه سرویس شما وارد نشده است!</b>\n\n"
                "برای ساخت آگهی، ابتدا باید:\n"
                "1️⃣ «قیمت پایه» سرویس خود را مشخص کنید\n"
                "2️⃣ سپس خدماتی که ارائه می‌دهید را ثبت نمایید ✅\n\n"
                "🔄 پس از آن می‌توانید به بخش «ساخت آگهی» بازگردید و ادامه دهید.\n\n"
                "⛔️ بدون این اطلاعات، امکان ثبت آگهی وجود ندارد.",
                reply_markup=markup,
                parse_mode="HTML"
            )

            self.bot.send_message(
                chat_id,
                MESSAGES["pleace_enter_base_price"].format(min_price = min(BASE_PRICE_FILTER), max_price=max(BASE_PRICE_FILTER)),
                reply_markup=markup,
                parse_mode= "Markdown"
            )
            self.bot.register_next_step_handler(
                message, self.parent.services_handler.get_service_price)
            return
        try:
            u_code = staff[0]["U_code"]
            if self._has_posted_today(u_code):
                self.bot.send_message(
                    chat_id,
                    "🚫 شما امروز یک آگهی ثبت کرده‌اید و تا فردا نمی‌توانید آگهی دیگری بسازید."
                )
                return self.parent.login_handler.show_ads_menu(message)
        except Exception as exc:
            logger.exception("Daily-ad guard failed: %s", exc)
            self.bot.send_message(
                chat_id,
                "❌ خطایی رخ داد. لطفاً بعداً دوباره تلاش کنید."
            )
            return self.parent.login_handler.show_ads_menu(message)


        self.parent.db.ensure_table_and_columns(
            "ads", columns=self.ADS_TABLE_SCHEMA)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data.setdefault(chat_id, {})["ad_creation"] = {
            "workflow": [
                "enter_start_time",
                "enter_end_time",
                "preview_and_confirm"
            ],
            "step_index": 0
        }
        # self.execute_next_step(message, section="ad_creation")

        self.execute_next_step(message, section="ad_creation")

    def time_to_minutes(self, time_str: str) -> int:
        """
        Converts ``HH:MM`` (with Latin or Persian digits) to the number of
        minutes since midnight.

        Raises
        ------
        ValueError
            If the input is empty, malformed or out of range.
        """
        if not time_str:
            raise ValueError("Invalid time format")

        normalized = (
            time_str.replace("۰", "0").replace("۱", "1").replace("۲", "2")
            .replace("۳", "3").replace("۴", "4").replace("۵", "5")
            .replace("۶", "6").replace("۷", "7").replace("۸", "8")
            .replace("۹", "9")
        )
        try:
            h, m = map(int, normalized.split(":"))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
        except Exception:
            raise ValueError("Invalid time format")

        return h * 60 + m

    def generate_time_slots(self, start_time: str, end_time: str, service_count: int):
        """Legacy-compatible behavior preserved for this callable."""
        from datetime import datetime, timedelta

        def align_15(dt):
            minute = (dt.minute + 14) // 15 * 15
            return dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minute)

        try:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
        except Exception:
            return []

        if service_count <= 0 or end_dt <= start_dt:
            return []

        total_min = int((end_dt - start_dt).total_seconds() // 60)
        interval = max(total_min // service_count, 15)

        slots, current = [], align_15(start_dt)
        while current < end_dt and len(slots) < service_count:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=interval)
            # keep 15-minute alignment
            if current.minute % 15:
                current += timedelta(minutes=15 - current.minute % 15)

        return slots


    def is_valid_time_format(self, time_str):
        return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str)) or \
            bool(re.match(r'^([۰-۲]?[۰-۹]|۲[۰-۳]):[۰-۵][۰-۹]$', time_str))

    def select_location_type(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("ad_creation", "select_location_type")
        prompt = step["prompt"]
        buttons = step["buttons"]
        back_btn = step["back_button"]

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,  row_width=2)
        for b in buttons:
            markup.add(b)
        markup.add(back_btn)

        self.bot.send_message(chat_id, prompt, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_location_type_choice)

    def handle_location_type_choice(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        step = self.get_step_by_name("ad_creation", "select_location_type")
        buttons = step["buttons"]
        back_btn = step["back_button"]
        if self.is_back(message):
            return

        if text == back_btn:
            return self.parent.login_handler.show_ads_menu(message)

        elif text not in buttons:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.select_location_type(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {})["location_type"] = [text]
        self.execute_next_step(message, section="ad_creation")

    def get_max_services_per_hour(self, chat_id: int) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        ad_data = self.data.get(chat_id, {}).get("ad_creation", {})

        # Regions are a list when dispatch is selected, otherwise a single str
        selected_zones = ad_data.get("region", [])
        if not isinstance(selected_zones, list):
            selected_zones = [selected_zones] if selected_zones else []

        location_type = ad_data.get("location_type", [])
        onsite = any("در محل" in t for t in location_type)
        delivery_zones = selected_zones if any("اعزام" in t for t in location_type) else []

        max_services = max(len(delivery_zones), 2 if onsite else 0)
        return max_services or 1


    def generate_hour_buttons(self, min_hour=None):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)

        # Internal implementation note: legacy behavior is preserved during modernization.
        now_tehran = jdatetime.datetime.now().togregorian()
        current_hour = now_tehran.hour

        # Internal implementation note: legacy behavior is preserved during modernization.
        start_hour = max(min_hour or 0, current_hour)
        buttons = []
        for hour in range(start_hour, 24):
            for minute in (0, 30):
                buttons.append(f"{str(hour).zfill(2)}:{str(minute).zfill(2)}")

        for i in range(0, len(buttons), 4):
            markup.add(*buttons[i:i+4])

        markup.add("🔙 بازگشت به پنل")
        return markup
    
    def generate_start_time_buttons(self, chat_id):
        markup = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
        now = datetime.now()
        START_TIME_RIMING = 30
        first_slot = ((now.hour*60 + now.minute + START_TIME_RIMING + BETWIN_TIME - 1) // BETWIN_TIME) * BETWIN_TIME
        gap = self._min_interval_minutes(chat_id)

        buttons = [self._minutes_to_time(t)
                   for t in range(first_slot, 24*60, BETWIN_TIME)
                   if t + gap < 24*60]     # Internal implementation note: legacy behavior is preserved during modernization.

        if not buttons:
            return None
        for i in range(0, len(buttons), 4):
            markup.add(*buttons[i:i+4])
        markup.add("🔙 بازگشت به پنل")
        return markup


#=------------------------------------+=+------------------------------------------

    def enter_start_time(self, message):
        chat_id = message.chat.id
        markup = self.generate_start_time_buttons(chat_id)
        if markup is None:
            self.bot.send_message(chat_id, "⛔️ امروز بازهٔ خالی نداریم؛ روز دیگری را امتحان کنید.")
            return self.parent.login_handler.show_ads_menu(message)

        self.bot.send_message(chat_id, "🕓 ساعت شروع را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.save_start_time)





    # Internal implementation note: legacy behavior is preserved during modernization.
    def save_start_time(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()

        if self.is_back(message):
            return

        if text == "🔙 بازگشت به پنل":
            return self.parent.login_handler.show_ads_menu(message)

        if not self.is_valid_time_format(text):
            self.bot.send_message(
                chat_id,
                "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید."
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.enter_start_time(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {}
        )["start_time"] = text

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.execute_next_step(message, section="ad_creation")


    def enter_end_time(self, message):
        chat_id = message.chat.id
        start_str = self.data.get(chat_id, {}).get("ad_creation", {}).get("start_time")
        if self.is_back(message):
            return

        if not start_str:
            return self.enter_start_time(message)

        start_min = self.time_to_minutes(start_str)
        gap = self._min_interval_minutes(chat_id)

        markup  = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
        buttons = [self._minutes_to_time(t) for t in range(start_min + gap, 24*60, gap)]


        if not buttons:
            self.bot.send_message(chat_id, "⛔️ این ساعت شروع End معتبر ندارد.")
            return self.enter_start_time(message)

        for i in range(0, len(buttons), 4):
            markup.add(*buttons[i:i+4])
        markup.add("🔙 بازگشت به پنل")

        self.bot.send_message(chat_id, "🕔 ساعت پایان را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.save_end_time)





# Internal implementation note: legacy behavior is preserved during modernization.
    def save_end_time(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = (message.text or "").strip()
        if self.is_back(message):
            return
        if text == "🔙 بازگشت به پنل":
            return self.parent.login_handler.show_ads_menu(message)

        if not self.is_valid_time_format(text):
            self.bot.send_message(
                chat_id,
                "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید."
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.enter_end_time(message)

        start_hour = self.data.get(chat_id, {}).get("ad_creation", {}).get("start_time")
        if not start_hour:
            return self.bot.send_message(chat_id, "❌ ابتدا ساعت شروع را انتخاب کنید.")

        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        start_h, start_m = map(int, start_hour.split(':'))
        end_h,   end_m   = map(int,   text.split(':'))

        if (end_h, end_m) <= (start_h, start_m):
            self.bot.send_message(
                chat_id,
                "❌ ساعت پایان باید حداقل یک دقیقه بعد از ساعت شروع باشد."
            )
            return self.enter_end_time(message)


        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {}
        )["end_time"] = text
        self.ask_service_count(message,True)
        # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
        # self.execute_next_step(message, section="ad_creation")




    # Internal implementation note: legacy behavior is preserved during modernization.
    # Publish-time picker
    # Internal implementation note: legacy behavior is preserved during modernization.
    def generate_publish_time_buttons(self, start_time_str):
        """
        Returns (markup, has_options)
        """
        now = datetime.now()

        # Round *up* to the next 30-minute boundary
        total_now_min = now.hour * 60 + now.minute
        rounded_min = ceil(total_now_min / 30) * 30
        rounded_hour, rounded_minute = divmod(rounded_min, 60)
        current = now.replace(
            hour=rounded_hour % 24,
            minute=rounded_minute,
            second=0,
            microsecond=0
        )
        if rounded_hour >= 24:
            current += timedelta(days=1)  # crossed midnight

        # Parse the selected *start_time*
        try:
            start_h, start_m = map(int, start_time_str.split(":"))
            start_time = current.replace(
                hour=start_h, minute=start_m, second=0, microsecond=0
            )
        except Exception:
            m = types.ReplyKeyboardMarkup(resize_keyboard=True)
            return m.add("❌ خطا در زمان شروع"), False

        latest_publish_time = start_time - timedelta(hours=1)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        markup.add("اکنون")
        buttons = []

        while current <= latest_publish_time:
            buttons.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)

        if buttons:
            for i in range(0, len(buttons), 4):
                markup.add(*buttons[i:i + 4])
            has_options = True
        else:
            markup.add("❌ هیچ گزینه‌ای موجود نیست")
            has_options = False

        markup.add("🔙 بازگشت به پنل")
        return markup, has_options


    def enter_publish_time(self, message):
        chat_id = message.chat.id
        start_time = self.data.get(chat_id, {}).get(
            "ad_creation", {}).get("start_time")
        if self.is_back(message):
            return
        if not start_time:
            return self.bot.send_message(chat_id, "❌ لطفاً ابتدا ساعت شروع را مشخص کنید.")

        markup, has_options = self.generate_publish_time_buttons(start_time)

        if not has_options:
            self.bot.send_message(
                chat_id,
                "❌ هیچ گزینه‌ای برای زمان انتشار در دسترس نیست.\n🔁 لطفاً ساعت شروع را تغییر دهید.",
                reply_markup=markup
            )
            return self.enter_start_time(message)

        self.bot.send_message(
            chat_id,
            "🕔 لطفاً ساعت انتشار آگهی را انتخاب کنید:",
            reply_markup=markup
        )

        self.bot.register_next_step_handler(message, self.save_publish_time)

    def save_publish_time(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "🔙 بازگشت به پنل":
            return self.parent.login_handler.show_ads_menu(message)

        if text == "اکنون":
            publish_time = ""  # Internal implementation note: legacy behavior is preserved during modernization.
        elif self.is_valid_time_format(text):
            publish_time = text
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            return self.enter_publish_time(message)

        # publish_time = text
        self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {})["publish_time"] = publish_time

        self.execute_next_step(message, section="ad_creation")

    def enter_service_count(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id, "🔢 لطفاً تعداد سرویس‌هایی که ارائه می‌دهید را وارد کنید:", reply_markup=self.cancel_markup())
        self.bot.register_next_step_handler(message, self.save_service_count)

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Service count
    # Internal implementation note: legacy behavior is preserved during modernization.
    def save_service_count(self, message):
        chat_id = message.chat.id
        text = (message.text or "").strip()
        if self.is_back(message):
            return
        if text == "🔙 بازگشت به پنل":
            return self.parent.login_handler.show_ads_menu(message)

        if not text.isdigit():
            self.bot.send_message(chat_id, "❌ لطفاً فقط عدد بنویسید.")
            return self.bot.register_next_step_handler(message, self.save_service_count)

        count   = int(text)
        max_srv = self.data[chat_id]["ad_creation"].pop("max_srv_tmp", 0)

        if not (1 <= count <= max_srv):
            self.bot.send_message(chat_id, f"❌ عدد باید بین 1 و {max_srv} باشد.")
            return self.bot.register_next_step_handler(message, self.save_service_count)

        self.data[chat_id]["ad_creation"]["service_count"] = count
        self.execute_next_step(message, section="ad_creation")



    def select_services(self, message):
        chat_id = message.chat.id
        user_data = self.data.setdefault(
            chat_id, {}).setdefault("ad_creation", {})
        selected = user_data.get("selected_services", [])

        step = self.get_step_by_name("ad_creation", "select_services")
        prompt = step.get("prompt", "انتخاب خدمات:")
        buttons = step.get("buttons", [])
        confirm_btn = step.get("confirm_button", "✔️ تایید")
        back_btn = step.get("back_button", "🔙 بازگشت")

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=len(buttons))
        markup.add(*[f"✅ {b}" if b in selected else b for b in buttons])
        markup.add(confirm_btn, back_btn)
        self.bot.send_message(chat_id, prompt, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_service_toggle)

    def handle_service_toggle(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None.replace("✅", "").strip()
        if self.is_back(message):
            return
        step = self.get_step_by_name("ad_creation", "select_services")
        valid_buttons = step.get("buttons", [])
        confirm_btn = step.get("confirm_button", "✔️ تایید")
        back_btn = step.get("back_button", "🔙 بازگشت")

        selected = self.data[chat_id]["ad_creation"].setdefault(
            "selected_services", [])

        if text == confirm_btn:
            return self.execute_next_step(message, section="ad_creation")

        elif text == back_btn:
            # you can go to a specific step later
            return self.execute_next_step(message, section="ad_creation")

        elif text not in valid_buttons:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.select_services(message)

        if text in selected:
            selected.remove(text)
        else:
            selected.append(text)

        return self.select_services(message)

    def ask_premium_services(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        user = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (user_id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ اطلاعات کاربری یافت نشد.")

        user = user[0]
        U_code = user["U_code"]

        # Get PREMIUM services
        premium_row = self.parent.db.select_dict(
            "premium_staff", "U_code = ? AND status = 'approved' ", (U_code,))
        # print(f"{user} | {U_code} | {premium_row}")
        if not premium_row:
            # Skip
            return self.execute_next_step(message, section="ad_creation")
        premium_service = self.parent.db.select_dict(
            "services", "U_code = ? ", (U_code,))
        if not premium_service:
            return self.execute_next_step(message, section="ad_creation")
        premium_service = premium_service[0]
        premium_services = []
        total_price = 0
        config = services_config

        for key, service in config.items():
            if service.get("category") != "premium":
                continue  # skip non-PREMIUM
            if key in ["confirm"]:
                continue  # skip system

            # Internal implementation note: legacy behavior is preserved during modernization.
            if premium_service.get(key):
                raw_price = premium_service.get(f"{key}_price")
                try:
                    price = int(raw_price) if raw_price else 0
                except:
                    price = 0
                title = service.get("title", key)
                premium_services.append(
                    f"▫️ {title} - {price:,} تومان" if price else f"▫️ {title}")
                total_price += price

            # Internal implementation note: legacy behavior is preserved during modernization.
            if "drinks" in service:
                drinks = service["drinks"]
                if drinks.get("enabled") and premium_service.get("drinks"):
                    raw_price = premium_service.get("drinks_price")
                    try:
                        price = int(raw_price) if raw_price else 0
                    except:
                        price = 0
                    title = "🍹 نوشیدنی"
                    premium_services.append(
                        f"▫️ {title} - {price:,} تومان" if price else f"▫️ {title}")
                    total_price += price

            # Internal implementation note: legacy behavior is preserved during modernization.
            if "sub_roles" in service:
                for sub_key, sub_conf in service["sub_roles"].items():
                    db_key = f"{key}_{sub_key}"  # e.g. special_service_option_a
                    if premium_service.get(db_key):
                        raw_price = premium_service.get(f"{db_key}_price")
                        try:
                            price = int(raw_price) if raw_price else 0
                        except:
                            price = 0
                        title = sub_conf.get("title", sub_key)
                        premium_services.append(
                            f"▫️ {title} - {price:,} تومان" if price else f"▫️ {title}")
                        total_price += price

        if not premium_services:
            # Skip
            return self.execute_next_step(message, section="ad_creation")

        self.data.setdefault(chat_id, {}).setdefault("ad_creation", {})[
            "premium_services_to_add"] = premium_service
        # self.data[chat_id]["ad_creation"]["premium_services"] = premium_service

        # Show to user
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ بله، اضافه کن", "❌ خیر، نمی‌خواهم")
        self.bot.send_message(
            chat_id,
            "💎 خدمات PREMIUM شما:\n" + "\n".join(premium_services) + "\n\n"
            "آیا مایلید این خدمات به آگهی شما اضافه شود؟",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_premium_service_choice)

    def handle_premium_service_choice(self, message):
        chat_id = message.chat.id
        choice = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if choice == "✅ بله، اضافه کن":
            self.data[chat_id]["ad_creation"]["include_premium_services"] = True

        else:
            self.data[chat_id]["ad_creation"]["include_premium_services"] = False

        self.execute_next_step(message, section="ad_creation")

    PRIVATE_CHANNEL_ID = STORAGE_CHANNEL

    def enter_ad_photo(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id,
            "📸 لطفاً یک عکس برای آگهی ارسال کنید.\nفقط *عکس* را ارسال کنید و از ارسال فایل یا ویدیو خودداری نمایید.",
            reply_markup=self.cancel_markup(),
            parse_mode="Markdown"
        )
        self.bot.register_next_step_handler(message, self.save_ad_photo)

    def ask_regular_services(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        user = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (user_id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ اطلاعات کاربر یافت نشد.")
        user = user[0]

        services_row = self.parent.db.select_dict(
            "services", "U_code = ?", (user["U_code"],))
        if not services_row:
            return self.execute_next_step(message, section="ad_creation")

        services = services_row[0]

        regulars = []

        for key, config in regular_services_config.items():
            if key in ["confirm", "view"]:
                continue

            # Internal implementation note: legacy behavior is preserved during modernization.
            if services.get(key):
                price = services.get(f"{key}_price", 0)
                try:
                    price = int(price)
                except:
                    price = 0
                title = config.get("title", key)
                regulars.append(
                    f"▫️ {title} - {price:,} تومان" if price else f"▫️ {title}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            if "subtypes" in config:
                for sub_key, sub_config in config["subtypes"].items():
                    if services.get(sub_key):
                        price = services.get(f"{sub_key}_price", 0)
                        try:
                            price = int(price)
                        except:
                            price = 0
                        title = sub_config.get("title", sub_key)
                        regulars.append(
                            f"▫️ {title} - {price:,} تومان" if price else f"▫️ {title}")

                if not regulars:
                    return self.execute_next_step(message, section="ad_creation")

                self.data.setdefault(chat_id, {}).setdefault("ad_creation", {})[
                    "regular_services_to_add"] = services
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("✅ بله، اضافه کن", "❌ خیر، نمی‌خواهم")
                self.bot.send_message(
                    chat_id,
                    "♨️ خدمات معمولی شما:\n" + "\n".join(regulars) + "\n\n"
                    "آیا مایلید این خدمات هم به آگهی شما اضافه شود؟",
                    reply_markup=markup
                )
                self.bot.register_next_step_handler(
                    message, self.handle_regular_service_choice)

    def handle_regular_service_choice(self, message):
        chat_id = message.chat.id
        choice = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        self.data.setdefault(chat_id, {}).setdefault("ad_creation", {})
        self.data[chat_id]["ad_creation"]["include_regular_services"] = (
            choice == "✅ بله، اضافه کن")
        self.execute_next_step(message, section="ad_creation")

    PRIVATE_CHANNEL_ID = STORAGE_CHANNEL

    def save_ad_photo(self, message):
        chat_id = message.chat.id
        PRIVATE_CHANNEL_ID = STORAGE_CHANNEL
        if message.text == "🔙 بازگشت به پنل":
            return self.parent.login_handler.show_ads_menu(message)

        if not message.photo:
            self.bot.send_message(
                chat_id, "❌ فقط *عکس* ارسال کنید. لطفاً دوباره امتحان کنید.", parse_mode="Markdown")
            return self.enter_ad_photo(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        sent_msg = self.bot.send_photo(
            PRIVATE_CHANNEL_ID,
            message.photo[-1].file_id
        )
        new_file_id = sent_msg.photo[-1].file_id

        self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {})["ad_photo"] = new_file_id
        self.execute_next_step(message, section="ad_creation")

    def select_payment_method(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("ad_creation", "select_payment_method")
        prompt = step["prompt"]
        buttons = step["buttons"]
        confirm_btn = step["confirm_button"]
        back_btn = step["back_button"]

        selected = self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {}).get("payment_method", [])

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*[f"✅ {b}" if b in selected else b for b in buttons])
        markup.add(confirm_btn, back_btn)

        self.bot.send_message(chat_id, prompt, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_payment_toggle)

    def handle_payment_toggle(self, message):
        chat_id = message.chat.id
        text = (message.text or "").replace("✅", "").strip()
        if self.is_back(message):
            return
        step        = self.get_step_by_name("ad_creation", "select_payment_method")
        buttons     = step["buttons"]
        confirm_btn = step["confirm_button"]
        back_btn    = step["back_button"]

        selected = self.data.setdefault(chat_id, {}) \
                            .setdefault("ad_creation", {}) \
                            .setdefault("payment_method", [])

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == confirm_btn:
            if not selected:                                            # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(chat_id,
                                      "❌ لطفاً حداقل یک روش پرداخت انتخاب کنید.")
                return self.select_payment_method(message)

            if "پیش‌پرداخت + مابقی در محل" in selected:
                return self.enter_prepayment_amount(message)

            return self.execute_next_step(message, section="ad_creation")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == back_btn:
            return self.execute_next_step(message, section="ad_creation")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text not in buttons:
            self.bot.send_message(chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
            return self.select_payment_method(message)

        # Internal implementation note: legacy behavior is preserved during modernization.
        selected.remove(text) if text in selected else selected.append(text)
        return self.select_payment_method(message)


    def enter_prepayment_amount(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id,
            "💵 <b>مبلغ پیش‌پرداخت را وارد کنید:</b>\n\n"
            "📌 شما می‌توانید مبلغ را به یکی از این روش‌ها بنویسید:\n"
            "• عدد کامل: <code>350000</code>\n"
            "• به‌صورت هزار تایی: <code>350</code>\n"
            "• به‌صورت اعشاری (میلیون): <code>0.35</code>\n\n"
            "🔢 مقدار وارد شده باید بین <b>۵۰٬۰۰۰</b> تا <b>۱٬۰۰۰٬۰۰۰</b> تومان باشد\n"
            "و <b>مضرب ۱٬۰۰۰</b> باشد.",
            reply_markup=self.cancel_markup(),
            parse_mode="HTML"
        )
        self.bot.register_next_step_handler(message, self.save_prepayment_amount)



    def save_prepayment_amount(self, message):
        chat_id = message.chat.id
        if self.is_back(message):
            return

        raw = (message.text or "").strip()

        try:
            amount = self._parse_amount(raw, min_t=50_000, max_t=1_000_000)
        except ValueError:
            self.bot.send_message(
                chat_id,
                "❌ مبلغ نامعتبر است.\n"
                "یک عدد بین ۵۰٬۰۰۰ تا ۱٬۰۰۰٬۰۰۰ (مضرب ۱٬۰۰۰) وارد کنید.",
                reply_markup=self.cancel_markup())
            return self.bot.register_next_step_handler(
                message, self.save_prepayment_amount)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {})["prepayment_amount"] = amount

        self.execute_next_step(message, section="ad_creation")


    def select_region(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("ad_creation", "select_region")
        prompt = step["prompt"]
        buttons = step["buttons"]
        confirm_btn = step["confirm_button"]
        back_btn = step["back_button"]

        location_type = self.data.get(chat_id, {}).get(
            "ad_creation", {}).get("location_type", [])
        is_dispatch = location_type and "اعزام" in location_type[0]
        selected = self.data.setdefault(chat_id, {}).setdefault(
            "ad_creation", {}).get("region", [] if is_dispatch else "")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        if is_dispatch:
            markup.add(*[f"✅ {b}" if b in selected else b for b in buttons])
            markup.add(step["confirm_button"])
        else:
            markup.add(*[f"✅ {b}" if b == selected else b for b in buttons])

        self.bot.send_message(chat_id, prompt, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_region_toggle)

    def handle_region_toggle(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None.replace("✅", "").strip()
        if self.is_back(message):
            return
        step = self.get_step_by_name("ad_creation", "select_region")
        buttons = step["buttons"]
        confirm_btn = step["confirm_button"]
        back_btn = step["back_button"]

        # Internal implementation note: legacy behavior is preserved during modernization.
        location_type = self.data.get(chat_id, {}).get(
            "ad_creation", {}).get("location_type", [])
        is_dispatch = location_type and "اعزام" in location_type[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
        if is_dispatch:
            selected = self.data[chat_id]["ad_creation"].setdefault(
                "region", [])
        else:
            selected = None  # Not needed for single region

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == back_btn:
            return self.execute_next_step(message, section="ad_creation")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if is_dispatch and text == confirm_btn:
            if not selected:
                return self.bot.send_message(chat_id, "❌ لطفاً حداقل یک منطقه را انتخاب کنید.")
            return self.execute_next_step(message, section="ad_creation")

        # Internal implementation note: legacy behavior is preserved during modernization.
        if text in buttons:
            if is_dispatch:
                # Toggle selected region
                if text in selected:
                    selected.remove(text)
                else:
                    selected.append(text)
                return self.select_region(message)  # Stay in region selection
            else:
                # Just one region, save and move on
                self.data[chat_id]["ad_creation"]["region"] = text
                return self.execute_next_step(message, section="ad_creation")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id, "❌ لطفاً فقط از گزینه‌های موجود استفاده کنید.")
        return self.select_region(message)

    def preview_and_confirm(self, message):
        chat_id = message.chat.id
        ad_creation = self.data.setdefault(
            chat_id, {}).setdefault("ad_creation", {})
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if ad_creation.get("is_repeat"):
            repeat_data = self.data[chat_id]["repeat_ad_data"]

            # Internal implementation note: legacy behavior is preserved during modernization.
            new_times = {
                k: ad_creation[k]
                for k in ("start_time", "end_time", "publish_time")
                if k in ad_creation
            }
            # Internal implementation note: legacy behavior is preserved during modernization.
            is_repeat_flag = ad_creation.get("is_repeat")

            # Internal implementation note: legacy behavior is preserved during modernization.
            ad_creation.clear()
            ad_creation.update(repeat_data)
            # Internal implementation note: legacy behavior is preserved during modernization.
            ad_creation.update(new_times)
            ad_creation["is_repeat"] = is_repeat_flag

        ad_data = ad_creation

        # Internal implementation note: legacy behavior is preserved during modernization.
        user_rows = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,)
        )
        if not user_rows:
            return self.bot.send_message(chat_id, "❌ اطلاعات کاربر یافت نشد.")
        user = user_rows[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
        services_row = self.parent.db.select_dict(
            "services", "U_code = ?", (user["U_code"],)
        )
        special_services = []
        special_price_total = 0
        if services_row:
            service_data = services_row[0]
            db_keys = ["back", "group_option_b", "group_option_a"]
            for fa_name, db_key in self.parent.services_handler.service_key_map.items():
                if db_key not in db_keys:
                    continue
                if service_data.get(db_key):
                    special_services.append(fa_name)
                    price_key = f"{db_key}_price"
                    if price_key in service_data and str(service_data[price_key]).isdigit():
                        special_price_total += int(service_data[price_key])

        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_services_to_add = ad_data.get("premium_services_to_add", {})
        include_premium = ad_data.get("include_premium_services", False)
        premium_service_lines = []
        premium_price_total = 0
        if include_premium and isinstance(premium_services_to_add, dict):
            for key, config in services_config.items():
                if premium_services_to_add.get(key):
                    raw_price = premium_services_to_add.get(f"{key}_price")
                    try:
                        price = int(raw_price) if raw_price is not None else 0
                    except (ValueError, TypeError):
                        price = 0
                    if price > 0:
                        premium_service_lines.append(
                            f"▫️ {config['title']} ({price:,} تومان)"
                        )
                        premium_price_total += price

        # Internal implementation note: legacy behavior is preserved during modernization.
        name = user.get("name", "نامشخص")
        U_code = user.get("U_code", "نامشخص")
        age = user.get("age", "نامشخص")
        province = user.get("province", "نامشخص")
        city = user.get("city", "نامشخص")
        breast_size = user.get("breast_size", "")
        appearance = user.get("appearance", "")
        try:
            base_price_int = int(user.get("service_price", 0))
        except:
            base_price_int = 0

        # Internal implementation note: legacy behavior is preserved during modernization.
        ad_price_total = base_price_int + special_price_total + premium_price_total

        # Internal implementation note: legacy behavior is preserved during modernization.
        region = ad_data.get("region", user.get("region","نامشخص"))
        selected_services = ad_data.get("selected_services", [])

        # Internal implementation note: legacy behavior is preserved during modernization.
        regular_services_to_add = ad_data.get("regular_services_to_add", {})
        include_regular = ad_data.get("include_regular_services", False)
        added_regulars = []
        if include_regular:
            for key, config in regular_services_config.items():
                if key in ["confirm", "view"]:
                    continue
                if regular_services_to_add.get(key):
                    price = int(regular_services_to_add.get(
                        f"{key}_price", 0) or 0)
                    title = config["title"]
                    added_regulars.append(
                        f"{title} ({price:,} تومان)" if price else title
                    )

        # Internal implementation note: legacy behavior is preserved during modernization.
        lines = [
            f"👤 نام: {name}",
            f"🔖 کد کاربری: {U_code}",
            f"🎂 سطح تجربه: {age}",
            f"📍 موقعیت: {province} - {city}",
            f"🗺 منطقه: {region}",
        ]
        if breast_size:
            lines.append(f"🔢 پارامتر عددی: {breast_size}")
        if appearance:
            lines.append(f"👗 ظاهر: {appearance}")

        lines.append(
            f"🛎 خدمات آگهی: {'، '.join(selected_services) or 'ندارد'}"
        )
        lines.append(
            f"💎 ویژگی‌های افزوده: {'، '.join(special_services) or 'ندارد'}"
        )

        if added_regulars:
            lines.append("♨️ خدمات معمولی اضافه‌شده:")
            for s in added_regulars:
                lines.append(f"▫️ {s}")

        if premium_service_lines:
            lines.append("👑 خدمات PREMIUM اضافه‌شده:")
            for vs in premium_service_lines:
                lines.append(vs)

        lines.append(f"💰 قیمت پایه: {base_price_int:,} تومان")
        lines.append(f"🧾 قیمت با خدمات: {ad_price_total:,} تومان")

        # Internal implementation note: legacy behavior is preserved during modernization.
        payment_methods = ad_data.get("payment_method", [])
        if isinstance(payment_methods, str):
            payment_methods = [payment_methods]
        elif not isinstance(payment_methods, list):
            payment_methods = []

        payment_map = {
            "پرداخت کامل قبل از شروع": "💳 پرداخت کامل پیش از شروع",
            "پرداخت در محل": "🏠 پرداخت در محل",
            "پیش‌پرداخت + مابقی در محل": "💵 پیش‌پرداخت + مابقی"
        }

        if payment_methods:
            lines.append("💰 روش‌های پرداخت انتخابی:")
            for p in payment_methods:
                lines.append(payment_map.get(p, f"🔸 {p}"))
            if "پیش‌پرداخت + مابقی در محل" in payment_methods:
                try:
                    pre_amt_int = int(ad_data.get("prepayment_amount", 0))
                except:
                    pre_amt_int = 0
                lines.append(f"💵 مبلغ پیش‌پرداخت: {pre_amt_int:,} تومان")

        # Internal implementation note: legacy behavior is preserved during modernization.
        preview_text = "\n".join(lines)
        photo_id = ad_data.get("ad_photo") or user.get("profile_photo")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ تایید نهایی", "❌ لغو آگهی")

        if photo_id:
            self.bot.send_photo(
                chat_id,
                photo_id,
                caption=preview_text,
                has_spoiler=True,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            self.bot.send_message(
                chat_id,
                f"📄 پیش‌نمایش آگهی شما:\n\n{preview_text}",
                reply_markup=markup
            )

        self.bot.register_next_step_handler(
            message, self.handle_preview_decision
        )

    def handle_preview_decision(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if self.is_back(message):
            return
        if text == "✅ تایید نهایی":
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.data.get(chat_id, {}).get("ad_creation", {}).get("is_repeat"):
                return self.finalize_repeat_ad(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            class MockCall:
                def __init__(self, message):
                    self.message = message
                    self.from_user = message.from_user
            self.submit_featured_ad_for_approval(MockCall(message))

        elif text == "❌ لغو آگهی":
            self.bot.send_message(chat_id, "❌ آگهی لغو شد.",
                                  reply_markup=self.cancel_markup())
            self.parent.login_handler.show_ads_menu(message)

        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً فقط یکی از گزینه‌های موجود را انتخاب کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_preview_decision)
            
    def submit_featured_ad_for_approval(self, call):
        chat_id = call.message.chat.id
        ad_data = self.data.get(chat_id, {}).get("ad_creation", {})

        user = self.parent.db.select_dict("staff", "telegram_id = ?", (call.from_user.id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ اطلاعات کاربر یافت نشد.")
        user = user[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
        services_row = self.parent.db.select_dict("services", "U_code = ?", (user["U_code"],))
        regular_services_dict = {}
        premium_services_dict = {}
        regular_services_list = []
        regular_services_price = 0
        premium_services_price = 0

        if services_row:
            services_data = services_row[0]

            # Internal implementation note: legacy behavior is preserved during modernization.
            for key, cfg in regular_services_config.items():
                if key in ["confirm", "view"]:
                    continue
                if services_data.get(key):
                    price = int(services_data.get(f"{key}_price", 0) or 0)
                    regular_services_dict[key] = {"title": cfg["title"], "price": price}
                    regular_services_price += price
                    regular_services_list.append(cfg["title"])

                # Internal implementation note: legacy behavior is preserved during modernization.
                if "subtypes" in cfg:
                    for sub_key, sub_cfg in cfg["subtypes"].items():
                        if services_data.get(sub_key):
                            price = int(services_data.get(f"{sub_key}_price", 0) or 0)
                            regular_services_dict[sub_key] = {"title": sub_cfg["title"], "price": price}
                            regular_services_price += price
                            regular_services_list.append(sub_cfg["title"])

            # Internal implementation note: legacy behavior is preserved during modernization.
            for key, cfg in services_config.items():
                if cfg.get("category") != "premium":
                    continue
                if services_data.get(key):
                    price = int(services_data.get(f"{key}_price", 0) or 0)
                    premium_services_dict[key] = {"title": cfg["title"], "price": price}
                    premium_services_price += price

                # Internal implementation note: legacy behavior is preserved during modernization.
                if "drinks" in cfg and services_data.get("drinks"):
                    price = int(services_data.get("drinks_price", 0) or 0)
                    premium_services_dict["drinks"] = {"title": "🍹 نوشیدنی", "price": price}
                    premium_services_price += price

                if "sub_roles" in cfg:
                    for sub_key, sub_cfg in cfg["sub_roles"].items():
                        db_key = f"{key}_{sub_key}"
                        if services_data.get(db_key):
                            price = int(services_data.get(f"{db_key}_price", 0) or 0)
                            premium_services_dict[db_key] = {"title": sub_cfg["title"], "price": price}
                            premium_services_price += price

        base_price_int = int(user.get("service_price", 0) or 0)
        ad_price_total = base_price_int + regular_services_price + premium_services_price

        payment_methods = ad_data.get("payment_method", ["در محل"])
        if isinstance(payment_methods, str):
            payment_methods = [payment_methods]

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.parent.db.insert("ads", {
            "U_code": user["U_code"],
            "start_time": ad_data.get("start_time"),
            "end_time": ad_data.get("end_time"),
            "service_count": ad_data.get("service_count", 0),
            "status": "pending",
            "ad_photo": ad_data.get("ad_photo", ""),
            "payment_method": ", ".join(payment_methods),
            "region": ad_data.get("region", user.get("region", "نامشخص")),
            "premium": bool(premium_services_dict),
            "premium_services": json.dumps(premium_services_dict, ensure_ascii=False),
            "services": json.dumps(regular_services_dict, ensure_ascii=False),
            "regular_services": ", ".join(regular_services_list),
            "publish_time": ad_data.get("publish_time", "اکنون"),
            "base_price": base_price_int,
            "regular_services_price": regular_services_price,
            "premium_services_price": premium_services_price,
            "ad_price": ad_price_total,
            "prepayment_amount": ad_data.get("prepayment_amount", 0),
            "dispatch_mode": user.get("dispatch_mode"),
        })

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id, "✅ آگهی شما با موفقیت ثبت شد و پس از تأیید ادمین در کانال منتشر می‌شود.")
        self.parent.login_handler.show_work_panel(call.message)
        
    def submit_featured_ad_for_approval2(self, call):
        chat_id = call.message.chat.id
        ad_data = self.data.get(chat_id, {}).get("ad_creation", {})

        user = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (call.from_user.id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ اطلاعات کاربر یافت نشد.")
        user = user[0]

        services_row = self.parent.db.select_dict(
            "services", "U_code = ?", (user["U_code"],))
        special_services = []
        special_price_total = 0

        include_regular = ad_data.get("include_regular_services", False)
        regular_services_dict = {}

        if include_regular and services_row:
            service_data = services_row[0]
            regular_keys = ["back", "group_option_b", "group_option_a"]
            for fa_name, db_key in self.parent.services_handler.service_key_map.items():
                if db_key in regular_keys and service_data.get(db_key):
                    price_key = f"{db_key}_price"
                    try:
                        price = int(service_data.get(price_key, 0))
                    except:
                        price = 0

                    if price > 0:
                        special_services.append(fa_name)
                        special_price_total += price
                        regular_services_dict[db_key] = {
                            "title": fa_name,
                            "price": price
                        }

        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_services_to_add = ad_data.get("premium_services_to_add", {})
        include_premium = ad_data.get("include_premium_services", False)

        ####################
        premium_services_dict = {}
        premium_service_lines = []  # Internal implementation note: legacy behavior is preserved during modernization.
        premium_price_total = 0
        ##################

        if include_premium and isinstance(premium_services_to_add, dict):
            for key, service in services_config.items():
                if service.get("category") != "premium":
                    continue  # only premium

                # Internal implementation note: legacy behavior is preserved during modernization.
                if premium_services_to_add.get(key):
                    raw_price = premium_services_to_add.get(f"{key}_price")
                    try:
                        price = int(raw_price) if raw_price else 0
                    except:
                        price = 0

                    fa_name = service.get("title", key)
                    premium_services_dict[key] = {"title": fa_name}
                    if price:
                        premium_services_dict[key]["price"] = price
                        premium_service_lines.append(
                            f"{fa_name} - {price:,} تومان")
                        premium_price_total += price
                    else:
                        premium_service_lines.append(f"{fa_name}")

                # Internal implementation note: legacy behavior is preserved during modernization.
                if "drinks" in service:
                    if premium_services_to_add.get("drinks"):
                        raw_price = premium_services_to_add.get("drinks_price")
                        try:
                            price = int(raw_price) if raw_price else 0
                        except:
                            price = 0
                        fa_name = "🍹 نوشیدنی"
                        premium_services_dict["drinks"] = {"title": fa_name}
                        if price:
                            premium_services_dict["drinks"]["price"] = price
                            premium_service_lines.append(
                                f"{fa_name} - {price:,} تومان")
                            premium_price_total += price
                        else:
                            premium_service_lines.append(f"{fa_name}")

                # Internal implementation note: legacy behavior is preserved during modernization.
                if "sub_roles" in service:
                    for sub_key, sub_config in service["sub_roles"].items():
                        db_key = f"{key}_{sub_key}"  # e.g., special_service_option_a
                        if premium_services_to_add.get(db_key):
                            raw_price = premium_services_to_add.get(
                                f"{db_key}_price")
                            try:
                                price = int(raw_price) if raw_price else 0
                            except:
                                price = 0
                            fa_name = sub_config.get("title", sub_key)
                            premium_services_dict[db_key] = {"title": fa_name}
                            if price:
                                premium_services_dict[db_key]["price"] = price
                                premium_service_lines.append(
                                    f"{fa_name} - {price:,} تومان")
                                premium_price_total += price
                            else:
                                premium_service_lines.append(f"{fa_name}")

        name = user.get("name", "نامشخص")
        U_code = user.get("U_code", "نامشخص")
        age = user.get("age", "نامشخص")
        province = user.get("province", "نامشخص")
        city = user.get("city", "نامشخص")
        breast_size = user.get("breast_size", "")
        appearance = user.get("appearance", "")
        base_price = user.get("service_price", "0")
        region = ad_data.get("region", user.get("region","نامشخص"))

        try:
            base_price_int = int(base_price)
        except:
            base_price_int = 0

        ad_price_total = base_price_int + special_price_total + premium_price_total

        payment_methods = ad_data.get("payment_method", ["در محل",])
        if isinstance(payment_methods, str):
            payment_methods = [payment_methods]
        elif not isinstance(payment_methods, list):
            payment_methods = []

        payment_map = {
            "پرداخت کامل قبل از شروع": "💳 پرداخت کامل پیش از شروع",
            "پرداخت در محل": "🏠 پرداخت در محل",
            "پیش‌پرداخت + مابقی در محل": "💵 پیش‌پرداخت + مابقی"
        }

        regular_services_price = special_price_total
        premium_services_price = premium_price_total
        ad_price_total = base_price_int + regular_services_price + premium_services_price

        # Internal implementation note: legacy behavior is preserved during modernization.
        lines = [
            f"🔥 آگهی ویژه جدید",
            f"👤 نام: {name}",
            f"🔖 کد کاربری: {U_code}",
            f"🎂 سطح تجربه: {age}",
            f"📍 موقعیت: {province} - {city}",
            f"🗺 منطقه: {region}",
        ]
        if breast_size:
            lines.append(f"🔢 پارامتر عددی: {breast_size}")
        if appearance:
            lines.append(f"👗 ظاهر: {appearance}")
        lines.append(
            f"🛎 خدمات آگهی: {'، '.join(ad_data.get('selected_services', [])) or 'ندارد'}")
        lines.append(f"💎 ویژگی‌های افزوده: {'، '.join(special_services) or 'ندارد'}")
        if premium_service_lines:
            lines.append("👑 خدمات PREMIUM اضافه‌شده:")
            lines.extend([f"▫️ {s}" for s in premium_service_lines])

        lines.append(f"💰 قیمت پایه: {base_price_int:,} تومان")
        lines.append(f"🧾 قیمت با خدمات: {ad_price_total:,} تومان")

        if payment_methods:
            lines.append("💰 روش‌های پرداخت:")
            for p in payment_methods:
                lines.append(payment_map.get(p, f"🔸 {p}"))

            if "پیش‌پرداخت + مابقی در محل" in payment_methods:
                pre_amt = ad_data.get("prepayment_amount", 0)
                lines.append(f"💵 مبلغ پیش‌پرداخت: {int(pre_amt):,} تومان")

        ad_text = "\n".join(lines)
        MAIN_CHANNEL = "@personeltest"
        ad_price_total = base_price_int + special_price_total + premium_price_total
        region_data = ad_data.get("region", "نامشخص")
        if isinstance(region_data, list):
            region = ", ".join(region_data)
        else:
            region = region_data

        start_time = ad_data.get("start_time")
        end_time = ad_data.get("end_time")
        service_count = ad_data.get("service_count", 0)
        selected_services = ad_data.get("selected_services", [])

        time_buttons = types.InlineKeyboardMarkup(row_width=4)
        if start_time and end_time and service_count:
            slots = self.generate_time_slots(
                start_time, end_time, service_count)
            buttons = []
            for t in slots:
                url = f"https://t.me/Moshtari90_bot?start={user['U_code']}_{t.replace(':', '')}"
                buttons.append(types.InlineKeyboardButton(t, url=url))
            for i in range(0, len(buttons), 4):
                time_buttons.add(*buttons[i:i+4])

        self.data[chat_id].pop("ad_creation", None)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.parent.db.insert("ads", {
            "U_code": user["U_code"],
            # "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "start_time": start_time,
            "end_time": end_time,
            "service_count": service_count,
            "status": "pending",
            "ad_photo": ad_data.get("ad_photo",""),
            "payment_method": ", ".join(payment_methods),
            # "user_account": None,
            # "description": None,
            "region": user["region"],
            "premium": include_premium,
            "premium_services": json.dumps(premium_services_dict, ensure_ascii=False),
            "services": json.dumps(regular_services_dict, ensure_ascii=False),
            "regular_services": ", ".join(selected_services) if include_regular else "",
            "publish_time": ad_data.get("publish_time","اکنون"),
            "base_price": base_price_int,
            "regular_services_price": regular_services_price,
            "premium_services_price": premium_services_price,
            "ad_price": ad_price_total,
            "prepayment_amount": ad_data.get("prepayment_amount", 0),
            "dispatch_mode": user["dispatch_mode"],





        })

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id, "✅ آگهی شما با موفقیت ثبت شد و پس از تأیید ادمین در کانال منتشر می‌شود.")
        self.parent.login_handler.show_work_panel(call.message)


#####################################################################################################################
# Internal implementation note: legacy behavior is preserved during modernization.
#####################################################################################################################

    def show_my_ads_menu(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📢 جاری", "⏳ در صف انتظار", "📦 قدیمی")

        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "📂 لطفاً وضعیت آگهی‌ها را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_ad_status_selection)

    def generate_ad_caption(self, user: dict, ad: dict, service_key_map: dict) -> str:

        name = user.get("name", "نامشخص")
        U_code = user.get("U_code", "نامشخص")
        age = user.get("age", "نامشخص")
        province = user.get("province", "")
        city = user.get("city", "")
        breast_size = user.get("breast_size", "")
        appearance = user.get("appearance", "")
        region = ad.get("region",  user.get("region","نا مشخص"))
        base_price = user.get("service_price", "0")

        try:
            base_price_int = int(base_price)
        except:
            base_price_int = 0

        # Internal implementation note: legacy behavior is preserved during modernization.
        regular_services = []
        if ad.get("regular_services"):
            regular_services = [
                s.strip() for s in ad["regular_services"].split(",") if s.strip()]

        # Internal implementation note: legacy behavior is preserved during modernization.
        special_services = []
        total_price = base_price_int

        try:
            services_dict = json.loads(ad.get("services", "{}"))
            for key, value in services_dict.items():
                if value:
                    fa_title = value.get("title", key)
                    price = int(value.get("price", 0))
                    special_services.append(
                        f"{fa_title} - {price:,} تومان" if price else fa_title)
                    total_price += price
        except:
            pass

        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_services = []
        try:
            premium_dict = json.loads(ad.get("premium_services", "{}"))
            for key, value in premium_dict.items():
                if value:
                    fa_title = value.get("title", key)
                    price = int(value.get("price", 0))
                    premium_services.append(
                        f"{fa_title} - {price:,} تومان" if price else fa_title)
                    total_price += price
        except:
            pass

        # Internal implementation note: legacy behavior is preserved during modernization.
        payment_lines = []
        payment_map = {
            "پرداخت کامل قبل از شروع": "💳 پرداخت کامل پیش از شروع",
            "پرداخت در محل": "🏠 پرداخت در محل",
            "پیش‌پرداخت + مابقی در محل": "💵 پیش‌پرداخت + مابقی"
        }
        if ad.get("payment_method"):
            payments = [p.strip() for p in ad["payment_method"].split(",")]
            for p in payments:
                payment_lines.append(payment_map.get(p, f"🔸 {p}"))
            if "پیش‌پرداخت + مابقی در محل" in payments:
                pre_amt = ad.get("prepayment_amount", 0)
                if str(pre_amt).isdigit():
                    payment_lines.append(
                        f"💵 مبلغ پیش‌پرداخت: {int(pre_amt):,} تومان")

        # Internal implementation note: legacy behavior is preserved during modernization.
        lines = [
            f"👤 نام: {name}",
            f"🔖 کد کاربری: {U_code}",
            f"🎂 سطح تجربه: {age}",
            f"📍 موقعیت: {province} - {city}",
            f"🗺 منطقه: {region}",
        ]
        if breast_size:
            lines.append(f"🔢 پارامتر عددی: {breast_size}")
        if appearance:
            lines.append(f"👗 ظاهر: {appearance}")
        lines.append(
            f"🛎 خدمات معمولی: {', '.join(regular_services) or 'ندارد'}")
        lines.append(f"💎 ویژگی‌های افزوده: {', '.join(special_services) or 'ندارد'}")
        if premium_services:
            lines.append("👑 خدمات PREMIUM:")
            lines.extend([f"▫️ {v}" for v in premium_services])
        lines.append(f"💰 قیمت پایه: {base_price_int:,} تومان")
        lines.append(f"🧾 قیمت کل: {total_price:,} تومان")
        if payment_lines:
            lines.append("💳 روش‌های پرداخت:")
            lines.extend(payment_lines)

        return "\n".join(lines)

    def handle_ad_status_selection(self, message):
        text = message.text.strip() if message.text else None
        chat_id = message.chat.id

        if text == "📢 جاری":
            self.data[chat_id] = {"status": "approved"}
        elif text == "⏳ در صف انتظار":
            self.data[chat_id] = {"status": "pending"}
        elif text == "📦 قدیمی":
            self.data[chat_id] = {"status": "expired"}
        elif text == "🔙 بازگشت":
            return self.parent.login_handler.show_ads_menu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های معتبر را انتخاب کنید.")
            return self.show_my_ads_menu(message)

        return self.list_user_ads(message)

    def list_user_ads(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        staff = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (user_id,))
        if not staff:
            self.bot.send_message(chat_id, "❌ شما هنوز ثبت‌نام نکرده‌اید.")
            return self.parent.login_handler.handle_ad_menu_selection(message)

        U_code = staff[0]["U_code"]
        status = self.data[chat_id]["status"]

        all_ads = self.parent.db.select_dict(
            "ads", "U_code = ? AND status = ?", (U_code, status))

        if not all_ads:
            self.bot.send_message(chat_id, "❌ آگهی‌ای با این وضعیت ندارید.")
            return self.show_my_ads_menu(message)

        self.data[chat_id]["current_ads"] = all_ads

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for ad in all_ads:
            ad_id = ad.get("id") or ad.get("rowid") or ad.get("creation_date")
            start = ad.get("start_time", "نامشخص")
            end = ad.get("end_time", "نامشخص")
            label = f"📌 آگهی {ad_id} | شروع: {start} | پایان: {end}"
            markup.add(label)

        markup.add("🔙 بازگشت")

        label = "منتشر شده" if status == "approved" else "در انتظار تایید"
        self.bot.send_message(
            chat_id, f"📂 آگهی‌های شما ({label}):", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.handle_ad_selection)

    def handle_ad_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "🔙 بازگشت":
            return self.show_my_ads_menu(message)

        text = text.replace("📌", "").replace("Ad", "").strip()
        parts = text.split("|")
        if len(parts) < 1:
            self.bot.send_message(chat_id, "❌ فرمت آگهی نامعتبر است.")
            return self.list_user_ads(message)

        ad_id = parts[0].replace("📌", "").replace("آگهی", "").strip()
        ads = self.data.get(chat_id, {}).get("current_ads", [])
        selected_ad = next((a for a in ads if str(a.get("id")) == ad_id), None)

        if not selected_ad:
            self.bot.send_message(chat_id, "❌ آگهی یافت نشد.")
            return self.list_user_ads(message)

        self.data[chat_id]["selected_ad"] = selected_ad
        # self.data[chat_id]["ad_type"] = ad_type
        self.data[chat_id]["previous_step"] = "list_user_ads"

        # Get user info for full caption
        user = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not user:
            self.bot.send_message(chat_id, "❌ اطلاعات کاربر یافت نشد.")
            return self.list_user_ads(message)
        user = user[0]

        # Generate full ad preview caption
        caption = self.generate_ad_caption(
            user, selected_ad, self.service_key_map)

        photo = selected_ad.get("ad_photo")
        if photo:
            self.bot.send_photo(
                chat_id,
                photo,
                caption=caption,
                has_spoiler=True,
                parse_mode="HTML"
            )
        else:
            self.bot.send_message(chat_id, caption)

        # Show action options
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if self.data[chat_id]["status"] == "pending":
            markup.add("🗑 حذف آگهی")
        else:
            markup.add("♻️ تکرار آگهی")
        markup.add("🔙 بازگشت")

        self.bot.send_message(
            chat_id,
            "📌 لطفاً عملیات مورد نظر را برای آگهی انتخاب کنید:",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.handle_selected_ad_action)

    def handle_selected_ad_action(self, message):
        chat_id = message.chat.id
        action = message.text.strip() if message.text else None
        ad = self.data.get(chat_id, {}).get("selected_ad", {})
        self.data[chat_id]["previous_step"] = "list_user_ads"

        if action == "🔙 بازگشت":
            return self.list_user_ads(message)

        if action == "🗑 حذف آگهی":
            ad = self.data[chat_id].get("selected_ad")
            if ad:
                ad_id = ad.get("id") or ad.get("rowid")
                if ad_id:
                    self.parent.db.update(
                        "ads", {"status": "deleted"}, "id = ?", (ad_id,))
                    self.bot.send_message(chat_id, "🗑 آگهی با موفقیت حذف شد.")
                else:
                    self.bot.send_message(chat_id, "❌ شناسه آگهی معتبر نیست.")
            else:
                self.bot.send_message(chat_id, "❌ آگهی یافت نشد.")
            return self.list_user_ads(message)

        elif action == "♻️ تکرار آگهی":
            self.repeat_ad(message, ad)

        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً گزینه‌ای معتبر انتخاب کنید.")
            self.bot.register_next_step_handler(
                message, self.handle_selected_ad_action)

    def repeat_ad(self, message, ad):
        chat_id = message.chat.id

        # Save the original ad so we can reuse all its fields
        self.data.setdefault(chat_id, {})["repeat_ad_data"] = ad.copy()

        # Only use 3 steps: start, end, publish (same as normal flow)
        self.data[chat_id]["ad_creation"] = {
            "workflow": [
                "enter_start_time",
                "enter_end_time",
                "enter_publish_time",
                "preview_and_confirm"  # Internal implementation note: legacy behavior is preserved during modernization.
            ],
            "step_index": 0,
            "is_repeat": True
        }

        # Start the first step (start_time), which uses button UI
        self.execute_next_step(message, section="ad_creation")

    def finalize_repeat_ad(self, message):
        chat_id = message.chat.id
        old_ad = self.data[chat_id].get("repeat_ad_data", {})
        new_data = self.data[chat_id].get("ad_creation", {})

        if not old_ad or not new_data:
            return self.bot.send_message(chat_id, "❌ خطا در تکرار آگهی. لطفاً دوباره امتحان کنید.")

        user = self.parent.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ اطلاعات کاربر یافت نشد.")
        user = user[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
        insert_data = {
            # Internal implementation note: legacy behavior is preserved during modernization.
            "U_code": user["U_code"],
            # "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),  # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            "start_time": new_data.get("start_time"),
            "end_time": new_data.get("end_time"),
            "publish_time": new_data.get("publish_time", ""),
            "status": "pending",
            # Internal implementation note: legacy behavior is preserved during modernization.
            "service_count": old_ad.get("service_count", 0),
            "ad_photo": old_ad.get("ad_photo", ""),
            "payment_method": old_ad.get("payment_method", "در محل"),
            "region": user.get("region", ""),
            "premium": old_ad.get("premium", False),
            "premium_services": old_ad.get("premium_services", "{}"),
            "services": old_ad.get("services", "{}"),
            "regular_services": old_ad.get("regular_services", ""),
            "base_price": old_ad.get("base_price", 0),
            "regular_services_price": old_ad.get("regular_services_price", 0),
            "premium_services_price": old_ad.get("premium_services_price", 0),
            "ad_price": old_ad.get("ad_price", 0),
            "prepayment_amount": old_ad.get("prepayment_amount", 0),
            "dispatch_mode": user.get("dispatch_mode", "")
        }


        # Internal implementation note: legacy behavior is preserved during modernization.
        self.parent.db.insert("ads", insert_data)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.data[chat_id].pop("repeat_ad_data", None)
        self.data[chat_id].pop("ad_creation", None)

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(chat_id, "♻️ آگهی با موفقیت تکرار و ثبت شد.")
        self.list_user_ads(message)
          # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _minutes_to_time(self, minutes: int) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        h = (minutes // 60) % 24
        m = minutes % 60
        return f"{h:02d}:{m:02d}"

    def _min_interval_minutes(self, chat_id: int) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        return BETWIN_TIME * (MULTIPLIER_DISPATCH if self._is_dispatch(chat_id) else 1)      # Internal implementation note: legacy behavior is preserved during modernization.
    def _is_dispatch(self, chat_id: int) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        loc = self.data.get(chat_id, {}).get("ad_creation", {}).get("location_type", [])
        return bool(loc and "اعزام" in loc[0])
    def _max_services_for_range(self, chat_id: int, start_min: int, end_min: int) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        gap = self._min_interval_minutes(chat_id)        # Internal implementation note: legacy behavior is preserved during modernization.
        duration = max(0, end_min - start_min)
        return duration // gap
    
    
    def ask_service_count(self, message , EveryTImeAuto:bool=False):
        chat_id = message.chat.id
        data = self.data.setdefault(chat_id, {}).setdefault("ad_creation", {})

        start_str = data.get("start_time")
        end_str   = data.get("end_time")
        if not (start_str and end_str):
            return self.enter_start_time(message)

        start_min = self.time_to_minutes(start_str)
        end_min   = self.time_to_minutes(end_str)
        max_srv   = self._max_services_for_range(chat_id, start_min, end_min)
        
        # Internal implementation note: legacy behavior is preserved during modernization.
        if max_srv == 0:
            self.bot.send_message(
                chat_id,
                "⛔️ بازهٔ زمانی انتخابی امکان ارائهٔ هیچ سرویسی را ندارد.\n"
                "لطفاً بازهٔ دیگری انتخاب کنید."
            )
            return self.enter_start_time(message)
        if EveryTImeAuto:
            data["service_count"] = max_srv
            self.bot.send_message(
                chat_id,
                f"تعداد سرویس قابل  انجام در این بازه زمانی برای شما {max_srv} میباشد !"
            )
            return self.execute_next_step(message, section="ad_creation")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if max_srv == 1 :
            data["service_count"] = 1
            self.bot.send_message(
                chat_id,
                "ℹ️ در این بازه فقط امکان ارائهٔ یک سرویس وجود دارد؛\n"
                "عدد 1 به‌صورت خودکار ثبت شد."
            )
            return self.execute_next_step(message, section="ad_creation")

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id,
            f"📊 لطفاً تعداد سرویس‌هایی که ارائه می‌دهید را وارد کنید:"
            f"\n(حداقل 1 و حداکثر {max_srv} سرویس)",
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        data["max_srv_tmp"] = max_srv
        self.bot.register_next_step_handler(message, self.save_service_count)
    # Internal implementation note: legacy behavior is preserved during modernization.
    
    def _parse_amount(self, raw: str,
                      *, min_t=1_000, max_t=999_999_999) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        txt = (raw or "").translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        txt = txt.replace(" ", "").replace(",", "")
        if "." in txt:               # Internal implementation note: legacy behavior is preserved during modernization.
            amount = int(float(txt) * 1_000_000)
        else:                        # Internal implementation note: legacy behavior is preserved during modernization.
            v = int(txt)
            amount = v * 1_000 if v < 100_000 else v

        if amount < min_t or amount > max_t or amount % 1_000:
            raise ValueError
        return amount

