import os
from pathlib import Path
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, '..'))
from telebot import TeleBot, types
from telegram_bot_platform.compat.localization import LocalizedTeleBot
import threading
import random
from telebot.types import ReplyKeyboardMarkup  , ReplyKeyboardRemove
from datetime import datetime, timedelta
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.runners.starter import Starter
from telegram_bot_platform.compat.config.settings import HAND_VERFIY , VERIFICATION_PHOTO_TIMEOUT , STORAGE_CHANNEL , BOT_CLIENT_TOKEN , DB_PARAMS , BOT_ADMIN_TOKEN
admin_username = os.getenv("ADMIN_SUPPORT_USERNAME", "").strip()
# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------

# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# EDU_IMAGES = {
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# }

# Internal implementation note: legacy behavior is preserved during modernization.
log = CustomLogger("SimpleRunner")
# Internal implementation note: legacy behavior is preserved during modernization.
IMAGES_DIR = os.path.join(BASE_DIR, "Data", "images")  # Internal implementation note: legacy behavior is preserved during modernization.
IMAGES_DIR = os.getenv("IMAGES_DIR", str(Path(__file__).resolve().parents[5] / "resources" / "images"))
BACK_BTN = "🔙 بازگشت"
# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------

class SimpleClientRunner:
    """Legacy-compatible behavior preserved for this callable."""

    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def __init__(self, bot: TeleBot, db: DatabaseManager):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.admin_bot = LocalizedTeleBot(BOT_ADMIN_TOKEN)
        self.db = db
        self.storage_channel = STORAGE_CHANNEL
        self.state = {}
        self.log = log
        self.starter = Starter(self.db, self.bot, welcome_cb=self._build_state_router)
        
        self.state_router = self._build_state_router()
        self.register_handlers()


        # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _build_state_router(self):
        """Legacy-compatible behavior preserved for this callable."""
        return {
            "get_code":          self._handle_staff_code,
            "get_region":        self._handle_region,
            "get_contact":       self._handle_contact,
            "get_verification_photo_1":      lambda msg: self._handle_verification_photo(msg, 1),
            "get_verification_photo_2":      lambda msg: self._handle_verification_photo(msg, 2),
            "get_time":          self._handle_time,
            "finished":          lambda msg: self.bot.send_message(msg.chat.id, "✅ پایان فرایند"),
        }
    def is_back(self, message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            text    = (message.text or "").strip()

            # Internal implementation note: legacy behavior is preserved during modernization.
            if text not in (BACK_BTN, "/start"):
                return False

            # --------------------------------------------
            # Internal implementation note: legacy behavior is preserved during modernization.
            # --------------------------------------------
            if "start" in text:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.state[chat_id] = {"step": "get_code"}
                self._ask_staff_code(message)  # Internal implementation note: legacy behavior is preserved during modernization.
                self.log.info("[IS_BACK] Restarted flow with /start")  # Internal implementation note: legacy behavior is preserved during modernization.
                return True

            # --------------------------------------------
            # Internal implementation note: legacy behavior is preserved during modernization.
            # --------------------------------------------
            current_step = self.state.get(chat_id, {}).get("step")

            # Internal implementation note: legacy behavior is preserved during modernization.
            prev_map = {
                "get_region"  : self._ask_staff_code,
                "get_contact" : self._ask_region,
                "get_verification_photo_1": self._ask_contact,
                "get_verification_photo_2": lambda m: self._request_verification_photo(m, step=1),
                "get_time"    : lambda m: self._request_verification_photo(m, step=2),
            }

            # Internal implementation note: legacy behavior is preserved during modernization.
            goto_func = prev_map.get(current_step, self._ask_staff_code)

            # Internal implementation note: legacy behavior is preserved during modernization.
            if goto_func == self._ask_staff_code:
                new_step_name = "get_code"
            elif goto_func == self._ask_region:
                new_step_name = "get_region"
            elif goto_func == self._ask_contact:
                new_step_name = "get_contact"
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                new_step_name = (
                    "get_verification_photo_1" if current_step == "get_verification_photo_2" else "get_code"
                )

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.state[chat_id]["step"] = new_step_name

            # Internal implementation note: legacy behavior is preserved during modernization.
            goto_func(message)
            self.log.info(
                f"[IS_BACK] Moved back from {current_step} to {new_step_name}"
            )
            return True

        except Exception as exc:
            self.log.exception(f"[IS_BACK] failed: {exc}")
            return False

    def register_handlers(self):
        """Legacy-compatible behavior preserved for this callable."""

        @self.bot.message_handler(func=lambda message: message.text is not None)
        def handle_all_messages(message):
            try:
                text = message.text.strip()

                if text == "/start":
                    self.starter.store_user_info(message)          # Internal implementation note: legacy behavior is preserved during modernization.
                    
                    self.bot.clear_step_handler(message)
                    self._reset_user(message.chat.id)
                    self._ask_staff_code(message)
                    self.log.info(f"[START] flow restarted for chat {message.chat.id}")
                    return

                if text == "از درخواست خود منصرف شدم 🚫":
                    self.cansel_handler(message)
                    self.log.info(f"[CANCEL] user cancelled request {message.chat.id}")
                    return

                # Internal implementation note: legacy behavior is preserved during modernization.
                # chat_id = message.chat.id
                # if chat_id in self.state:
                #     current_step = self.state[chat_id].get("step")
                #     handler = self.state_router.get(current_step)
                #     if handler:
                #         handler(message)
                #     else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                #         self.log.warning(f"[STATE] No handler for step '{current_step}'")
                # else:
                # Internal implementation note: legacy behavior is preserved during modernization.
            except Exception as exc:
                self.log.exception(f"[HANDLER] failed: {exc}")


    def cansel_handler(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()
            chat_id = message.chat.id

            result = self.db.select_dict(
                "request_drafts",
                "telegram_id = ? AND date(created_at) = ? AND status IN ('pending', 'approved')",
                (message.from_user.id, today)
            )

            if result:
                latest = result[-1]
                status = latest.get("status")
                name = latest.get("name", "❓")
                tg_id = latest.get("telegram_id", "❓")
                username = latest.get("username", "❓")
                staff_code = latest.get("staff_code", "❓")
                phone = latest.get("phone", "❓")
                req_time = latest.get("request_time", "❓")

                if status == "approved":
                    reserved_time = latest.get("request_time", "❓")
                    phone = latest.get("phone", "❓")

                    self.bot.send_message(
                        chat_id,
                        f"✅ سفارش شما برای ساعت **{reserved_time}** تأیید و رزرو شده است.\n\n"
                        "در صورتی که قصد کنسل کردن دارید، لطفاً به آیدی زیر پیام دهید:\n"
                        f"{admin_username}\n\n"
                        f"در غیر این‌صورت منتظر تماس پرسنل با شماره‌ی **{phone}** باشید.",
                        parse_mode="Markdown",
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(admin_username)
                    )

                    self.message_to_admin(
                        f"⚠️ کاربر تأییدشده قصد کنسل کردن دارد:\n"
                        f"👤 نام: {name}\n"
                        f"🆔 آیدی عددی: {tg_id}\n"
                        f"🔗 یوزرنیم: @{username}\n"
                        f"📝 کد ارائه‌دهنده: {staff_code}\n"
                        f"📞 شماره تماس: {phone}\n"
                        f"🕒 ساعت رزرو: {reserved_time}"
                    )



                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.update("request_drafts", {"status": "canceled"}, "id = ?", (latest["id"],))
                    self.bot.send_message(chat_id, "❌ سفارش شما کنسل شد", reply_markup=ReplyKeyboardRemove())

                    self.message_to_admin(
                        f"❌ سفارش لغو شد توسط کاربر:\n"
                        f"👤 نام: {name}\n"
                        f"🆔 آیدی عددی: {tg_id}\n"
                        f"🔗 یوزرنیم: @{username}\n"
                        f"📝 کد ارائه‌دهنده: {staff_code}\n"
                        f"📞 شماره تماس: {phone}\n"
                        f"🕒 زمان درخواست: {req_time}"
                    )


            else:
                self.bot.send_message(chat_id, "⚠️ شما سفارش جاری ندارید", reply_markup=ReplyKeyboardRemove())

        except Exception as exc:
            self.log.exception(f"[CANCEL_HANDLER] failed: {exc}")


    def _has_pending_request(self, message: int) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()
            telegram_id = message.from_user.id
            chat_id = message.chat.id
            rows = self.db.select_dict(
                table="request_drafts",
                condition="telegram_id = ? AND date(created_at) = ? AND status = 'pending' ",
                params=(telegram_id,today)
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            # "telegram_id = ? AND status = 'pending' AND date(created_at) = ?",
            # params=(chat_id, today)
            if rows :
                self.log.info(f"[CHECK_PENDING] chat={chat_id} pending={True}")
                return True
            else:
                return False
 

        except Exception as exc:
            self.log.exception(f"[CHECK_PENDING] failed: {exc}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            return False


    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _ask_staff_code(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self._has_pending_request(message):
                cancel_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
                cancel_btn.add("از درخواست خود منصرف شدم 🚫")
                self.bot.send_message(
                    chat_id,
                    "⚠️ شما یک سفارش در حالت *در انتظار تأیید* دارید.\n"
                    "در صورت نیاز می‌توانید با دکمه زیر آن را لغو کنید.",
                    parse_mode="Markdown",
                    reply_markup=cancel_btn
                )
                return  # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                "لطفا کد پرسنل مورد نظر را (فقط از فعال‌های امروز) وارد کنید:",
                reply_markup= ReplyKeyboardRemove()
            )
            self.bot.register_next_step_handler(message, self._handle_staff_code )
        except Exception as exc:
            self.log.exception(f"[ASK_CODE] failed: {exc}")

    def _handle_staff_code(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            code = message.text
                    # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            # if not self._is_active_today(code):
            # Internal implementation note: legacy behavior is preserved during modernization.
            #     return self._ask_staff_code(message)
            if not code:
                self.bot.send_message(chat_id, "❌ لطفا کد صحیح وارد کنید")
                return self._ask_staff_code(message)
            
            self.state[chat_id]["staff_code"] = code
            
            
            # Internal implementation note: legacy behavior is preserved during modernization.
            # if self._is_dispatch(code):
            self.state[chat_id]["step"] = "get_code"
            
            return self._ask_region(message)

            # return self._ask_contact(message)
        except Exception as exc:
            self.log.exception(f"[HANDLE_CODE] failed: {exc}")
            self._ask_staff_code(message)
    
    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _ask_region(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("✂ ارائه در محل مشتری نیست")
            markup.add(BACK_BTN)
            self.bot.send_message(
                chat_id,
                "در صورتی که کد انتخابی شما ارائه در محل مشتری‌ست لطفا محدوده مکان خود را وارد کنید:\n\nمثال: قاسم آباد",
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self._handle_region)
        except Exception as exc:
            self.log.exception(f"[ASK_REGION] failed: {exc}")


    def _handle_region(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
                    # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return

            region = (message.text or "").strip()
           
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, "✅ محدوده ثبت شد.", reply_markup=types.ReplyKeyboardRemove())

            if region == "✂ ارائه در محل مشتری نیست":
                region = None
            self.state[chat_id]["step"] = "get_region"

            self.state[chat_id]["region"] = region
            return self._ask_contact(message)
        except Exception as exc:
            self.log.exception(f"[HANDLE_REGION] failed: {exc}")
            self._ask_region(message)
    

    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _ask_contact(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            contact_btn = types.KeyboardButton("📱 ارسال شماره من", request_contact=True)
            markup.add(contact_btn)
            markup.add(BACK_BTN)

            text = (
                "لطفاً شماره تماس خود را با استفاده از دکمه زیر به اشتراک بگذارید:\n\n"
                "توجه :\n"
                "شماره واردشده همان شماره‌ایست که با آن وارد تلگرام شده‌اید. این شماره جهت هماهنگی باید در دسترس باشد."
            )
            self.bot.send_message(chat_id, text, reply_markup=markup)
            self.bot.register_next_step_handler(message, self._handle_contact)
        except Exception as exc:
            self.log.exception(f"[ASK_CONTACT] failed: {exc}")

    def _handle_contact(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
                    # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return

            
            if message.contact and message.contact.user_id == message.from_user.id:
                phone = message.contact.phone_number
                self.state[chat_id]["phone"] = phone
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(chat_id, "✅ شماره ثبت شد.", reply_markup=types.ReplyKeyboardRemove())
                return self._request_verification_photo(message, step=1, retry=False)

            self.bot.send_message(chat_id, """لطفاً برای ارسال شماره تلفن، فقط از دکمه «ارسال شماره من» استفاده کنید.
توجه داشته باشید که شماره‌ای که ارسال می‌کنید، باید همان شماره‌ای باشد که در تلگرام از آن استفاده می‌کنید""")
            self.state[chat_id]["step"] = "get_contact"
            
            return self._ask_contact(message)
        except Exception as exc:
            self.log.exception(f"[HANDLE_CONTACT] failed: {exc}")
            self._ask_contact(message)

    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _request_verification_photo(self, message, step: int, retry: bool = False):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            key = f"verification_photo_{step}_emoji"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(BACK_BTN)
            # Internal implementation note: legacy behavior is preserved during modernization.
            used = [self.state[chat_id].get("verification_photo_1_emoji"), self.state[chat_id].get("verification_photo_2_emoji")]
            emoji_options = [e for e in list(HAND_VERFIY.keys()) if e not in used]
            emoji = random.choice(emoji_options)
            self.state[chat_id][key] = emoji

            # Internal implementation note: legacy behavior is preserved during modernization.
            text = (
                f"یک عکس سلفی با علامت {emoji} بفرستین"
                if step == 1 else
                f"یک عکس سلفی با علامت {emoji} متفاوت با قبلی بفرستین"
            )
            if retry:
                text = f"⏰ زمان شما به پایان رسید!\n{text}"

            # Internal implementation note: legacy behavior is preserved during modernization.
            emoji_code = HAND_VERFIY.get(emoji)
            image_path = rf"{IMAGES_DIR}/{emoji_code}.jpg"

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                with open(image_path, "rb") as img:
                    sent_msg = self.bot.send_photo(chat_id, img, caption=text , reply_markup=markup)

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.state[chat_id][f"verification_photo_{step}_message_id"] = sent_msg.message_id
                self.state[chat_id][f"verification_photo_{step}_photo_path"] = image_path

            except Exception as e:
                self.log.exception(f"[EDU_IMAGE] Could not send image for {emoji}: {e}")
                sent_msg = self.bot.send_message(chat_id, text, reply_markup=markup)
                self.state[chat_id][f"verification_photo_{step}_message_id"] = sent_msg.message_id
                self.state[chat_id][f"verification_photo_{step}_photo_path"] = None

            # Internal implementation note: legacy behavior is preserved during modernization.
            timer = threading.Timer(VERIFICATION_PHOTO_TIMEOUT, self._verification_photo_timeout, args=(chat_id, step, message))
            self.state[chat_id][f"verification_photo_{step}_timer"] = timer
            timer.start()

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.register_next_step_handler(message, lambda m, s=step: self._handle_verification_photo(m, s))

        except Exception as exc:
            self.log.exception(f"[REQ_VERIFICATION_PHOTO] failed: {exc}")
            
    def _verification_photo_timeout(self, chat_id: int, step: int, origin_msg):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            self.log.info(f"[TIMEOUT] chat={chat_id} step={step}")

            prev_msg_id = self.state[chat_id].get(f"verification_photo_{step}_message_id")
            prev_photo_path = self.state[chat_id].get(f"verification_photo_{step}_photo_path")

            # Internal implementation note: legacy behavior is preserved during modernization.
            used = [self.state[chat_id].get("verification_photo_1_emoji"), self.state[chat_id].get("verification_photo_2_emoji")]
            emoji_options = [e for e in list(HAND_VERFIY.keys()) if e not in used]
            if not emoji_options:
                emoji_options = list(HAND_VERFIY.keys())  # fallback
            new_emoji = random.choice(emoji_options)
            self.state[chat_id][f"verification_photo_{step}_emoji"] = new_emoji

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                msg = self.bot.forward_message(chat_id, chat_id, prev_msg_id)
                current_caption = msg.caption or ""
            except Exception as e:
                self.log.warning(f"[TIMEOUT] failed to fetch caption of message_id={prev_msg_id}: {e}")
                current_caption = "⏰ زمان شما به پایان رسید! لطفا عکس جدید ارسال کنید."

            # Internal implementation note: legacy behavior is preserved during modernization.
            for old in HAND_VERFIY.keys():
                if old in current_caption:
                    new_caption = current_caption.replace(old, new_emoji)
                    break
            else:
                new_caption = current_caption + f" {new_emoji}"

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=prev_msg_id,
                    caption=new_caption
                )
                self.log.info(f"[TIMEOUT] Caption updated with new emoji: {new_emoji}")
            except Exception:
                self.log.warning(f"[TIMEOUT] failed to edit caption, sending new message...")

                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    self.bot.delete_message(chat_id, prev_msg_id)
                except:
                    self.log.warning(f"[TIMEOUT] failed to delete old message")

                # Internal implementation note: legacy behavior is preserved during modernization.
                if prev_photo_path:
                    with open(prev_photo_path, "rb") as img:
                        sent = self.bot.send_photo(chat_id, img, caption=new_caption)
                    self.state[chat_id][f"verification_photo_{step}_message_id"] = sent.message_id
                else:
                    sent = self.bot.send_message(chat_id, new_caption)
                    self.state[chat_id][f"verification_photo_{step}_message_id"] = sent.message_id

            # Internal implementation note: legacy behavior is preserved during modernization.
            fake_msg = types.Message()
            fake_msg.chat = origin_msg.chat
            fake_msg.from_user = origin_msg.from_user
            self._request_verification_photo(fake_msg, step=step, retry=True)

        except Exception as exc:
            self.log.exception(f"[TIMEOUT_HANDLER] failed: {exc}")


    def _handle_verification_photo(self, message, step: int):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
                    # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return

            
            timer_key = f"verification_photo_{step}_timer"
            if timer_key in self.state[chat_id]:
                self.state[chat_id][timer_key].cancel()  # Internal implementation note: legacy behavior is preserved during modernization.

            if not message.photo:
                self.bot.send_message(chat_id, "❌ لطفاً یک عکس معتبر ارسال کنید.")
                return self._request_verification_photo(message, step=step)

            # Internal implementation note: legacy behavior is preserved during modernization.
            forwarded = self.bot.forward_message(self.storage_channel, chat_id, message.message_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            file_id = forwarded.photo[-1].file_id if forwarded.photo else ""
            self.state[chat_id][f"verification_photo_{step}_file_id"] = file_id
            self.state[chat_id]["step"] = f"get_verification_photo_{step}"

            if step == 1:
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self._request_verification_photo(message, step=2)
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                return self._ask_time(message)
        except Exception as exc:
            self.log.exception(f"[HANDLE_VERIFICATION_PHOTO] failed: {exc}")
            self._request_verification_photo(message, step=step)

    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _ask_time(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            self.bot.send_message(chat_id, "لطفا ساعت درخواستی خود را وارد کنید:")
            self.bot.register_next_step_handler(message, self._handle_time)
        except Exception as exc:
            self.log.exception(f"[ASK_TIME] failed: {exc}")

    def _handle_time(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
                    # Internal implementation note: legacy behavior is preserved during modernization.
            if self.is_back(message):
                return

            
            request_time = (message.text or "").strip()
            self.state[chat_id]["request_time"] = request_time
            self.state[chat_id]["step"] = "get_time"
            
            self._finalize(message)
        except Exception as exc:
            self.log.exception(f"[HANDLE_TIME] failed: {exc}")
            self._ask_time(message)

    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _finalize(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = message.chat.id
            data = self.state.get(chat_id, {})

            record = {
                "name": message.from_user.first_name,
                "telegram_id": message.from_user.id,
                "username": message.from_user.username,
                "staff_code": data.get("staff_code"),
                "region": data.get("region"),
                "phone": data.get("phone"),
                "verification_photo_1_emoji": data.get("verification_photo_1_emoji"),
                "verification_photo_1_file_id": data.get("verification_photo_1_file_id"),
                "verification_photo_2_emoji": data.get("verification_photo_2_emoji"),
                "verification_photo_2_file_id": data.get("verification_photo_2_file_id"),
                "status": "pending",
                "request_time": data.get("request_time"),
            }
            self.db.execute_query("ALTER TABLE request_drafts MODIFY COLUMN rejection_reason JSON;")
            self.db.insert(table_name="request_drafts", data=record, column_types={"telegram_id": "varchar(50)" , "rejection_reason":"JSON"})
            self.log.info(f"[SAVE] request_drafts record inserted for chat {chat_id}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            final_text = (
                "سفارش شما با موفقیت ثبت شد. نتیجه نهایی از طریق همین بات برای شما ارسال خواهد شد.\n\n"
                "▪️در صورت وارد کردن اطلاعات نادرست، درخواست شما رد می‌شود.\n"
                "▪️ در صورت نهایی شدن سفارش و تأیید درخواست، کد مورد نظر با شما تماس خواهد گرفت؛ لطفاً به گوشی خود دقت داشته باشید."
            )
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("از درخواست خود منصرف شدم 🚫")
            self.bot.send_message(chat_id, final_text, reply_markup=markup)

            # Internal implementation note: legacy behavior is preserved during modernization.
            name = record["name"]
            username = record.get("username") or "—"
            telegram_id = record["telegram_id"]
            staff_code = record.get("staff_code") or "—"
            request_time = record.get("request_time") or "—"

            self.message_to_admin(
                "📥 سفارش جدید ثبت شد:\n\n"
                "👤 نام: " + name + "\n"
                "🔗 یوزرنیم: @" + username + "\n"
                "🆔 آیدی عددی: " + str(telegram_id) + "\n"
                "🧾 کد ارائه‌دهنده: " + staff_code + "\n"
                "🕒 ساعت درخواستی: " + request_time
            )


            # Internal implementation note: legacy behavior is preserved during modernization.
            self._reset_user(chat_id)

        except Exception as exc:
            self.log.exception(f"[FINALIZE] failed: {exc}")
            self.bot.send_message(chat_id, "❌ خطایی رخ داد. لطفاً بعداً دوباره تلاش کنید.")

            
    def message_to_admin(self, text: str):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            admins = self.get_admins()
            if not admins:
                self.log.warning("[ADMIN_MSG] No eligible admins to notify.")
                return

            for admin in admins:
                try:
                    self.admin_bot.send_message(admin["telegram_id"], text)
                    self.log.info(f"[ADMIN_MSG] Message sent to admin ID={admin['telegram_id']}")
                except Exception as send_exc:
                    self.log.error(f"[ADMIN_MSG] Failed to send to admin ID={admin['telegram_id']}: {send_exc}")

        except Exception as exc:
            self.log.exception(f"[ADMIN_MSG] Unexpected failure in admin messaging: {exc}")

    def get_admins(self):
        """Legacy-compatible behavior preserved for this callable."""
        import json
        try:
            admins = self.db.select_dict("admins")
            filtered_admins = []

            if admins:
                for admin in admins:
                    try:
                        permissions = json.loads(admin.get("permissions", "{}"))
                        if permissions.get("manage_requests"):
                            filtered_admins.append(admin)
                    except json.JSONDecodeError as json_err:
                        self.log.warning(f"[ADMIN-PERMISSIONS] Invalid JSON for admin ID={admin.get('id')}: {json_err}")

            return filtered_admins

        except Exception as exc:
            self.log.exception(f"[GET_ADMINS] Failed to fetch admins: {exc}")
            return []

    # -----------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # -----------------------------
    def _reset_user(self, chat_id):
        """Legacy-compatible behavior preserved for this callable."""
        self.state[chat_id] = {}

    def _is_active_today(self, staff_code: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()
            rows = self.db.select_dict(
                "today_codes", "code = ? AND date = ?", (staff_code, today)
            )
            return bool(rows)
        except Exception as exc:
            self.log.exception(f"[CHECK_ACTIVE] failed: {exc}")
            return False

    def _is_dispatch(self, staff_code: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            rows = self.db.select_dict(
                "staff", "U_code = ?", (staff_code,)
            )
            if rows:
                return rows[0].get("dispatch_mode") == "اعزام"
            return False
        except Exception as exc:
            self.log.exception(f"[CHECK_DISPATCH] failed: {exc}")
            return False
        
    def run(self):
        self.bot.polling(none_stop=True)

def start_client_bot():
    """Legacy-compatible behavior preserved for this callable."""
    # Internal implementation note: legacy behavior is preserved during modernization.
    db = DatabaseManager(**DB_PARAMS)  # **DB_PARAMS)
    log.info("Initializing ClientBot...")

    # Internal implementation note: legacy behavior is preserved during modernization.
    main_menu = SimpleClientRunner(LocalizedTeleBot(BOT_CLIENT_TOKEN), db)
    log.info("Client Bot running started ...")

    # Internal implementation note: legacy behavior is preserved during modernization.
    main_menu.run()
    log.warning("Client Bot running stopped ...")


if __name__ == "__main__":
    # Internal implementation note: legacy behavior is preserved during modernization.
    start_client_bot()
