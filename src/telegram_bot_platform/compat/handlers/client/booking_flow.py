# Internal implementation note: legacy behavior is preserved during modernization.

import json


from telebot import TeleBot, types

# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# Client Handlers

from telegram_bot_platform.compat.handlers.client.booking.booking_requests import BookingHandler
# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

log = CustomLogger("booking")


class Reserve_manager:
    def __init__(self, bot: TeleBot, db: DatabaseManager, back, new_requests):
        self.bot = bot
        self.db = db
        self.back = back
        self.new = new_requests  # Internal implementation note: legacy behavior is preserved during modernization.
        self.normal_reserve_requests_menu = BookingHandler(
            self.bot, self.db,  self.back, self.show_main_menu, self.new)
        self.temp_ad_Data = {}

    def user_do_that(self, message, that):
        log.info(
            f"user {message.from_user.id}  {that}")

    def get_data_from_database(self, reserve_ad_code):
        try:
            log.info(f"📥Getting book full {reserve_ad_code}")
            book, table, ad_row_id, slot_time1, slot_time2 = reserve_ad_code.split(
                "_")

            log.info(
                f"🔍 parsed : book={book}, table={table}, ad_row_id={ad_row_id}, slot={slot_time1}:{slot_time2}")

            slot_list = self.db.select_dict(
                "live_ads", "ad_id = ?", (ad_row_id,))
            ad_list = self.db.select_dict(table, "id = ? AND status = 'approved' ", (ad_row_id,))

            log.info(f"📦 slot_list: {slot_list}")
            log.info(f"📦 ad_list: {ad_list}")

            if not slot_list or not ad_list:
                log.warning(
                    f"⚠️data or ads not found ad_list = {ad_list} slot_list = {slot_list}")
                return None

            slot_row_id = slot_list[0]["id"]
            data = {
                "book": book,
                "table": table,
                "ad_row": ad_list[0],
                "ad_row_id": ad_row_id,
                "slot_row_id": slot_row_id,
                "slot": slot_list,
                "slot_time": f"{slot_time1}:{slot_time2}"
            }
            log.info(f"✅ داده نهایی آماده: {data}")
            return data
        except Exception as e:
            log.exception(f"❌ خطا در get_data_from_database: {e}")
            return None
    # |================================|
    # Internal implementation note: legacy behavior is preserved during modernization.
    # |================================|

    def format_field(self, label: str, value: any, suffix: str = "") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if value and str(value).strip().lower() not in ["", "null", "none"]:
            return f"{label} {value}{suffix}"
        return ""

    def format_boolean_field(self, label: str, value: str, true_text="✅ دارد", false_text="❌ ندارد") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if value == "1":
            return f"{label} {true_text}"
        elif value == "0":
            return f"{label} {false_text}"
        return ""

