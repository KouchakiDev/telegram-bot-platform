# Internal implementation note: legacy behavior is preserved during modernization.
# import re
import json
import html

import random
from  telebot import types
# Internal implementation note: legacy behavior is preserved during modernization.
# import telebot
from telebot import TeleBot
from telebot.types import (
    Message,
    CallbackQuery,

)
# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# Client Handlers


# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger


log = CustomLogger()  # log_file="show_pp.log")


class StaffProfileHandler:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot: TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db

        # Internal implementation note: legacy behavior is preserved during modernization.
        # bot.message_handler(regexp=r'^/p\d+$')(self.handle_staff_profile)
        # Internal implementation note: legacy behavior is preserved during modernization.
    
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


    def format_staff_profile(self, data: dict) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        u_code = data.get('U_code', '—')
        name = data.get('name', '—')
        age = data.get('age', '—')
        profile_category = data.get('profile_category', '—')
        height = data.get('height', '—')
        weight = data.get('weight', '—')
        province = data.get('province', '—')
        city = data.get('city', '—')
        marital = data.get('marital_status', '—')
        appearance = data.get('appearance', '—')
        eye_color = data.get('eye_color', '—')
        hair_color = data.get('hair_color', '—')
        service = data.get('service_price', '—')

        # Internal implementation note: legacy behavior is preserved during modernization.
        bot_username = self.bot.get_me().username
        gallery_link = f"https://t.me/{bot_username}?start=gallery_{u_code}"

        profile_text = (
            f"👤 <b>پروفایل ارائه‌دهنده</b>\n\n"
            f"🔖 <b>کد:</b> /{html.escape(u_code)}\n"
            f"👤 <b>نام:</b> {html.escape(name)}\n"
            f"🎂 <b>سطح تجربه:</b> {age}\n"
            f"🧩 <b>پروفایلت:</b> #{profile_category}\n"
            f"📏 <b>ظرفیت:</b> {height} cm   <b>حجم خدمات:</b> {weight} kg\n"
            f"📍 <b>موقعیت:</b> {province} / {city}\n"
            f"📅 <b>وضعیت دسترسی:</b> {marital}\n"
            f"🎨 <b>ظاهر:</b> {appearance}\n"
            f"👁️ <b>تخصص اصلی:</b> {eye_color}   <b>روش ارائه:</b> {hair_color}\n"
            f"💰 <b>قیمت سرویس:</b> {service} تومان"
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        profile_text += (
            f"\n\n🖼 <a href=\"{gallery_link}\">مشاهده عکس‌های بیشتر</a>"
        )
        return profile_text
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

    def handle_gallery_callback(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        code = call.data.split('_', 1)[1]
        rows = self.db.select_dict('staff', 'U_code = ?', (code,))
        if not rows:
            self.bot.answer_callback_query(
                call.id, 'عکس موجود نیست.', show_alert=True)
            return

        profile = rows[0]
        # text = self.build_staff_caption(profile)


# Internal implementation note: legacy behavior is preserved during modernization.
        try:
            profile_photos = json.loads(profile.get('profile_photos', '[]'))
        except Exception:
            profile_photos = []

        try:
            gallery_photos = json.loads(profile.get('gallery_photos', '[]'))
        except Exception:
            gallery_photos = []

        # Internal implementation note: legacy behavior is preserved during modernization.
        # main_photo = profile.get('profile_photo')

        # Internal implementation note: legacy behavior is preserved during modernization.
        photo_ids = []
        photo_ids.extend(profile_photos)
        photo_ids.extend(gallery_photos)


        if not photo_ids:
            self.bot.answer_callback_query(
                call.id, 'عکسی ثبت نشده.', show_alert=True)
            return

        for pid in photo_ids:
            self.bot.send_photo(call.message.chat.id, pid)
        self.bot.answer_callback_query(call.id)
