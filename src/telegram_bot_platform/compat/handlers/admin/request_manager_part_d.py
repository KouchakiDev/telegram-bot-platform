from __future__ import annotations

from .request_manager_context import *


class RequestManagerPartDMixin:
    def _save_field_update(self, message, value):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        data = self.temp_data[chat_id]
        table = data["table"]
        field = data["editing_field"]
        req_id = data["request_id"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update(table, {field: value}, "id = ?", (req_id,))
        self.bot.send_message(chat_id, MESSAGES["changes_saved"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        if chat_id in self.ifuserwantedit:
            original_message = self.ifuserwantedit[chat_id][1]
            # table = self.ifuserwantedit[chat_id][1]
            # current_request = self.ifuserwantedit[chat_id][2]
            self.current_request[chat_id] = self.ifuserwantedit[chat_id][2]
            current = self.current_request[chat_id]
            table = current[0]
            # Internal implementation note: legacy behavior is preserved during modernization.
            request_id = current[1]
            # self.send_full_details(chat_id, table, request_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.handle_request_action(original_message)
    def is_json_dict(self, s):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            obj = json.loads(s)
            return isinstance(obj, dict)
        except:
            return False
    def handle_rejection_reason_selection(self, message, table, request_id):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        reason = message.text
        try:
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
                    message, self.handle_custom_rejection_reason, table, request_id)
                return
            now = datetime.now().strftime("%Y/%m/%d ⏰ %H:%M")
            old_data = self.db.select_dict(table, "id = ?", (request_id,))
            old_reasons = []
            if old_data and old_data[0].get("rejection_reason"):
                try:
                    old_reasons = json.loads(old_data[0]["rejection_reason"])
                except Exception:
                    old_reasons = []
            old_reasons.append({"date": now, "reason": reason})
            self.db.update(table, {"status": "rejected", "rejection_reason": json.dumps(old_reasons, ensure_ascii=False)},
                           "id = ?", (request_id,))
            self.bot.send_message(
                chat_id, MESSAGES["request_rejected"].format(reason=reason))
            self.notify_user(table, request_id, "rejected",
                             extra_message=reason)
            del self.current_request[chat_id]
            self.requests_menu(message, chat_id, table)
            log.info(f"Request #{request_id} rejected with reason: {reason}")
        except Exception as e:
            log.exception(f"Error in handle_rejection_reason_selection: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_menu(message, chat_id, table)
    def handle_custom_rejection_reason(self, message, table, request_id, type3=False):
        chat_id = message.chat.id
        custom_reason = message.text.strip()
        if not custom_reason:
            self.bot.send_message(chat_id, MESSAGES["custom_reason_lost"])
            self.requests_menu(message, chat_id, table)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        rejection_reason_json = json.dumps({"reason": custom_reason}, ensure_ascii=False)
        self.temp_rejection_reason[chat_id] = rejection_reason_json
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(KeyboardButton(BUTTONS["yes"]), KeyboardButton(BUTTONS["no"]))
        self.bot.send_message(chat_id, MESSAGES["save_reason_prompt"].format(
            reason=custom_reason), reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.handle_save_custom_reason, table, request_id, type3)
    def handle_save_custom_reason(self, message, table, request_id, type3):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        choice = message.text.strip()
        custom_reason = self.temp_rejection_reason.get(chat_id, "")
        # Internal implementation note: legacy behavior is preserved during modernization.
        review_column = self.current_request[chat_id][2] if (
            chat_id in self.current_request and len(self.current_request[chat_id]) == 3) else None
        if self.is_back(message):
            return
        try:
            if not custom_reason:
                self.bot.send_message(chat_id, MESSAGES["custom_reason_lost"])
                self.requests_menu(message, chat_id, table)
                return
            if choice == BUTTONS["yes"]:
                try:
                    self.db.insert("rejection_reasons", {
                                   "reason": custom_reason})
                    reason_id = self.get_reason_id(custom_reason)
                    log.info(
                        f"Custom reason '{custom_reason}' saved with ID {reason_id}.")
                    update_reason = reason_id
                except sqlite3.IntegrityError:
                    reason_id = self.get_reason_id(custom_reason)
                    log.info(
                        f"Custom reason '{custom_reason}' already exists with ID {reason_id}.")
                    update_reason = reason_id
            elif choice == BUTTONS["no"]:
                update_reason = custom_reason
            else:
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(KeyboardButton(
                    BUTTONS["yes"]), KeyboardButton(BUTTONS["no"]))
                self.bot.send_message(chat_id, MESSAGES["save_reason_prompt"].format(
                    reason=custom_reason), reply_markup=markup)
                self.bot.register_next_step_handler(
                    message, self.handle_save_custom_reason, table, request_id, type3)
                return
            if type3:
                # Internal implementation note: legacy behavior is preserved during modernization.
                pending_fields = self.pending_rejection_fields.get(chat_id, [])
                if pending_fields:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    next_field = pending_fields[0]
                    message.text = custom_reason
                    self.handle_field_rejection_reason(
                        message,
                        table,
                        request_id,
                        next_field,
                        review_column
                    )
                    log.info(
                        f"Request #{request_id}: custom reason '{custom_reason}' recorded for field '{next_field}'; moving to next field.")
                    return
                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.update(table, {
                        review_column: json.dumps(self.temp_updated_dict.get(chat_id, {}), ensure_ascii=False),
                        "rejection_reason": json.dumps(update_reason, ensure_ascii=False),
                        "status": "approved"
                    }, "id = ?", (request_id,))
                    self.notify_user(table, request_id,
                                     "approved", extra_message=custom_reason)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.temp_rejection_reason.pop(chat_id, None)
                    self.current_request.pop(chat_id, None)
                    self.temp_updated_dict.pop(chat_id, None)
                    self.temp_review_dict.pop(chat_id, None)
                    self.pending_rejection_fields.pop(chat_id, None)
                    self.requests_menu(message, chat_id, table)
                    log.info(
                        f"Request #{request_id}: all custom rejection reasons collected; request now approved.")
                    return
            # Internal implementation note: legacy behavior is preserved during modernization.
            else:
                self.db.update(table, {
                               "status": "rejected", "rejection_reason": update_reason}, "id = ?", (request_id,))
                self.bot.send_message(
                    chat_id, MESSAGES["request_rejected"].format(reason=custom_reason))
                self.notify_user(table, request_id, "rejected",
                                 extra_message=custom_reason)
                self.temp_rejection_reason.pop(chat_id, None)
                self.current_request.pop(chat_id, None)
                self.requests_menu(message, chat_id, table)
                log.info(
                    f"Request #{request_id} rejected with custom reason '{custom_reason}'")
        except Exception as e:
            log.exception(f"Error in handle_save_custom_reason: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_menu(message, chat_id, table)
    def get_reason_id(self, reason_text):
        """Legacy-compatible behavior preserved for this callable."""
        result = self.db.select_dict(
            "rejection_reasons", "reason = ?", (reason_text,))
        return result[0]["id"] if result else None
    def convert_to_shamsi(self, date_str: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        def normalize_to_datetime_str(date_input: any) -> str:
            """Legacy-compatible behavior preserved for this callable."""
            from datetime import datetime
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(date_input, datetime):
                    return date_input.strftime('%Y-%m-%d %H:%M:%S')
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(date_input, (float, int)):
                    dt = datetime.fromtimestamp(date_input)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(date_input, str):
                    date_str = date_input.replace("⏰", "").strip()
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    return date_str.replace("/", "-")
                # Internal implementation note: legacy behavior is preserved during modernization.
                return str(date_input)
            except Exception:
                return str(date_input)  # Internal implementation note: legacy behavior is preserved during modernization.
        from datetime import datetime
        from persiantools.jdatetime import JalaliDateTime
        if not date_str:
            return "نامشخص"
        try :
            date_str = normalize_to_datetime_str(date_str)
        except:
            return "نامشخص"
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            date_str = date_str.replace("⏰", "").strip()
            # Internal implementation note: legacy behavior is preserved during modernization.
            if '.' in date_str:
                date_str = date_str.split('.')[0]
            # Internal implementation note: legacy behavior is preserved during modernization.
            normalized = date_str.replace("/", "-")
            # Internal implementation note: legacy behavior is preserved during modernization.
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(normalized, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_str  # Internal implementation note: legacy behavior is preserved during modernization.
            jdt = JalaliDateTime(dt)
            formatted = f"\n  📅 {jdt.strftime('%Y/%m/%d')} تاریخ\n  " \
                f"🗓 {jdt.strftime('%A')} {jdt.day} {jdt.strftime('%B')}\n  " \
                f"⏰ ساعت : {jdt.strftime('%H:%M')}"
            # Internal implementation note: legacy behavior is preserved during modernization.
            days = {
                'Shanbeh': 'شنبه', 'Yekshanbeh': 'یک‌شنبه', 'Doshanbeh': 'دوشنبه',
                'Seshanbeh': 'سه‌شنبه', 'Chaharshanbeh': 'چهارشنبه',
                'Panjshanbeh': 'پنج‌شنبه', 'Jomeh': 'جمعه'
            }
            months = {
                'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
                'Tir': 'تیر', 'Mordad': 'عضواد', 'Shahrivar': 'شهریور',
                'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
                'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند'
            }
            for en, fa in days.items():
                formatted = formatted.replace(en, fa)
            for en, fa in months.items():
                formatted = formatted.replace(en, fa)
            return formatted
        except Exception:
            return date_str
    def send_full_details(self, chat_id: int, table: str, request_id: int) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            rows = self.db.select_dict(table, "id = ?", (request_id,))
            if not rows:
                self.bot.send_message(chat_id, MESSAGES["error_displaying_details"])
                return
            request = rows[0]
            settings = self.settings.get(table, {})
            # Internal implementation note: legacy behavior is preserved during modernization.
            out_lines: list[str] = []
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            def add_parent_section(record: dict, wanted_fields: list[str] | None, title: str | None = None):
                """Legacy-compatible behavior preserved for this callable."""
                if title:
                    out_lines.append(title)
                fields = wanted_fields or record.keys()
                for f in fields:
                    if f in MEDIA_FIELDS or f in ignor_labels:
                        continue
                    lbl = field_labels.get(f, f)
                    val = record.get(f)
                    if f in ("phone", "phone_number"):
                        val = self.normalize_phone_number(val)
                    if f in ("is_premium", "premium"):
                        val = "هست" if val else "نیست"
                    if f in ("U_code", "PU_code") and val:
                        val = f"/{val}"
                    out_lines.append(f"📌 {lbl} : {val or 'ندارد'}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            if settings.get("parent_table") and settings.get("link_field"):
                p_table = settings["parent_table"]
                p_link  = settings["link_field"]
                wanted  = settings.get("user_info_fields", [])
                overview = settings.get("request_overview", [])
                if p_link in request:
                    prow = self.db.select_dict(p_table, f"{p_link} = ?", (request[p_link],))
                    if prow:
                        add_parent_section(prow[0], wanted)
                # Internal implementation note: legacy behavior is preserved during modernization.
                for ov in overview:
                    p_table = ov["table"]
                    p_link  = ov["link_field"]
                    col_con = ov["column_connect"]
                    if col_con in request:
                        prow = self.db.select_dict(p_table, f"{p_link} = ?", (request[col_con],))
                        if prow:
                            add_parent_section(prow[0], ov.get("fields"), ov.get("title_name"))
            # Internal implementation note: legacy behavior is preserved during modernization.
            for p_cfg in settings.get("parent_tables", []):
                p_table = p_cfg["table"]
                link_field = p_cfg["link_field"]
                col_con    = p_cfg["column_connect"]
                if link_field not in request:
                    continue
                prow = self.db.select_dict(p_table, f"{col_con} = ?", (request[link_field],))
                if prow:
                    add_parent_section(prow[0], p_cfg.get("fields"), p_cfg.get("title_name"))
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            out_lines.append("\n📋 جزئیات کامل درخواست:")
            created_at   = request.get("created_at")
            last_updated = request.get("last_updated")
            for key, value in request.items():
                if not value:
                    continue
                if key in MEDIA_FIELDS or key in ignor_labels:
                    continue
                # Internal implementation note: legacy behavior is preserved during modernization.
                if key == "last_updated" and created_at and value == created_at:
                    continue
                lbl = field_labels.get(key, key)
                # Internal implementation note: legacy behavior is preserved during modernization.
                if table == "request_drafts" and key == "staff_code":
                    row = self.db.select_dict("codes" ,"code = ?" , (value,) )
                    if row:
                        username = str(row[0].get("username")).replace("@" , "")
                        if username and username.lower() != "none":
                            value = f"<a href='https://t.me/{username}'>{value}</a>"
                # Internal implementation note: legacy behavior is preserved during modernization.
                if re.fullmatch(PHONE_PT, str(value)):
                    value = self.normalize_phone_number(value)
                # Internal implementation note: legacy behavior is preserved during modernization.
                if key.lower() in DATE_FIELDS:
                    value = self.convert_to_shamsi(value)
                # username
                if key == "username":
                    if isinstance(value, str) and not value.startswith("@"):
                        value = "@" + value
                # PREMIUM / status
                if key in ("premium", "is_premium", "status"):
                    value = "هست" if str(value).lower() in ("1", "true", "approved") else "نیست"
                # Internal implementation note: legacy behavior is preserved during modernization.
                if key == "rejection_reason":
                    parsed = None
                    if isinstance(value, str) and value.strip().startswith("{"):
                        try:
                            parsed = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(value, dict):
                        parsed = value
                    if parsed:
                        out_lines.append("🚫 دلایل رد دفعات قبل:")
                        dict_col = settings.get("dict_column")
                        identity_verification_status = json.loads(request.get(dict_col, "{}") or "{}") if dict_col else {}
                        for fld, info in parsed.items():
                            if identity_verification_status.get(fld) is False:  # Internal implementation note: legacy behavior is preserved during modernization.
                                continue
                            fld_lbl = field_labels.get(fld, fld)
                            reason  = info.get("reason", "بدون دلیل مشخص")
                            when    = self.convert_to_shamsi(info.get("date", "")) or ""
                            out_lines.append(f" • {fld_lbl} : {reason} {when}")
                    else:
                        out_lines.append(f"🚫 دلیل رد: {value}")
                    continue
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(value, str) and value.strip().startswith("{"):
                    try:
                        obj = json.loads(value)
                        if isinstance(obj, dict):
                            value = obj
                    except json.JSONDecodeError:
                        pass
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(value, dict):
                    if all(isinstance(v, bool) for v in value.values()):
                        continue  # Internal implementation note: legacy behavior is preserved during modernization.
                    out_lines.append(f"{lbl} :")
                    for sub_k, sub_v in value.items():
                        sub_lbl = field_labels.get(sub_k, sub_k)
                        if isinstance(sub_v, dict):               # services
                            title = sub_v.get("title", sub_lbl)
                            price = sub_v.get("price")
                            out_lines.append(f"  • {title}" + (f" – {int(price):,} تومان" if price else ""))
                        else:
                            out_lines.append(f"  • {sub_lbl} : {sub_v}")
                    continue
                # Internal implementation note: legacy behavior is preserved during modernization.
                if key in ("U_code", "PU_code"):
                    value = f"/{value}"
                out_lines.append(f"📌 {lbl} : {value}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            whole_text = "\n".join(out_lines).strip() or "—"
            def send_chunk(txt: str):
                self.bot.send_message(
                    chat_id,
                    txt,
                    parse_mode="HTML",
                    reply_markup=self.request_actions_menu(
                        is_not_ditails=True,
                        is_type3=(settings.get("type", 1) == 3)
                    )
                )
            if len(whole_text) <= MAX_TELEGRAM_CHARS:
                send_chunk(whole_text)
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                chunk = []
                total = 0
                for line in whole_text.splitlines():
                    total += len(line) + 1
                    chunk.append(line)
                    if total >= MAX_TELEGRAM_CHARS:
                        send_chunk("\n".join(chunk))
                        chunk, total = [], 0
                if chunk:
                    send_chunk("\n".join(chunk))
            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.send_media(chat_id, request):
                log.info(f"Full details sent for request #{request_id} in {table}")
            else:
                log.info(f"Text details sent, but media failed for request #{request_id} in {table}")
        except Exception as exc:
            log.exception(f"Error in send_full_details: {exc}")
            self.bot.send_message(chat_id, MESSAGES["error_displaying_details"])
    def send_media(self, chat_id, request):
        """Legacy-compatible behavior preserved for this callable."""
        media_success = True
        for field, media_type in MEDIA_FIELDS.items():
            if field in request and request[field] and field not in ignor_labels:
                file_id = request[field]
                caption = f"{field_labels.get(field, field)}"
                try:
                    send_method = self.S_media.get_method(media_type)
                    if send_method:
                        log.info(
                            f"Trying to send '{file_id}' as '{media_type}' to chat {chat_id}...")
                        sig = inspect.signature(send_method)
                        params = {'chat_id': chat_id}
                        file_param = list(sig.parameters.keys())[1]
                        params[file_param] = file_id
                        if 'caption' in sig.parameters:
                            params['caption'] = caption
                        message = send_method(**params)
                        if message:
                            log.info(
                                f"✅ Media '{field}' sent with message_id {message.message_id}")
                        else:
                            log.warning(
                                f"⚠️ Media sending returned None for chat {chat_id}")
                    else:
                        log.exception(
                            f"❌ Unsupported media type: '{media_type}' for field '{field}'")
                        media_success = False
                except telebot.apihelper.ApiException as e:
                    log.warning(
                        f"⚠️ Failed sending '{file_id}' as '{media_type}': {e}, trying auto-detect...")
                    if not self.S_media.send_by_auto_detect(chat_id, file_id, caption=caption):
                        log.exception(
                            f"❌ Auto-detect failed for '{file_id}' ({field})")
                        media_success = False
                except Exception as e:
                    log.exception(
                        f"❌ Unexpected error processing media '{field}': {e}")
                    media_success = False
        return media_success
    def prompt_publish_time_option(self, chat_id, ad_row):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        has_publish_time = ad_row.get("publish_time")
        if has_publish_time and not "اکنون" in has_publish_time:
            # Internal implementation note: legacy behavior is preserved during modernization.
            buttons.append(KeyboardButton(BUTTONS["publish_at_ad_time"]))
        buttons.extend([
            KeyboardButton(BUTTONS["publish_now"]),     # Internal implementation note: legacy behavior is preserved during modernization.
            KeyboardButton(BUTTONS["publish_manual"]),  # Internal implementation note: legacy behavior is preserved during modernization.
            KeyboardButton(BUTTONS["publish_list"])     # Internal implementation note: legacy behavior is preserved during modernization.
        ])
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)
      # Internal implementation note: legacy behavior is preserved during modernization.
        publish_time_text = f"\n🕒 زمان تعیین‌شده در آگهی: {ad_row.get('publish_time')}" if ad_row.get(
            "publish_time") else ""
        full_text = MESSAGES["prompt_publish_time"] + publish_time_text
        # Internal implementation note: legacy behavior is preserved during modernization.
        msg = self.bot.send_message(
            chat_id,
            full_text,
            reply_markup=markup
        )
        self.bot.register_next_step_handler(
            msg,
            self.handle_publish_option
        )
    def return_to_request_menu(self, message, table="ads"):
        # Internal implementation note: legacy behavior is preserved during modernization.
        base = "درخواست‌های"
        center = f"{self.settings[table]['Translate']['table_name']}"
        hamintori = "(1)"
        message.text = f"{base} {center} {hamintori}"
        print(message.text)
        self.route_menu(message)
    def handle_publish_option(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text
        data = self.current_publish_selection.get(chat_id)
        if self.is_back(message):
            return
        if not data:
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup = self.add_back_buttons(markup)
        remove_kb = markup
        ad_row = data["ad_row"]
        table = data["table"]
        request_id = data["request_id"]
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text == BUTTONS["publish_at_ad_time"] and ad_row.get("publish_time"):
            publish_time = ad_row["publish_time"]
            self.publish_scheduler.add_to_publish_queue(
                ad_id=request_id,
                table_name=table,
                publish_time=publish_time
            )
            # 4$
            self.bot.send_message(
                chat_id,
                MESSAGES["publish_scheduled"] % {
                    "id": request_id, "time": publish_time},
                reply_markup=remove_kb
            )
            self.notify_user(table, request_id, "approved")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.current_publish_selection.pop(chat_id, None)
            self.return_to_request_menu(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif text == BUTTONS["publish_now"]:
            future_time = datetime.now() + timedelta(seconds=30)
            publish_time = future_time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"publish time = {publish_time}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.publish_scheduler.add_to_publish_queue(
                ad_id=request_id,
                table_name=table,
                publish_time=publish_time
            )
            self.bot.send_message(
                chat_id,
                MESSAGES["publish_immediate"] % {"id": request_id},
                reply_markup=remove_kb
            )
            self.notify_user(table, request_id, "approved")
            self.current_publish_selection.pop(chat_id, None)
            self.return_to_request_menu(message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif text == BUTTONS["publish_manual"]:
            # Internal implementation note: legacy behavior is preserved during modernization.
            msg = self.bot.send_message(
                chat_id,
                MESSAGES["prompt_manual_time"],
                reply_markup=markup
            )
            self.bot.register_next_step_handler(
                msg,
                self.handle_manual_time
            )
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif text == BUTTONS["publish_list"]:
            times = self.generate_publish_time_list()
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            buttons = [KeyboardButton(t) for t in times]
            markup.add(*buttons)
            markup = self.add_back_buttons(markup)
            msg = self.bot.send_message(
                chat_id,
                MESSAGES["prompt_list_time"],
                reply_markup=markup
            )
            self.bot.register_next_step_handler(
                msg,
                self.handle_publish_list
            )
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id,
                MESSAGES["error_invalid_option"],
                reply_markup=remove_kb
            )
    def handle_manual_time(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        data = self.current_publish_selection.get(chat_id)
        remove_kb = ReplyKeyboardRemove()
        if self.is_back(message):
            return
        if not data:
            return
        try:
            now = datetime.now()
            publish_dt = datetime.strptime(text, "%H:%M").replace(
                year=now.year,
                month=now.month,
                day=now.day
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            if publish_dt < now:
                publish_dt += timedelta(days=1)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if publish_dt < now + timedelta(minutes=5):
                raise ValueError()
        except Exception:
            # Internal implementation note: legacy behavior is preserved during modernization.
            msg = self.bot.send_message(
                chat_id,
                MESSAGES["error_invalid_time"] % {"min": 5},
                reply_markup=remove_kb
            )
            self.bot.register_next_step_handler(
                msg,
                self.handle_manual_time
            )
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        publish_time = publish_dt.strftime("%Y-%m-%d %H:%M:%S")
        self.publish_scheduler.add_to_publish_queue(
            ad_id=data["request_id"],
            table_name=data["table"],
            publish_time=publish_time
        )
        self.bot.send_message(
            chat_id,
            MESSAGES["publish_scheduled"] % {
                "id": data["request_id"],
                "time": publish_dt.strftime("%H:%M")},
            reply_markup=remove_kb
        )
        self.notify_user(data["table"], data["request_id"], "approved")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_publish_selection.pop(chat_id, None)
        self.return_to_request_menu(message)
    def handle_publish_list(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        data = self.current_publish_selection.get(chat_id)
        remove_kb = ReplyKeyboardRemove()
        valid_times = self.generate_publish_time_list()
        if self.is_back(message):
            return
        if not data:
            return
        if text not in valid_times:
            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            buttons = [KeyboardButton(t) for t in valid_times]
            markup.add(*buttons)
            markup = self.add_back_buttons(markup)
            msg = self.bot.send_message(
                chat_id,
                MESSAGES["error_invalid_option"],
                reply_markup=remove_kb
            )
            self.bot.register_next_step_handler(
                msg,
                self.handle_publish_list
            )
            return
        now = datetime.now()
        publish_dt = datetime.strptime(text, "%H:%M").replace(
            year=now.year,
            month=now.month,
            day=now.day
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        if publish_dt < now:
            publish_dt += timedelta(days=1)
        # Internal implementation note: legacy behavior is preserved during modernization.
        publish_time = publish_dt.strftime("%Y-%m-%d %H:%M:%S")
        self.publish_scheduler.add_to_publish_queue(
            ad_id=data["request_id"],
            table_name=data["table"],
            publish_time=publish_time
        )
        self.bot.send_message(
            chat_id,
            MESSAGES["publish_scheduled"] % {
                "id": data["request_id"],
                "time": publish_dt.strftime("%H:%M")},
            reply_markup=remove_kb
        )
        self.notify_user(data["table"], data["request_id"], "approved")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_publish_selection.pop(chat_id, None)
        self.return_to_request_menu(message)
    def generate_publish_time_list(self) -> list:
        """Legacy-compatible behavior preserved for this callable."""
        now = datetime.now()
        # Internal implementation note: legacy behavior is preserved during modernization.
        minute = now.minute
        if minute == 0:
            next_dt = now.replace(second=0, microsecond=0)
        elif minute <= 30:
            next_dt = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_dt = (now + timedelta(hours=1)
                       ).replace(minute=0, second=0, microsecond=0)
        end_dt = now.replace(hour=23, minute=30, second=0, microsecond=0)
        slots = []
        current = next_dt
        while current <= end_dt:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)
        return slots
    def route_menu(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.is_back(message):
            return
        chat_id = message.chat.id
        text = message.text
        if text == BUTTONS["back_to_previous"]:
            self.back_to_pervious(message)
            return True
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
            return True
        table = self.current_table.get(chat_id)
        request_info = self.current_request.get(chat_id)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if text.startswith("درخواست‌های "):
            table_label = text.split(
                " (")[0].replace("درخواست‌های ", "").strip()
            for table in self.settings.keys():
                table_name = self.settings[table]["Translate"]["table_name"]
                if table_name == table_label:
                    resolved_table = table
                    break
            if resolved_table:
                # print(resolved_table)
                self.current_table[chat_id] = resolved_table
                self.requests_menu(message, chat_id, resolved_table)
                return
            else:
                log.warning(f"we cant detect {resolved_table} table")
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.requests_main_menu(message)
                return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if table and text.startswith("درخواست #"):
            self.handle_request_selection(message, table)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if request_info:
            if text in [BUTTONS["edit"], BUTTONS["accept"], BUTTONS["reject"], BUTTONS["block"], BUTTONS["view_more_details"], BUTTONS["view_less_ditails"]]:
                self.handle_request_action(message)
            elif text == BUTTONS["back_to_previous"]:
                del self.current_request[chat_id]
                self.requests_menu(message, chat_id, table)
            else:
                print("Are Haminjast")
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.requests_menu(message, chat_id, table)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if table:
            print("na injast")
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.requests_menu(message, chat_id, table)
        else:
            print("nakhiram injast")
            self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
            self.requests_main_menu(message)
    def register_handlers(self):
        """Legacy-compatible behavior preserved for this callable."""
        @self.bot.callback_query_handler(func=lambda c: c.data == "show_request_manager")
        def open_request_manager(cb):
            self.requests_main_menu(cb.message)
            self.bot.answer_callback_query(cb.id)
        @self.bot.message_handler(func=lambda m: m.text == BUTTONS["update"])
        def update_handler(m):
            self.handle_requests_menu(m)
        @self.bot.message_handler(func=lambda m: m.text.startswith("درخواست‌های "))
        def request_router(m):
            chat_id = m.chat.id
            selected_label = m.text.split(
                " (")[0].replace("درخواست‌های ", "").strip()
            resolved_table = next((t for t, label in TABLE_NAME["table_names"].items(
            ) if label == selected_label), None)
            if not resolved_table:
                print("naaaaa injasstttt ")
                self.bot.send_message(chat_id, MESSAGES["invalid_choice"])
                self.requests_main_menu(m)
                return
            self.current_table[chat_id] = resolved_table
            self.requests_menu(m, chat_id, resolved_table)
        @self.bot.message_handler(func=lambda m: m.text.startswith("درخواست #"))
        def request_selection(m):
            table = self.current_table.get(m.chat.id)
            if table:
                self.handle_request_selection(m, table)
        @self.bot.message_handler(func=lambda m: m.text in [BUTTONS["edit"], BUTTONS["accept"], BUTTONS["reject"], BUTTONS["block"], BUTTONS["view_more_details"], BUTTONS["view_less_ditails"]])
        def request_action(m):
            self.handle_request_action(m)
        @self.bot.message_handler(func=lambda m: m.text in [BUTTONS["back_to_previous"], BUTTONS["back_to_requests"]])
        def back_previous(m):
            chat_id = m.chat.id
            if chat_id in self.current_request:
                table = self.current_request[chat_id][0]
                del self.current_request[chat_id]
                self.requests_menu(m, chat_id, table)
            elif chat_id in self.current_table:
                del self.current_table[chat_id]
                self.requests_main_menu(message=m)
        @self.bot.message_handler(func=lambda m: m.text == BUTTONS["back_to_main"])
        def back_main(m):
            chat_id = m.chat.id
            self.current_request.pop(chat_id, None)
            self.current_table.pop(chat_id, None)
            self.back_to_main(m)