# =======================
# Internal implementation note: legacy behavior is preserved during modernization.
# =======================

    def build_full_ad_caption(self, data: dict) -> str:
        ad = data.get("ad_row", {})
        user = data.get("staff", {})
        slot_time = data.get("slot_time", "نامشخص")

        parts = []
        parts.append(self.format_field("👤 نام:", user.get("name")))
        parts.append(self.format_field(
            "🔖 کد کاربری:", f"/{user.get("U_code")}"))
        parts.append(self.format_field("🎂 سطح تجربه:", user.get("age")))
        parts.append(self.format_field("📍 شهر:", user.get("city")))
        parts.append(self.format_field("🟫 استان:", user.get("province")))
        parts.append(self.format_field(
            "🔢 پارامتر عددی:", user.get("breast_size")))
        parts.append(self.format_field("👗 ظاهر:", user.get("appearance")))
        parts.append(self.format_field("🎨 دسته‌بندی خدمات:", user.get("skin_color")))
        parts.append(self.format_field("👁 تخصص اصلی:", user.get("eye_color")))
        parts.append(self.format_field("🧩 روش ارائه:", user.get("hair_color")))
        parts.append(self.format_field(
            "📏 ظرفیت:", user.get("height"), " سانتی‌متر"))
        parts.append(self.format_field(
            "⚖️ حجم خدمات:", user.get("weight"), " واحد"))
        parts.append(self.format_field(
            "📅 وضعیت دسترسی:", user.get("marital_status")))
        parts.append(self.format_boolean_field(
            "🏠 خانه شخصی:", user.get("has_home")))
        parts.append(self.format_boolean_field(
            "🚗 امکان مراجعه به مشتری:", user.get("visit_client_home")))

        # Internal implementation note: legacy behavior is preserved during modernization.
        parts.append(self.format_field(
            "🛎 خدمات:", ad.get("regular_services", "ندارد")))

        # Internal implementation note: legacy behavior is preserved during modernization.
        special_services = ""
        try:
            services_dict = json.loads(ad.get("services", "{}"))
            if services_dict:
                temp = []
                for key, val in services_dict.items():
                    title = val.get("title", key)
                    price = val.get("price")
                    temp.append(
                        f"{title}(+{int(price):,})" if price else title)
                special_services = " ، ".join(temp)
        except:
            pass
        parts.append(self.format_field("💎 خدمات خاص:", special_services))

        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_info = ""
        try:
            premium_dict = json.loads(ad.get("premium_services", "{}"))
            if premium_dict:
                premium_parts = []
                for key, val in premium_dict.items():
                    title = val.get("title", key)
                    price = val.get("price")
                    premium_parts.append(
                        f"▫️ {title} (+{int(price):,})" if price else f"▫️ {title}")
                premium_info = "👑 خدمات PREMIUM اضافه‌شده:\n" + "\n".join(premium_parts)
        except:
            pass
        parts.append(premium_info)

        # Internal implementation note: legacy behavior is preserved during modernization.
        base_price = user.get("service_price", "نامشخص")
        if isinstance(base_price, (int, float, str)) and str(base_price).isdigit():
            base_price = f"{int(base_price):,} تومان"
        else:
            base_price = "نامشخص"
        parts.append(self.format_field("💰 قیمت پایه:", base_price))

        # Internal implementation note: legacy behavior is preserved during modernization.
        parts.append(self.format_field("💳 روش‌های پرداخت:",
                     ad.get("payment_method", "نامشخص")))

        parts.append(f"\n<b>🕒 ساعت انتخاب‌شده: « {slot_time} »</b>\n")

        # Internal implementation note: legacy behavior is preserved during modernization.
        parts.append("\n❓ آیا این آگهی مورد نظر شماست؟")

        return "\n".join([p for p in parts if p.strip()])

    def show_main_menu(self, message, reserve_ad_code):
        chat_id = message.chat.id
        try:
            log.info(
                f"🔁 اجرای show_main_menu برای chat_id={chat_id} با کد: {reserve_ad_code}")
            results = self.get_data_from_database(reserve_ad_code)
            print(results)
            if not results:
                self.bot.send_message(
                    chat_id, "❗ مشکلی در دریافت اطلاعات آگهی پیش آمده.")
                self.back(message)
                return

            photo_id = results["ad_row"].get("ad_photo")
            staff = self.db.select_dict(
                "staff", "U_code = ?", (results["ad_row"].get("U_code"),))
            if staff:
                results["staff"] = staff[0]

            caption = self.build_full_ad_caption(results)

            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=2)
            markup.add(
                types.KeyboardButton(BUTTONS["yes"]),
                types.KeyboardButton(BUTTONS["back"])
            )

            if photo_id:
                self.bot.send_photo(chat_id, photo_id,
                                    caption=caption, reply_markup=markup, parse_mode="HTML")
            else:
                self.bot.send_message(
                    chat_id, caption, reply_markup=markup, parse_mode="HTML")

            self.temp_ad_Data[chat_id] = results
            self.bot.register_next_step_handler(message, self.route)
        except Exception as e:
            log.exception(
                f"❌ خطا در show_main_menu برای chat_id={chat_id}: {e}")
            self.bot.send_message(chat_id, "❗ این آگهی منقضی شده است.")
            self.back(message)

    def route(self, message):
        text = message.text

        if text == BUTTONS["back"]:
            self.user_do_that(message, f"choice back menu")

            self.back(message)
            return
        elif text == BUTTONS["yes"]:
            self.user_do_that(message, f"user confirmed the ad")

            self.normal_reserve_requests_menu.start_menu(
                message, self.temp_ad_Data[message.chat.id])
            return
        elif text.startswith("/start"):
            self.new(message)
            return
        else:
            self.back(message)

            # Internal implementation note: legacy behavior is preserved during modernization.
