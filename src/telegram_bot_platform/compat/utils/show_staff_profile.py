# handlers/staff_profile_handler.py

import html
import json
from telebot import TeleBot, types
from telebot.types import Message, CallbackQuery
from telegram_bot_platform.compat.database.database_manager import DatabaseManager


class StaffProfileHandler:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot: TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db

        # Internal implementation note: legacy behavior is preserved during modernization.
        # bot.message_handler(regexp=r'^/p\d+$')(self.handle_staff_profile)
        # Internal implementation note: legacy behavior is preserved during modernization.

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

    def handle_staff_profile(self, message: Message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        code = message.text.lstrip('/').strip()

        rows = self.db.select_dict('staff', 'U_code = ?', (code,))
        if not rows:
            self.bot.send_message(chat_id, '❌ ارائه‌دهنده‌ای با این کد یافت نشد.')
            return

        profile = rows[0]
        text = self.format_staff_profile(profile)
        photo_id = profile.get('profile_photo')

        if photo_id:
            self.bot.send_photo(
                chat_id,
                photo=photo_id,
                caption=text,
                parse_mode='HTML',
                # disable_web_page_preview=True
            )
        else:
            self.bot.send_message(
                chat_id,
                text,
                parse_mode='HTML',
                # disable_web_page_preview=True
            )

    def handle_gallery_callback(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        code = call.data.split('_', 1)[1]
        rows = self.db.select_dict('staff', 'U_code = ?', (code,))
        if not rows:
            self.bot.answer_callback_query(
                call.id, 'عکس موجود نیست.', show_alert=True)
            return

        gallery = rows[0].get('gallery_photos') or '[]'
        try:
            photo_ids = json.loads(gallery)
        except:
            photo_ids = []

        if not photo_ids:
            self.bot.answer_callback_query(
                call.id, 'عکسی ثبت نشده.', show_alert=True)
            return

        for pid in photo_ids:
            self.bot.send_photo(call.message.chat.id, pid)
        self.bot.answer_callback_query(call.id)
