# notification_manager.py

from telebot import TeleBot, apihelper
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import DYNAMIC_NOTIFICATION_CONFIG
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger


class NotificationManager:
    """
    NotificationManager:

    This class is responsible for sending dynamic notifications to users
    based on request type and status (approved, rejected, blocked).

    Key Features:
      - Supports multiple bots (e.g. staff, client, admin)
      - Fetches user information from the database
      - Generates custom messages using dynamic templates
      - Can be used for any new request type without code modification
    """

    def __init__(self, bots: dict, db: DatabaseManager):
        """
        :param bots: A dictionary of bot keys and TeleBot instances.
                     Example: {'staff': telebot1, 'client': telebot2}
        :param db: An instance of DatabaseManager for database access.
        """
        self.bots = bots
        self.db = db
        self.logger = CustomLogger("notifications.log")

    def send_notification(self, telegram_id, request_type: str, request_id: int, status: str, extra: str = "") -> bool:
        """
        Sends a notification based on request type and current status.

        :param telegram_id: Optional fallback Telegram ID (used if not found in DB).
        :param request_type: String identifier of request type, e.g., 'staff.ad_request'
        :param request_id: ID of the request in the DB.
        :param status: One of ['approved', 'rejected', 'blocked']
        :param extra: Optional extra message (e.g. rejection reason)
        :return: True if successful, False otherwise.
        """
        try:
            config = DYNAMIC_NOTIFICATION_CONFIG.get(request_type)
            if not config:
                self.logger.warning(
                    f"[NotificationManager] No config found for request_type='{request_type}'. Skipping notification.")
                return False

            table = config.get("table")
            bot_key = config.get("bot")
            template = config.get("template", {}).get(status)

            if not all([table, bot_key, template]):
                self.logger.error(
                    f"[NotificationManager] Incomplete config for request_type='{request_type}': "
                    f"Missing table, bot key, or template.")
                return False

            # Fetching request data from DB
            result = self.db.select_dict(table, "id = ?", (request_id,))
            if not result:
                self.logger.warning(
                    f"[NotificationManager] No request with ID={request_id} found in table '{table}'.")
                return False

            data = result[0]
            chat_id = data.get("telegram_id", telegram_id)

            if not chat_id:
                self.logger.warning(
                    f"[NotificationManager] Telegram ID not found for request_type='{request_type}', ID={request_id}.")
                return False

            # Format the message
            message = self._format_template(template, data, extra)

            # Select the appropriate bot
            bot = self.bots.get(bot_key)
            if not bot:
                self.logger.error(
                    f"[NotificationManager] Bot with key '{bot_key}' not found in self.bots.")
                return False

            bot.send_message(chat_id, message,parse_mode= "Markdown")

            self.logger.info(
                f"[NotificationManager] ✅ Notification sent to chat_id={chat_id} | "
                f"type={request_type} | status={status} | id={request_id}")
            return True

        except apihelper.ApiException as api_ex:
            self.logger.error(
                f"[NotificationManager] Telegram API error while sending message | "
                f"type={request_type} | id={request_id} | error={api_ex}")
            return False
        except Exception as e:
            self.logger.error(
                f"[NotificationManager] 🔥 Unexpected error in send_notification | "
                f"type={request_type} | id={request_id} | error={e}")
            return False

    def _format_template(self, template: str, data: dict, extra: str) -> str:
        """
        Fills in the template using request data.

        :param template: The message template with placeholders.
        :param data: The dictionary of values to replace in the template.
        :param extra: Additional content to append.
        :return: Formatted message.
        """
        try:
            return template.format(**data, extra=extra)
        except KeyError as ke:
            self.logger.error(
                f"[NotificationManager] Missing key '{ke}' in request data for template formatting.")
            return f"{template}\n⚠️ Extra Info: {extra}"
