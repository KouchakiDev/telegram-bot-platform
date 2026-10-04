import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import MESSAGES, BUTTONS, REQUEST_TYPES, TABLE_NAME, COLUMN_NAMES, IGNORED_COLUMNS_CONFIG
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
import sqlite3

# Logger for RequestSettings events
log = CustomLogger("RequestSettings.log")


class RequestSettings:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager, back_to_main, back_to_settings):
        """
        Initialize RequestSettings with necessary dependencies.
        :param bot: Telebot instance for interacting with Telegram.
        :param db: DatabaseManager instance for database operations.
        :param back_to_main: Callback function to return to the main menu.
        :param back_to_settings: Callback function to return to the previous settings menu.
        """
        self.bot = bot
        self.db = db
        self.back_to_main = back_to_main
        self.back_to_settings = back_to_settings
        # Temporary storage for settings per chat
        self.temp_settings = {}
        # Temporary storage for user column selections (for checkboxes)
        self.user_selections = {}
        # Placeholders for request overview and details text
        self.request_overview_text = {}
        self.request_details_text = {}
        # Ignored columns set by admin for each table
        self.ignored_columns = {}
        log.info("RequestSettings initialized successfully.")

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def get_settings(self, table: str) -> dict | None:
        """Legacy-compatible behavior preserved for this callable."""
        query = """
            SELECT categorization_column, display_columns, max_requests_per_row, request_overview, request_details, ignored_columns 
            FROM bot_settings 
            WHERE table_name = ?
        """
        try:
            result = self.db.fetch_data(query, (table,))
            if result:
                (cat_col, disp_cols, max_per_row, overview,
                 details, ignored_cols) = result[0]
                disp_cols = disp_cols.split(",") if disp_cols else []
                ignored = ignored_cols.split(",") if ignored_cols else []
                return {
                    "categorization_column": cat_col,
                    "display_columns": disp_cols,
                    "max_requests_per_row": max_per_row,
                    "request_overview": overview or "",
                    "request_details": details or "",
                    "ignored_columns": ignored
                }
            return None
        except Exception as e:
            log.error(f"Error fetching settings for table {table}: {e}")
            return None

    def set_settings(self, table: str, settings: dict) -> None:
        """Legacy-compatible behavior preserved for this callable."""

        display_columns_str = ",".join(settings.get("display_columns", []))
        ignored_str = ",".join(settings.get("ignored_columns", []))
        # Internal implementation note: legacy behavior is preserved during modernization.
        ro = settings.get("request_overview", "")
        rd = settings.get("request_details", "")
        if isinstance(ro, list):
            ro = ",".join(ro)
        if isinstance(rd, list):
            rd = ",".join(rd)
        query = """
            INSERT OR REPLACE INTO bot_settings 
            (table_name, categorization_column, display_columns, max_requests_per_row, request_overview, request_details, ignored_columns)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.db.execute_query(query, (
                table,
                settings.get("categorization_column", ""),
                display_columns_str,
                settings.get("max_requests_per_row", 3),
                ro,
                rd,
                ignored_str
            ))
            log.info(f"Settings saved for table {table}.")
        except Exception as e:
            log.error(f"Error saving settings for table {table}: {e}")

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def main_settings_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        # Internal implementation note: legacy behavior is preserved during modernization.
        table_buttons = []
        for table_key, table_name in TABLE_NAME["table_names"].items():
            if self.db.column_exists(table_key, "status"):
                table_buttons.append(KeyboardButton(table_name))
        if table_buttons:
            markup.add(*table_buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(KeyboardButton(BUTTONS["manage_rejection_reasons"]))
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["request_settings_main_menu"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_main_menu_selection)

    def handle_main_menu_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.back_to_settings(message)
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
        elif text == BUTTONS["manage_rejection_reasons"]:
            self.manage_rejection_reasons(message)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            table = next(
                (k for k, v in TABLE_NAME["table_names"].items() if v == text), None)
            if not table:
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.main_settings_menu(message)
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            current_settings = self.get_settings(table) or {
                "categorization_column": "",
                "display_columns": [],
                "max_requests_per_row": 3,
                "request_overview": "",
                "request_details": "",
                "ignored_columns": []
            }
            self.temp_settings[chat_id] = {
                "table": table, "settings": current_settings.copy()}
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.table_settings_menu(message)

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def table_settings_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton(BUTTONS["set_categorization_column"]),
            KeyboardButton(BUTTONS["set_display_columns"])
        )
        markup.add(
            KeyboardButton(BUTTONS["set_request_overview"]),
            KeyboardButton(BUTTONS["set_request_details"])

        )
        markup.add(
            KeyboardButton(BUTTONS["set_ignored_columns"])
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(KeyboardButton(BUTTONS["help"]))
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["table_settings_menu"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_table_settings_selection)

    def handle_table_settings_selection(self, message):
        """
        Process selection from the table settings submenu.
        """
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.temp_settings.pop(chat_id, None)
            self.main_settings_menu(message)
        elif text == BUTTONS["back_to_main"]:
            self.temp_settings.pop(chat_id, None)
            self.back_to_main(message)
        elif text == BUTTONS["help"]:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, MESSAGES["help_table_settings"])
            self.table_settings_menu(message)
        elif text == BUTTONS["set_categorization_column"]:
            self.set_categorization_column(message)
        elif text == BUTTONS["set_display_columns"]:
            self.set_display_columns(message)
        elif text == BUTTONS["set_request_overview"]:
            self.set_request_overview_columns(message)
        elif text == BUTTONS["set_request_details"]:
            self.set_request_details_columns(message)
        elif text == BUTTONS["set_ignored_columns"]:
            self.set_ignored_columns(message)
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.table_settings_menu(message)

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def set_categorization_column(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if chat_id not in self.temp_settings:
            self.bot.send_message(chat_id, MESSAGES["session_expired"])
            self.main_settings_menu(message)
            return
        table = self.temp_settings[chat_id]["table"]
        columns = self.db.get_columns(table)
        # Internal implementation note: legacy behavior is preserved during modernization.
        ignored = self.temp_settings[chat_id]["settings"].get(
            "ignored_columns", [])
        available = [
            col for col in columns if col not in IGNORED_COLUMNS_CONFIG and col not in ignored]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for col in available:
            display_name = COLUMN_NAMES.get(col, col)
            status = "✅" if self.temp_settings[chat_id]["settings"].get(
                "categorization_column") == col else "❌"
            buttons.append(KeyboardButton(f"{status} {display_name}"))
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["help"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["select_categorization_column"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.process_categorization_column, available)

    def process_categorization_column(self, message, available):
        """
        Process the selection of the categorization column.
        """
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.table_settings_menu(message)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == BUTTONS["help"]:
            self.bot.send_message(chat_id, MESSAGES["help_set_categorization"])
            self.set_categorization_column(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        candidate = text.split(" ", 1)[1].strip() if " " in text else text
        selected = next(
            (col for col in available if COLUMN_NAMES.get(col, col) == candidate), None)
        if selected and selected in available:
            self.temp_settings[chat_id]["settings"]["categorization_column"] = selected
            self.set_settings(
                self.temp_settings[chat_id]["table"], self.temp_settings[chat_id]["settings"])
            self.bot.send_message(chat_id, MESSAGES["categorization_column_set"].format(
                text=COLUMN_NAMES.get(selected, selected)))
            self.table_settings_menu(message)

        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.set_categorization_column(message)

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def set_display_columns(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if chat_id not in self.temp_settings:
            self.bot.send_message(chat_id, MESSAGES["session_expired"])
            self.main_settings_menu(message)
            return
        table = self.temp_settings[chat_id]["table"]
        columns = self.db.get_columns(table)
        ignored = self.temp_settings[chat_id]["settings"].get(
            "ignored_columns", [])
        available = [
            col for col in columns if col not in IGNORED_COLUMNS_CONFIG and col not in ignored]
        self.user_selections[chat_id] = self.temp_settings[chat_id]["settings"].get(
            "display_columns", []).copy()
        self.show_display_columns(
            chat_id, available, self.user_selections[chat_id])

    def show_display_columns(self, chat_id, available, selected_columns):
        """
        Display available display columns with checkbox status in rows of 3.
        """
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for col in available:
            display_name = COLUMN_NAMES.get(col, col)
            status = "✅" if col in selected_columns else "❌"
            buttons.append(KeyboardButton(f"{status} {display_name}"))
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(*buttons)
        buttons.clear()
        markup.add(KeyboardButton(BUTTONS["help"]))
        markup.add(KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["select_display_columns"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.process_display_columns, available)

    def process_display_columns(self, message, available):
        """
        Process user's selection of display columns.
        """
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.table_settings_menu(message)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == BUTTONS["help"]:
            self.bot.send_message(chat_id, MESSAGES["help_set_display_columns"])
            self.set_display_columns(message)
            return
        elif text == BUTTONS["confirm"]:
            if not self.user_selections.get(chat_id):
                self.bot.send_message(
                    chat_id, "⚠️ حداقل یک ستون باید انتخاب شود.")
                self.show_display_columns(
                    chat_id, available, self.user_selections[chat_id])
                return
            self.temp_settings[chat_id]["settings"]["display_columns"] = self.user_selections.get(
                chat_id, [])
            self.set_settings(
                self.temp_settings[chat_id]["table"], self.temp_settings[chat_id]["settings"])
            self.bot.send_message(chat_id, MESSAGES["display_columns_set"].format(
                columns=" | ".join([COLUMN_NAMES.get(col, col)
                                  for col in self.user_selections.get(chat_id, [])])
            ))
            self.table_settings_menu(message)
            return

        candidate = text.split(" ", 1)[1].strip() if " " in text else text
        # Internal implementation note: legacy behavior is preserved during modernization.
        if candidate in [COLUMN_NAMES.get(col, col) for col in available]:
            real_col = next(
                (col for col in available if COLUMN_NAMES.get(col, col) == candidate), None)
            if real_col:
                current = self.user_selections.get(chat_id, [])
                if real_col in current:
                    current.remove(real_col)
                else:
                    current.append(real_col)
                self.user_selections[chat_id] = current
                self.show_display_columns(chat_id, available, current)
            else:
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.show_display_columns(
                    chat_id, available, self.user_selections.get(chat_id, []))
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.show_display_columns(
                chat_id, available, self.user_selections.get(chat_id, []))

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def set_request_overview_columns(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if chat_id not in self.temp_settings:
            self.bot.send_message(chat_id, MESSAGES["session_expired"])
            self.main_settings_menu(message)
            return
        table = self.temp_settings[chat_id]["table"]
        columns = self.db.get_columns(table)
        # Internal implementation note: legacy behavior is preserved during modernization.
        ignored = self.temp_settings[chat_id]["settings"].get(
            "ignored_columns", [])
        available = [
            col for col in columns if col not in IGNORED_COLUMNS_CONFIG and col not in ignored]
        # Internal implementation note: legacy behavior is preserved during modernization.
        ro = self.temp_settings[chat_id]["settings"].get(
            "request_overview", "")
        if isinstance(ro, str):
            ro_list = ro.split(",") if ro.strip() else []
        elif isinstance(ro, list):
            ro_list = ro
        else:
            ro_list = []
        self.user_selections[chat_id] = ro_list.copy()

        self.show_request_overview_columns(
            chat_id, available, self.user_selections[chat_id])

    def show_request_overview_columns(self, chat_id, available, selected_columns):
        """Legacy-compatible behavior preserved for this callable."""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for col in available:
            display_name = COLUMN_NAMES.get(col, col)
            status = "✅" if col in selected_columns else "❌"
            buttons.append(KeyboardButton(f"{status} {display_name}"))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["help"]))
        markup.add(KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["select_request_overview_columns"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.process_request_overview_columns, available)

    def process_request_overview_columns(self, message, available):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.table_settings_menu(message)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == BUTTONS["help"]:
            self.bot.send_message(
                chat_id, "ℹ️ با کلیک روی دکمه‌ها، ستون‌های مورد نظر را برای نمایش در کلیات درخواست انتخاب یا از انتخاب خارج کنید.")
            self.set_request_overview_columns(message)
            return
        elif text == BUTTONS["confirm"]:
            self.temp_settings[chat_id]["settings"]["request_overview"] = self.user_selections.get(
                chat_id, [])
            self.set_settings(
                self.temp_settings[chat_id]["table"], self.temp_settings[chat_id]["settings"])
            self.bot.send_message(chat_id, MESSAGES["request_overview_set"].format(
                text=" | ".join([COLUMN_NAMES.get(col, col)
                                 for col in self.user_selections.get(chat_id, [])])
            ))
            self.table_settings_menu(message)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        candidate = text.split(" ", 1)[1].strip() if " " in text else text
        if candidate in [COLUMN_NAMES.get(col, col) for col in available]:
            real_col = next(
                (col for col in available if COLUMN_NAMES.get(col, col) == candidate), None)
            if real_col:
                current = self.user_selections.get(chat_id, [])
                if real_col in current:
                    current.remove(real_col)
                else:
                    current.append(real_col)
                self.user_selections[chat_id] = current
                self.show_request_overview_columns(chat_id, available, current)
            else:
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.show_request_overview_columns(
                    chat_id, available, self.user_selections.get(chat_id, []))
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.show_request_overview_columns(
                chat_id, available, self.user_selections.get(chat_id, []))

    def set_request_details_columns(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if chat_id not in self.temp_settings:
            self.bot.send_message(chat_id, MESSAGES["session_expired"])
            self.main_settings_menu(message)
            return
        table = self.temp_settings[chat_id]["table"]
        columns = self.db.get_columns(table)
        ignored = self.temp_settings[chat_id]["settings"].get(
            "ignored_columns", [])
        available = [
            col for col in columns if col not in IGNORED_COLUMNS_CONFIG and col not in ignored]
        rd = self.temp_settings[chat_id]["settings"].get("request_details", "")
        if isinstance(rd, str):
            rd_list = rd.split(",") if rd.strip() else []
        elif isinstance(rd, list):
            rd_list = rd
        else:
            rd_list = []
        self.user_selections[chat_id] = rd_list.copy()

        self.show_request_details_columns(
            chat_id, available, self.user_selections[chat_id])

    def show_request_details_columns(self, chat_id, available, selected_columns):
        """Legacy-compatible behavior preserved for this callable."""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for col in available:
            display_name = COLUMN_NAMES.get(col, col)
            status = "✅" if col in selected_columns else "❌"
            buttons.append(KeyboardButton(f"{status} {display_name}"))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["help"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["select_request_details_columns"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.process_request_details_columns, available)

    def process_request_details_columns(self, message, available):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.table_settings_menu(message)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == BUTTONS["help"]:
            self.bot.send_message(
                chat_id, "ℹ️ با کلیک روی دکمه‌ها، ستون‌های مورد نظر برای نمایش در جزییات درخواست انتخاب یا از انتخاب خارج می‌شوند.")
            self.set_request_details_columns(message)
            return
        elif text == BUTTONS["confirm"]:
            self.temp_settings[chat_id]["settings"]["request_details"] = self.user_selections.get(
                chat_id, [])
            self.set_settings(
                self.temp_settings[chat_id]["table"], self.temp_settings[chat_id]["settings"])
            self.bot.send_message(chat_id, MESSAGES["request_details_set"].format(
                text=" | ".join([COLUMN_NAMES.get(col, col)
                                  for col in self.user_selections.get(chat_id, [])])
            ))
            self.table_settings_menu(message)
            return

        candidate = text.split(" ", 1)[1].strip() if " " in text else text
        if candidate in [COLUMN_NAMES.get(col, col) for col in available]:
            real_col = next(
                (col for col in available if COLUMN_NAMES.get(col, col) == candidate), None)
            if real_col:
                current = self.user_selections.get(chat_id, [])
                if real_col in current:
                    current.remove(real_col)
                else:
                    current.append(real_col)
                self.user_selections[chat_id] = current
                self.show_request_details_columns(chat_id, available, current)
            else:
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.show_request_details_columns(
                    chat_id, available, self.user_selections.get(chat_id, []))
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.show_request_details_columns(
                chat_id, available, self.user_selections.get(chat_id, []))

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    def set_request_details(self, message):
        """
        Allow admin to set the detailed text that is displayed when 'View More Details' is clicked.
        """
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id, MESSAGES["enter_request_details"], reply_markup=ReplyKeyboardRemove())
        self.bot.register_next_step_handler(
            message, self.process_request_details)

    def process_request_details(self, message):
        """
        Save the entered request details text.
        """
        chat_id = message.chat.id
        details_text = message.text.strip()
        if not details_text:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.set_request_details(message)
            return
        self.temp_settings[chat_id]["settings"]["request_details"] = details_text
        self.bot.send_message(
            chat_id, MESSAGES["request_details_set"].format(text=details_text))
        self.table_settings_menu(message)

        #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################

    def set_ignored_columns(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if chat_id not in self.temp_settings:
            self.bot.send_message(chat_id, MESSAGES["session_expired"])
            self.main_settings_menu(message)
            return
        table = self.temp_settings[chat_id]["table"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        columns = self.db.get_columns(table)
        # Internal implementation note: legacy behavior is preserved during modernization.
        available = [
            col for col in columns if col not in IGNORED_COLUMNS_CONFIG]
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_selections[chat_id] = self.temp_settings[chat_id]["settings"].get(
            "ignored_columns", []).copy()
        self.show_ignored_columns(
            chat_id, available, self.user_selections[chat_id])

    def show_ignored_columns(self, chat_id, available, selected_columns):
        """Legacy-compatible behavior preserved for this callable."""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []
        for col in available:
            display_name = COLUMN_NAMES.get(col, col)
            status = "✅" if col in selected_columns else "❌"
            buttons.append(KeyboardButton(f"{status} {display_name}"))
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(*buttons)
        buttons.clear()
        markup.add(KeyboardButton(BUTTONS["help"]),
                   KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["select_ignored_columns"], reply_markup=markup)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self.process_ignored_columns, available)

    def process_ignored_columns(self, message, available):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.table_settings_menu(message)
            return
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        elif text == BUTTONS["help"]:
            self.bot.send_message(chat_id, MESSAGES["help_set_ignored_columns"])
            self.set_ignored_columns(message)
            return
        elif text == BUTTONS["confirm"]:
            self.temp_settings[chat_id]["settings"]["ignored_columns"] = self.user_selections.get(
                chat_id, [])
            self.set_settings(
                self.temp_settings[chat_id]["table"], self.temp_settings[chat_id]["settings"])
            self.bot.send_message(chat_id, MESSAGES["ignored_columns_set"].format(
                columns=" | ".join([COLUMN_NAMES.get(col, col)
                                  for col in self.user_selections.get(chat_id, [])])
            ))
            self.table_settings_menu(message)
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        candidate = text.split(" ", 1)[1].strip() if " " in text else text
        # Internal implementation note: legacy behavior is preserved during modernization.
        if candidate in [COLUMN_NAMES.get(col, col) for col in available]:
            real_col = next(
                (col for col in available if COLUMN_NAMES.get(col, col) == candidate), None)
            if real_col:
                current = self.user_selections.get(chat_id, [])
                if real_col in current:
                    current.remove(real_col)
                else:
                    current.append(real_col)
                self.user_selections[chat_id] = current
                self.show_ignored_columns(chat_id, available, current)
            else:
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.show_ignored_columns(
                    chat_id, available, self.user_selections.get(chat_id, []))
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.show_ignored_columns(
                chat_id, available, self.user_selections.get(chat_id, []))

    def manage_rejection_reasons(self, message):
        """Display the menu for managing rejection reasons."""
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton(BUTTONS["add_reason"]),
            KeyboardButton(BUTTONS["edit_reason"]),
            KeyboardButton(BUTTONS["delete_reason"]),
            KeyboardButton(BUTTONS["back_to_previous"]),
            KeyboardButton(BUTTONS["back_to_main"])
        )
        self.bot.send_message(
            chat_id, MESSAGES["manage_reasons"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_rejection_reason_management)

    def handle_rejection_reason_management(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.table_settings_menu(message)
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
        elif text == BUTTONS["add_reason"]:
            self.bot.send_message(
                chat_id, MESSAGES["add_rejection_reason_title"], reply_markup=ReplyKeyboardRemove())
            self.bot.register_next_step_handler(
                message, self.process_new_rejection_reason)
        elif text == BUTTONS["edit_reason"]:
            self.show_rejection_reasons_for_edit(message)
        elif text == BUTTONS["delete_reason"]:
            self.show_rejection_reasons_for_delete(message)
        else:
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.manage_rejection_reasons(message)

    def process_new_rejection_reason(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        reason = message.text.strip()
        if len(reason) < 3:
            self.bot.send_message(chat_id, MESSAGES["reason_too_short"])
            self.bot.register_next_step_handler(
                message, self.process_new_rejection_reason)
            return
        try:
            self.db.insert("rejection_reasons", {"reason": reason})
            self.bot.send_message(
                chat_id, MESSAGES["reason_added"].format(reason=reason))
            log.info(
                f"New rejection reason '{reason}' added by chat {chat_id}.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.manage_rejection_reasons(message)
        except sqlite3.IntegrityError:
            self.bot.send_message(chat_id, MESSAGES["reason_exists"])
            log.warning(
                f"Attempt to add duplicate reason '{reason}' by chat {chat_id}.")
            self.bot.register_next_step_handler(
                message, self.process_new_rejection_reason)
        except Exception as e:
            log.error(
                f"Error adding reason '{reason}' for chat {chat_id}: {e}")
            self.bot.send_message(chat_id, MESSAGES["error"])
            self.manage_rejection_reasons(message)

    def show_rejection_reasons_for_edit(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        reasons = self.db.select_dict("rejection_reasons")
        if not reasons:
            self.bot.send_message(chat_id, MESSAGES["no_reasons_available"])
            self.manage_rejection_reasons(message)
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        butttons = []
        for r in reasons:
            butttons.append(KeyboardButton(r["reason"]))
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup.add(*butttons)
        butttons.clear()
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["edit_rejection_reason_select"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_edit_reason_selection)

    def show_rejection_reasons_for_delete(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        reasons = self.db.select_dict("rejection_reasons")
        if not reasons:
            self.bot.send_message(chat_id, MESSAGES["no_reasons_available"])
            self.manage_rejection_reasons(message)
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for r in reasons:
            buttons.append(KeyboardButton(r["reason"]))

        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            chat_id, MESSAGES["delete_rejection_reason_select"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_delete_reason_selection)

    def process_edit_reason_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        reason = message.text.strip()
        if reason == BUTTONS["back_to_previous"]:
            self.manage_rejection_reasons(message)
            return
        elif reason == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not self.db.select_dict("rejection_reasons", "reason = ?", (reason,)):
            self.bot.send_message(chat_id, MESSAGES["reason_not_found"])
            self.show_rejection_reasons_for_edit(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.send_message(
            chat_id, MESSAGES["enter_new_reason"], reply_markup=ReplyKeyboardRemove())
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(
            message, self.update_rejection_reason, reason)

    def process_delete_reason_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        reason = message.text.strip()
        if reason == BUTTONS["back_to_previous"]:
            self.manage_rejection_reasons(message)
            return
        elif reason == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not self.db.select_dict("rejection_reasons", "reason = ?", (reason,)):
            self.bot.send_message(chat_id, MESSAGES["reason_not_found"])
            self.show_rejection_reasons_for_delete(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.delete("rejection_reasons", "reason = ?", (reason,))
        self.bot.send_message(
            chat_id, MESSAGES["reason_deleted"].format(reason=reason))
        log.info(f"Reason '{reason}' deleted by chat {chat_id}.")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.manage_rejection_reasons(message)

    def update_rejection_reason(self, message, old_reason):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        new_reason = message.text.strip()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if len(new_reason) < 3:
            self.bot.send_message(chat_id, MESSAGES["reason_too_short"])
            self.bot.register_next_step_handler(
                message, self.update_rejection_reason, old_reason)
            return

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update("rejection_reasons", {
                           "reason": new_reason}, "reason = ?", (old_reason,))
            self.bot.send_message(chat_id, MESSAGES["reason_updated"].format(
                old_reason=old_reason, new_reason=new_reason))
            log.info(
                f"Reason updated from '{old_reason}' to '{new_reason}' by chat {chat_id}.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.manage_rejection_reasons(message)
        except sqlite3.IntegrityError:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, MESSAGES["reason_exists"])
            log.warning(
                f"Attempt to update to duplicate reason '{new_reason}' by chat {chat_id}.")
            self.bot.register_next_step_handler(
                message, self.update_rejection_reason, old_reason)
        except Exception as e:
            log.error(
                f"Error upsocial_service reason from '{old_reason}' to '{new_reason}' for chat {chat_id}: {e}")
            self.bot.send_message(chat_id, MESSAGES["error"])
            self.manage_rejection_reasons(message)

    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    #############################################################
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
