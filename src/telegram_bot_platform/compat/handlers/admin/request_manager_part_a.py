from __future__ import annotations

from .request_manager_context import *


class RequestManagerPartAMixin:
    def format_label_value(self, key, value):
        label = field_labels.get(key, key)
        if key in ("U_code", "PU_code") and value:
            return f"{label} : /{value}"
        return f"{label} : {value}"
    def get_request_type(self, table):
        settings = self.settings.get(table)
        if settings and "type" in settings:
            return settings["type"]
        return 1
    def is_back(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not isinstance(message, Message):
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            text = message.text
            if not text:
                return False
            log.debug(text)
            text = text.strip()
            chat_id = message.chat.id
            args = message.text.split()
            regexp=r'^/p\d+$'
            if re.match(regexp , text):
                self.parent.ProfPer.handle_staff_profile(message)
            elif len(args) > 1:
                param = args[1]
                regexp = r'^p\d+$'
                if re.match(regexp , param):
                    message.text = f"/{param}"
                    self.parent.ProfPer.handle_staff_profile(message)
            elif text.startswith("/start"):
                self.back_to_main(message)
                return True
            elif BUTTONS["back_to_previous"] in text:
                self.back_to_pervious(message)
                return True
            elif BUTTONS["back_to_main"] in text:
                self.back_to_main(message)
                return True
        except Exception as e:
            logger.exception(f"[MessagesHandler.is_back] Exception occurred: {e}")
            return False
    def normalize_phone_number(self , number: Union[str, int, bytes], with_plus: bool = True) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        log.debug("normalize_phone_number called with number=%r, with_plus=%s", number, with_plus)
        # 1) Validate None
        if number is None:
            log.error("Input number is None")
            return number
        # 2) Convert to string
        if isinstance(number, bytes):
            try:
                number_str = number.decode('utf-8')
                log.debug("Decoded bytes to string: %r", number_str)
            except UnicodeDecodeError as e:
                log.exception("UTF-8 decoding error")
                return number
        else:
            number_str = str(number)
            log.debug("Converted input to string: %r", number_str)
        # 3) Normalize digits and remove separators
        cleaned = number_str.translate(_P2E)
        log.debug("After Persian->English digits: %r", cleaned)
        for sep in (' ', '-', '(', ')', '.'):
            cleaned = cleaned.replace(sep, '')
        log.debug("After removing separators: %r", cleaned)
        cleaned = cleaned.lstrip()
        log.debug("After stripping leading whitespace: %r", cleaned)
        # 4) Remove international prefixes: '+', '00', '98', '0'
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
            log.debug("Removed '+': %r", cleaned)
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
            log.debug("Removed '00': %r", cleaned)
        if cleaned.startswith('98'):
            cleaned = cleaned[2:]
            log.debug("Removed '98': %r", cleaned)
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
            log.debug("Removed leading '0': %r", cleaned)
        # 5) Validate final pattern: exactly 10 digits starting with '9'
        if not re.fullmatch(r"9\d{9}", cleaned):
            log.error("Validation failed for cleaned number: %r", cleaned)
            return number
        # 6) Prepend country code and return
        normalized = f"98{cleaned}"
        result = f"+{normalized}" if with_plus else normalized
        log.info("Normalized phone number: %r", result)
        return result
    def add_back_buttons(self, markup):
        """Legacy-compatible behavior preserved for this callable."""
        buttons = [
            KeyboardButton(BUTTONS["back_to_main"]),
            KeyboardButton(BUTTONS["back_to_previous"])
        ]
        markup.add(*buttons)
        return markup
    def is_dict_column(self, table, column_name):
        """Legacy-compatible behavior preserved for this callable."""
        data = self.db.select_dict(table, f"{column_name} IS NOT NULL")
        return bool(data) and isinstance(data[0].get(column_name), str) and self.is_json_dict(data[0][column_name])
    def is_json_dict(self, s):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            obj = json.loads(s)
            return isinstance(obj, dict)
        except:
            return False
    @staticmethod
    def invert_dict(d: dict) -> dict:
        return {v: k for k, v in d.items()}
    def create_checkbox_panel(self, message, chat_id, table, column_name):
        """Legacy-compatible behavior preserved for this callable."""
        db_row = self.db.select_dict(
            table, "id = ?", (self.current_request[chat_id][1],))
        original_dict = {}
        # field_labels
        if db_row and db_row[0].get(column_name):
            try:
                original_dict = json.loads(db_row[0][column_name])
            except:
                original_dict = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        display_keys = [k for k, v in original_dict.items()]
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_review_dict[chat_id] = {
            k: True for k in display_keys
        }
        # markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup = self.request_actions_menu(True, True)
        buttons = []
        for key in display_keys:
            label = field_labels.get(key, key)
            value = self.temp_review_dict[chat_id][key]
            icon = "✅" if value else "❌"
            buttons.append(KeyboardButton(f"{icon} {label}"))
        for i in range(0, len(buttons), 2):
            markup.add(*buttons[i:i + 2])
        markup.add(KeyboardButton(BUTTONS["submit_request"]))
        markup = self.add_back_buttons(markup)
        header = self.settings.get(table, {}).get(
            "review_header", "موارد زیر را بررسی و در صورت نیاز رد کنید:")
        self.bot.send_message(chat_id, header, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.toggle_review_checkbox)  # bananas
    def show_check_box(self, message, table):
        chat_id = message.chat.id
        check_boxs = self.temp_review_dict.get(chat_id, {})
        markup = self.request_actions_menu(True, True)
        buttons = []
        for box in check_boxs:
            label = field_labels.get(box, box)
            status = "✅" if check_boxs[box] else "❌"
            buttons.append(KeyboardButton(
                f"{status} {label}"))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["submit_request"]))
        markup = self.add_back_buttons(markup)
        header = self.settings.get(table, {}).get(
            "review_header", "موارد زیر را بررسی و در صورت نیاز رد کنید:")
        self.bot.send_message(
            chat_id, header, reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.toggle_review_checkbox)
    def toggle_review_checkbox(self, message):
        chat_id = message.chat.id
        text = message.text
        if self.is_back(message):
            return
        if text == BUTTONS["view_more_details"]:
            table, request_id, review_column = self.current_request[chat_id]
            self.send_full_details(chat_id, table, request_id)
            self.show_check_box(message, table)  # Internal implementation note: legacy behavior is preserved during modernization.
            return
        if text == BUTTONS["edit"]:
            # line 1804
            edit_label = BUTTONS["edit"]
            # print(f"clicked on the {edit_label}")
            self.edit_request_fields(message)
            return
        if text == BUTTONS["submit_request"]:
            table, request_id, review_column = self.current_request[chat_id]
            self.handle_submit_request(message, chat_id, table, review_column)
            return
        if self.is_back(message):
            return
        if not (text.startswith("✅") or text.startswith("❌")):
            return
        label = text[2:].strip()
        conv = self.invert_dict(field_labels)
        label = conv.get(label, label)
        if label in self.temp_review_dict[chat_id]:
            self.temp_review_dict[chat_id][label] = not self.temp_review_dict[chat_id][label]
        table, request_id, review_column = self.current_request[chat_id]
        self.show_check_box(message, table)
    def handle_submit_request(self, message, chat_id, table, review_column):
        """Legacy-compatible behavior preserved for this callable."""
        conv = self.invert_dict(field_labels)
        updated_dict = {
            conv.get(k, k): v for k, v in self.temp_review_dict.get(chat_id, {}).items()
        }
        if self.is_back(message):
            return
        false_fields = [k for k, v in updated_dict.items() if not v]
        if false_fields:
            self.temp_updated_dict[chat_id] = updated_dict
            self.pending_rejection_fields[chat_id] = false_fields
            first_field = false_fields[0]
            self.bot.send_message(
                chat_id,
                f"لطفاً دلیل رد برای {field_labels.get(first_field, first_field)} را وارد کنید:"
            )
            if self.rejection_reason_menu(chat_id):
                self.bot.register_next_step_handler(
                    message,
                    self.handle_field_rejection_reason,
                    table,
                    self.current_request[chat_id][1],
                    first_field,
                    self.current_request[chat_id][2]  # review_column
                )
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(table, {
                review_column: json.dumps(updated_dict, ensure_ascii=False),
                "status": "approved"
            }, "id = ?", (self.current_request[chat_id][1],))
            self.notify_user(
                table, self.current_request[chat_id][1], "approved")
            self.bot.send_message(chat_id, "درخواست تایید شد.")
            del self.current_request[chat_id]
            if chat_id in self.temp_review_dict:
                del self.temp_review_dict[chat_id]
            self.requests_menu(message, chat_id, table)
    def ask_rejection_reasons(self, message, chat_id, table, review_column, updated_dict):
        """Legacy-compatible behavior preserved for this callable."""
        rejection_items = [key for key,
                           value in updated_dict.items() if not value]
        if self.is_back(message):
            return
        if rejection_items:
            self.pending_rejection_fields[chat_id] = rejection_items
            first_field = rejection_items[0]
            # Internal implementation note: legacy behavior is preserved during modernization.
            shown = self.rejection_reason_menu(chat_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if shown:
                self.bot.send_message(
                    chat_id,
                    f"لطفاً دلیل رد برای {field_labels.get(first_field, first_field)} را وارد کنید:"
                )
                self.bot.register_next_step_handler(
                    message,
                    self.handle_field_rejection_reason,
                    table,
                    self.current_request[chat_id][1],  # request_id
                    first_field,
                    review_column
                )
    def handle_field_rejection_reason(self, message, table, request_id, field, review_column):
        chat_id = message.chat.id
        reason = message.text.strip()
        if self.is_back(message):
            return
        try:
            if reason:
                if reason == BUTTONS["back_to_previous"]:
                    self.requests_menu(message, chat_id, table)
                    return
                elif reason == BUTTONS["back_to_main"]:
                    del self.current_request[chat_id]
                    self.back_to_main(message)
                    return
                elif reason == DEFAULT_REASONS[1]:
                    self.bot.send_message(
                        chat_id, MESSAGES["enter_custom_reason"], reply_markup=ReplyKeyboardRemove())
                    self.bot.register_next_step_handler(
                        message, self.handle_custom_rejection_reason, table, request_id, True)
                    return
            now = datetime.now().strftime("%Y/%m/%d ⏰ %H:%M")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if chat_id not in self.temp_rejections:
                self.temp_rejections[chat_id] = {}
            self.temp_rejections[chat_id][field] = {
                "reason": reason,
                "date": now
            }
            pending = self.pending_rejection_fields.get(chat_id, [])
            if field in pending:
                pending.remove(field)
            if pending:
                next_field = pending[0]
                self.bot.send_message(
                    chat_id, f"لطفاً دلیل رد برای {field_labels.get(next_field, next_field)} را وارد کنید:")
                if self.rejection_reason_menu(chat_id):
                    self.bot.register_next_step_handler(
                        message, self.handle_field_rejection_reason, table, request_id, next_field, review_column)
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                updated_dict = self.temp_updated_dict.get(chat_id, {})
                self.db.update(table, {
                    review_column: json.dumps(updated_dict, ensure_ascii=False),
                    "rejection_reason": json.dumps(self.temp_rejections[chat_id], ensure_ascii=False),
                    "status": "approved"
                }, "id = ?", (request_id,))
                extra_lines = []
                for f, data in self.temp_rejections[chat_id].items():
                    label = field_labels.get(f, f)
                    reason_text = data.get("reason", "بدون دلیل مشخص")
                    extra_lines.append(
                        f"❌ {label} رد شده به دلیل: {reason_text}")
                extra_text = "\n\n" + \
                    "\n".join(extra_lines) if extra_lines else ""
                self.notify_user(table, request_id, "approved",
                                 extra_message=extra_text)
                # Internal implementation note: legacy behavior is preserved during modernization.
                del self.current_request[chat_id]
                self.temp_updated_dict.pop(chat_id, None)
                self.temp_review_dict.pop(chat_id, None)
                self.pending_rejection_fields.pop(chat_id, None)
                self.temp_rejections.pop(chat_id, None)
                self.bot.send_message(
                    chat_id, "✅ همه دلایل ثبت شدند و درخواست تایید شد.")
                self.requests_menu(message, chat_id, table)
        except Exception as e:
            log.exception(f"Error in handle_field_rejection_reason: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_menu(message, chat_id, table)
    def requests_main_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        try:
            tables = self.settings.keys()
            # print(tables)
            buttons = []
            for table in tables:
                try:
                    if self.db.table_exists(table):
                        table_translate = self.settings[table]["Translate"]["table_name"]
                        count = self.db.count_rows(
                            table, f'{self.settings[table]["status_column"]} = ?', ('pending',))
                        if count > 0:
                            buttons.append(KeyboardButton(
                                f"درخواست‌های {table_translate} ({count})"))
                    else:
                        continue
                except Exception as e:
                    log.exception(f"Error :{e}")
            if not buttons:
                self.bot.send_message(chat_id, MESSAGES["no_pending_requests"])
                self.back_to_pervious(message)
                return
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*buttons)
            markup = self.add_back_buttons(markup)
            self.bot.send_message(
                chat_id, MESSAGES["select_request_type"], reply_markup=markup)
            log.info(
                f"Main menu displayed for chat {chat_id} with {len(buttons)} tables.")
            self.bot.register_next_step_handler(message, self.route_menu)
        except Exception as e:
            log.exception(
                f"Error in requests_main_menu for chat {chat_id}: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.back_to_main(message)
    def requests_menu(self, message, chat_id, table):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        try:
            settings = self.settings.get(table)
            if not settings:
                self.bot.send_message(
                    chat_id, MESSAGES["error_processing_action"])
                return
            categorization = settings.get("categorization_column")
            status_column = settings.get("status_column", "status")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if categorization and self.db.column_exists(table, categorization):
                query = f"SELECT {categorization}, COUNT(*) as count FROM {table} WHERE {status_column} = 'pending' GROUP BY {categorization}"
                categorization_data = self.db.fetch_data(query, ())
                if categorization_data:
                    markup = ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                    buttons = []
                    for row in categorization_data:
                        category_value = row[0] if row[0] else "نامشخص"
                        count = row[1]
                        buttons.append(KeyboardButton(
                            f"درخواست‌های {category_value} ({count})"))
                    markup.add(*buttons)
                    markup = self.add_back_buttons(markup)
                    self.bot.send_message(
                        chat_id, MESSAGES["choose_request_category"], reply_markup=markup)
                    log.info(
                        f"Categorization menu displayed for table {table} with {len(categorization_data)} categories.")
                    self.bot.register_next_step_handler(
                        message, self.handle_request_selection, table)
                    return
            dbtype = settings.get("type", 1)
            display_columns = settings.get("display_columns")
            if dbtype == 1:
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                query = f"SELECT id, {', '.join(display_columns)} FROM {table} WHERE {status_column} = 'pending'"
                requests = self.db.fetch_data(query, ())
                if not requests:
                    self.requests_main_menu(message)
                    return
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                buttons = []
                for req in requests:
                    req_id = req[0]
                    label_parts = [str(val) for i, val in enumerate(req[1:])]
                    display_text = f"درخواست #{req_id} - {' | '.join(label_parts)}"
                    buttons.append(KeyboardButton(display_text))
                markup.add(*buttons)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(
                    chat_id, MESSAGES["choose_request"], reply_markup=markup)
                return
            elif dbtype in (2, 4):
                parent_table = settings["parent_table"]
                link_field = settings["link_field"]
                status_column = settings.get("status_column", "status")
                display_columns = settings.get("display_columns", [])
                # Internal implementation note: legacy behavior is preserved during modernization.
                safe_columns = [col for col in display_columns if col not in (
                    MEDIA_FIELDS or ignor_labels)]
                main_cols = self.db.get_columns(table)
                parent_cols = self.db.get_columns(parent_table)
                # Internal implementation note: legacy behavior is preserved during modernization.
                select_parts = [f"{table}.id", f"{table}.{link_field}"]
                label_sources = []
                for col in display_columns:
                    if col in ignor_labels or col in MEDIA_FIELDS:
                        continue
                    if col in main_cols:
                        select_parts.append(f"{table}.{col}")
                        label_sources.append((col, "self"))
                    elif col in parent_cols:
                        select_parts.append(f"{parent_table}.{col}")
                        label_sources.append((col, "parent"))
                    else:
                        log.warning(
                            f"[REQUEST_MANAGER] ستون '{col}' در هیچ جدولی پیدا نشد.")
                # Internal implementation note: legacy behavior is preserved during modernization.
                query = f"""
                    SELECT {', '.join(select_parts)}
                    FROM {table}
                    LEFT JOIN {parent_table} ON {table}.{link_field} = {parent_table}.{link_field}
                    WHERE {table}.{status_column} = 'pending'
                """
                requests = self.db.fetch_data(query)
                if not requests:
                    self.requests_main_menu(message)
                    return
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                buttons = []
                if chat_id not in self.target_request:
                    self.target_request[chat_id] = {}
                # Internal implementation note: legacy behavior is preserved during modernization.
                time_pattern = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
                for req in requests:
                    req_id = req[0]
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    user_code = req[1]
                    values = req[2:]
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    col_values = dict(
                        zip([col for col, _ in label_sources], values))
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    label_parts = []
                    for col in display_columns:
                        if col in ignor_labels or col in MEDIA_FIELDS:
                            continue
                        value = str(col_values.get(col, "نامشخص"))
                        if time_pattern.match(value):
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            parts = value.split(":")
                            formatted_time = f"{parts[0]}:{parts[1]}"
                            label_parts.append(formatted_time)
                        else:
                            label_parts.append(value)
                    display_text = f"درخواست #{req_id} - {' | '.join(label_parts)}"
                    buttons.append(KeyboardButton(display_text))
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    telegram_id = None
                    row = self.db.select_dict(
                        parent_table, f"{link_field} = ?", (user_code,))[0]
                    if row:
                        telegram_id = row.get("telegram_id")
                    self.target_request[chat_id][req_id] = telegram_id
                markup.add(*buttons)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(
                    chat_id, MESSAGES["choose_request"], reply_markup=markup)
                return
            elif dbtype == 3:
                parent_table = settings["parent_table"]
                link_field = settings["link_field"]
                status_column = settings.get("status_column", "status")
                display_columns = settings.get("display_columns", [])
                dict_column = settings.get("dict_column")
                if not dict_column:
                    self.bot.send_message(
                        chat_id, MESSAGES["error_processing_action"])
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                safe_columns = [col["field"] for col in display_columns if col["field"] not in (
                    MEDIA_FIELDS or ignor_labels)]
                main_cols = self.db.get_columns(table)
                parent_cols = self.db.get_columns(parent_table)
                # Internal implementation note: legacy behavior is preserved during modernization.
                select_parts = [f"{table}.id", f"{table}.{link_field}"]
                label_sources = []
                for col in display_columns:
                    field = col["field"]
                    source = col["source"]
                    if source == "self" and field in main_cols:
                        select_parts.append(f"{table}.{field}")
                        label_sources.append((field, "self"))
                    elif field in parent_cols:
                        select_parts.append(f"{parent_table}.{field}")
                        label_sources.append((field, "parent"))
                    else:
                        log.warning(
                            f"[REQUEST_MANAGER] ستون '{field}' در جدول {source} پیدا نشد.")
                query = f"""
                    SELECT {', '.join(select_parts)}
                    FROM {table}
                    LEFT JOIN {parent_table} ON {table}.{link_field} = {parent_table}.{link_field}
                    WHERE {table}.{status_column} = 'pending'
                """
                requests = self.db.fetch_data(query)
                if not requests:
                    self.requests_main_menu(message)
                    return
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                buttons = []
                if chat_id not in self.target_request:
                    self.target_request[chat_id] = {}
                for req in requests:
                    req_id = req[0]
                    user_code = req[1]
                    values = req[2:]
                    col_values = dict(
                        zip([col for col, _ in label_sources], values))
                    label_parts = []
                    for col in display_columns:
                        field = col["field"]
                        if field in ignor_labels or field in MEDIA_FIELDS:
                            continue
                        label_parts.append(
                            str(col_values.get(field, "نامشخص")))
                    display_text = f"درخواست #{req_id} - {' | '.join(label_parts)}"
                    buttons.append(KeyboardButton(display_text))
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    telegram_id = None
                    row = self.db.select_dict(
                        parent_table, f"{link_field} = ?", (user_code,))
                    if row:
                        telegram_id = row[0].get("telegram_id")
                    self.target_request[chat_id][req_id] = telegram_id
                markup.add(*buttons)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(
                    chat_id, MESSAGES["choose_request"], reply_markup=markup)
                return
            elif dbtype == 5:
                # Internal implementation note: legacy behavior is preserved during modernization.
                settings = self.settings.get(table, {})
                status_column = settings.get("status_column", "status")
                display_columns = settings.get("display_columns", [])
                # Internal implementation note: legacy behavior is preserved during modernization.
                # categorization = settings.get("categorization_column")
                parent_tables_config = settings.get("parent_tables", [])
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                parent_data_cache = {}
                for parent in parent_tables_config:
                    parent_table = parent.get("table")
                    parent_rows = self.db.select_dict(parent_table)
                    cache = {}
                    for row in parent_rows:
                        key = row.get("U_code")
                        if key:
                            cache[key] = row
                    parent_data_cache[parent_table] = cache
                # Internal implementation note: legacy behavior is preserved during modernization.
                all_requests = self.db.select_dict(
                    table, f"{status_column} = 'pending'")
                if not all_requests:
                    self.requests_main_menu(message)
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                filtered_requests = []
                # if categorization:
                #     cat_field = categorization.get("field")
                #     cat_source = categorization.get("source", "self")
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                #     selected_category = self.get_user_category(chat_id)
                #     for req in all_requests:
                # Internal implementation note: legacy behavior is preserved during modernization.
                #         if cat_source == "self":
                #             value = req.get(cat_field)
                #         else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                #             link_field = next(
                #                 (p["link_field"]
                #                  for p in parent_tables_config if p["table"] == cat_source), None
                #             )
                #             foreign_key = req.get(link_field)
                #             parent_row = parent_data_cache.get(
                #                 cat_source, {}).get(foreign_key)
                #             value = parent_row.get(
                #                 cat_field) if parent_row else None
                #         if value == selected_category:
                #             filtered_requests.append(req)
                # else:
                filtered_requests = all_requests
                if not filtered_requests:
                    self.bot.send_message(
                        chat_id, "درخواستی در این دسته وجود ندارد.")
                    self.requests_main_menu(message)
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                buttons = []
                for req in filtered_requests:
                    req_id = req.get("id")
                    parts = []
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    for item in display_columns:
                        if isinstance(item, dict):
                            field = item.get("field")
                            source = item.get("source", "self")
                        else:
                            field = item
                            source = "self"
                        if source == "self":
                            value = req.get(field, "—")
                        else:
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            link_field = next(
                                (p["link_field"]
                                 for p in parent_tables_config if p["table"] == source),
                                None
                            )
                            foreign_key = req.get(link_field)
                            parent_row = parent_data_cache.get(
                                source, {}).get(foreign_key, {})
                            value = parent_row.get(field, "—")
                        parts.append(str(value))
                    label = f"درخواست #{req_id} - {' | '.join(parts)}"
                    buttons.append(KeyboardButton(label))
                markup.add(*buttons)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(
                    chat_id, MESSAGES["choose_request"], reply_markup=markup)
                log.info(
                    f"Requests menu (type 5) displayed for table {table} with {len(filtered_requests)} requests.")
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            table_to_query, display_columns, from_parent = self.resolve_display_columns(
                table, settings)
            safe_columns = [
                col for col in display_columns if col not in MEDIA_FIELDS]
            log.info(
                f"Resolved columns for {table} → {display_columns} from {table_to_query}")
            if from_parent:
                parent_table = settings["parent_table"]
                link_field = settings["link_field"]
                query = f"""
                    SELECT {table}.id, {table}.{link_field}, {', '.join([f'{parent_table}.{col}' for col in safe_columns])}
                    FROM {table}
                    LEFT JOIN {parent_table} ON {table}.{link_field} = {parent_table}.{link_field}
                    WHERE {table}.{status_column} = 'pending'
                """
            else:
                query = f"SELECT id, {', '.join(safe_columns)} FROM {table} WHERE {status_column} = 'pending'"
            requests = self.db.fetch_data(query, ())
            if not requests:
                self.requests_main_menu(message)
                return
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            buttons = []
            for req in requests:
                req_id = req[0]
                label_parts = [str(val) for i, val in enumerate(
                    req[2:] if from_parent else req[1:]) if safe_columns[i] not in MEDIA_FIELDS]
                display_text = f"درخواست #{req_id} - {' | '.join(label_parts)}"
                buttons.append(KeyboardButton(display_text))
            markup.add(*buttons)
            markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
                BUTTONS["back_to_main"]))
            self.bot.send_message(
                chat_id, MESSAGES["choose_request"], reply_markup=markup)
            log.info(
                f"Requests menu displayed for table {table} with {len(requests)} pending requests.")
        except Exception as e:
            log.exception(f"Error in requests_menu for table {table}: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_main_menu(message)
