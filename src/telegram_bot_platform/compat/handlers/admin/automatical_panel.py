import time
import threading
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telegram_bot_platform.compat.config.settings import *
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from datetime import  time
import json
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.utils.task_manager import ThreadManager
from datetime import datetime, timedelta
from time import sleep
from telegram_bot_platform.compat.utils.media_recovery import MediaRecoveryManager
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot_platform.compat.config.settings import CHANNEL_ID , CLIENT_BOT_ID
import random
from typing import Dict, List, Optional ,Callable

# Internal implementation note: legacy behavior is preserved during modernization.
log = CustomLogger(AUTO_CONFIG["log_file"])

CLIENT_BOT_NUMERIC_ID = None
class AutomaticalPanel:
    def __init__(self,bots:Dict[str, telebot.TeleBot] , bot: telebot.TeleBot, db: DatabaseManager, back_to_main, back_to_settings,backup, T_M: ThreadManager = ThreadManager() ):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.bots = bots
        cust_bot = self.bots["client"]
        self.db = db
        self.T_M = T_M
        self.backup = backup
        self.back_to_main = back_to_main
        self.back_to_settings = back_to_settings
        self.mediaReoverer = MediaRecoveryManager(self.db,self.bot ,STORAGE_CHANNEL)
        self.db_lock = threading.Lock()  # Internal implementation note: legacy behavior is preserved during modernization.
        self.notified_request_ids = set()
        self._nightly_timer = None
        self.log = log
        self.settings = REQUEST_SETTINGS
        CLIENT_BOT_NUMERIC_ID = cust_bot.get_me().id  # Internal implementation note: legacy behavior is preserved during modernization.
        
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.expirable_tables = EXPIRE_ABLE_TABLE
        self.backup_sended = False
                # Internal implementation note: legacy behavior is preserved during modernization.
        self.last_publish_date = None
        self._schedule_nightly_publish()                
        self.T_M.add_task(
            self.periodic_notify_admins,
            1,
            "Admin Notifications ALARM")
        
        self.T_M.add_task(
            self.post_random_promo,
            5,
            "auto channel promo"
        )

            # Internal implementation note: legacy behavior is preserved during modernization.
        self.T_M.add_task(
            self.post_random_promo,
            6,
            "auto bot promo"
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        with self.db_lock:
            self.db.create_auto_settings_table()
            global_settings = self.db.get_auto_settings("global")
            if not global_settings:
                self.db.set_auto_settings(
                    "global", {"auto_check_interval": AUTO_CONFIG["default_auto_check_interval"]})
    
    
    def _reschedule_promo_tasks(self, dest: str, minutes: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        if dest == "کانال":
            task_name = "auto channel promo"
        else:
            task_name = "auto bot promo"

        # Internal implementation note: legacy behavior is preserved during modernization.
        if hasattr(self.T_M, "update_task") and self.T_M.update_task(task_name, minutes):
            self.log.info("[Scheduler] Rescheduled %s → %d min", task_name, minutes)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.T_M.remove_task(task_name)
            except Exception:
                pass
            self.T_M.add_task(self.post_random_promo, minutes, task_name)
            self.log.info("[Scheduler] Re-created %s → %d min", task_name, minutes)
    # ---------------------------------------------
    #  AutomaticalPanel.post_random_promo  (FULL)
    
    # ---------------------------------------------
    
    def post_random_promo(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""

        # Internal implementation note: legacy behavior is preserved during modernization.
        photo_texts = [
            "📸 محتوای منتخب و معرفی‌های جدید را همین حالا ببینید.",
            "🔥 محتوای تصویری منتخب در دسترس است — همین حالا ببینید.",
            "👀 محتوای تصویری منتخب را در گالری ببینید.",
            "🕶📸 محتوای تصویری منتخب برای مرور سریع آماده است.",
            "🔥 برای مشاهدهٔ محتوای منتخب آماده‌اید؟",
            "✨ محتوای منتخب برای کاربران در دسترس است — بخش ویژه را ببینید.",
            "🚀📷 هر انتخاب یک محتوای جدید — بخش منتخب را بررسی کنید.",
            "🚀📸 مرور گالری منتخب ما رایگان است.",
        ]
        photo_button_texts = [
            "📸 مشاهده محتوا",
            "👀 مشاهده بیشتر",
            "📷 مشاهده رسانه‌ها",
            "🔥 مشاهده محتوای منتخب",
            "📸 مشاهده گالری",
            "✨ گالری ویژه",
            "📷 محتوای منتخب",
            "🖼 محتوای اختصاصی",
            "✨ محتوای عمومی و مناسب برای کاربران مجاز است",
            "🎞 مشاهده رسانه‌ها",
            "🔥 مشاهده پیشنهادهای ویژه",
            "🎯 مشاهده پیشنهادها",
            "📷 ورود به بخش ویژه",
            "🌟 گالری منتخب",
            "📸 مشاهده محتوای تصویری",
            "🎬 محتوای ویژه",
            "💫 مشاهده جزئیات",
            "👀 مجموعهٔ منتخب ما را ببینید",
        ]
        order_texts = [
            "💡 همین حالا یک خدمت مناسب را رزرو کنید.",
            "🔥 فرصت ویژه: سفارش خدمت سریع و آسان.",
            "🎯 همین حالا یکی از خدمات فعال را انتخاب کنید.",
            "⚡️ برای دریافت سریع خدمت، همین حالا سفارش ثبت کنید.",
            "✨ آماده‌اید خدمت موردنظر را رزرو کنید؟",
            "⚡️ ظرفیت محدود—همین الان ثبت سفارش کن!",
            "✅ گزینهٔ موردنظر شما آمادهٔ ثبت است.",
        ]
        order_button_texts = [
            "▶️ ثبت سفارش",
            "💳 ادامه پرداخت",
            "✅ ثبت سفارش",
            "📲 شروع سفارش",
            "🚀 شروع",
        ]

        # Internal implementation note: legacy behavior is preserved during modernization.
        

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            settings = self.db.select_dict("promo_settings", "id = ?", (1,))[0]
        except Exception as exc:
            self.log.exception("[AutoPromo] cannot read promo_settings: %s", exc)
            return

        now_ts = int(datetime.now().timestamp())

        # Internal implementation note: legacy behavior is preserved during modernization.
        send_to_channel = (
            settings.get("channel_enabled")
            and now_ts - int(settings.get("last_channel_promo_at", 0))
            >= int(settings.get("channel_interval", 180)) * 60
        )
        send_to_bot = (
            settings.get("bot_enabled")
            and now_ts - int(settings.get("last_bot_promo_at", 0))
            >= int(settings.get("bot_interval", 180)) * 60
        )
        if not send_to_channel and not send_to_bot:
            self.log.debug("[AutoPromo] nothing to send (interval/channel/bot disabled).")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            has_active_code = bool(self.db.select_dict("codes", "activity = 1"))
        except Exception as exc:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.log.warning(
                "[AutoPromo] codes table missing/unreadable, assuming no active code: %s",
                exc
            )
            has_active_code = False

        activity = "photo" if not has_active_code else random.choice(["photo", "order"])

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            texts = [
                r["content"]
                for r in self.db.select_dict(
                    "promo_texts",
                    "activity = ? AND kind = 'text'",
                    (activity,),
                )
            ]
            buttons = [
                r["content"]
                for r in self.db.select_dict(
                    "promo_texts",
                    "activity = ? AND kind = 'button'",
                    (activity,),
                )
            ]
        except Exception as exc:
            self.log.exception("[AutoPromo] DB error fetching promo_texts: %s", exc)
            texts, buttons = [], []

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not texts:
            if activity == "photo":
                texts = photo_texts.copy()
            elif activity == "order":
                texts = order_texts.copy()
        if not buttons:
            if activity == "photo":
                buttons = photo_button_texts.copy()
            elif activity == "order":
                buttons = order_button_texts.copy()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not texts or not buttons:
            self.log.warning("[AutoPromo] no promo texts/buttons even after fallback.")
            return

        text = random.choice(texts)
        btn_text = random.choice(buttons)
        url_map = {
            "photo": f"https://t.me/{CLIENT_BOT_ID}?start=play_photos",
            "order": f"https://t.me/{CLIENT_BOT_ID}?start=start",
            "codes": f"https://t.me/{CLIENT_BOT_ID}?start=code_keyboard",
        }
        url = url_map[activity]

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text=btn_text, url=url))

        # Internal implementation note: legacy behavior is preserved during modernization.
        if send_to_channel:
            try:
                prev_rows = self.db.select_dict(
                    "promo_channel_msgs", "activity = ?", (activity,)
                )
                if prev_rows:
                    old_mid = int(prev_rows[0]["msg_id"])
                    try:
                        self.bot.delete_message(CHANNEL_ID, old_mid)
                    except Exception:
                        pass  # Internal implementation note: legacy behavior is preserved during modernization.

                new_msg = self.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=text,
                    reply_markup=kb,
                    disable_web_page_preview=True,
                )
                self.db.upsert(
                    table_name="promo_channel_msgs",
                    data={
                        "activity": activity,
                        "msg_id": new_msg.message_id
                    },
                    key="activity",                               # Internal implementation note: legacy behavior is preserved during modernization.
                    column_types={
                        "activity": "VARCHAR(25) UNIQUE",    # Internal implementation note: legacy behavior is preserved during modernization.
                        "msg_id": "VARCHAR(50)"
                    },
                    unique_column="activity"                      # Internal implementation note: legacy behavior is preserved during modernization.
                )


                self.db.update(
                    "promo_settings", {"last_channel_promo_at": now_ts}, "id = ?", (1,)
                )
                self.log.info("[AutoPromo] promo sent to CHANNEL | act=%s", activity)
            except Exception as exc:
                self.log.exception("[AutoPromo] failed to send to channel: %s", exc)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if send_to_bot:
            cust_bot = self.bots["client"]
            try:
                user_rows = self.db.select_dict("users")
                targets = []
                for row in user_rows:
                    try:
                        bots = json.loads(row.get("bots", "[]"))
                        if CLIENT_BOT_NUMERIC_ID and CLIENT_BOT_NUMERIC_ID not in bots:
                            continue
                        chat_id = row.get("chat_id") or row.get("telegram_id")
                        if chat_id:
                            targets.append(chat_id)
                    except Exception:
                        continue

                success, failed = 0, 0
                for uid in targets:
                    try:
                        cust_bot.send_message(
                            chat_id=uid,
                            text=text,
                            reply_markup=kb,
                            disable_web_page_preview=True,
                        )
                        success += 1
                    except Exception:  # noqa: BLE001
                        failed += 1

                if success:
                    self.db.update(
                        "promo_settings", {"last_bot_promo_at": now_ts}, "id = ?", (1,)
                    )
                self.log.info("[AutoPromo] promo to BOT | ok=%d, fail=%d", success, failed)
            except Exception as exc:
                self.log.exception("[AutoPromo] failed bot broadcast: %s", exc)

    # ============================================#
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ============================================#
    
    def seconds_until(self, hour: int, minute: int = 0) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        seconds = int((target - now).total_seconds())
        log.debug(f"[schedule] Seconds until {hour:02}:{minute:02} → {seconds} seconds")
        return seconds

    def _schedule_nightly_publish(self):
        """Legacy-compatible behavior preserved for this callable."""
        if hasattr(self, "_nightly_timer") and self._nightly_timer is not None:
            if self._nightly_timer.is_alive():
                log.warning("[schedule] ⛔ Timer already set, skipping duplicate scheduling.")
                return

        delay = self.seconds_until(0, 1)  # Internal implementation note: legacy behavior is preserved during modernization.
        self._nightly_timer = threading.Timer(delay, self._run_nightly_publish)
        self._nightly_timer.daemon = True
        self._nightly_timer.start()

        hours, minutes = delay // 3600, (delay % 3600) // 60
        log.info(f"[schedule] ✅ Timer set → next publish in {hours}h {minutes}m")

        self.backup_sended = False
    
    def _run_nightly_publish(self):
        """Legacy-compatible behavior preserved for this callable."""
        # today = datetime.now().date()

        log.info("[Nightly] 🌙 Starting scheduled 00:01 process...")

        
        try:
            self.backup()
            log.info("[Nightly] ✅ Database backup completed.")
        except Exception as e:
            log.exception(f"[Nightly] ❌ Backup failed: {e}")
        try:
            self.mediaReoverer.run()
            log.info("[Nightly] ✅ Media file_id recovery completed.")
        except Exception as e:
            log.exception(f"[Nightly] ❌ Media recovery failed: {e}")
        
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update("codes", {"activity": False}, "activity = ?", (True,))
            log.info("[Nightly] 🔄 Reset all staff activity to False.")
        
            # Internal implementation note: legacy behavior is preserved during modernization.
            bios_rows = self.db.select_dict("bios", None)  # Internal implementation note: legacy behavior is preserved during modernization.
            deleted, failed = 0, 0
            
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                row = self.db.select_dict(
                    table="bot_meta",
                    condition="`key` = ?",
                    params=("codes_kb_msg_id",),
                )
                msg_id = int(row[0]["value"]) if row else None
            except Exception as exc:
                log.error("get_meta failed · key=%s · err=%s", "codes_kb_msg_id", exc, exc_info=True)
                msg_id = None
        
            # Internal implementation note: legacy behavior is preserved during modernization.
            if msg_id:
                try:
                    self.bot.delete_message(CHANNEL_ID, msg_id)
                    log.debug("Old codes keyboard cleared · msg_id=%s", msg_id)
                except Exception as exc:
                    log.warning("Clear keyboard failed · msg_id=%s · err=%s", msg_id, exc)
            
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.db.execute_query(
                    "UPDATE bot_meta SET value = ? WHERE `key` = ?",
                    params=("", "codes_kb_msg_id"),
                )
            except Exception as exc:
                log.error("set_meta failed · key=%s · err=%s", "codes_kb_msg_id", exc, exc_info=True)
        
            for bio in bios_rows:
                try:
                    self.bot.delete_message(
                        chat_id=bio["channel_id"],   # Internal implementation note: legacy behavior is preserved during modernization.
                        message_id=bio["message_id"]
                    )
                    deleted += 1
                    log.debug(
                        "[Nightly] 🗑 Deleted bio message "
                        f"(code={bio['code']}, msg_id={bio['message_id']})"
                    )
        
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.delete("bios", "code = ?", (bio["code"],))
        
                except Exception as del_err:
                    failed += 1
                    log.warning(
                        "[Nightly] ⚠️ Could NOT delete bio "
                        f"(code={bio['code']}, msg_id={bio['message_id']}): {del_err}"
                    )
            log.info(
                "[Nightly] 🧹 Bio clean-up finished · deleted=%s, failed=%s",
                deleted, failed
            )
        
        except Exception as e:
            log.exception("[Nightly] ❌ Failed to reset activity or clean bios: %s", e)
        

        try:
            with self.db_lock:
                rows = self.db.select_dict(
                    "staff_publish_queue",
                    "status = ?",
                    ("queued",)
                )
            log.debug(f"[publish_queue] ✅ {len(rows)} 'queued' rows fetched for processing.")

        except Exception as e:
            log.error(f"[publish_queue] ❌ Failed to fetch queued profiles: {e}")
            self._schedule_nightly_publish()
            return

        # Keep only the latest queue entry per staff_id
        latest_per_staff = {}
        for row in rows:
            pid = row["staff_id"]
            if pid not in latest_per_staff or row["id"] > latest_per_staff[pid]["id"]:
                latest_per_staff[pid] = row

        log.debug(f"[publish_queue] 🧮 Filtered to {len(latest_per_staff)} unique staff entries.")

        sent = 0

        for row in latest_per_staff.values():
            try:
                staff_id = row["staff_id"]
                queue_id = row["id"]
                log.debug(f"[publish_queue] 🔄 Processing queue_id={queue_id} for staff_id={staff_id}...")

                # Check if staff exists
                try:
                    result = self.db.select_dict("staff", "id = ?", (staff_id,))
                    if not result:
                        log.warning(f"[publish_queue] 🚫 Staff with ID {staff_id} not found. Marking as 'not_valid'.")
                        with self.db_lock:
                            self.db.update("staff_publish_queue", {"status": "not_valid"}, "id = ?", (queue_id,))
                        continue
                    log.debug(f"[publish_queue] ✅ Staff found: ID={staff_id}, Name={result[0].get('name')}")
                except Exception as e:
                    log.error(f"[publish_queue] ❗ Error while checking staff_id={staff_id}: {e}")
                    continue

                # Parse caption and photos
                caption = row.get("caption", "")
                try:
                    photos = json.loads(row.get("photos", "[]"))
                    log.debug(f"[publish_queue] 📸 Loaded {len(photos)} photos for queue_id={queue_id}.")
                except Exception as e:
                    log.error(f"[publish_queue] ❗ Failed to parse photo JSON for queue_id={queue_id}: {e}")
                    continue

                if not photos:
                    log.warning(f"[publish_queue] ⚠️ No photos available in queue_id={queue_id}. Skipping.")
                    continue

                # Build media group (up to 10 images)
                media = []
                for i, pid in enumerate(photos[:10]):
                    media.append(
                        telebot.types.InputMediaPhoto(
                            media=pid,
                            caption=caption if i == 0 else None,
                            parse_mode="HTML" if i == 0 else None,
                            has_spoiler=True
                        )
                    )
                log.debug(f"[publish_queue] 🖼 MediaGroup constructed for queue_id={queue_id}.")

                # Send to channel
                try:
                    self.bot.send_media_group(chat_id=CHANNEL_ID, media=media)
                    log.info(f"[publish_queue] ✅ Media group sent successfully (queue_id={queue_id}, staff_id={staff_id}).")

                    with self.db_lock:
                        self.db.update(
                            "staff_publish_queue",
                            {"status": "sent", "sent_at":datetime.now()},
                            "id = ?",
                            (queue_id,)
                        )
                    sent += 1

                except Exception as e:
                    log.error(f"[publish_queue] ❌ Failed to send media group for queue_id={queue_id}: {e}")

            except Exception as e:
                log.exception(f"[publish_queue] ❗ Unexpected error while processing queue_id={row.get('id')}: {e}")

        log.info(f"[PUBLISH @00:01] 📦 Nightly publishing completed. Total successful: {sent}")
        # self.last_publish_date = today
        self._schedule_nightly_publish()

    def _expire_old_requests(self):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        midnight_today = datetime.combine(datetime.now().date(), time.min)

        with self.db_lock:
            for table in self.expirable_tables:
                # Internal implementation note: legacy behavior is preserved during modernization.
                status_col   = self.settings[table]["status_column"]
                created_col  = self.settings[table].get("created_at_column", "created_at")

                # Internal implementation note: legacy behavior is preserved during modernization.
                old_reqs = self.db.select_dict(
                    table,
                    f"{status_col} = ? AND {created_col} < ?",
                    ("pending", midnight_today)
                )

                if not old_reqs:
                    continue

                ids = [r["id"] for r in old_reqs]
                placeholders = ",".join("?" * len(ids))

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.execute_query(
                    f"UPDATE {table} SET {status_col} = ? WHERE id IN ({placeholders})",
                    ("expired", *ids)
                )

                # Internal implementation note: legacy behavior is preserved during modernization.
                self.notified_request_ids.difference_update(ids)

                log.info(f"[expire_old_requests] {table}: {len(ids)} request(s) expired.")

    def periodic_notify_admins(self):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._expire_old_requests()
        
        # Internal implementation note: legacy behavior is preserved during modernization.
        total_pending = 0
        new_unnotified = []
        with self.db_lock:
            tables = self.settings.keys()
        pending_summary = {}
        for table in tables:
            with self.db_lock:
                status_column = self.settings[table]["status_column"]
                pending_requests = self.db.select_dict(
                    table, f"{status_column} = ?", ("pending",))
            count_pending = len(pending_requests)
            total_pending += count_pending
            # Internal implementation note: legacy behavior is preserved during modernization.
            new_requests = [
                req for req in pending_requests
                if req["id"] not in self.notified_request_ids
            ]
            if new_requests:
                pending_summary[table] = [req["id"]
                                          for req in new_requests]
                new_unnotified.extend(new_requests)
        log.info(
            f"[periodic_notify_admins] total_pending={total_pending}, new_unnotified={len(new_unnotified)}")
        if total_pending < 10:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if len(new_unnotified) > 0:
                self._notify_admins_with_summary(pending_summary)
                for req in new_unnotified:
                    self.notified_request_ids.add(req["id"])
            else:
                log.info(
                    "[periodic_notify_admins] Few total, but no new requests.")
        elif 10 <= total_pending < 50:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if len(new_unnotified) >= 10:
                self._notify_admins_with_summary(pending_summary)
                for req in new_unnotified:
                    self.notified_request_ids.add(req["id"])
            else:
                log.info(
                    "[periodic_notify_admins] Medium load, less than 10 new.")
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if len(new_unnotified) >= 20:
                self._notify_admins_with_summary(pending_summary)
                for req in new_unnotified:
                    self.notified_request_ids.add(req["id"])
            else:
                log.info(
                    "[periodic_notify_admins] High load, less than 20 new.")

   # Internal implementation note: legacy behavior is preserved during modernization.

    def _notify_admins_with_summary(self, pending_summary):
        """Legacy-compatible behavior preserved for this callable."""
        if not pending_summary:
            log.info("[_notify_admins_with_summary] No new requests to notify.")
            return
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        text = "📢 <b>خلاصه درخواست‌های جدید:</b>\n"
        for table, ids in pending_summary.items():
            table_name = TABLE_NAME["table_names"].get(table, table)
            count = len(ids)
            text += f"• ({count}) درخواست جدید در ({table_name})\n"
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                text="📋 مشاهده درخواست‌ها",
                callback_data="show_request_manager"
            )
        )
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.SendNotifToAdmins(text, reply_markup=kb)
    

    def start_auto_approval_thread(self):
        """Legacy-compatible behavior preserved for this callable."""
        thread = threading.Thread(
            target=self.auto_approve_requests, daemon=True)
        thread.start()

    def SendNotifToAdmins(self, txt: str, reply_markup: InlineKeyboardMarkup | None = None):
        """Legacy-compatible behavior preserved for this callable."""
        admins = self.db.select_dict("admins")
        qualified_admins = []
        for admin in admins:
            try:
                perms = json.loads(admin.get("permissions", "{}"))
                if perms.get("manage_requests") is True:
                    qualified_admins.append(admin)
            except Exception as e:
                log.info(
                    AUTO_CONFIG["log_error_parsing_permissions"].format(
                        id=admin.get("id"), error=e
                    )
                )

        for admin in qualified_admins:
            chat_id = admin.get("telegram_id") or admin.get("chat_id")
            if not chat_id:
                continue

            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.send_message(
                    chat_id,
                    txt,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                log.info(
                    AUTO_CONFIG["log_notification_sent"].format(
                        name=admin.get("name"), chat_id=chat_id
                    )
                )
            except Exception as e:
                log.error(
                    AUTO_CONFIG["log_notification_failed"].format(
                        name=admin.get("name"),
                        chat_id=chat_id,
                        error=e
                    )
                )

    def auto_approve_requests(self):
        """Legacy-compatible behavior preserved for this callable."""
        while True:

            approved_requests = 0
            with self.db_lock:
                tables_with_status = self.db.get_tables_with_parm("status")

            for table in tables_with_status:
                with self.db_lock:
                    settings = self.db.get_auto_settings(table)

                auto_enabled = settings.get("auto_approval_enabled", 0)
                if not auto_enabled:
                    continue

                with self.db_lock:
                    pending_requests = self.db.select_dict(
                        table, "status = ?", (AUTO_CONFIG["status_pending"],))
                    log.info(AUTO_CONFIG["log_start_approver"].format(
                        hash_line=AUTO_CONFIG["hash_line"],
                        table=table,
                        count=len(pending_requests),
                        hash_subline=AUTO_CONFIG["hash_subline"]
                    ))

                # Internal implementation note: legacy behavior is preserved during modernization.
                threshold = settings.get(
                    "auto_threshold", AUTO_CONFIG["default_auto_threshold"])
                try:
                    threshold = int(threshold)
                    if len(pending_requests) >= threshold:
                        for req in pending_requests:
                            try:
                                with self.db_lock:
                                    self.db.update(
                                        table, {"status": AUTO_CONFIG["status_approved"]}, "id = ?", (req["id"],))
                                    approved_requests += 1
                            except Exception as e:
                                log.error(
                                    AUTO_CONFIG["log_update_error"].format(error=e))
                    else:
                        log.info(AUTO_CONFIG["log_threshold_not_met"].format(
                            table=table, hash_subline=AUTO_CONFIG["hash_subline"]))
                except Exception as e:
                    log.error(AUTO_CONFIG["log_error_threshold"].format(
                        table=table, error=e, hash_subline=AUTO_CONFIG["hash_subline"]))

                # Internal implementation note: legacy behavior is preserved during modernization.
                auto_timer = settings.get(
                    "auto_timer", AUTO_CONFIG["default_auto_timer"])
                try:
                    if isinstance(auto_timer, str) and ":" in auto_timer:
                        parts = auto_timer.split(":")
                        hours, minutes = int(parts[0]), int(parts[1])
                        auto_timer = hours * 60 + minutes
                    else:
                        auto_timer = int(auto_timer)
                    current_time = datetime.now()
                    for req in pending_requests:
                        created_at_str = req.get("created_at")
                        try:
                            created_at = datetime.strptime(
                                created_at_str, "%Y-%m-%d %H:%M:%S.%f")
                        except Exception:
                            try:
                                created_at = datetime.strptime(
                                    created_at_str, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                created_at = datetime.strptime(
                                    created_at_str, "%Y-%m-%d %H:%M")
                        elapsed = (current_time -
                                   created_at).total_seconds() / 60
                        if elapsed >= auto_timer:
                            with self.db_lock:
                                self.db.update(
                                    table, {"status": AUTO_CONFIG["status_approved"]}, "id = ?", (req["id"],))
                            approved_requests += 1
                            self.bot.send_message(
                                req["id"], MESSAGES["auto_approved_timer"])
                except Exception as e:
                    log.error(AUTO_CONFIG["log_error_timer"].format(
                        table=table, error=e, hash_subline=AUTO_CONFIG["hash_subline"]))

            # Internal implementation note: legacy behavior is preserved during modernization.
            with self.db_lock:
                global_settings = self.db.get_auto_settings("global")
            check_interval = global_settings.get(
                "auto_check_interval", AUTO_CONFIG["default_auto_check_interval"])
            try:
                check_interval = int(check_interval)
            except Exception as e:
                log.error(f"Error parsing global auto_check_interval: {e}")
                check_interval = AUTO_CONFIG["default_auto_check_interval"]

            # Internal implementation note: legacy behavior is preserved during modernization.
            if approved_requests:
                tb_name = REQUEST_TYPE_NAMES.get(
                    TB_CONV.get(table, table), table)
                text = MESSAGES["notif_approved_to_admins"].format(
                    table=tb_name, count=approved_requests)
                self.SendNotifToAdmins(text)
                log.debug(f"Approved requests: {approved_requests}")
            else:
                log.debug("No approved requests")
            log.info(AUTO_CONFIG["log_global_interval"].format(
                interval=check_interval, hash_line=AUTO_CONFIG["hash_line"]))
            sleep(check_interval * 60)

    def auto_operations_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        with self.db_lock:
            tables_with_status = self.db.get_tables_with_parm("status")
        buttons = []
        for table in tables_with_status:
            table_name = TABLE_NAME["table_names"].get(table, table)
            with self.db_lock:
                settings = self.db.get_auto_settings(table)
            auto_enabled = settings.get("auto_approval_enabled", 0)
            status_label = AUTO_CONFIG["status_active"] if auto_enabled else AUTO_CONFIG["status_inactive"]
            buttons.append(KeyboardButton(f"{table_name} [{status_label}]"))
        if buttons:
            markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["set_auto_check_interval"]))
        markup.add(
            KeyboardButton(BUTTONS["back_to_previous"]),
            KeyboardButton(BUTTONS["back_to_main"]),
            KeyboardButton(BUTTONS.get("auto_help", "راهنما"))
        )
        self.bot.send_message(
            chat_id, MESSAGES["select_table_for_auto"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_auto_operations_selection)

    def handle_auto_operations_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.back_to_settings(message)
            return
        elif text == BUTTONS.get("auto_help", "راهنما"):
            self.bot.send_message(chat_id, MESSAGES.get(
                "auto_help_text", "راهنمای عملیات خودکار در دسترس نیست."))
            self.auto_operations_menu(message)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == BUTTONS["set_auto_check_interval"]:
            self.bot.send_message(
                chat_id, MESSAGES["Please_enter_Checking_time"])
            self.bot.register_next_step_handler(
                message, self.set_auto_check_interval)
            return

        selected_table = None
        print(text)
        panel = text.split("[")[0].strip()
        print(panel)

        for key, name in TABLE_NAME["table_names"].items():
            print(name)

            if name == panel:
                selected_table = key
                break
        if not selected_table:
            self.bot.send_message(chat_id, MESSAGES["invalid_table"])
            self.auto_operations_menu(message)
            return
        self.show_table_settings_menu(message, selected_table)

    def show_table_settings_menu(self, message, table):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        with self.db_lock:
            settings = self.db.get_auto_settings(table)
        auto_enabled = settings.get("auto_approval_enabled", 0)
        auto_threshold = settings.get(
            "auto_threshold", AUTO_CONFIG["default_auto_threshold"])
        auto_timer = settings.get(
            "auto_timer", AUTO_CONFIG["default_auto_timer"])
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        toggle_label = AUTO_CONFIG["status_active"] if not auto_enabled else AUTO_CONFIG["status_inactive"]
        markup.add(KeyboardButton(
            MESSAGES["toggle_auto_status"].format(status=toggle_label)))
        markup.add(KeyboardButton(
            MESSAGES["set_auto_threshold"].format(threshold=auto_threshold)))
        markup.add(KeyboardButton(
            MESSAGES["set_auto_timer"].format(timer=auto_timer)))
        markup.add(
            KeyboardButton(BUTTONS["back_to_previous"]),
            KeyboardButton(BUTTONS["back_to_main"]),
            KeyboardButton(BUTTONS.get("auto_help", "راهنما"))
        )
        self.bot.send_message(chat_id, MESSAGES["auto_settings_for_table"].format(
            table=TABLE_NAME["table_names"].get(table, table)), reply_markup=markup)
        self.bot.register_next_step_handler(
            message, lambda m: self.handle_table_settings_selection(m, table))

    def handle_table_settings_selection(self, message, table):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.auto_operations_menu(message)
            return
        elif text == BUTTONS.get("auto_help", "راهنما"):
            self.bot.send_message(chat_id, MESSAGES.get(
                "auto_help_text", "راهنمای عملیات خودکار در دسترس نیست."))
            self.show_table_settings_menu(message, table)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif MESSAGES["toggle_auto_status"].split(":")[0] in text:
            self.toggle_auto_approval(table, message)
        elif MESSAGES["set_auto_threshold"].split(":")[0] in text:
            self.bot.send_message(chat_id, MESSAGES["enter_threshold"])
            self.bot.register_next_step_handler(
                message, lambda m: self.set_auto_threshold(m, table))
        elif MESSAGES["set_auto_timer"].split(":")[0] in text:
            self.bot.send_message(chat_id, MESSAGES["enter_timer"])
            self.bot.register_next_step_handler(
                message, lambda m: self.set_auto_timer(m, table))
        else:
            self.show_table_settings_menu(message, table)

    def toggle_auto_approval(self, table, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        with self.db_lock:
            settings = self.db.get_auto_settings(table)
        current = settings.get("auto_approval_enabled", 0)
        new_status = 1 - current  # Internal implementation note: legacy behavior is preserved during modernization.
        settings["auto_approval_enabled"] = new_status
        with self.db_lock:
            self.db.set_auto_settings(table, settings)
        status_text = MESSAGES["auto_enabled_changed"].format(
            table=TABLE_NAME["table_names"].get(table, table),
            status=AUTO_CONFIG["status_active"] if new_status else AUTO_CONFIG["status_inactive"])
        self.bot.send_message(chat_id, status_text)
        self.show_table_settings_menu(message, table)

    def set_auto_threshold(self, message, table):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        try:
            threshold = int(message.text.strip())
            with self.db_lock:
                settings = self.db.get_auto_settings(table)
                settings["auto_threshold"] = threshold
                self.db.set_auto_settings(table, settings)
            self.bot.send_message(
                chat_id, MESSAGES["auto_threshold_set"].format(threshold=threshold))
        except ValueError:
            self.bot.send_message(chat_id, MESSAGES["invalid_input"])
        self.show_table_settings_menu(message, table)

    def set_auto_timer(self, message, table):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        input_time = message.text.strip()
        try:
            if ":" in input_time:
                parts = input_time.split(":")
                hours, minutes = int(parts[0]), int(parts[1])
                total_minutes = hours * 60 + minutes
            else:
                total_minutes = int(input_time)
            with self.db_lock:
                settings = self.db.get_auto_settings(table)
                settings["auto_timer"] = total_minutes
                self.db.set_auto_settings(table, settings)
            self.bot.send_message(
                chat_id, MESSAGES["auto_timer_set"].format(timer=total_minutes))
        except ValueError:
            self.bot.send_message(chat_id, MESSAGES["invalid_input"])
        self.show_table_settings_menu(message, table)

    def set_auto_check_interval(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        try:
            interval = int(message.text.strip())
            if interval < 5 or interval > 10100:
                raise ValueError
            with self.db_lock:
                global_settings = self.db.get_auto_settings("global") or {}
                global_settings["auto_check_interval"] = interval
                self.db.set_auto_settings("global", global_settings)
            self.bot.send_message(
                chat_id, MESSAGES["global_interval_set"].format(interval=interval))
        except ValueError:
            self.bot.send_message(
                chat_id, MESSAGES["invalid_interval"] + "\n" + MESSAGES["Please_enter_Checking_time"])
        self.auto_operations_menu(message)
