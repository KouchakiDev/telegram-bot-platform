from __future__ import annotations

from .request_manager_context import *


class RequestManagerPartBMixin:
    def show_requests_by_category(self, message, chat_id, table, category_value):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        try:
            settings = self.settings.get(table)
            categorization = settings.get(
                "categorization_column") if settings else None
            if not categorization:
                log.debug("Categorization not set")
                self.requests_menu(message, chat_id, table)
                return
            print("haminjashhaaa")
            rows = self.db.select_dict(
                table, f"{categorization} = ? AND  {settings['status_column']}= ?",
                (category_value, "pending"))
            log.info(f"Count of Requests in {category_value} : {len(rows)}")
            if not rows:
                self.bot.send_message(
                    chat_id, f"ℹ️ هیچ درخواستی در دسته {category_value} یافت نشد.")
                return
            display_columns = settings["display_columns"] if settings and settings.get(
                "display_columns") else (["name"] if self.db.column_exists(table, "name") else ["id"])
            if not display_columns or not isinstance(display_columns, list):
                display_columns = ["name"] if self.db.column_exists(table, "name") else [
                    "id"]
            query = f"SELECT id, {', '.join(display_columns)} FROM {table} WHERE {settings['status_column']} = 'pending' AND {categorization} = ?"
            requests = self.db.fetch_data(query, (category_value,))
            log.info(
                f"Count of Requests in display_columns : {display_columns} : {len(requests)}")
            if not requests:
                log.warning(f"no request find in {category_value}")
                self.bot.send_message(chat_id, MESSAGES["no_pending_requests"])
                self.requests_main_menu(message)
                return
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            if len(display_columns) > 1 or display_columns[0] != "id":
                buttons = [KeyboardButton(
                    f"درخواست #{req[0]} - {' | '.join(str(req[i+1]) for i in range(len(display_columns)))}") for req in requests]
            else:
                buttons = [KeyboardButton(
                    f"درخواست #{req[0]}") for req in requests]
            markup.add(*buttons)
            markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
                BUTTONS["back_to_main"]))
            self.bot.send_message(
                chat_id, MESSAGES["choose_request"], reply_markup=markup)
            log.info(
                f"Requests for category '{category_value}' displayed for table {table} with {len(requests)} pending requests.")
        except Exception as e:
            log.exception(
                f"Error in show_requests_by_category for table {table}: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_main_menu(message)
    def request_actions_menu(self, is_type3: bool = False, no_back_but: bool = False, is_not_ditails: bool = False):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        if not is_type3:
            buttons.extend([
                KeyboardButton(BUTTONS["accept"]),
                KeyboardButton(BUTTONS["reject"]),
                KeyboardButton(BUTTONS["block"])
            ])
        # buttons.extend([
        #     KeyboardButton(BUTTONS["view_more_details"]
        #                    if not is_not_ditails else BUTTONS["view_less_ditails"]),
        #     KeyboardButton(BUTTONS["edit"])
        # ])
        markup.add(*buttons)
        if no_back_but:
            return markup
        else:
            markup = self.add_back_buttons(markup)
            return markup
    def rejection_reason_menu(self, chat_id):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            reasons = self.db.select_dict("rejection_reasons")
            all_reasons = [r["reason"] for r in reasons] + DEFAULT_REASONS
            if not all_reasons:
                self.bot.send_message(
                    chat_id, MESSAGES["no_reasons_available"])
                return False
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*[KeyboardButton(reason) for reason in all_reasons])
            markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
                BUTTONS["back_to_main"]))
            self.bot.send_message(
                chat_id, MESSAGES["choose_request"], reply_markup=markup)
            log.info(
                f"Displayed {len(all_reasons)} rejection reasons for chat {chat_id}.")
            return True
        except Exception as e:
            log.exception(
                f"Error in rejection_reason_menu for chat {chat_id}: {e}")
            self.bot.send_message(
                chat_id, MESSAGES["error_displaying_reasons"])
            return False
    def handle_requests_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        log.info(f"User {message.from_user.id} accessed requests menu.")
        self.requests_main_menu(message)
    def handle_request_type_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        if self.is_back(message):
            return
        try:
            text = message.text.split(
                " (")[0].replace("درخواست‌های ", "").strip()
            table = next(
                (t for t, p in TABLE_NAME["table_names"].items() if p == text), text)
            if table:
                self.current_table[chat_id] = table
                log.info(
                    f"User {message.from_user.id} selected table: {table}")
                self.requests_menu(message, chat_id, table)
            else:
                table = text
                self.current_table[chat_id] = table
                log.info(
                    f"User {message.from_user.id} selected table: {table}")
                self.requests_menu(message, chat_id, table)
        except Exception as e:
            log.exception(f"Error in handle_request_type_selection: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_main_menu(message)
    def handle_request_selection(self, message, table):
        """Legacy-compatible behavior preserved for this callable."""
            # Internal implementation note: legacy behavior is preserved during modernization.
        phone_pt = PHONE_PT # r"(?:(?:\+98|0098|0)?9\d{9})"
        chat_id = message.chat.id
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        for attr in ["temp_rejection_reason", "pending_rejection_fields", "temp_updated_dict", "temp_review_dict"]:
            getattr(self, attr).pop(chat_id, None)
        def get_msg_id_for_edit(message):
            self.current_ditails[chat_id] = {"id": message.message_id,
                                             "text": message.text}
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            settings = self.settings.get(table)
            request_type = settings.get("type", 1)
            log.info(
                f"📥 user {chat_id} choice on request from {table} type {request_type})")
            self.ifuserwantedit[chat_id] = [message.text]
            # Internal implementation note: legacy behavior is preserved during modernization.
            if "#" not in message.text:
                categorization = settings.get("categorization_column")
                if categorization:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    category = message.text.split(
                        "درخواست‌های")[-1].split("(")[0].strip()
                    log.info(
                        f"📂Showing Requests by categoraiz system : {category}")
                    self.show_requests_by_category(
                        message, chat_id, table, category)
                    return
                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    status_col = settings.get("status_column", "status")
                    pending_requests = self.db.select_dict(
                        table, f"{status_col} = ?", ("pending",))
                    if not pending_requests:
                        self.bot.send_message(
                            chat_id, MESSAGES["no_pending_requests"])
                        self.requests_main_menu(message)
                        return
                    display_columns = settings.get(
                        "display_columns", ["name"] if self.db.column_exists(table, "name") else ["id"])
                    markup = ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                    buttons = [
                        KeyboardButton(
                            f"درخواست #{r['id']} - {' | '.join(str(r.get(col, '')) for col in display_columns)}")
                        for r in pending_requests
                    ] if display_columns != ["id"] else [
                        KeyboardButton(f"درخواست #{r['id']}") for r in pending_requests
                    ]
                    markup.add(*buttons)
                    markup = self.add_back_buttons(markup)
                    self.bot.send_message(
                        chat_id, MESSAGES["choose_request"], reply_markup=markup)
                    return
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                request_id = int(message.text.split(
                    "#")[1].split(" - ")[0].strip())
            except Exception:
                log.warning(
                    f"❌ the format of requests is not valid {message.text}")
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.requests_menu(message, chat_id, table)
                return
            request = self.db.select_dict(table, "id = ?", (request_id,))[0]
            self.current_request[chat_id] = (table, request_id)
            # -----------------------------------------------
            # Internal implementation note: legacy behavior is preserved during modernization.
            if request_type == 1:
                log.info(f"🔍 showing single requests (Type 1) #{request_id}")
                fields = settings.get("request_overview") or ",".join(
                    k for k in request if k not in MEDIA_FIELDS and k not in ignor_labels
                )
                overview_fields = [f.strip() for f in fields.split(",") if f.strip()]
                summary_lines = []
                for f in overview_fields:
                    val = request.get(f, "نامشخص")
                    label = field_labels.get(f, f)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if re.match(phone_pt , str(val)):
                        val = self.normalize_phone_number(val)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if f == "created_at":
                        val = self.convert_to_shamsi(val)
                    if f == "username":
                        if isinstance(val, str) and not val.startswith("@"):
                            val = "@" + val
                    summary_lines.append(f"📌 {label} : {val}")
                summary = "\n".join(summary_lines)
                get_msg_id_for_edit(
                    self.bot.send_message(
                        chat_id,
                        MESSAGES["request_details"].format(details=summary),
                        reply_markup=self.request_actions_menu()
                    )
                )
            # Internal implementation note: legacy behavior is preserved during modernization.
            elif request_type in (2, 4):
                log.info(
                    f"🔍 showing parentable requests (Type 2) #{request_id}")
                # Internal implementation note: legacy behavior is preserved during modernization.
                parent_table = settings["parent_table"]
                link_field = settings["link_field"]
                request_overview = settings.get("request_overview", [])
                if link_field in request:
                    prow = self.db.select_dict(
                        parent_table,
                        f"{link_field} = ?",
                        (request[link_field],)
                    )
                    if prow:
                        parent = prow[0]
                        parent.update(request)
                        parent_lines = []
                        for f in request_overview:
                            lbl = field_labels.get(f, f)
                            val = parent.get(f)
                            if re.match(phone_pt , str(val)):
                                normal_phone = self.normalize_phone_number(val)
                                val= f"\n📌 {field_labels.get(f,f)} : {normal_phone}\n"
                            if f == "created_at":
                                shamsidate = self.convert_to_shamsi(val)
                                val= f"\n📌 {field_labels.get(f,f)} : {shamsidate}\n"
                            if f == "username":
                                if isinstance(val, str) and not val.startswith("@"):
                                    val = "@" + val
                            if f in MEDIA_FIELDS or f in ignor_labels:
                                continue
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            if f in ("is_premium", "premium"):
                                val = "هست" if val else "نیست"
                            if f in ("U_code", "PU_code") and val:
                                val = f"/{val}"
                            parent_lines.append(f"📌 {lbl} : {val or 'ندارد'}")
                parent_info = "\n".join(parent_lines)
                if parent_info:
                    get_msg_id_for_edit(self.bot.send_message(
                        chat_id, f"📌 کلیات درخواست:\n{parent_info}", reply_markup=self.request_actions_menu()))
                # fields = settings.get("request_overview") or ",".join(
                #     k for k in request if k not in MEDIA_FIELDS and k not in ignor_labels
                # )
                # overview_fields = [f.strip() for f in fields.split(",") if f.strip()]
                # Internal implementation note: legacy behavior is preserved during modernization.
                # self.bot.send_message(chat_id, MESSAGES["request_details"].format(details=summary),
                #                       reply_markup=self.request_actions_menu())
            # Internal implementation note: legacy behavior is preserved during modernization.
            elif request_type == 3:
                log.info(f"🔍checking requests by dict (Type 3) #{request_id}")
                review_column = settings.get("dict_column")
                rejection_column = settings.get(
                    "rejection_column", "rejection_reason")
                review_header = settings.get(
                    "review_header", "لطفاً روی مواردی که مورد تایید نیستند کلیک کنید.")
                if not review_column:
                    self.bot.send_message(
                        chat_id, MESSAGES["error_processing_action"])
                    return
                request_row = self.db.select_dict(
                    table, "id = ?", (request_id,))
                if not request_row:
                    self.bot.send_message(chat_id, MESSAGES["not_found"])
                    return
                request_row = request_row[0]
                # Internal implementation note: legacy behavior is preserved during modernization.
                overview_sections = settings.get("request_overview", [])
                info_lines = []
                for section in overview_sections:
                    parent_table = section["table"]
                    link_field = section["link_field"]
                    column_connect = section["column_connect"]
                    fields = section["fields"]
                    title = section.get("title_name", "اطلاعات")
                    info_lines.append(f"📌 <b>{title}:</b>")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    connect_value = request_row.get(column_connect)
                    parent_row = self.db.select_dict(
                        parent_table, f"{link_field} = ?", (connect_value,)
                    ) or {}
                    parent_row = parent_row[0] if parent_row else {}
                    for f in fields:
                        lbl = field_labels.get(f, f)
                        val = parent_row.get(f)
                        if re.match(phone_pt , str(val)):
                            normal_phone = self.normalize_phone_number(val)
                            val= f"\n📌 {field_labels.get(f,f)} : {normal_phone}\n"
                        if f == "created_at":
                            shamsidate = self.convert_to_shamsi(val)
                            val= f"\n📌 {field_labels.get(f,f)} : {shamsidate}\n"
                        if f == "username":
                            if isinstance(val, str) and not val.startswith("@"):
                                val = "@" + val
                        if f in MEDIA_FIELDS or f in ignor_labels:
                            continue
                        info_lines.append(f"📌 {lbl} : {val or 'ندارد'}")
                # Internal implementation note: legacy behavior is preserved during modernization.
                if info_lines:
                    get_msg_id_for_edit(self.bot.send_message(
                        chat_id,
                        f"<b>📌 کلیات درخواست:</b>\n" + "\n".join(info_lines),
                        parse_mode="HTML",
                    ))
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.current_request[chat_id] = (
                    table, request_id, review_column)
                self.create_checkbox_panel(
                    message, chat_id, table, review_column)
            # Internal implementation note: legacy behavior is preserved during modernization.
            # elif request_type == 4:
            # Internal implementation note: legacy behavior is preserved during modernization.
            #     fields = settings.get("request_overview", "").split(", ")
            #     summary = "\n".join(
            # Internal implementation note: legacy behavior is preserved during modernization.
            #     )
            #     self.bot.send_message(chat_id, MESSAGES["request_details"].format(details=summary),
            #                           reply_markup=self.request_actions_menu())
            # Internal implementation note: legacy behavior is preserved during modernization.
            elif request_type == 5:
                log.info(
                    f"🔗 checking multiple parentable requests (Type 5) #{request_id}")
                # Internal implementation note: legacy behavior is preserved during modernization.
                # if settings.get("parent_tables"):
                # if settings.get("parent_table") and settings.get("link_field"):
                parent_lines = []
                details_text = ""
                self.target_request[chat_id] = {}
                self.target_request[chat_id][request_id] = {}
                for parent_table in settings.get("request_overview"):
                    table = parent_table["table"]
                    link_field = parent_table["link_field"]
                    column_connect = parent_table["column_connect"]
                    request_overview = parent_table["fields"]
                    if link_field in request:
                        prow = self.db.select_dict(
                            table,
                            f"{column_connect} = ?",
                            (request[link_field],)
                        )
                        # prow.upda
                        if prow:
                            parent = prow[0]
                            if parent.get('telegram_id'):
                                self.target_request[chat_id][request_id].update(
                                    {f"{parent_table["table"]}": f"{parent['telegram_id']}"})
                            parent_lines.append(parent_table["title_name"])
                            for f in request_overview:
                                if f in MEDIA_FIELDS:
                                    continue
                                lbl = field_labels.get(f, f)
                                val = parent.get(f)
                                if re.match(phone_pt , str(val)):
                                    normal_phone = self.normalize_phone_number(val)
                                    val= f"\n📌 {field_labels.get(f,f)} : {normal_phone}\n"
                                if f == "created_at":
                                    shamsidate = self.convert_to_shamsi(val)
                                    val= f"\n📌 {field_labels.get(f,f)} : {shamsidate}\n"
                                if f == "username":
                                    if isinstance(val, str) and not val.startswith("@"):
                                        val = "@" + val
                                if f in MEDIA_FIELDS or f in ignor_labels:
                                    continue
                                # print(val)
                                # Internal implementation note: legacy behavior is preserved during modernization.
                                if f in ("is_premium", "premium"):
                                    val = "هست" if val else "نیست"
                                if f in ("U_code", "PU_code") and val:
                                    val = f"/{val}"
                                if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
                                    # Internal implementation note: legacy behavior is preserved during modernization.
                                    try:
                                        val = json.loads(val)
                                    except Exception as e:
                                        log.warning(
                                            f"Could not parse JSON string in field {f}: {e}")
                                    if all(isinstance(v, bool) for v in val.values()):
                                        continue
                                    details_text += f"\n📌 {lbl} :"
                                    pretty_lines = []
                                    for sub_k, sub_v in val.items():
                                        sub_lbl = field_labels.get(
                                            sub_k, sub_k)
                                        # Internal implementation note: legacy behavior is preserved during modernization.
                                        if isinstance(sub_v, dict):
                                            title = sub_v.get("title", sub_lbl)
                                            price = sub_v.get("price")
                                            if price:
                                                pretty_lines.append(
                                                    f"  • {title} – {int(price):,} تومان")
                                            else:
                                                pretty_lines.append(
                                                    f"  • {title}")
                                        else:
                                            pretty_lines.append(
                                                f"  • {sub_lbl} : {sub_v}")
                                    details_text += "\n" + \
                                        "\n".join(pretty_lines) + "\n"
                                    parent_lines.append(details_text)
                                    continue
                                else:
                                    parent_lines.append(
                                        f"📌 {lbl} : {val or 'ندارد'}")
                parent_info = "\n".join(parent_lines)
                get_msg_id_for_edit(self.bot.send_message(
                    chat_id,
                    f"📌 کلیات درخواست:\n{parent_info}",
                    reply_markup=self.request_actions_menu()
                ))
            else:
                log.warning(f"🚫 requests with no vaild type {request_type}")
                self.bot.send_message(chat_id, "❗ نوع درخواست ناشناخته است.")
                self.requests_menu(message, chat_id, table)
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if table == "request_drafts":
                    origin_tid = request.get("telegram_id")      # Internal implementation note: legacy behavior is preserved during modernization.
                    origin_mid = request.get("intro_msg_id")     # Internal implementation note: legacy behavior is preserved during modernization.
                    if origin_tid and origin_mid:
                        try:
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            storage_msg = self.client_bot.forward_message(   # Internal implementation note: legacy behavior is preserved during modernization.
                                chat_id=STORAGE_CHANNEL,
                                from_chat_id=origin_tid,
                                message_id=origin_mid,
                            )
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            self.bot.forward_message(
                                chat_id,                    # Internal implementation note: legacy behavior is preserved during modernization.
                                STORAGE_CHANNEL,         # Internal implementation note: legacy behavior is preserved during modernization.
                                storage_msg.message_id      # Internal implementation note: legacy behavior is preserved during modernization.
                            )
                        except Exception as exc:
                            logger.warning("Forward failed · %s", exc)
                self.send_full_details(chat_id, table, request_id)
            except:
                pass
            # Internal implementation note: legacy behavior is preserved during modernization.
        except Exception as e:
            log.exception(
                f"❌ خطا در handle_request_selection برای chat_id={chat_id}, table={table}: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_menu(message, chat_id, table)
    def notify_user(self, real_table, request_id, status, extra_message=""):
        """
        Sends a notification to the user (or admin) based on the request type and new status.
        :param real_table: Actual table name (e.g., staff)
        :param request_id: ID of the request
        :param status: New status (approved/rejected/etc.)
        :param extra_message: Extra message to append to the notification
        """
        try:
            log.debug(
                f"[notify_user] Start | table={real_table}, request_id={request_id}, status={status}")
            request_type = REQUEST_TYPE_MAP.get(
                real_table, f"unknown.{real_table}")
            # Step 1: Detect request type
            log.debug(f"[notify_user] Detected request_type: {request_type}")
            # Step 2: Try getting telegram_id from self.target_request
            telegram_id = None
            # Internal implementation note: legacy behavior is preserved during modernization.
            if request_id in self.target_request:
                telegram_id = self.target_request[request_id]
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                for chat_requests in self.target_request.values():
                    if isinstance(chat_requests, dict) and request_id in chat_requests:
                        telegram_id = chat_requests[request_id]
                        break
            # print(telegram_id)
            if not telegram_id:
                log.debug(
                    f"[notify_user] telegram_id not found in self.target_request for request_id={request_id}")
                # Fallback: Try getting it from database
                try:
                    result = self.db.select_dict(
                        real_table, "id = ?", (request_id,))
                    telegram_id = result[0].get(
                        "telegram_id") if result else None
                    log.debug(
                        f"[notify_user] Fetched telegram_id from DB: {telegram_id}")
                except Exception as db_ex:
                    log.exception(
                        f"[notify_user] ❌ Failed to fetch telegram_id from DB for table={real_table}, id={request_id} | Error: {db_ex}")
            if not telegram_id:
                log.exception(
                    f"[notify_user] ❌ telegram_id not found for request_id={request_id}")
                return
            # Step 3: Send notification
            log.info(
                f"[notify_user] Sending notification to Telegram ID: {telegram_id} | "
                f"Type: {request_type} | Table: {real_table} | Request ID: {request_id} | Status: {status}"
            )
            success = self.notification_manager.send_notification(
                telegram_id=telegram_id,
                request_type=request_type,
                request_id=request_id,
                status=status,
                extra=extra_message
            )
            if success:
                log.info(
                    f"[notify_user] ✅ Notification sent successfully for {request_type}, ID={request_id}")
            else:
                log.warning(
                    f"[notify_user] ⚠️ Notification failed silently for {request_type}, ID={request_id}")
        except Exception as e:
            log.exception(
                f"[notify_user] 🔥 Unexpected error in notify_user: {e}")
    def get_request_type(self, table):
        return self.settings.get(table, {}).get("type", 1)
    def format_field(self, label: str, value: any, suffix: str = "") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if value and str(value).strip().lower() not in ["", "null", "none"]:
            return f"{label} {value}{suffix}\n"
        return ""
    def format_boolean_field(self, label: str, value: str, true_text="✅ دارد", false_text="❌ ندارد") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if value == "1":
            return f"{label} {true_text}\n"
        elif value == "0":
            return f"{label} {false_text}\n"
        return ""
    def generate_ad_caption(self, ad: dict, staff: dict = None) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            u_code = ad.get('U_code', '---')
            ad_number = u_code.replace('p', '')
            ad_code = (
                f"#کدویژه{ad_number} | "
                f"<a href='https://t.me/{CLIENT_BOT_ID}?start={u_code}'>/{u_code}</a>"
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            age = str(staff.get('age')) if staff and staff.get('age') else str(random.randint(21, 24))
            skin = str(staff.get('skin_color') or 'سفید')
            body = str(staff.get('appearance') or random.choice(bodies))
            profile_category = staff.get("profile_category","عضو")
            # Internal implementation note: legacy behavior is preserved during modernization.
            mood = random.choice(moods)
            style = random.choice(styles)
            while len(set([mood.strip(), body.strip(), style.strip()])) < 3:
                mood = random.choice(moods)
                style = random.choice(styles)
            # Internal implementation note: legacy behavior is preserved during modernization.
            body_parts = [skin, body, style]
            body_parts = [str(x) if x else '' for x in body_parts]
            random.shuffle(body_parts)
            body_phrase = " | ".join(body_parts)
            # Internal implementation note: legacy behavior is preserved during modernization.
            region_text = ad.get("region", "")
            regions = [r.strip() for r in region_text.split(",") if r.strip()]
            dispatch_mode = staff.get("dispatch_mode") if staff else "اعزام به"
            dispatch_line = f"👛 {dispatch_mode} : ({'، '.join(regions)})" if regions else "👛 منطقه: نامشخص"
            # Internal implementation note: legacy behavior is preserved during modernization.
            start_str = ad.get("start_time", "")[:5]
            end_str = ad.get("end_time", "")[:5]
            hour_line = f"🕒 امروز {start_str} تا {end_str}"
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                start_time = datetime.strptime(start_str, "%H:%M")
                end_time = datetime.strptime(end_str, "%H:%M")
                total_minutes = int((end_time - start_time).total_seconds() // 60)
                service_count = int(ad.get("service_count", 1))
                slot_duration = total_minutes // service_count if service_count else 30
            except Exception as e:
                log.warning(f"[caption] time calc failed: {e}")
                slot_duration = 30
            timeslottoworld = {
                15: "ربع ساعته",
                30: "نیم ساعت",
                45: "سه ربع",
                60: "ساعتی"
            }
            slot_label = timeslottoworld.get(slot_duration, f"{slot_duration} دقیقه")
            # Internal implementation note: legacy behavior is preserved during modernization.
            base_price = ad.get("base_price", 0)
            price_str = f"{int(base_price):,}".replace(",", ".")
            price_line = f"🛎 {slot_label}: {price_str} میلیون"
            # Internal implementation note: legacy behavior is preserved during modernization.
            gallery_line = ""
            try:
                if staff:
                    gallery_photos = json.loads(staff.get("gallery_photos", "[]"))
                    profile_photos = json.loads(staff.get("profile_photos", "[]"))
                    all_photos = gallery_photos + profile_photos
                    if all_photos:
                        gallery_link = f"https://t.me/{CLIENT_BOT_ID}?start=gallery_{staff['U_code']}"
                        gallery_line = f"<a href='{gallery_link}'>👁 برای دیدن عکس کلیک کنید 👁</a>"
            except Exception as e:
                log.error(f"[caption] failed to load gallery: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            extra_services = []
            total_extra_price = 0
            try:
                # PREMIUM services
                premium_dict = json.loads(ad.get('premium_services', '{}'))
                for key, item in premium_dict.items():
                    title = item.get('title', key)
                    price = item.get('price', 0)
                    if title:
                        extra_services.append(f"▫️ {title}")
                        total_extra_price += int(price)
                # Regular services (structured)
                reg_dict = json.loads(ad.get('services', '{}'))
                for key, item in reg_dict.items():
                    title = item.get('title', key)
                    price = item.get('price', 0)
                    if title:
                        extra_services.append(f"▫️ {title}")
                        total_extra_price += int(price)
                # # Regular services (simple string)
                # regular_raw = ad.get('regular_services', '')
                # if regular_raw:
                #     for service_name in regular_raw.split(','):
                #         service_name = service_name.strip()
                #         if service_name:
                # Internal implementation note: legacy behavior is preserved during modernization.
            except Exception as e:
                log.warning(f"[caption] failed to parse extra services: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            lines = [
                f"#{profile_category} | {ad_code}",
                "",
                f"👠 {age} ساله | {mood}",
                f"🎨 {body_phrase}",
                "",
                dispatch_line,
                f"{hour_line} | {price_line}",
                "",
            ]
            if gallery_line:
                lines.append(gallery_line)
                lines.append("")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if extra_services:
                lines.append("➕ <b>خدمات اضافه:</b>")
                lines.extend(extra_services)
                try:
                    reg_price = int(ad.get("regular_services_price", 0) or 0)
                except:
                    reg_price = 0
                try:
                    premium_price = int(ad.get("premium_services_price", 0) or 0)
                except:
                    premium_price = 0
                total_price = reg_price + premium_price
                if total_price:
                    lines.append(f"💵 <b>قیمت فول خدمات:</b> {(total_price + base_price):,} تومان")
                lines.append("")
            lines.append("🔥 یکی از تایم‌های زیر رو بزن و رزرو کن 👇")
            lines.append("")
            lines.append(" ".join(PROFILE_CHANNEL_TAGS))
            return "\n".join([line for line in lines if line is not None])
        except Exception as e:
            log.error(f"[caption] failed to generate ad caption: {e}")
            return "❌ خطا در ساخت کپشن آگهی"
    def generate_ad_caption2(self, ad: dict, staff: dict = None) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        import json
        import html
        # Internal implementation note: legacy behavior is preserved during modernization.
        user_code = f"/{ad.get('U_code')}" or 'نامشخص'
        region = ad.get('region') or 'نامشخص'
        service_count = ad.get('service_count', 0)
        pay_method = ad.get('payment_method') or 'نامشخص'
        lines = []
        lines.append(
            f"📢 <b>آگهی کد کاربر : <code>{html.escape(user_code)}</code></b>")
        if staff:
            lines.append("")
            lines.append("<b>👤 ویژگی‌های ارائه‌دهنده:</b>")
            appearance_fields = [
                ('name', '👤 نام'),
                ('age', '🎂 سطح تجربه'),
                ('city', '🏙️ شهر'),
                ('height', '📏 ظرفیت'),
                ('weight', '⚖️ حجم خدمات'),
                ('breast_size', '🔢 پارامتر عددی'),
                ('eye_color', '👁 تخصص اصلی'),
                ('hair_color', '🧩 روش ارائه'),
                ('skin_color', '🎨 دسته‌بندی خدمات'),
                ('appearance', '🧩 سبک خدمت'),
                ('marital_status', '📅 وضعیت دسترسی'),
                ('has_home', '🏠 مکان اختصاصی'),
                ('visit_client_home', '🚗 امکان مراجعه')
            ]
            for field, label in appearance_fields:
                val = staff.get(field)
                if val is not None and val != "":
                    if field in ['has_home', 'visit_client_home']:
                        val = 'دارد' if str(val) == '1' else 'ندارد'
                    elif field == 'is_premium':
                        val = 'هست' if str(val).lower() in (
                            'approved', 'true', '1') else 'نیست'
                    lines.append(f"{label} : {html.escape(str(val))}")
        lines.append(f"📍 <b>منطقه:</b> {html.escape(region)}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        premium_services = []
        try:
            premium_dict = json.loads(ad.get('premium_services', '{}'))
            for key, item in premium_dict.items():
                title = item.get('title', key)
                price = item.get('price', 0)
                if title:
                    if price:
                        premium_services.append(
                            f"🔸 <b>{html.escape(title)}</b> – {price:,} تومان")
                    else:
                        premium_services.append(f"🔸 <b>{html.escape(title)}</b>")
        except:
            pass
        if premium_services:
            lines.append("")
            lines.append("<b>⭐ ویژگی‌های افزوده PREMIUM:</b>")
            lines.extend(premium_services)
        else:
            lines.append("")
            lines.append("<b>⭐ ویژگی‌های افزوده PREMIUM:</b> ندارد")
        # Internal implementation note: legacy behavior is preserved during modernization.
        reg_services = []
        try:
            reg_dict = json.loads(ad.get('services', '{}'))
            for key, item in reg_dict.items():
                title = item.get('title', key)
                price = item.get('price', 0)
                if title:
                    if price:
                        reg_services.append(
                            f"🔸 <b>{html.escape(title)}</b> – {price:,} تومان")
                    else:
                        reg_services.append(f"🔸 <b>{html.escape(title)}</b>")
        except:
            pass
        extra = ad.get('regular_services', '').strip()
        if extra:
            for part in extra.split(','):
                part = part.strip()
                if part:
                    reg_services.append(f"🔸 <b>{html.escape(part)}</b>")
        if reg_services:
            lines.append("")
            lines.append("<b>🧰 خدمات معمولی:</b>")
            lines.extend(reg_services)
        else:
            lines.append("")
            lines.append("<b>🧰 خدمات معمولی:</b> ندارد")
        price_lines = []
        base_price = ad.get('base_price', 0)
        if base_price:
            price_lines.append(f"💰 <b>مبلغ پایه:</b> {base_price:,} تومان")
        reg_price = ad.get('regular_services_price', 0)
        if reg_price:
            price_lines.append(
                f"✨ <b>هزینه خدمات عادی:</b> {reg_price:,} تومان")
        premium_price = ad.get('premium_services_price', 0)
        if premium_price:
            price_lines.append(
                f"🔥 <b>هزینه ویژگی‌های افزوده:</b> {premium_price:,} تومان")
        total = ad.get('ad_price', 0)
        if total:
            price_lines.append(f"💵 <b>مبلغ کل:</b> {total:,} تومان")
        prepay = ad.get('prepayment_amount', 0)
        if prepay:
            price_lines.append(f"🎯 <b>پیش‌پرداخت:</b> {prepay:,} تومان")
        if price_lines:
            lines.append("")
            lines.extend(price_lines)
        lines.append(f"💳 <b>روش پرداخت:</b> {html.escape(pay_method)}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        if staff and staff.get("gallery_photos"):
            try:
                gallery_photos = json.loads(
                    staff.get("gallery_photos", "[]"))
                if gallery_photos:
                    # bot_username = self.bot.get_me().username
                    gallery_link = f"https://t.me/{html.escape(CLIENT_BOT_ID)}?start=gallery_{staff['U_code']}"
                    lines.append("")
                    lines.append(
                        f'🖼 <a href="{gallery_link}">مشاهده عکس‌های بیشتر</a>')
            except Exception:
                pass
        caption = "\n".join(lines)
        return caption
    def generate_time_slots(self, start_time, end_time, service_count: int) -> dict[str, bool]:
        """Legacy-compatible behavior preserved for this callable."""
        log.debug(
            f"🔔 شروع generate_time_slots با: start_time={start_time}, end_time={end_time}, service_count={service_count}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        def to_datetime(t):
            if isinstance(t, str):
                log.debug(f"🛠 تبدیل رشته '{t}' به datetime با strptime")
                return datetime.strptime(t, "%H:%M")
            elif isinstance(t, timedelta):
                # Internal implementation note: legacy behavior is preserved during modernization.
                dt = datetime.combine(date.today(), time.min) + t
                log.debug(
                    f"🛠 تبدیل timedelta '{t}' به datetime '{dt.time().strftime('%H:%M')}'")
                return dt
            elif isinstance(t, datetime):
                log.debug(f"🛠 تبدیل datetime '{t}' به فرمت HH:MM")
                return datetime.combine(date.today(), t.time())
            else:
                msg = f"مقدار start/end time باید str یا datetime یا timedelta باشد، ولی دریافت شد: {type(t)}"
                log.error(msg)
                raise ValueError(msg)
        # Internal implementation note: legacy behavior is preserved during modernization.
        start_dt = to_datetime(start_time)
        end_dt = to_datetime(end_time)
        log.info(
            f"✅ start_dt={start_dt.time().strftime('%H:%M')}, end_dt={end_dt.time().strftime('%H:%M')}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        total_seconds = (end_dt - start_dt).total_seconds()
        if service_count <= 0:
            msg = "service_count باید عدد صحیح مثبت باشد."
            log.error(msg)
            raise ValueError(msg)
        interval = total_seconds / service_count
        log.debug(
            f"⏱ total_seconds={total_seconds}, interval_per_slot={interval} seconds")
        # Internal implementation note: legacy behavior is preserved during modernization.
        slots: dict[str, bool] = {}
        for i in range(service_count):
            slot_dt = start_dt + timedelta(seconds=i * interval)
            slot_str = slot_dt.strftime("%H:%M")
            slots[slot_str] = True
            log.debug(f"➕ اسلات {i+1}: {slot_str}")
        log.info(
            f"🎯 تولید {len(slots)} اسلات زمانی برای بازه {start_dt.time().strftime('%H:%M')} - {end_dt.time().strftime('%H:%M')}")
        return slots
    @staticmethod
    def timedelta_to_str(tdelta: timedelta) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        total_seconds = int(tdelta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    def build_staff_caption(self, p_row: dict) -> tuple[str, list[str]]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            def safe_str(val, fallback='؟'):
                """Legacy-compatible behavior preserved for this callable."""
                return str(val) if val not in [None, ''] else fallback
            name = safe_str(p_row.get('name'), 'نامشخص')
            age = safe_str(p_row.get('age'), '?')
            profile_category = safe_str(p_row.get("profile_category" , "عضو"))
            dispatch_mode = safe_str(p_row.get('dispatch_mode'))
            region = safe_str(p_row.get('region'))
            province = safe_str(p_row.get('province'))
            city = safe_str(p_row.get('city'))
            location = f"{city} - {region}" if city and region else region or city or "؟"
            height = safe_str(p_row.get('height'), '?')
            weight = safe_str(p_row.get('weight'), '?')
            skin_color = safe_str(p_row.get('skin_color'), 'نامشخص')
            u_code = safe_str(p_row.get("U_code"), "نامشخص")
            ad_code = (
                f"#کدویژه{u_code.replace('p', '')} | "
                f"<a href='https://t.me/{CLIENT_BOT_ID}?start={u_code}'>/{u_code}</a>"
                f" | #{profile_category}"
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            appearance = safe_str(p_row.get('appearance'), random.choice(bodies))
            # Internal implementation note: legacy behavior is preserved during modernization.
            mood = safe_str(random.choice(moods))
            style = safe_str(random.choice(styles))
            while len(set([mood, appearance, style])) < 3:
                mood = safe_str(random.choice(moods))
                style = safe_str(random.choice(styles))
            body_parts = [mood, appearance, style]
            random.shuffle(body_parts)
            body_phrase = " | ".join([safe_str(p) for p in body_parts])
            gallery_link = f"https://t.me/{CLIENT_BOT_ID}?start=gallery_{safe_str(p_row.get('U_code'))}"
            gallery_line = f"<a href='{gallery_link}'>👁 برای دیدن عکس کلیک کنید 👁</a>"
            caption = (
                "📍 <b>معرفی ارائه‌دهندگان خدمات و پیشنهادهای منتخب</b>\n\n"
                f"{ad_code}\n\n"
                f"👤 <b>نام:</b> {name}\n"
                f"🎂 <b>سطح تجربه:</b> {age} سال\n"
                f"📍 <b>وضعیت:</b> {dispatch_mode}\n"
                f"🏘 <b>منطقه:</b> {location}\n\n"
                f"📏 <b>ظرفیت:</b> {height} سانتی‌متر\n"
                f"⚖️ <b>حجم خدمات:</b> {weight} واحد\n"
                f"🎨 <b>دسته‌بندی خدمات:</b> {skin_color}\n\n"
                f"💢<b>{body_phrase}</b>\n"
                f"🖼<b>{gallery_line}</b>\n"
                "📩 <b>برای ثبت سفارش و هماهنگی:</b>\n"
                f"@{CLIENT_BOT_ID}\n\n"
                f"{' '.join(PROFILE_CHANNEL_TAGS)}"
            )
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                photo = random.choice(json.loads(p_row.get("profile_photos", "[]")))
                photos = [photo,]
                if not isinstance(photos, list):
                    log.warning("[caption] profile_photos is not a list.")
                    photos = []
                # random.shuffle(photos)
            except Exception as e:
                log.error(f"[caption] error loading or shuffling photos: {e}")
                photos = []
            return caption, photos
        except Exception as e:
            log.error(f"[caption] Failed to build staff caption: {e}")
            return "❌ خطا در ساخت کپشن", []
    def _queue_staff_for_publish(self, staff_id: int):
        try:
            rows = self.db.select_dict("staff", "id = ?", (staff_id,))
            if not rows:
                log.error(f"[queue_publish] Staff ID {staff_id} not found.")
                return
            p_row = rows[0]
            caption, photos = self.build_staff_caption(p_row)
            if not photos:
                log.warning(f"[queue_publish] Staff ID {staff_id} has no photos.")
                return
            self.db.create_table("staff_publish_queue",
                    {
                    "staff_id" : "INT NOT NULL",
                    "caption"     : "TEXT NOT NULL",
                    "photos"      : "JSON NOT NULL",
                    "status"     : "VARCHAR(255) NOT NULL DEFAULT 'queued'",
                    "queued_at"   : "DATETIME DEFAULT CURRENT_TIMESTAMP",
                    "sent_at"      : "DATETIME"})
            # Internal implementation note: legacy behavior is preserved during modernization.
            # self.db.execute_query("""
            #     CREATE TABLE IF NOT EXISTS staff_publish_queue (
            #         id            INT AUTO_INCREMENT PRIMARY KEY,
            #         staff_id  INT NOT NULL,
            #         caption       TEXT NOT NULL,
            #         photos        JSON NOT NULL,
            #         status        VARCHAR(255) NOT NULL DEFAULT 'queued',
            #         queued_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            #         sent_at       DATETIME
            #     );
            # """)
            self.db.insert("staff_publish_queue",{"staff_id":staff_id,
                                                      "caption":caption,
                                                      "photos":json.dumps(photos, ensure_ascii=False)})
            # self.db.execute_query(
            #     "INSERT INTO staff_publish_queue (staff_id, caption, photos) "
            # Internal implementation note: legacy behavior is preserved during modernization.
            #     (staff_id, caption, json.dumps(photos, ensure_ascii=False))
            # )
            log.info(f"[queue_publish] Staff ID {staff_id} added to publish queue.")
        except Exception as e:
            log.error(f"[queue_publish] error while queuing ID {staff_id}: {e}")
    def send_ad_to_channel(self, ad_row: dict, table: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            start_time = ad_row.get("start_time")
            end_time = ad_row.get("end_time")
            service_count = int(ad_row.get("service_count", 1))
            # Internal implementation note: legacy behavior is preserved during modernization.
            slots = self.update_expired_slots(self.generate_time_slots(
                start_time, end_time, service_count))
            # Internal implementation note: legacy behavior is preserved during modernization.
            link_base = f"https://t.me/{html.escape(CLIENT_BOT_ID)}?start"
            # Internal implementation note: legacy behavior is preserved during modernization.
            if isinstance(start_time, timedelta):
                total_seconds = int(start_time.total_seconds())
                start_time_str = f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}"
                log.debug(
                    f"🔄 Converted start_time timedelta to string: {start_time_str}")
            else:
                start_time_str = start_time
                log.debug(f"✅ start_time already string: {start_time_str}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if isinstance(end_time, timedelta):
                total_seconds = int(end_time.total_seconds())
                end_time_str = f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}"
                log.debug(
                    f"🔄 Converted end_time timedelta to string: {end_time_str}")
            else:
                end_time_str = end_time
                log.debug(f"✅ end_time already string: {end_time_str}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            start_dt = datetime.strptime(start_time_str, "%H:%M")
            end_dt = datetime.strptime(end_time_str, "%H:%M")
            interval = (end_dt - start_dt).total_seconds() / service_count
            buttons = []
            for slot, available in slots.items():
                slot_time_fmt = datetime.strftime(
                    datetime.strptime(slot, "%H:%M"), "%H_%M")
                param = f"reserve_ads_{ad_row["id"]}_{slot_time_fmt}"
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
                    text=BUTTONS["Goto_Cutsomer_bot"], url=link_base),
                InlineKeyboardButton(
                    text=BUTTONS["Add_toFavoris"], callback_data=f"AddToFavorits_{ad_row.get('U_code')}")
            ])
            keyboard = InlineKeyboardMarkup()
            for r in rows:
                keyboard.row(*r)
            # Internal implementation note: legacy behavior is preserved during modernization.
            staff = None
            settings_ads = self.settings.get("ads", {})
            if settings_ads.get("parent_table") and settings_ads.get("link_field"):
                parent = self.db.select_dict(
                    settings_ads["parent_table"],
                    f"{settings_ads['link_field']} = ?", (ad_row.get(
                        settings_ads['link_field']),)
                )
                if parent:
                    staff = parent[0]
            # Internal implementation note: legacy behavior is preserved during modernization.
            caption = self.generate_ad_caption(ad_row, staff)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if ad_row.get("ad_photo"):
                msg = self.notification_manager.bots["client"].send_photo(
                    chat_id=CHANNEL_ID,
                    photo=ad_row.get("ad_photo"),
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                    has_spoiler=True
                )
            else:
                msg = self.notification_manager.bots["client"].send_message(
                    chat_id=CHANNEL_ID,
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            try:
                self.db.insert("live_ads", {
                    "ad_id": ad_row["id"],
                    "time_slots": json.dumps(slots, ensure_ascii=False),
                    "channel_message_id": msg.message_id
                })
                log.info(f"✅ ads #{ad_row['id']}susfully sended!")
            except Exception as e:
                log.error(f"Error : {e}")
                return
        except Exception as e:
            log.exception(f"❌ خطا در ارسال آگهی #{ad_row.get('id')}: {e}")
