import telebot
from typing import Dict
import json
import logging
import html
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot_platform.compat.utils.task_manager import ThreadManager
from telegram_bot_platform.compat.config.settings import CHANNEL_ID, BUTTONS, CLIENT_BOT_ID
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from datetime import datetime, time
logger = CustomLogger()  # log_file="publish_ad_at_time.log")


class AdPublishScheduler:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bots: Dict[str, telebot.TeleBot], db: DatabaseManager, notification_manager, ad_sender, ad_publish_interval_min=5, T_M=ThreadManager()):

        self.db = db
        self.notification_manager = notification_manager
        self.send_ad_to_channel = ad_sender
        self.ad_publish_interval_min = ad_publish_interval_min
        self.bots = bots
        self.T_M = T_M
        import threading
        self.db_lock = threading.Lock()

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("AdPublishScheduler started")
        # self._create_publish_queue_table()
        self.T_M.add_task(self._cleanup_expired_slots,
                          10, "Checking Ads for expired")
        self.T_M.add_task(self.expire_yesterdays_pending_ads,
                          12 * 60, "Expiring yesterday's pending ads")
        self.T_M.add_task(self.markAll_recent_expired_live_slots_false,
                          48 * 60, "Falsing expired ad slot times")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.publish_queue = {}

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._reschedule_pending()
        
        
    def expire_orphan_approved_ads(self):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            approved_ads = self.db.select_dict("ads", "status = 'approved'")
            if not approved_ads:
                logger.info("✅ No approved ads found for orphan-check.")
                return
    
            # Internal implementation note: legacy behavior is preserved during modernization.
            live_rows = self.db.select_dict("live_ads")
            live_map  = {row["ad_id"]: row for row in live_rows}
            live_ids  = set(live_map.keys())
    
            # Internal implementation note: legacy behavior is preserved during modernization.
            staff_rows = self.db.select_dict("staff")
            valid_ucodes   = {p["U_code"] for p in staff_rows}
    
            # Internal implementation note: legacy behavior is preserved during modernization.
            for ad in approved_ads:
                ad_id = ad["id"]
                ucode = ad.get("U_code")
    
                # Internal implementation note: legacy behavior is preserved during modernization.
                if ad_id not in live_ids:
                    self.db.update("ads", {"status": "expired"},
                                   "id = ?", (ad_id,))
                    logger.info(f"✅ Ad #{ad_id} set to expired "
                                f"(missing in live_ads).")
                    continue  # Internal implementation note: legacy behavior is preserved during modernization.
                
                # Internal implementation note: legacy behavior is preserved during modernization.
                if ucode not in valid_ucodes:
                    live_row   = live_map.get(ad_id, {})
                    msg_id     = live_row.get("channel_message_id")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self._expire_ad_in_channel(ad_id, msg_id,
                                               reason="orphan staff")
                    logger.info(f"✅ Ad #{ad_id} removed because staff "
                                f"U_code='{ucode}' not found.")
                    continue
                
            logger.info("🎯 Orphan-approved ads check completed.")
    
        except Exception as e:
            logger.exception(f"❌ Error while expiring orphan ads: {e}")
    
    
    def expire_yesterdays_pending_ads(self):
        """Legacy-compatible behavior preserved for this callable."""
        yesterday_start = (datetime.now() - timedelta(days=1)
                           ).replace(hour=0, minute=0, second=0, microsecond=0)
        today_start = yesterday_start + timedelta(days=1)

        try:
            pending_ads = self.db.select_dict(
                "ads",
                "status = 'pending' AND created_at >= ? AND created_at < ?",
                (yesterday_start.strftime("%Y-%m-%d %H:%M:%S"),
                 today_start.strftime("%Y-%m-%d %H:%M:%S"))
            )
            if not pending_ads:
                logger.info(
                    "✅ هیچ آگهی پندینگ دیروزی برای Expire شدن پیدا نشد.")
                return

            for ad in pending_ads:
                ad_id = ad['id']
                self.db.update(
                    "ads", {"status": "expired"}, "id = ?", (ad_id,))
                logger.info(
                    f"✅ آگهی #{ad_id} (دیروزی) به expired تغییر وضعیت یافت.")

        except Exception as e:
            logger.exception(f"❌ خطا در expire کردن آگهی‌های دیروزی: {e}")

    def _cleanup_expired_slots(self):
        """Legacy-compatible behavior preserved for this callable."""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        tomorrow_start = today_start + timedelta(days=1)
        self.expire_orphan_approved_ads()
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            # ads = self.db.select_dict(
            #     "ads",
            #     "created_at >= ? AND created_at < ? AND status = 'approved'",
            #     (today_start.strftime("%Y-%m-%d %H:%M:%S"),
            #      tomorrow_start.strftime("%Y-%m-%d %H:%M:%S"))
            # )
            ads = self.db.select_dict(
                "ads",
                "status = 'approved'",
            )
            adids = [ad["id"] for ad in ads]
            if not adids:
                logger.info("No ads found for cleanup")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            placeholder = f"({','.join('?' * len(adids))})"
            params = tuple(adids)
            live_ads = self.db.select_dict(
                "live_ads",
                f"ad_id IN {placeholder}",
                params
            )

            logger.info(f"Found {len(live_ads)} live ads")

            for ad in live_ads:
                ad_id = ad['ad_id']
                message_id = ad.get('channel_message_id')
                time_slots = ad.get('time_slots')

                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(time_slots, str):
                    try:
                        time_slots = json.loads(time_slots)
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"Invalid JSON in time_slots for ad #{ad_id}: {e}")
                        continue

                updated = False
                # Internal implementation note: legacy behavior is preserved during modernization.
                for slot, status in time_slots.items():

                    try:
                        slot_dt = datetime.strptime(slot, "%H:%M")
                        slot_time_in_minutes = slot_dt.hour * 60 + slot_dt.minute
                    except ValueError:
                        logger.error(f"❌ Invalid slot time format: {slot}")
                        continue  # Internal implementation note: legacy behavior is preserved during modernization.

                    current_time_in_minutes = current_hour * 60 + current_minute

                    if status is True:
                        if current_time_in_minutes > slot_time_in_minutes:
                            time_slots[slot] = False
                            updated = True
                            logger.info(
                                f"⏰ Slot {slot} expired and marked as unavailable.")

                # Internal implementation note: legacy behavior is preserved during modernization.
                if updated:
                    with self.db_lock:
                        self.db.update("live_ads", {"time_slots": json.dumps(
                            time_slots)}, "ad_id = ?", (ad_id,))

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    keyboard = InlineKeyboardMarkup(row_width=4)
                    buttons = []
                    link_base = f"https://t.me/{html.escape(CLIENT_BOT_ID)}?start"
                    for slot, available in time_slots.items():
                        slot_time_fmt = datetime.strftime(
                            datetime.strptime(slot, "%H:%M"), "%H_%M")
                        param = f"reserve_ads_{ad_id}_{slot_time_fmt}"
                        if available:
                            buttons.append(InlineKeyboardButton(
                                slot, url=f"{link_base}={param}"))
                        else:
                            buttons.append(InlineKeyboardButton(
                                "رزوشده🕰", url=f"{link_base}=ShowAvalabelCodes"))

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
                    if len(rows) >= 2 and len(rows[-1]) == 1:
                        flat = sum(rows, [])
                        rows = [flat[i:i+3] for i in range(0, len(flat), 3)]

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    rows.append([
                        InlineKeyboardButton(
                            text=BUTTONS["Goto_Cutsomer_bot"], url=f"https://t.me/{CLIENT_BOT_ID}?start"),
                        InlineKeyboardButton(
                            text=BUTTONS["Add_toFavoris"], callback_data=f"AddToFavorits_{ad.get('U_code')}")
                    ])

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    keyboard = InlineKeyboardMarkup()
                    for r in rows:
                        keyboard.row(*r)

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if not message_id:
                        logger.warning(f"No message_id for ad #{ad_id}")
                        continue

                    try:
                        self.bots["client"].edit_message_reply_markup(
                            chat_id=CHANNEL_ID,
                            message_id=message_id,
                            reply_markup=keyboard
                        )
                        logger.info(
                            f"Updated buttons for ad #{ad_id} after expiring slots")
                    except Exception as e:
                        logger.warning(
                            f"Failed to update buttons for ad #{ad_id}: {e}")

                # Internal implementation note: legacy behavior is preserved during modernization.
                if all(v is False for v in time_slots.values()):
                    self._expire_ad_in_channel(
                        ad_id, message_id, reason="all slots expired")
                    continue

                # Internal implementation note: legacy behavior is preserved during modernization.
                created_time = ad.get('created_at')
                if created_time:
                    try:
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        try:
                            ad_date = datetime.strptime(
                                created_time, "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            ad_date = datetime.strptime(
                                created_time, "%Y-%m-%d %H:%M:%S")

                        now = datetime.now()

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        expire_time = ad_date.replace(
                            hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                        if now >= expire_time:
                            self._expire_ad_in_channel(
                                ad_id, message_id, reason="past midnight")

                    except Exception as e:
                        logger.warning(
                            f"Error parsing created_at for ad #{ad_id}: {e}")

        except Exception as e:
            logger.exception(f"Error in cleanup_expired_slots: {e}")

    def _expire_ad_in_channel(self, ad_id, message_id, reason=""):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if message_id and isinstance(message_id, (int, str)) and str(message_id).isdigit():
                self.bots['client'].delete_message(
                    CHANNEL_ID, int(message_id))
                logger.info(
                    f"Deleted message {message_id} from channel for ad #{ad_id} ({reason})")
            else:
                logger.warning(
                    f"No valid message_id found for ad #{ad_id} → skipping channel deletion")

            # Internal implementation note: legacy behavior is preserved during modernization.

            self.db.update(
                'ads', {'status': 'expired'}, 'id = ?', (ad_id,))
            self.mark_live_slots_false(ad_id)

            logger.info(
                f"Marked ad #{ad_id} as expired in database ({reason})")

        except Exception as e:
            self.db.update(
                'ads', {'status': 'Deleted'}, 'id = ?', (ad_id,))
            self.mark_live_slots_false(ad_id)
            logger.exception(f"Error expiring ad #{ad_id} in channel: {e}")

    def mark_live_slots_false(self, ad_id):
        """Legacy-compatible behavior preserved for this callable."""
        live_ad = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
        if not live_ad:
            logger.info(f"No live_ads entry found for ad #{ad_id}")
            return

        time_slots = live_ad[0].get("time_slots")
        if isinstance(time_slots, str):
            time_slots = json.loads(time_slots)

        updated = False
        for slot in time_slots:
            if time_slots[slot] is True:
                time_slots[slot] = False
                updated = True

        if updated:
            self.db.update(
                "live_ads",
                {"time_slots": json.dumps(time_slots)},
                "ad_id = ?",
                (ad_id,)
            )
            logger.info(
                f"All time_slots marked False for ad #{ad_id} in live_ads")

    def markAll_recent_expired_live_slots_false(self):
        """Legacy-compatible behavior preserved for this callable."""
        cutoff_time = datetime.now() - timedelta(hours=72)

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            expired_ads = self.db.select_dict(
                "ads",
                "status = 'expired' AND last_updated >= ?",
                (cutoff_time.strftime("%Y-%m-%d %H:%M:%S"),)
            )
            if not expired_ads:
                logger.info("✅ هیچ آگهی expired تازه برای بررسی پیدا نشد.")
                return

            ad_ids = [ad["id"] for ad in expired_ads]

            # Internal implementation note: legacy behavior is preserved during modernization.
            placeholder = f"({','.join('?' * len(ad_ids))})"
            live_ads = self.db.select_dict(
                "live_ads",
                f"ad_id IN {placeholder}",
                tuple(ad_ids)
            )
            if not live_ads:
                logger.info("ℹ️ هیچ رکورد live_ads مرتبط پیدا نشد.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            for live_ad in live_ads:
                ad_id = live_ad["ad_id"]
                time_slots = live_ad.get("time_slots")

                if not time_slots:
                    logger.warning(
                        f"⚠️ live_ads #{ad_id} فاقد time_slots است.")
                    continue

                if isinstance(time_slots, str):
                    try:
                        time_slots = json.loads(time_slots)
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"❌ JSON نامعتبر در time_slots آگهی #{ad_id}: {e}")
                        continue

                # Internal implementation note: legacy behavior is preserved during modernization.
                updated = any(time_slots.values())
                if not updated:
                    logger.info(
                        f"ℹ️ همه اسلات‌های آگهی #{ad_id} قبلاً False بوده‌اند.")
                    continue

                for slot in time_slots:
                    time_slots[slot] = False

                with self.db_lock:
                    self.db.update(
                        "live_ads",
                        {"time_slots": json.dumps(time_slots)},
                        "ad_id = ?",
                        (ad_id,)
                    )
                logger.info(
                    f"✅ همه time_slots آگهی #{ad_id} در live_ads به False تغییر کرد.")

        except Exception as e:
            logger.exception(
                f"❌ خطا در markAll_recent_expired_live_slots_false: {e}")

    def ensure_time_string(self, publish_time):
        if publish_time is None:
            return None
        if isinstance(publish_time, timedelta):
            logger.error(
                "❌ Got timedelta for publish_time; expected datetime or string. Converting now.")
            future_time = datetime.now() + publish_time
            return future_time.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(publish_time, datetime):
            return publish_time.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(publish_time, time):
            now = datetime.now()
            combined = datetime.combine(now.date(), publish_time)
            return combined.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(publish_time, str):
            if len(publish_time) == 5:  # HH:MM
                today = datetime.now().strftime("%Y-%m-%d")
                return f"{today} {publish_time}:00"
            elif len(publish_time) == 8:  # HH:MM:SS
                today = datetime.now().strftime("%Y-%m-%d")
                return f"{today} {publish_time}"
            else:
                return publish_time  # assume already full
        else:
            logger.error(
                f"Unsupported type for publish_time: {type(publish_time)}")
            return None

    def _reschedule_pending(self):
        rows = self.db.select_dict("publish_queue", "status = 'pending'")
        now = datetime.now()
        for row in rows:
            if not row.get('publish_time'):
                logger.error(
                    f"❌ Skipping pending row with missing publish_time: {row}")
                continue
            self._schedule_jobs_for_row(row, now)

    def add_to_publish_queue(self, ad_id: int, table_name: str, publish_time: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        now = datetime.now()
        logger.info(
            f"time now is :({now.strftime('%H:%M')}) & publish_time is :({publish_time})")
        # created = now.isoformat(sep=' ', timespec='seconds')
        if not publish_time:
            logger.error(
                f"❌ Cannot queue ad #{ad_id} because publish_time is None or empty! Skipping insertion.")
            return

        publish_time = self.ensure_time_string(publish_time)

        print(f'publish_time : {publish_time}')
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            same = self.db.select_dict(
                "publish_queue",
                "status = 'pending' AND publish_time = ?",
                (publish_time,)
            )
            position = len(same)
        except:
            position = 0

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.insert("publish_queue", {
            "ad_id": ad_id,
            "table_name": table_name,
            "publish_time": publish_time,
            "status": "pending",
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S")
        })
        logger.info(
            f"Queued ad #{ad_id} at {publish_time} (position={position})")

        # Internal implementation note: legacy behavior is preserved during modernization.
        row = self.db.select_dict(
            "publish_queue",
            "ad_id = ? ",
            (ad_id, )
        )

        # rowsitahajian = self.db.select_dict("publish_queue")

        if not row:
            logger.error(f"Failed to fetch queued row for ad #{ad_id}")
            return
        row = row[0]
        print(row["publish_time"])
        self._schedule_jobs_for_row(row, now, position)

    def _schedule_jobs_for_row(self, row: dict, now: datetime, position: int = None):
        """Legacy-compatible behavior preserved for this callable."""
        import logging
        from datetime import datetime, timedelta

        logger = logging.getLogger(__name__)

        publish_time_raw = row.get('publish_time')
        if not publish_time_raw:
            logger.error(f"❌ Missing publish_time for row: {row}")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if isinstance(publish_time_raw, datetime):
            scheduled = publish_time_raw
        elif isinstance(publish_time_raw, str):
            try:
                scheduled = datetime.strptime(
                    publish_time_raw, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    today = now.date()
                    pub_time = datetime.strptime(
                        publish_time_raw, "%H:%M:%S").time()
                    scheduled = datetime.combine(today, pub_time)
                except ValueError:
                    try:
                        pub_time = datetime.strptime(
                            publish_time_raw, "%H:%M").time()
                        scheduled = datetime.combine(today, pub_time)
                    except ValueError:
                        logger.error(
                            f"❌ Invalid time string format: {publish_time_raw}")
                        return

        else:
            logger.error(
                f"❌ Unsupported publish_time type: {type(publish_time_raw)}")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if position is None:
            same = self.db.select_dict(
                "publish_queue",
                "status = 'pending' AND publish_time = ? AND created_at <= ?",
                (row['publish_time'], row['created_at'])
            )
            position = len(same) - 1

        # Internal implementation note: legacy behavior is preserved during modernization.
        offset = timedelta(minutes=self.ad_publish_interval_min * position)
        run_dt = scheduled + offset

        if run_dt < now:
            logger.warning(
                f"⚠️ Run time {run_dt} already passed. Expiring immediately.")
            self._expire_scheduled_job(row['id'])
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        job_id = f"publish_{row['id']}"
        self.scheduler.add_job(
            self._run_publish_job, 'date',
            run_date=run_dt,
            args=[row['id']],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"✅ Scheduled publish job {job_id} at {run_dt}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        exp_dt = run_dt + timedelta(hours=1)
        exp_job_id = f"expire_{row['id']}"
        self.scheduler.add_job(
            self._expire_scheduled_job, 'date',
            run_date=exp_dt,
            args=[row['id']],
            id=exp_job_id,
            replace_existing=True
        )
        logger.info(f"✅ Scheduled expire job {exp_job_id} at {exp_dt}")

    def _run_publish_job(self, queue_id: int):
        """Legacy-compatible behavior preserved for this callable."""
        rows = self.db.select_dict(
            "publish_queue", "id = ? AND status = 'pending'", (queue_id,)
        )
        if not rows:
            return
        row = rows[0]
        ad_id = row['ad_id']
        table = row['table_name']
        data = self.db.select_dict(table, "id = ?", (ad_id,))
        if not data:
            self._update_queue(queue_id, 'expired')
            return

        try:
            self.send_ad_to_channel(data[0], table)
            self._update_queue(queue_id, 'published')
            logger.info(f"Ad #{ad_id} published successfully.")
        except Exception as e:
            logger.exception(f"Error publishing ad #{ad_id}: {e}")

    def _expire_scheduled_job(self, queue_id: int):
        """Legacy-compatible behavior preserved for this callable."""
        rows = self.db.select_dict(
            "publish_queue", "id = ? AND status = 'pending'", (queue_id,)
        )
        if not rows:
            return
        row = rows[0]
        ad_id = row['ad_id']
        self._update_queue(queue_id, 'expired')
        admins = self.db.select_dict("admins")
        # Internal implementation note: legacy behavior is preserved during modernization.
        for admin in admins:
            if admin.get("manage_requests", False):
                self.bots["admin"].send_message(
                    admin["telegram_id"], (f"⚠️ آگهی #{ad_id} منقضی شد."))
        # Internal implementation note: legacy behavior is preserved during modernization.
        pers = self._fetch_staff(ad_id)
        if pers.get('telegram_id'):
            self.bots['staff'].send_message(
                pers['telegram_id'], f"⛔ آگهی شما #{ad_id} منقضی شد، لطفاً مجدداً ارسال کنید.")
        logger.info(f"Ad #{ad_id} expired via scheduler.")

    def _update_queue(self, queue_id: int, status: str):
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        self.db.update(
            "publish_queue",
            {"status": status, "updated_at": now},
            "id = ?", (queue_id,)
        )

    def _fetch_staff(self, ad_queue_id: int) -> dict:
        """Legacy-compatible behavior preserved for this callable."""
        row = self.db.select_dict('publish_queue', "id = ?", (ad_queue_id,))
        if not row:
            return {}
        ad_id = row[0]['ad_id']
        live = self.db.select_dict('live_ads', "ad_id = ?", (ad_id,))
        if live:
            u_code = live[0].get('U_code')
            pers = self.db.select_dict('staff', "U_code = ?", (u_code,))
            return pers[0] if pers else {}
        return {}

    def shutdown(self):
        """Legacy-compatible behavior preserved for this callable."""
        self.scheduler.shutdown(wait=False)
        logger.info("AdPublishScheduler stopped.")
