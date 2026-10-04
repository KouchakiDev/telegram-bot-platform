import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, '..'))
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.handlers.client.to_day_cods import TodayCodesFilterHandler
from telegram_bot_platform.compat.handlers.client.ads_handler import AdsHandler
from telegram_bot_platform.compat.handlers.client.show_staff_profile import StaffProfileHandler
from telegram_bot_platform.compat.handlers.client.see_requests_results import SeeRequestsHandler
from telegram_bot_platform.compat.handlers.client.booking_flow import Reserve_manager
from telegram_bot_platform.compat.handlers.client.premium_manager import PREMIUMManager
import threading
import uuid
import time
from telebot.types import CallbackQuery, Message, Chat, User
from telegram_bot_platform.compat.handlers.client.filter import FilterHandler
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.
from telebot.types import (
    CallbackQuery,
    
)
import re
from telegram_bot_platform.compat.runners.starter import Starter       # Internal implementation note: legacy behavior is preserved during modernization.
       # Internal implementation note: legacy behavior is preserved during modernization.

import threading
import time
import random
from telebot import types
import telebot
import json
from datetime import datetime, timedelta   # Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.


# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.


# Client Handlers

# Database Manager

# Logger


log = CustomLogger()  # log_file="C_bot.log")


class ClientBot:
    def __init__(self, token, db: DatabaseManager):
        log.info("Bot inishilayz started ...")
        self.bot = telebot.TeleBot(token)
        self.db = db
        self.see_Rr = SeeRequestsHandler(self.bot, self.db)
        self.premium = PREMIUMManager(
            self.bot, self.db, self.send_welcome, self.handle_start_message,  self.see_Rr)
        self.ads = AdsHandler(self.bot, self.db)
        self.today = TodayCodesFilterHandler(
            self.bot, self.db, self.send_welcome, self.send_welcome,  self.handle_start_message)
        self.ads.register_handlers()
        self.filter_handler = FilterHandler(self.bot, self.db)

        self.staff_profile = StaffProfileHandler(self.bot, self.db)
        log.info("Bot inishilayz Completed !")
        self.bookings = Reserve_manager(
            self.bot, self.db, self.send_welcome, self.handle_start_message)
        self.add_favorits_for_normal_users = False
        self.setup_handlers()
        self.starter = Starter(self.db, self.bot, welcome_cb=self.send_welcome)
        self.starter.broadcast_fake_message_to_all()

        
    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        text = message.text or ''
        if text == BUTTONS["back_to_main_menu"]:
            self.send_welcome(message)
            return True
        if text.startswith("/start"):
            self.starter.store_user_info(message)           # Internal implementation note: legacy behavior is preserved during modernization.
            
            self.handle_start_message(message)
            return True
        if text == BUTTONS["back_to_pervious_menu"]:
            try:
                self.send_welcome(message)
            except:
                self.send_welcome(message)
            return True
        return False

    def send_welcome(self, message,Reset_pannel:bool=False):
        chat_id = message.chat.id
        user_id = message.from_user.id
        self.user_do_that(message, "started the bot")
        count = ""

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not Reset_pannel:
            try:
                if self.db.table_exists("premium_clients"):
                    results = self.db.select_dict(
                        "premium_clients", "telegram_id = ? AND C_status = 'approved'", (user_id,)
                    )
                    if results:
                        self.user_do_that(message, "has a PREMIUM membership")
                        self.bot.send_message(
                            chat_id,
                            MESSAGES.get("premium_panel_welcome", "🎉 به پنل PREMIUM خوش آمدید."),
                            reply_markup=None,
                        )
                        self.premium.premium_menu.show_panel(message)
                        return
            except Exception as e:
                log.warning(f"[send_welcome] PREMIUM check failed: {e}")
            try:
                count = self.see_Rr.counter_of_requests_results(message)
            except Exception as e:
                log.warning(f"[send_welcome] request count failed: {e}")
                count = ""

        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        # Internal implementation note: legacy behavior is preserved during modernization.

        label = BUTTONS.get("see_requests", "📄 درخواست‌ها")
        suffix = f" ({count})" if count else ""

        markup.add(
            types.KeyboardButton(BUTTONS.get("today_codes", "📅 کدهای امروز")),
            types.KeyboardButton(f"{label}{suffix}"),
            types.KeyboardButton(BUTTONS.get("premium_login", "💎 ورود PREMIUM")),
        )

        try:
            self.bot.send_message(
                chat_id,
                MESSAGES.get("start_menu", "🎯 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"),
                reply_markup=markup
            )
        except Exception as e:
            log.error(f"[send_welcome] failed to send welcome message: {e}")

    def user_do_that(self, message, that):
        log.info(
            f"user {message.from_user.id}  {that}")

    def show_available_codes(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        self.bot.send_message(chat_id, MESSAGES['slot_already_reserved'])
        # Internal implementation note: legacy behavior is preserved during modernization.
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        # Internal implementation note: legacy behavior is preserved during modernization.
        live_rows = self.db.select_dict(
            "live_ads",
            "created_at >= ? AND created_at < ?",
            (today, tomorrow)
        ) or []

        # Internal implementation note: legacy behavior is preserved during modernization.
        available_ad_ids = []
        for row in live_rows:
            try:
                slots = json.loads(row.get("time_slots", "{}"))
            except Exception:
                slots = {}
            if any(slots.values()):
                available_ad_ids.append(row["ad_id"])

        if not available_ad_ids:
            self.bot.send_message(
                chat_id, "📭 امروز هیچ آگهیِ دارای زمان آزاد وجود ندارد.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        ph = ",".join("?" * len(available_ad_ids))
        ads_rows = self.db.select_dict(
            "ads",
            f"id IN ({ph}) AND status = 'approved'",
            tuple(available_ad_ids)
        ) or []

        codes = list({row["U_code"] for row in ads_rows})
        if not codes:
            self.bot.send_message(
                chat_id, "📭 هیچ کد پرسنلی برای نمایش وجود ندارد.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.today.user_state[chat_id] = {
            "filters": {},
            "codes": codes,
            "page": 1,
            "msg_id": None,
            "premium": False,
            "city": None,
            "province": None,
        }
        self.today._show_codes_page(chat_id)

    def handle_start_message(self, message):
        chat_id = message.chat.id
        args = message.text.split()
        if len(args) > 1:
            param = args[1]
            regexp = r'^p\d+$'
            if re.match(regexp , param):
                message.text = f"/{param}"
                self.staff_profile.handle_staff_profile(message)
            elif param.startswith("book"):
                self.bookings.show_main_menu(message, param)
                return
            elif param == "ShowAvalabelCodes":   # Internal implementation note: legacy behavior is preserved during modernization.
                self.show_available_codes(message)
                return

            elif param.startswith("gallery_"):
                u_code = args[1].replace("gallery_", "")
                rows = self.db.select_dict(
                    "staff", "U_code = ?", (u_code,))
                if rows:
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
                    photos = photo_ids
                    if not photos:
                        self.bot.send_message(
                            message.chat.id, "📭 این پرسنل هیچ عکس اضافی‌ای ندارد.")
                    else:
                        
                        try:
                            amount = random.randint(1, 3)
                            random.shuffle(photos)
                            selected_photos = photos[:amount]

                            media = [
                                types.InputMediaPhoto(photo, has_spoiler=True)
                                for photo in selected_photos
                            ]

                            # Internal implementation note: legacy behavior is preserved during modernization.
                            messages = self.bot.send_media_group(message.chat.id, media)

                            # Internal implementation note: legacy behavior is preserved during modernization.
                            def delete_spoiler_group():
                                for msg in messages:
                                    try:
                                        self.bot.delete_message(message.chat.id, msg.message_id)
                                    except Exception as e:
                                        log.warning(f"[gallery] failed to delete msg: {e}")

                            # Internal implementation note: legacy behavior is preserved during modernization.
                            total_delay = amount * DURATION_TIME
                            threading.Timer(total_delay, delete_spoiler_group).start()

                        except Exception as e:
                            log.error(f"[gallery] failed to send spoiler gallery: {e}")
                            self.bot.send_message(message.chat.id, "❌ خطا در ارسال عکس‌ها.")
                else:
                    self.bot.send_message(message.chat.id, "❌ پرسنل یافت نشد.")
                return
        else:
            c_premium = self.db.table_exists("premium_clients")
            if c_premium:
                results = self.db.select_dict(
                    "premium_clients",  "telegram_id = ? AND C_status = 'approved'", (chat_id,))
                print(results)
                if results:
                    result = results[0]
                    print(result)
                    self.user_do_that(message, f"has a Premium member!")
                    self.bot.send_message(
                        chat_id, MESSAGES["premium_panel_welcome"], reply_markup=None)
                    self.premium.premium_menu.show_panel(message)
                    return
                else:
                    self.send_welcome(message)
            else:
                self.send_welcome(message)  #
      
    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            # self.bot.send_photo(message.chat.id,"DQACAgQAAxkBAAIw5Wf-TSZMZOvd9Skm3GdPs8aZVup7AAKMGAACic0IU6EEafenjrJNNgQ","test")
            self.starter.store_user_info(message)          # Internal implementation note: legacy behavior is preserved during modernization.

            print("start")
            self.handle_start_message(message)

        @self.bot.message_handler(regexp=r'^/p\d+$')
        def _handle_staff_command(message):
            """Legacy-compatible behavior preserved for this callable."""
            self.staff_profile.handle_staff_profile(message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_my_callback(call: CallbackQuery):
            try:

                param = call.data  # Internal implementation note: legacy behavior is preserved during modernization.
                user_id = call.from_user.id

                # Internal implementation note: legacy behavior is preserved during modernization.
                if param.startswith("AddToFavorits"):
                    fp_u_code = param.split("_")[1]

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    is_premium_Client = self.db.select_dict(
                        "premium_clients",
                        "telegram_id = ? AND C_status = 'approved'",
                        (user_id,)
                    )

                    if is_premium_Client:
                        premium_row = is_premium_Client[0]
                        current_favs = premium_row.get("favorite_codes") or []

                        if isinstance(current_favs, str):
                            try:
                                current_favs = json.loads(current_favs)
                            except:
                                current_favs = []

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        if fp_u_code in current_favs:
                            self.bot.answer_callback_query(
                                call.id, text="این مورد در حال حاضر هم در لیست علاقه‌مندی‌های شماست ⭐", show_alert=True)
                            return

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        current_favs.append(fp_u_code)
                        self.db.update(
                            "premium_clients",
                            {"favorite_codes": json.dumps(current_favs)},
                            "telegram_id = ?",
                            (user_id,)
                        )
                        self.bot.answer_callback_query(
                            call.id, text=f"کد {fp_u_code} به لیست علاقه‌مندی‌های شما اضافه شد ⭐", show_alert=True)
                        return

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    elif self.add_favorits_for_normal_users:
                        fav_data = [fp_u_code]

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        existing = self.db.select_dict(
                            "clients", "telegram_id = ?", (user_id,))
                        if existing:
                            current_favs = existing[0].get(
                                "favorite_codes") or []
                            if isinstance(current_favs, str):
                                try:
                                    current_favs = json.loads(current_favs)
                                except:
                                    current_favs = []

                            if fp_u_code in current_favs:
                                self.bot.answer_callback_query(
                                    call.id, text="این کد قبلاً در لیست علاقه‌مندی‌های شما بوده ⭐", show_alert=True)
                                return

                            fav_data = current_favs + [fp_u_code]

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        data = {
                            "telegram_id": user_id,
                            "U_code": f"c{self.db.count_rows("clients") + 1}",
                            "favorite_codes": json.dumps(fav_data)
                        }
                        if call.from_user.username:
                            data["username"] = call.from_user.username

                        self.db.upsert("clients", data, "telegram_id", {
                            "telegram_id": "INTEGER UNIQUE",
                            "U_code": "TEXT UNIQUE",
                        })
                        self.bot.answer_callback_query(
                            call.id, text=f"کد {fp_u_code} به لیست علاقه‌مندی‌های شما اضافه شد ⭐", show_alert=True)
                        return

                    else:
                        self.bot.answer_callback_query(
                            call.id, text="❌ این قابلیت فقط برای مشتریان ویژه فعال است", show_alert=True)
                        return
                elif param.startswith("book"):
                    try:
                        print(call.data)
                        # self.bot.answer_callback_query(call.id)
                        data = call.data  # Internal implementation note: legacy behavior is preserved during modernization.
                        parts = data.split("_")
                        ad_id = parts[2]
                        slot = parts[3] + ":" + parts[4]

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        fake_message = call.message
                        fake_message.from_user = call.from_user
                        fake_message.chat = call.message.chat
                        fake_message.text = f"/start reserve_ads_{ad_id}_{slot}"

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        self.bookings.show_main_menu(
                            fake_message, call.data)

                    except Exception as e:
                        print("❌ Booking error:", e)
                        self.bot.answer_callback_query(
                            call.id, text="خطایی رخ داد.", show_alert=True)

                elif param.startswith("premium_fav_profile_"):
                    chat_id = call.message.chat.id
                    try:
                        print(call.data)
                        # self.bot.answer_callback_query(call.id)
                        data = call.data  # Internal implementation note: legacy behavior is preserved during modernization.
                        code = call.data.replace("premium_fav_profile_", "")
                    # chat_id = call.message.chat.id

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        fake_message = call.message
                        fake_message.from_user = call.from_user
                        fake_message.chat = call.message.chat
                        fake_message.text = f"/{code}"
                        self.staff_profile.handle_staff_profile(fake_message)

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        # self.bookings.show_main_menu(
                        #     fake_message, call.data)

                    except Exception as e:
                        print("❌ Booking error:", e)
                        self.bot.answer_callback_query(
                            call.id, text="خطایی رخ داد.", show_alert=True)
                    # code = call.data.replace("premium_fav_profile_", "")

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # rows = self.db.select_dict(
                    #     "staff", "U_code = ?", (code,))
                    # if not rows:
                    #     self.bot.answer_callback_query(
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    #     return
                    # log.debug(rows)
                    # profile = rows[0]
                    # person = rows[0]
                    # caption = self.staff_profile.build_staff_caption(
                    #     person)
                    # log.debug(caption)

                    # try:
                    #     profile_photos = json.loads(profile.get('profile_photos', '[]'))
                    # except Exception:
                    #     profile_photos = []

                    # try:
                    #     gallery_photos = json.loads(profile.get('gallery_photos', '[]'))
                    # except Exception:
                    #     gallery_photos = []

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # # main_photo = profile.get('profile_photo')

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # photo_ids = []
                    # photo_ids.extend(profile_photos)
                    # photo_ids.extend(gallery_photos)

        

                    # photo_id = profile.get('profile_photo',random.choice(photo_ids))
                    # log.debug(photo_id)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # markup = types.InlineKeyboardMarkup()
                    # markup.add(
                    #     types.InlineKeyboardButton(
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    #         callback_data=f"premium_fav_today_ads_{code}"
                    #     )
                    # )

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # if photo_id and isinstance(photo_id, str) and not photo_id.startswith("http") and len(photo_id) > 10:
                    #     try:
                    #         self.bot.send_photo(
                    #             chat_id, photo_id, caption=caption, reply_markup=markup, parse_mode="HTML")
                    #     except Exception as e:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    #         self.bot.send_message(
                    #             chat_id, caption, reply_markup=markup, parse_mode="HTML")
                    # else:
                    #     self.bot.send_message(
                    #         chat_id, caption, reply_markup=markup, parse_mode="HTML")
                    def send_choice_option():
                        """Legacy-compatible behavior preserved for this callable."""
                        try:
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            rows = self.db.select_dict(
                                "filters",
                                "telegram_id = ?",
                                (chat_id,)
                            )
                            if not rows:
                                log.warning(f"[Filters] No snapshot found for chat {chat_id}")
                                return False

                            row = rows[0]
                            snapshot_id = row.get("snapshot_id")
                            msg_id = row.get("msg_id", 0)

                            # Internal implementation note: legacy behavior is preserved during modernization.
                            # fake_chat = Chat(id=chat_id, type="private")
                            # fake_user = User(id=0, first_name="System", is_bot=True)
                            # fake_msg = Message(
                            #     message_id=msg_id,
                            #     from_user=fake_user,
                            #     date=int(time.time()),
                            #     chat=fake_chat,
                            #     content_type="text",
                            #     options={},
                            #     json_string={}
                            # )
                            # fake_callback = CallbackQuery(
                            #     id=str(uuid.uuid4()),
                            #     from_user=fake_user,
                            #     chat_instance="",
                            #     data=,
                            #     message=fake_msg
                            # )
                            call.data = f"Actives|{snapshot_id}"
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            self.filter_handler._send_filtered_codes(call)
                            return True

                        except Exception as e:
                            log.exception(f"[Filters] resend_last_codes_list failed → {e}")
                            return False
                    # total_delay = amount * DURATION_TIME
                    threading.Timer(3, send_choice_option).start()
                elif param.startswith("premium_fav_today_ads_"):
                    try:
                        chat_id = user_id
                        code = param.replace("premium_fav_today_ads_", "")
                        self.ads.handle_show_ads_for_ucode(call.message, code)
                        log.info(f"[PREMIUMAds] Showing PREMIUM ads for code: {code} to user {chat_id}.")

                        
                            # if not rows:
                            #     log.warning(f"[Filters] No previous list for user {chat_id}")
                            # Internal implementation note: legacy behavior is preserved during modernization.

                            # msg_id = rows[0].get("msg_id")
                            # if not msg_id:
                            #     log.warning(f"[Filters] Row has no msg_id for user {chat_id}")
                            #     return False

                            # Internal implementation note: legacy behavior is preserved during modernization.
                            # self.bot.copy_message(chat_id, chat_id, msg_id)
                            # log.debug(f"[Filters] Resent codes list msg_id={msg_id} to {chat_id}")
                            # return True
                            

                    except Exception as e:
                        log.exception(f"[PREMIUMAds] Error handling PREMIUM favorite today ads for code={code} user={chat_id}: {e}")


                elif param.startswith('filter_search'):
                    self.filter_handler.start_filtering(call)
                    return
                elif param.startswith("filter_") or param.startswith("field_") or param.startswith("select_") or param.startswith("toggle_") or param.startswith("Actives") or param == "apply_filters":
                    print(param)
                    self.filter_handler.callback_query(call)
                    return

            except Exception as e:
                log.error(f"❌ خطا در handle_my_callback → {e}")
                try:
                    self.bot.answer_callback_query(
                        call.id, text="🚫 خطایی رخ داد. لطفاً دوباره تلاش کنید.", show_alert=True)
                except:
                    pass  # Internal implementation note: legacy behavior is preserved during modernization.

        @self.bot.message_handler(func=lambda m: True)
        def handle_menu_selection(message):
            text = message.text

            if text.endswith(')') and '(' in text:
                text = text[:text.rfind('(')].strip()
            if self.is_back(message):
                return
            elif text == BUTTONS["see_requests"]:
                self.user_do_that(
                    message, f"Choice << see_requests >> Menu")
                self.see_Rr.handle(message)
            elif text == BUTTONS["today_codes"]:
                self.user_do_that(message, f"Choice << today_codes >> Menu")
                self.today._start(message)

            elif text == BUTTONS["premium_login"]:
                self.user_do_that(message, f"Choice << premium_login >> Menu")

                self.premium.show_main_menu(message)
            elif text in BUTTONS.values():
                self.send_welcome(message)

            else:
                self.user_do_that(message, f"Entered  ({text}) invalid Choice")

                self.bot.send_message(
                    message.chat.id, MESSAGES["invalid_option"])
                self.send_welcome(message)

    def run(self):
        self.bot.polling(none_stop=True)


# -*- coding: utf-8 -*-
"""
ماژول اصلی مدیریت منوی ربات تلگرام
تمام رشته‌های ثابت در telegram_bot_platform.compat.config.settings قرار گرفته‌اند.
"""


# Internal implementation note: legacy behavior is preserved during modernization.
# log = CustomLogger("main")


def start_client_bot():
    """Legacy-compatible behavior preserved for this callable."""
    # Internal implementation note: legacy behavior is preserved during modernization.
    db = DatabaseManager(**DB_PARAMS)  # **DB_PARAMS)
    log.info("Initializing ClientBot...")

    # Internal implementation note: legacy behavior is preserved during modernization.
    main_menu = ClientBot(BOT_CLIENT_TOKEN, db)
    log.info("Client Bot running started ...")

    # Internal implementation note: legacy behavior is preserved during modernization.
    main_menu.run()
    log.warning("Client Bot running stopped ...")


if __name__ == "__main__":
    # Internal implementation note: legacy behavior is preserved during modernization.
    start_client_bot()
