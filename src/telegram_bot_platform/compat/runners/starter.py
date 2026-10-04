# ---------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Callable, List

from telebot import TeleBot
from telebot.types import Message, Chat, User

from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import MESSAGES

log = CustomLogger("STARTER")


class Starter:
    """Legacy-compatible behavior preserved for this callable."""

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def __init__(
        self,
        db: DatabaseManager,
        bot: TeleBot,
        *,
        welcome_cb: Optional[Callable[[Message], None]] = None,
    ) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        self.db = db
        self.bot = bot
        self._welcome_cb = welcome_cb  # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    @staticmethod
    def _safe_attr(obj: Any, attr: str, default: Any = '') -> Any:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            return getattr(obj, attr, default) or default
        except Exception as exc:  # noqa: BLE001
            log.debug(f"_safe_attr error | {exc}")
            return default

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _extract_user_info(self, message: Message) -> Dict[str, Any]:
        """Legacy-compatible behavior preserved for this callable."""
        log.debug("[extract_user_info] Start extracting info")
        clicks = 1
        bots: List[int] = []

        try:
            user: User = message.from_user
            chat_id: int = message.chat.id
            log.debug(f"[extract_user_info] user_id={user.id}, chat_id={chat_id}")

            today_date = datetime.now().date().isoformat()
            log.debug(f"[extract_user_info] today_date={today_date}")
            
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                data = {"telegram_id": user.id, "clicks": 1}
                log.debug(f"[extract_user_info] daily-click data prepared: {data}")
            
                # Internal implementation note: legacy behavior is preserved during modernization.
                if self.db.table_exists("clicks"):
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    row = self.db.select_dict(
                        "clicks",
                        "telegram_id = ? AND date(created_at) = ?",
                        (user.id, today_date)
                    )
                    log.debug(f"[extract_user_info] daily-click row fetched: {row}")
            
                    if row:
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        prev = int(row[0]["clicks"])
                        new_count = prev + 1
                        log.info(f"[extract_user_info] upsocial_service clicks from {prev} to {new_count}")
                        self.db.update(
                            "clicks",
                            {"clicks": new_count, "last_updated": datetime.now().isoformat()},
                            "telegram_id = ? AND date(created_at) = ?",
                            (user.id, today_date)
                        )
                        clicks = new_count
                    else:
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        log.info(f"[extract_user_info] inserting new daily-click for user {user.id}")
                        self.db.insert(
                            "clicks",
                            {
                                "telegram_id": user.id,
                                "clicks": 1,
                                "created_at": datetime.now().isoformat(),
                                "last_updated": datetime.now().isoformat()
                            },
                            {
                                "telegram_id": "varchar(50)",
                                "clicks": "int",
                                "created_at": "timestamp",
                                "last_updated": "timestamp"
                            }
                        )
                        clicks = 1
                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    log.info(f"[extract_user_info] clicks table missing, creating & inserting for user {user.id}")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.insert(
                        "clicks",
                        {
                            "telegram_id": user.id,
                            "clicks": 1,
                            "created_at": datetime.now().isoformat(),
                            "last_updated": datetime.now().isoformat()
                        },
                        {
                            "telegram_id": "varchar(50)",
                            "clicks": "int",
                            "created_at": "timestamp",
                            "last_updated": "timestamp"
                        }
                    )
                    clicks = 1
            
            except Exception as exc:
                log.error(f"[extract_user_info] daily click insert/update failed: {exc}")


            # Internal implementation note: legacy behavior is preserved during modernization.
            phone_number = (
                message.contact.phone_number
                if getattr(message, "contact", None) and message.contact
                else ''
            )
            log.debug(f"[extract_user_info] phone_number={phone_number or '—'}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            bio = ''
            profile_photos = 0
            try:
                chat_info = self.bot.get_chat(chat_id)
                bio = self._safe_attr(chat_info, 'bio', '')
                photos = self.bot.get_user_profile_photos(user.id, limit=1)
                profile_photos = self._safe_attr(photos, 'total_count', 0)
                log.debug(f"[extract_user_info] bio length={len(bio)}, profile_photos={profile_photos}")
            except Exception as exc:
                log.warning(f"[extract_user_info] chat/photo fetch failed: {exc}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                previous_rows = self.db.select_dict(
                    "users",
                    "telegram_id = ?",
                    (user.id,),
                )
                log.debug(f"[extract_user_info] previous user rows: {previous_rows}")
                if previous_rows:
                    previous_data = previous_rows[0] if isinstance(previous_rows, list) else previous_rows
                    bots_json = previous_data.get("bots", "[]")
                    total_clicks = int(previous_data.get("clicks", 0))
                    clicks += total_clicks
                    bots.extend(json.loads(bots_json))
                    log.info(f"[extract_user_info] loaded previous clicks={total_clicks}, bots={bots}")
            except Exception as exc:
                log.error(f"[extract_user_info] fetch previous bots failed: {exc}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                current_bot_id = self.bot.get_me().id
                if current_bot_id not in bots:
                    bots.append(current_bot_id)
                    log.debug(f"[extract_user_info] appended current bot_id={current_bot_id}")
            except Exception as exc:
                log.warning(f"[extract_user_info] get_me() failed: {exc}")

            now_iso = datetime.now().isoformat()
            log.debug(f"[extract_user_info] last_interaction={now_iso}")

            result = {
                "bots": json.dumps(bots),
                "telegram_id": user.id,
                "clicks": clicks,
                "chat_id": chat_id,
                "username": self._safe_attr(user, "username"),
                "first_name": self._safe_attr(user, "first_name"),
                "last_name": self._safe_attr(user, "last_name"),
                "phone_number": phone_number,
                "bio": bio,
                "profile_photos": profile_photos,
                "last_interaction": now_iso,
            }
            log.debug(f"[extract_user_info] result prepared: {result}")
            return result

        except Exception as exc:
            log.error(f"[extract_user_info] Failed completely: {exc}")
            return {}

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def store_user_info(self, message: Message) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            data = self._extract_user_info(message)
            if not data:
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            existing = self.db.select_dict(
                "users",
                "telegram_id = ?",
                (data["telegram_id"],),
            )
            if existing:
                # Internal implementation note: legacy behavior is preserved during modernization.
                data["created_at"] = existing[0].get("created_at")

            # Internal implementation note: legacy behavior is preserved during modernization.
            now_iso = datetime.now(tz=timezone.utc).isoformat()
            data["last_updated"] = now_iso

            # Internal implementation note: legacy behavior is preserved during modernization.
            if not existing:
                data["first_seen"] = now_iso

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.upsert(
                table_name="users",
                data=data,
                column_types={
                    "bots":        "json",
                    "telegram_id": "varchar(50)",
                    "clicks":      "int",
                    "chat_id":     "varchar(50)",
                    "username":    "varchar(255)",
                    "first_name":  "varchar(255)",
                    "last_name":   "varchar(255)",
                    "phone_number":"varchar(50)",
                    "bio":         "varchar(255)",
                    "profile_photos":"int",
                    "last_interaction":"varchar(50)",
                    "first_seen":  "timestamp",
                },
                key="telegram_id",
                unique_column="telegram_id",
            )
            self.db.execute_query("ALTER TABLE users MODIFY COLUMN telegram_id VARCHAR(50) NOT NULL")
            self.db.execute_query("ALTER TABLE users MODIFY COLUMN chat_id    VARCHAR(50) NOT NULL")

            log.info(f"[store_user_info] Upsert OK → {data['telegram_id']}")
        except Exception as exc:
            log.exception("[store_user_info] Failed")


    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def broadcast_fake_message_to_all(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            rows = self.db.select_dict("users")
            if not rows:
                log.info("[broadcast] No users found")
                return
            log.info(f"[broadcast] Resetting {len(rows)} users")
        except Exception as exc:  # noqa: BLE001
            log.error(f"[broadcast] fetch users failed | {exc}")
            return

        my_bot_id = self.bot.get_me().id

        for user_row in rows:
            try:
                bots_raw = user_row.get("bots", "[]")
                if not bots_raw:
                    continue
                bots_list: List[int] = json.loads(bots_raw) or []

                # Internal implementation note: legacy behavior is preserved during modernization.
                if my_bot_id not in bots_list:
                    continue

                chat_id = user_row.get("chat_id") or user_row["telegram_id"]
                if not chat_id:
                    continue

                # Internal implementation note: legacy behavior is preserved during modernization.
                user_obj = User(
                    id=user_row["telegram_id"],
                    is_bot=False,
                    first_name=user_row.get("first_name", "کاربر"),
                )
                user_obj.last_name = user_row.get("last_name", "")
                user_obj.username = user_row.get("username", "")

                chat_obj = Chat(id=chat_id, type="private")  # type: ignore[arg-type]

                fake_msg = Message(
                    message_id=int(time.time()),
                    from_user=user_obj,
                    date=int(time.time()),
                    chat=chat_obj,
                    content_type="text",
                    options={},
                    json_string={},
                )
                fake_msg.text = "/start"

                # Internal implementation note: legacy behavior is preserved during modernization.
                try:
                    self.bot.send_message(chat_id, MESSAGES["Restart_bots"])
                except Exception as send_exc:  # noqa: BLE001
                    log.debug(f"[broadcast] send_message failed | {send_exc}")

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    new_bots = [bid for bid in bots_list if bid != my_bot_id]
                    try:
                        self.db.update(
                            "users",
                            {"bots": json.dumps(new_bots)},
                            "telegram_id = ?",
                            (user_row["telegram_id"],),
                        )
                    except Exception as upd_exc:  # noqa: BLE001
                        log.error(f"[broadcast] update bots failed | {upd_exc}")
                    continue  # Internal implementation note: legacy behavior is preserved during modernization.

                # Internal implementation note: legacy behavior is preserved during modernization.
                if callable(self._welcome_cb):
                    try:
                        self._welcome_cb(fake_msg)
                        log.debug(f"[broadcast] welcome_cb OK → {chat_id}")
                    except Exception as cb_exc:  # noqa: BLE001
                        log.error(f"[broadcast] welcome_cb failed → {chat_id} | {cb_exc}")

            except Exception as outer_exc:  # Internal implementation note: legacy behavior is preserved during modernization.
                log.error(f"[broadcast] outer loop error → {outer_exc}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        log.info("[broadcast] Finished broadcasting reset message to all users.")
