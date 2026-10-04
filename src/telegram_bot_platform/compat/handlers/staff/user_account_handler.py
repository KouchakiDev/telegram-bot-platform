from telegram_bot_platform.compat.config.settings import *
import re
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from telebot import types
from datetime import datetime
# from telebot import types  
from telebot.types import Message
import random , json
import re
from telegram_bot_platform.compat.utils.workflow_steps import StepHandlerMixin
from datetime import datetime
import jdatetime
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="user_account.log")
log = logger

class UserAccountHandler(StepHandlerMixin):
    def __init__(self, bot, db, data, parent, work, identity_verification, card):
        self.bot = bot
        self.db = db
        self.data = data
        self.parent = parent
        self.work = work
        self.identity_verification = identity_verification
        self.card = card
        self.pucode = "p0000"
        self.field_labels = {
            "name": "🧕 نام",
            "age": "🎂 سطح تجربه",
            "profile_category": "🧩 پروفایلت",
            "phone_number": "📞 شماره تلفن",
            "height": "📏 ظرفیت",
            "weight": "⚖️ حجم خدمات",
            "province": "🏳️ استان",
            "city": "🏙️ شهر",
            "U_code": "🔑 کد ورود",
            "U_refC": "👤 کد دعوت",
            "status": "📌 وضعیت",
            "username": "👥 نام کاربری",
            "maritial_status": "📅 وضعیت دسترسی",
            "breast_size": "🔢 پارامتر عددی",
            "has_health_card": "🩺 مدرک مجوز/تأیید",
            "appearance": "👗 ظاهر",
            "eye_color": "👁️ تخصص اصلی",
            "hair_color": "💇 روش ارائه",
            "dispatch_mode":"نوع مراجعه",
            "region":"مناطق/منطقه کاری",
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            "service_price": "💰 قیمت سرویس",
            "identity_verification_status": "🛂 وضعیت احراز هویت",
            # Internal implementation note: legacy behavior is preserved during modernization.
            "card_number": "💳 شماره کارت",
            "card_number_info": "🏦 اطلاعات کارت",
            "crypto_wallet": "💼 کیف پول کریپتو",
            "crypto_wallet_network": "🌐 شبکه کریپتو",
        }

    def show_account_menu(self, message):
        chat_id = message.chat.id
        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ اطلاعات شما یافت نشد.")
            return

        U_code = result[0]["U_code"]
        self.pucode = U_code
        requests_label = self.parent.requests_handler.get_requests_button_label(
            U_code)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("پروفایل👤")
        markup.add("کیف پول/کارت💳", "احراز هویت✅")
        messages_count = self.parent.messages_handler.get_unread_count(U_code)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # markup.add(requests_label, messages_label)
        markup.add("🔙 بازگشت به پنل")

        self.bot.send_message(
            chat_id, "📁 لطفاً یکی از گزینه‌های حساب کاربری را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_account_action)

    def process_account_action(self, message):
        text = message.text.strip() if message.text else None
        if text == "پروفایل👤":
            self.show_profile_menu(message)
        elif text == "🔙 بازگشت به پنل":
            self.parent.login_handler.login_menu(message)
        elif text == "احراز هویت✅":
            self.identity_verification.start_identity_verification(message)
        elif text == "کیف پول/کارت💳":
            self.card.handle_payments(message)
        elif text == "📨 رفتن به درخواست‌ها":
            return self.parent.requests_handler.show_requests_menu(message)

        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.show_account_menu(message)

    def show_profile_menu(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("مشاهده پروفایل", "تکمیل اطلاعات☑️")
        markup.add("🔙 بازگشت به حساب کاربری")
        self.bot.send_message(
            chat_id, "📋 لطفاً یکی از گزینه‌های مربوط به پروفایل را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_profile_menu_action)

    def process_profile_menu_action(self, message):
        text = message.text.strip() if message.text else None
        if text == "مشاهده پروفایل":
            self.show_profile(message)
        elif text == "تکمیل اطلاعات☑️":
            self.work.confirm_work_settings_intro(message)
        elif text == "🔙 بازگشت به حساب کاربری":
            self.show_account_menu(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_profile_menu_action)
    
    def build_staff_caption(self, p_row: dict) -> tuple[str, list[str]]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            def safe_str(val, fallback='؟'):
                """Legacy-compatible behavior preserved for this callable."""
                return str(val) if val not in [None, ''] else fallback
    
            name = safe_str(p_row.get('name'), 'نامشخص')
            age = safe_str(p_row.get('age'), '?')
            profile_category = safe_str(p_row.get("profile_category" , "عضو"))
            dispatch_mode = safe_str(p_row.get('dispatch_mode'))
            region = safe_str(p_row.get('region'))
            province = safe_str(p_row.get('province'))
            city = safe_str(p_row.get('city'))
            location = f"{city} - {region}" if city and region else region or city or "؟"
    
            height = safe_str(p_row.get('height'), '?')
            weight = safe_str(p_row.get('weight'), '?')
            skin_color = safe_str(p_row.get('skin_color'), 'نامشخص')
            u_code = safe_str(p_row.get("U_code"), "نامشخص")
            ad_code = (
                f"#کدویژه{u_code.replace('p', '')} | "
                f"<a href='https://t.me/{CLIENT_BOT_ID}?start={u_code}'>/{u_code}</a>"
                f" | #{profile_category}"
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            appearance = safe_str(p_row.get('appearance'), random.choice(bodies))
    
            # Internal implementation note: legacy behavior is preserved during modernization.
            mood = safe_str(random.choice(moods))
            style = safe_str(random.choice(styles))
            while len(set([mood, appearance, style])) < 3:
                mood = safe_str(random.choice(moods))
                style = safe_str(random.choice(styles))
    
            body_parts = [mood, appearance, style]
            random.shuffle(body_parts)
            body_phrase = " | ".join([safe_str(p) for p in body_parts])
    
            gallery_link = f"https://t.me/{CLIENT_BOT_ID}?start=gallery_{safe_str(p_row.get('U_code'))}"
            gallery_line = f"<a href='{gallery_link}'>👁 برای دیدن عکس کلیک کنید 👁</a>"
    
            caption = (
                "📍 <b>معرفی ارائه‌دهندگان خدمات و پیشنهادهای منتخب</b>\n\n"
                f"{ad_code}\n\n"
                f"👤 <b>نام:</b> {name}\n"
                f"🎂 <b>سطح تجربه:</b> {age} سال\n"
                f"📍 <b>وضعیت:</b> {dispatch_mode}\n"
                f"🏘 <b>منطقه:</b> {location}\n\n"
                f"📏 <b>ظرفیت:</b> {height} سانتی‌متر\n"
                f"⚖️ <b>حجم خدمات:</b> {weight} واحد\n"
                f"🎨 <b>دسته‌بندی خدمات:</b> {skin_color}\n\n"
                f"💢<b>{body_phrase}</b>\n"
                f"🖼<b>{gallery_line}</b>\n"
                "📩 <b>برای ثبت سفارش و هماهنگی:</b>\n"
                f"@{CLIENT_BOT_ID}\n\n"
                f"{' '.join(PROFILE_CHANNEL_TAGS)}"
            )
    
            return caption, []
    
        except Exception as e:
            log.error(f"[caption] Failed to build staff caption: {e}")
            return "❌ خطا در ساخت کپشن", []
    
    def handle_staff_profile(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            chat_id: int = message.chat.id           # Internal implementation note: legacy behavior is preserved during modernization.
            staff_code: str = message.text.lstrip("/").strip()  # Internal implementation note: legacy behavior is preserved during modernization.
        except AttributeError as exc:
            log.exception(f"[Bot] ❌ Unable to parse message object: {exc}")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            rows: list[dict] = self.db.select_dict(
                "staff",
                "U_code = ?",
                (staff_code,),
            )
        except Exception as exc:
            log.exception(f"[Bot] ❌ DB error while fetching staff {staff_code}: {exc}")
            self.bot.send_message(chat_id, "❌ خطا در ارتباط با پایگاه داده.")
            return

        if not rows:
            self.bot.send_message(chat_id, "❌ ارائه‌دهنده‌ای با این کد یافت نشد.")
            log.info(f"[Bot] No staff found for code={staff_code}")
            return

        profile: dict = rows[0]

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            caption: str = self.build_staff_caption(profile)
        except Exception as exc:
            log.exception(f"[Bot] ❌ Failed to build caption for {staff_code}: {exc}")
            caption = "⚠️ خطا در ساخت توضیحات."

        # Internal implementation note: legacy behavior is preserved during modernization.
        def _safe_json_list(raw: str | None, field_name: str) -> list[str]:
            """Legacy-compatible behavior preserved for this callable."""
            try:
                return json.loads(raw or "[]")
            except Exception as exc:
                log.warning(f"[Bot] Malformed JSON in {field_name}: {exc}")
                return []

        profile_photos: list[str] = _safe_json_list(profile.get("profile_photos"), "profile_photos")
        gallery_photos: list[str] = _safe_json_list(profile.get("gallery_photos"), "gallery_photos")

        # Internal implementation note: legacy behavior is preserved during modernization.
        photo_ids: list[str] = [pid for pid in (profile_photos + gallery_photos) if pid]
        log.debug(f"[Bot] photos found for {staff_code}: {photo_ids}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        photo_id: str | None = profile.get("profile_photo") or (random.choice(photo_ids) if photo_ids else None)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                text="🔍 آگهی‌های این کد",
                callback_data=f"premium_fav_today_ads_{staff_code}"
            )
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            if photo_id:
                self.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_id,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                log.info(f"[Bot] Sent photo to chat_id={chat_id}")
            else:
                self.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode="HTML",
                    reply_markup=markup,
                )
                log.info(f"[Bot] Sent message to chat_id={chat_id}")
        except Exception as exc:
            log.exception(f"[Bot] ❌ Failed to send message/photo to chat_id={chat_id}: {exc}")

    def show_profile(self, message):
        chat_id = message.chat.id
        # telegram_id = message.from_user.id
        try :
            message.text = f"/{self.pucode}"
            self.handle_staff_profile(message)
        except:
            pass
        

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📄 جزئیات بیشتر", "📝 درخواست ویرایش")
        markup.add("🔙 بازگشت به حساب کاربری")
        self.bot.send_message(
            chat_id, "لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_profile_action)

    def process_profile_action(self, message):
        text = message.text.strip() if message.text else None
        if text == "📄 جزئیات بیشتر":
            self.show_full_profile(message)
        elif text == "📝 درخواست ویرایش":
            self.ask_for_edit_request(message)
        elif text == "🔙 بازگشت به حساب کاربری":
            self.show_account_menu(message)
        else:
            self.bot.send_message(
                message.chat.id, "❌ لطفاً فقط از دکمه‌های موجود استفاده کنید.")
            self.bot.register_next_step_handler(
                message, self.process_profile_action)

    def show_full_profile(self, message):
        chat_id = message.chat.id
        result = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not result:
            self.bot.send_message(chat_id, "❌ اطلاعاتی برای شما یافت نشد.")
            return

        profile = result[0]
        media_fields = [
            "id", "video_message", "profile_photo",
            "id_card_front", "id_card_back", "verification_photo_with_id", "gallery_photos"
        ]
        skip_field = ["status","username",""]
        full_fields = [k for k in self.field_labels if k not in media_fields and k not in skip_field]

        profile_text = self.format_profile_fields(
            profile, allowed_fields=full_fields)
        self.bot.send_message(
            chat_id, f"📄 اطلاعات کامل پروفایل:\n\n{profile_text}", parse_mode = "Markdown")

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📝 درخواست ویرایش", "🔙 بازگشت به حساب کاربری")
        self.bot.send_message(
            chat_id, "⬅️ لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_profile_action)

    def ask_for_edit_request(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 بازگشت به حساب کاربری")
        self.bot.send_message(
            chat_id,
            "📝 لطفاً توضیح دهید که چه بخشی از پروفایل خود را می‌خواهید ویرایش کنید و چرا؟",
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            message, self.save_edit_request_message)

    def save_edit_request_message(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if text == "🔙 بازگشت به حساب کاربری":
            return self.show_account_menu(message)

        result = self.db.select_dict(
            "staff", "telegram_id = ?", (chat_id,))
        if not result or not result[0].get("U_code"):
            self.bot.send_message(
                chat_id, "❌ خطا در یافتن کد کاربری شما. لطفاً مجدداً تلاش کنید.")
            return

        request_data = {
            "U_code": result[0]["U_code"],
            "telegram_id": chat_id,                        # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            "status": "pending",
            "request_type": "profile_edit",
            "content": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.db.ensure_table_and_columns("Requests", request_data)
        self.db.insert("Requests", request_data)

        self.bot.send_message(
            chat_id,
            "✅ درخواست ویرایش شما ثبت شد. پس از تأیید ادمین، امکان ویرایش فراهم می‌شود."
        )
        self.show_account_menu(message)

    import re

    def format_profile_fields(self, profile: dict, allowed_fields: list = None) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        def escape_md(text):
            """Legacy-compatible behavior preserved for this callable."""
            if isinstance(text, str):
                return re.sub(r'([_*`\[\]()])', r'\\\1', text)
            return str(text)

        lines = []

        for field, label in self.field_labels.items():
            # Internal implementation note: legacy behavior is preserved during modernization.
            if allowed_fields and field not in allowed_fields:
                continue

            value = profile.get(field)

            # Internal implementation note: legacy behavior is preserved during modernization.
            if value in [None, "", "None"]:
                continue

            # Internal implementation note: legacy behavior is preserved during modernization.
            if str(value) in ["0", "1"]:
                value = "دارد" if str(value) == "1" else "ندارد"

            # Internal implementation note: legacy behavior is preserved during modernization.
            if field in ("U_refC","U_code"):
                value = f"`{escape_md(value)}`"
            else:
                value = escape_md(value)

            lines.append(f"*{label}:* {value}")

        return "\n".join(lines)


    def to_persian_date(self, gregorian_date_str):
        try:
            if " " in gregorian_date_str:
                gregorian_date_str = gregorian_date_str.split(" ")[
                    0]  # Just the date
            g_date = datetime.strptime(gregorian_date_str, "%Y-%m-%d")
            j_date = jdatetime.date.fromgregorian(date=g_date.date())
            return f"{j_date.year}/{j_date.month:02}/{j_date.day:02}"
        except:
            return "تاریخ نامعتبر"

    def is_valid_time_format(self, time_str):
        return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str)) or bool(re.match(r'^([۰-۲]?[۰-۹]|۲[۰-۳]):[۰-۵][۰-۹]$', time_str))

    def show_my_ads(self, message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📤 آگهی‌های تأییدشده", "⌛ آگهی‌های در انتظار تأیید")
        markup.add("🔙 بازگشت")
        self.bot.send_message(
            chat_id, "🔍 لطفاً دسته‌بندی آگهی‌ها را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_ads_category_selection)

    def handle_ads_category_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "📤 آگهی‌های تأییدشده":
            return self.display_user_ads_by_status(message, status="approved")
        elif text == "⌛ آگهی‌های در انتظار تأیید":
            return self.display_user_ads_by_status(message, status="pending")
        elif text == "🔙 بازگشت":
            return self.show_account_menu(message)
        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.show_my_ads(message)

    def display_user_ads_by_status(self, message, status):
        chat_id = message.chat.id
        user = self.db.select_dict(
            "staff", "telegram_id = ?", (message.from_user.id,))
        if not user:
            return self.bot.send_message(chat_id, "❌ کاربر یافت نشد.")

        user = user[0]
        ads = self.db.select_dict(
            "ads", "U_code = ? AND status = ?", (user["U_code"], status))

        if not ads:
            self.bot.send_message(
                chat_id, "📭 آگهی‌ای در این دسته‌بندی وجود ندارد.")
            return self.bot.register_next_step_handler(message, self.handle_ads_category_selection)
        self.data.setdefault(chat_id, {})[
            "last_ads_status"] = status  # Internal implementation note: legacy behavior is preserved during modernization.

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for ad in ads:
            persian_date = self.to_persian_date(
                ad.get("creation_date") or ad.get("created_at", ""))
            status_label = "در انتظار تأیید ادمین" if ad["status"] == "pending" else "تأییدشده"
            button_text = f"آگهی {ad['id']} - تاریخ {persian_date} - وضعیت {status_label}"
            markup.add(button_text)

        markup.add("🔙 بازگشت")
        self.data[chat_id]["ads_list"] = [ad["id"] for ad in ads]
        self.bot.send_message(chat_id, "📋 آگهی‌های شما:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_my_ads_selection)

    def handle_my_ads_selection(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "🔙 بازگشت":
            self.show_my_ads(message)  # Go back to main category menu
            return

        match = re.match(r"آگهی (\d+)", text)
        if not match:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            # Use last viewed filter
            self.display_user_ads_by_status(
                message, status=self.data[chat_id].get("last_ads_status", "pending"))
            return
        ad_id = int(match.group(1))
        ad = self.db.select_dict("ads", "id = ?", (ad_id,))
        if not ad:
            self.bot.send_message(chat_id, "❌ آگهی مورد نظر یافت نشد.")
            return
        ad = ad[0]
        status_label = "در انتظار تأیید ادمین" if ad["status"] == "pending" else "تأییدشده"
        persian_date = self.to_persian_date(
            ad.get("creation_date") or ad.get("created_at", ""))

        details = (
            f"🆔 شناسه آگهی: {ad['id']}\n"
            f"📅 تاریخ ثبت: {persian_date}\n"
            f"🕒 زمان: {ad['start_time']} تا {ad['end_time']}\n"
            f"🔢 تعداد سرویس قابل پذیرش: {ad['service_count']}\n"
            f"📌 وضعیت: {status_label}"
        )

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📝 ویرایش آگهی", "🗑 حذف آگهی")
        markup.add("🔙 بازگشت")
        self.bot.send_message(chat_id, details, reply_markup=markup)

        self.data.setdefault(chat_id, {})["selected_ad_id"] = ad_id
        self.bot.register_next_step_handler(
            message, self.handle_ad_action_choice)

    def handle_ad_action_choice(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        if text == "🔙 بازگشت":
            return self.show_my_ads(message)

        elif text == "🗑 حذف آگهی":
            ad_id = self.data.get(chat_id, {}).get("selected_ad_id")
            if ad_id:
                self.db.remove("ads", "id = ?", (ad_id,))
                self.bot.send_message(chat_id, "🗑 آگهی با موفقیت حذف شد.")
            else:
                self.bot.send_message(
                    chat_id, "❌ مشکلی در شناسایی آگهی وجود دارد.")
            return self.show_my_ads(message)

        elif text == "📝 ویرایش آگهی":
            return self.start_edit_ad_flow(message)

        else:
            self.bot.send_message(
                chat_id, "❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
            return self.bot.register_next_step_handler(message, self.handle_ad_action_choice)

    def start_edit_ad_flow(self, message):
        chat_id = message.chat.id
        self.data.setdefault(chat_id, {})["edit_ad"] = {
            "step_index": 0,
            "workflow": [step["name"] for step in self.edit_ad_steps],
        }
        return self.execute_next_step(message, section="edit_ad")

    def edit_start_time(self, message):
        chat_id = message.chat.id
        step = self.get_step_by_name("edit_ad", "edit_start_time")
        self.bot.send_message(chat_id, step["prompt"])
        self.bot.register_next_step_handler(
            message, self.process_edit_start_time)

    def process_edit_start_time(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if not self.is_valid_time_format(text):
            self.bot.send_message(
                chat_id, "❌ لطفاً ساعت را در فرمت صحیح مانند 14:00 وارد کنید.")
            return self.edit_start_time(message)  # Re-ask
        self.data[chat_id]["edit_ad"]["start_time"] = text
        self.execute_next_step(message, "edit_ad")

    def edit_end_time(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if not self.is_valid_time_format(text):
            self.bot.send_message(
                chat_id, "❌ لطفاً ساعت را در فرمت صحیح مانند 18:00 وارد کنید.")
            return self.execute_current_step(message, section="edit_ad")
        self.data[chat_id]["edit_ad"]["end_time"] = text
        return self.execute_next_step(message, section="edit_ad")

    def edit_service_count(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        if not text.isdigit():
            self.bot.send_message(chat_id, "❌ لطفاً فقط عدد وارد کنید.")
            return self.execute_current_step(message, section="edit_ad")
        self.data[chat_id]["edit_ad"]["service_count"] = int(text)
        return self.execute_next_step(message, section="edit_ad")

    def edit_description(self, message):
        chat_id = message.chat.id
        text = message.text.strip() if message.text else None
        self.data[chat_id]["edit_ad"]["description"] = text if text.lower(
        ) != "ندارد" else ""

        ad_id = self.data[chat_id].get("selected_ad_id")
        if ad_id:
            update_data = {
                "start_time": self.data[chat_id]["edit_ad"].get("start_time"),
                "end_time": self.data[chat_id]["edit_ad"].get("end_time"),
                "service_count": self.data[chat_id]["edit_ad"].get("service_count"),
                "description": self.data[chat_id]["edit_ad"].get("description"),
            }
            self.db.update("ads", update_data, "id = ?", (ad_id,))
            self.bot.send_message(chat_id, "✅ آگهی با موفقیت ویرایش شد.")
        else:
            self.bot.send_message(
                chat_id, "❌ مشکلی در شناسایی آگهی وجود دارد.")

        return self.show_my_ads(message)
