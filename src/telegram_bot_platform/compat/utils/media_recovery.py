import json
import re
import threading
from typing import Any, Dict, List, Optional, Tuple
import time  # Internal implementation note: legacy behavior is preserved during modernization.

import telebot
from io import BytesIO
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import MEDIA_FIELDS           # Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger                # Internal implementation note: legacy behavior is preserved during modernization.
from datetime import datetime, timedelta
# -----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# -----------------------------------------------------------------------------

log = CustomLogger("Recovery-fileIds")


class MediaRecoveryManager:
    """Legacy-compatible behavior preserved for this callable."""

    FILE_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{40,}")  # Internal implementation note: legacy behavior is preserved during modernization.

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def __init__(
        self,
        db : DatabaseManager,
        bot: telebot.TeleBot,
        upload_chat_id: int,
        *,
        max_threads: int = 4,
        chunk_size: int = 100,
    ) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        self.db = db
        self.bot = bot
        self.upload_chat_id = upload_chat_id
        self.max_threads = max_threads
        self.chunk_size = chunk_size
        self.media_field_types = MEDIA_FIELDS     # Internal implementation note: legacy behavior is preserved during modernization.
        self._lock = threading.Lock()   
        self.sleep_between_requests = 0.1  # Internal implementation note: legacy behavior is preserved during modernization.
        self.max_retries = 10  # Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _extract_file_ids(self, value: Any) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        ids: List[str] = []
        try:
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    ids.extend(self._extract_file_ids(parsed))
                except (json.JSONDecodeError, TypeError):
                    ids.extend(self.FILE_ID_PATTERN.findall(value))
            elif isinstance(value, list):
                for item in value:
                    ids.extend(self._extract_file_ids(item))
            elif isinstance(value, dict):
                for v in value.values():
                    ids.extend(self._extract_file_ids(v))
        except Exception as e:
            log.exception(f"[Recovery] Extract error: {e}")
        return list(set(ids))

    def _replace_ids_in_value(self, original: Any, mapping: Dict[str, str]) -> Any:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if isinstance(original, str):
                try:
                    parsed = json.loads(original)
                    return json.dumps(
                        self._replace_ids_in_value(parsed, mapping),
                        ensure_ascii=False,
                    )
                except (json.JSONDecodeError, TypeError):
                    out = original
                    for old, new in mapping.items():
                        out = out.replace(old, new)
                    return out
            if isinstance(original, list):
                return [self._replace_ids_in_value(i, mapping) for i in original]
            if isinstance(original, dict):
                return {k: self._replace_ids_in_value(v, mapping) for k, v in original.items()}
        except Exception as e:
            log.exception(f"[Recovery] Replace error: {e}")
        return original

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _detect_type(self, column: str, file_id: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""

        # Internal implementation note: legacy behavior is preserved during modernization.
        if column in self.media_field_types:
            return self.media_field_types[column]

        # Internal implementation note: legacy behavior is preserved during modernization.
        if file_id.startswith("AgAC"):
            return "photo"
        elif file_id.startswith("BQAD"):  # Internal implementation note: legacy behavior is preserved during modernization.
            return "photo"
        elif file_id.startswith("CAAD"):  # Internal implementation note: legacy behavior is preserved during modernization.
            return "document"
        elif file_id.startswith("DAAD"):  # Internal implementation note: legacy behavior is preserved during modernization.
            return "video_note"
        elif file_id.startswith("DQAD"):
            return "video"
        elif file_id.startswith("BAAD"):
            return "document"
        elif file_id.startswith("CQAD"):
            return "voice"
        elif file_id.startswith("AwAD"):
            return "audio"
        elif file_id.startswith("BQAD"):
            return "sticker"  # Internal implementation note: legacy behavior is preserved during modernization.
        elif file_id.startswith("CQAD"):
            return "voice"
        elif file_id.startswith("CgAD"):
            return "animation"  # Internal implementation note: legacy behavior is preserved during modernization.
        elif file_id.startswith("BgAD"):
            return "video"
        # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        return "document"


    from io import BytesIO

    def _reupload(self, old_id: str, column: str) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        mtype = self._detect_type(column, old_id)
        for attempt in range(self.max_retries):
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                file_info = self.bot.get_file(old_id)
                file_bytes = self.bot.download_file(file_info.file_path)

                # Internal implementation note: legacy behavior is preserved during modernization.
                file_obj = BytesIO(file_bytes)
                file_obj.name = "file"  # Internal implementation note: legacy behavior is preserved during modernization.

                # Internal implementation note: legacy behavior is preserved during modernization.
                if mtype == "photo" or column in ["gallery_photos", "profile_photos"]:
                    msg = self.bot.send_photo(self.upload_chat_id, file_obj)
                    new_id = msg.photo[-1].file_id
                elif mtype == "video":
                    msg = self.bot.send_video(self.upload_chat_id, file_obj)
                    new_id = msg.video.file_id
                elif mtype == "audio":
                    msg = self.bot.send_audio(self.upload_chat_id, file_obj)
                    new_id = msg.audio.file_id
                elif mtype == "voice":
                    msg = self.bot.send_voice(self.upload_chat_id, file_obj)
                    new_id = msg.voice.file_id
                elif mtype == "video_note":
                    msg = self.bot.send_video_note(self.upload_chat_id, file_obj)
                    new_id = msg.video_note.file_id
                else:
                    msg = self.bot.send_document(self.upload_chat_id, file_obj)
                    new_id = msg.document.file_id

                # Internal implementation note: legacy behavior is preserved during modernization.
                time.sleep(self.sleep_between_requests)
                return new_id

            except telebot.apihelper.ApiTelegramException as e:
                # Internal implementation note: legacy behavior is preserved during modernization.
                retry_after = (
                    e.result_json.get("parameters", {}).get("retry_after")
                    if hasattr(e, "result_json") and isinstance(e.result_json, dict)
                    else None
                )
                if retry_after:
                    log.warning(f"[Recovery] Rate-limit hit → sleep {retry_after}s (attempt {attempt+1})")
                    time.sleep(retry_after + 1)
                    continue
                log.warning(f"[Recovery] API error for {old_id}: {e}")
                break
            except Exception as e:
                log.exception(f"[Recovery] Unexpected upload error: {e}")
                break
        return None



    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _scan_chunk(
        self,
        rows: List[Tuple[str, Dict[str, Any], str, List[str]]],
        sink: List[Tuple[str, Dict[str, Any], str, List[str]]],
    ) -> None:
        with self._lock:
            sink.extend(rows)

    # ------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ------------------------------------------------------------------
    def scan_database(self) -> List[Tuple[str, Dict[str, Any], str, List[str]]]:
        """Legacy-compatible behavior preserved for this callable."""

        media_fields_dynamic = self.detect_media_columns()
        collected: List[Tuple[str, Dict[str, Any], str, List[str]]] = []

        for table in self.db.list_tables():
            try:
                rows = self.db.select_dict(table)
            except Exception as e:
                log.warning(f"[Recovery] Cannot read '{table}': {e}")
                continue
            if not rows:
                continue

            # Internal implementation note: legacy behavior is preserved during modernization.
            media_columns = media_fields_dynamic.get(table, [])

            # Internal implementation note: legacy behavior is preserved during modernization.
            buffer, threads = [], []

            for row in rows:
                last_str = (
                    row.get("last_media_recharge")
                    or row.get("last_update")
                    or row.get("last_updated")
                )
                if last_str:
                    last_time = self._parse_date_safe(str(last_str).strip())
                    if last_time and datetime.now() - last_time < timedelta(days=1):
                        continue

                for col in media_columns:
                    val = row.get(col)
                    if val:
                        fids = self._extract_file_ids(val)
                        if fids:
                            buffer.append((table, row, col, fids))
                        if len(buffer) >= self.chunk_size:
                            t = threading.Thread(
                                target=self._scan_chunk, args=(buffer.copy(), collected)
                            )
                            threads.append(t)
                            t.start()
                            buffer.clear()

            if buffer:
                t = threading.Thread(target=self._scan_chunk, args=(buffer.copy(), collected))
                threads.append(t)
                t.start()
            for th in threads:
                th.join()

        log.info(f"[Recovery] Scan done → {len(collected)} rows with media.")
        return collected

    def detect_media_columns(self, sample_rows_per_table: int = 10, min_matches: int = 2) -> Dict[str, List[str]]:
        """Legacy-compatible behavior preserved for this callable."""
        media_columns_per_table = {}
        for table in self.db.list_tables():
            try:
                rows = self.db.select_dict(table)
            except Exception as e:
                log.warning(f"[Recovery] Cannot read '{table}': {e}")
                continue
            if not rows:
                continue

            # Internal implementation note: legacy behavior is preserved during modernization.
            columns = rows[0].keys()
            media_columns = []

            for col in columns:
                match_count = 0
                for row in rows:
                    val = row.get(col)
                    if not val or not isinstance(val, str):
                        continue
                    if self.FILE_ID_PATTERN.search(val):
                        match_count += 1
                    if match_count >= min_matches:
                        media_columns.append(col)
                        break

            if media_columns:
                media_columns_per_table[table] = media_columns

        return media_columns_per_table

    def _parse_date_safe(self, s: str) -> Optional[datetime]:
        """Legacy-compatible behavior preserved for this callable."""
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        log.warning(f"[Recovery] Invalid date format: {s}")
        return None
    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    
    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def _update_row(self, table: str, row: Dict[str, Any], mapping: Dict[str, str]) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            updated: Dict[str, Any] = {
                col: self._replace_ids_in_value(val, mapping)
                for col, val in row.items()
                if any(old in str(val) for old in mapping)
            }

            if not updated:
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            updated["last_media_recharge"] = datetime.now()

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.ensure_table_and_columns(
                table,
                data=updated,
                column_types={"last_media_recharge": "TIMESTAMP"},
            )

            row_id = row.get("id")
            if row_id is None:
                log.warning(f"[Recovery] Table '{table}' lacks 'id' column.")
                return

            self.db.update(table, updated, "id = ?", (row_id,))
            log.info(f"[Recovery] Updated {table}.id={row_id} ({len(updated)} cols).")

        except Exception as e:
            log.exception(f"[Recovery] DB update error on {table}.id={row.get('id')}: {e}")

    # ------------------------------------------------------------------
    # Internal implementation note: legacy behavior is preserved during modernization.
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        targets = self.scan_database()
        updated_rows = 0
        total_files = 0
        changed_files = 0
        unchanged_files = 0

        for table, row, col, fids in targets:
            mapping: Dict[str, str] = {}
            total_files += len(fids)
            for fid in fids:
                new_id = self._reupload(fid, col)
                if new_id:
                    mapping[fid] = new_id
                    if new_id != fid:
                        changed_files += 1
                    else:
                        unchanged_files += 1
                else:
                    unchanged_files += 1  # Internal implementation note: legacy behavior is preserved during modernization.

            if mapping:
                self._update_row(table, row, mapping)
                updated_rows += 1

        log.info(f"[Recovery] ✅ Finished. Rows updated: {updated_rows}, Total files: {total_files}, Changed IDs: {changed_files}, Unchanged IDs: {unchanged_files}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        report_text = (
            f"✅ Media Recovery Report:\n"
            f"Total rows scanned: {len(targets)}\n"
            f"Rows updated: {updated_rows}\n"
            f"Total files processed: {total_files}\n"
            f"File IDs changed: {changed_files}\n"
            f"File IDs unchanged: {unchanged_files}"
        )

        try:
            self.bot.send_message(self.upload_chat_id, report_text)
        except Exception as e:
            log.error(f"[Recovery] Failed to send report message: {e}")



# -----------------------------------------------------------------------------
#  Usage Example (uncomment and integrate in project)
# -----------------------------------------------------------------------------
"""
# db_manager = DatabaseManager(...)                  # شی دیتابیس
# bot        = telebot.TeleBot(BOT_TOKEN, threaded=True)
# recovery   = MediaRecoveryManager(
#     db=db_manager,
#     bot=bot,
#     upload_chat_id=PRIVATE_CHAT_ID,
#     max_threads=6,
#     chunk_size=200,
# )
# recovery.run()
"""