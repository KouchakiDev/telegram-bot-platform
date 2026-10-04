import os
import sys
import multiprocessing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, '..'))
"""
ماژول BotAdmin
این ماژول شامل کلاس BotAdmin است که مسئول راه‌اندازی و مدیریت ربات ادمین، پرسنل و مشتری در یک نقطه ورود مشترک می‌باشد.
"""
import re
import json
from telebot import TeleBot
from telebot.types import Message
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import BOT_AUTOREPONSER_TOKEN, DB_PARAMS


# -----------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# -----------------------------------------------------------------------------
BLACKLIST_QUESTIONS = {"/start", "back", "بازگشت"}
logger = CustomLogger("autoresponder")

class AutoResponder:
    """Legacy-compatible behavior preserved for this callable."""
    def __init__(self, bot: TeleBot, db: DatabaseManager, logger: CustomLogger, blacklist=None):
        self.bot = bot
        self.db = db
        self.logger = logger
        self.blacklist = blacklist or BLACKLIST_QUESTIONS
        self.logger.debug(f"Initialized AutoResponder: blacklist={self.blacklist}")
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        def _auto_answer_entry(message: Message):
            self.logger.debug(f"[Handler] Received message: chat_id={message.chat.id}, text={message.text}")
            handled = self.try_auto_answer(message)
            if handled:
                self.logger.debug(f"[Handler] Auto-answer sent for chat_id={message.chat.id}")
            else:
                self.logger.debug(f"[Handler] No auto-answer for chat_id={message.chat.id}")
            return

        self.bot.register_message_handler(
            _auto_answer_entry,
            content_types=["text"],
            func=lambda m: (m.chat.type == "private") and not m.from_user.is_bot,
        )
        self.logger.info("Auto-answer handler registered.")

    def try_auto_answer(self, message: Message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        text = (message.text or "").strip().lower()
        self.logger.debug(f"[AutoAnswer] Processing text: '{text}'")
        if not text:
            self.logger.debug("[AutoAnswer] Empty text, skipping.")
            return False
        if text in self.blacklist:
            self.logger.debug(f"[AutoAnswer] Text '{text}' is in blacklist, skipping.")
            return False

        try:
            answers = self.db.select_dict("auto_answers")
            self.logger.debug(f"[AutoAnswer] Fetched {len(answers)} records from auto_answers.")
            for rec in answers:
                q = rec.get("question", "").strip().lower()
                if not q:
                    self.logger.debug(f"[AutoAnswer] Skipping record id={rec.get('id')} with empty question.")
                    continue
                pattern = rf"\b{re.escape(q)}\b"
                self.logger.debug(f"[AutoAnswer] Testing pattern '{pattern}' for record id={rec.get('id')}.")
                if re.search(pattern, text):
                    answer = rec.get("answer", "")
                    self.logger.info(f"[AutoAnswer] Match: QID={rec.get('id')} question='{q}'")
                    self.logger.debug(f"[AutoAnswer] Sending answer: '{answer}' to chat_id={message.chat.id}")
                    self.bot.send_message(message.chat.id, answer)

                    new_cnt = int(rec.get("usage_count", 0)) + 1
                    self.logger.debug(f"[AutoAnswer] Upsocial_service usage_count for QID={rec.get('id')} to {new_cnt}")
                    self.db.update(
                        table_name="auto_answers",
                        data={"usage_count": new_cnt},
                        condition="id = ?",
                        params=(rec.get("id"),)
                    )
                    self.logger.info(
                        f"[AutoAnswer] Auto-answered QID {rec.get('id')} (usage={new_cnt}) for user {message.chat.id}"
                    )
                    return True
            self.logger.debug("[AutoAnswer] No matching question found.")
            return False
        except Exception as e:
            self.logger.exception(f"[AutoAnswer] Exception checking auto-answer for user {message.chat.id}: {e}")
            return False

    def run(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        self.logger.info("🤖 Bot is running... Polling started.")
        try:
            self.bot.polling(none_stop=True)
        except Exception as e:
            self.logger.exception(f"[Run] Polling failed: {e}")


def start_autoresponser_bot() -> None:
    """Legacy-compatible behavior preserved for this callable."""
    db = DatabaseManager(**DB_PARAMS)
    log = CustomLogger("admin_runner.log")
    log.info("[Start] Database initialized and logger set.")

    try:
        bot = TeleBot(BOT_AUTOREPONSER_TOKEN, parse_mode="HTML")
        log.debug(f"[Start] Bot token: {BOT_AUTOREPONSER_TOKEN[:10]}... (hidden)")
        responder = AutoResponder(bot, db, log, BLACKLIST_QUESTIONS)
        log.info("[Start] AutoResponder instance created. Starting run...")
        responder.run()
    except Exception as e:
        log.exception(f"[Start] Failed to start AutoResponder bot: {e}")

if __name__ == "__main__":
    start_autoresponser_bot()
