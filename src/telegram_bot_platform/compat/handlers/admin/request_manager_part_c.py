from __future__ import annotations

from .request_manager_context import *


class RequestManagerPartCMixin:
    def update_expired_slots(self, time_slots: dict) -> dict:
        """Legacy-compatible behavior preserved for this callable."""
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        return {
            slot: False if status and (
                int(slot[:2]) * 60 + int(slot[3:])) < current_time else status
            for slot, status in time_slots.items()
        }
    def handle_request_action(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        action = message.text
        # print(f"action = {action}")
        if self.is_back(message):
            return
        #Actions
        # Internal implementation note: legacy behavior is preserved during modernization.
        if chat_id not in self.current_request:
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        current = self.current_request[chat_id]
        table = current[0]
        request_id = current[1]
        settings = self.settings.get(table, {})
        dbtype = settings.get("type", 1)
        # Internal implementation note: legacy behavior is preserved during modernization.
        status_column = settings.get("status_column", "status")
        # ================================================================================
        # ad_data = self.db.select_dict(
        #     table, "id = ?", (request_id,))
        # if not ad_data:
        # Internal implementation note: legacy behavior is preserved during modernization.
        # ad_row = ad_data[0]
        self.ifuserwantedit[chat_id].extend([
            message,
            current,
        ])
        # print(ad_row)
        # ================================================================================
        try:
            if action == BUTTONS["accept"]:
                self.current_request.pop(chat_id, None)
                if dbtype in (1, 2):
                    approved_successfully = False
                    if dbtype == 1 and table == "staff":
                        try:
                            self.bot.send_message(
                                chat_id,
                                "✅ پروفایل ارائه‌دهنده با موفقیت ثبت شد.\n"
                                "📤 این پروفایل در پایان روز، رأس ساعت ۱۲:۰۰ امشب به کانال ارسال خواهد شد.\n"
                                "پروفایل ارائه‌دهنده⏬",
                                parse_mode="HTML"
                            )
                            rows = self.db.select_dict("staff", "id = ?", (request_id,))
                            if not rows:
                                self.bot.send_message(chat_id, "❌ پرسنل یافت نشد.")
                                log.error(f"[accept] Staff ID {request_id} not found.")
                                return
                            p_row = rows[0]
                            caption, photos = self.build_staff_caption(p_row)
                            if not photos:
                                self.bot.send_message(chat_id, "❌ این پرسنل هیچ عکسی ندارد.")
                                log.warning(f"[accept] Staff ID {request_id} has no photos.")
                                return
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            media = []
                            for i, pid in enumerate(photos[:10]):
                                media.append(
                                    telebot.types.InputMediaPhoto(
                                        media=pid,
                                        caption=caption if i == 0 else None,
                                        parse_mode="HTML" if i == 0 else None
                                    )
                                )
                            self.bot.send_media_group(chat_id, media)
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            self._queue_staff_for_publish(request_id)
                        except Exception as e:
                            log.error(f"[accept] Error processing staff ID {request_id}: {e}")
                            self.bot.send_message(chat_id, "❌ خطا هنگام پردازش پرسنل.")
                            return
                    adminreq = False
                    if dbtype == 1 and table == "request_drafts":
                        try:
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            row = self.db.select_dict("request_drafts", "id = ?", (request_id,))
                            if not row:
                                self.bot.send_message(chat_id, "❌ درخواستی با این شناسه یافت نشد.")
                                return
                            cust = row[0]
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            photo_id = cust.get("verification_photo_1_file_id")
                            if not photo_id:
                                self.bot.send_message(chat_id, "⚠️ تصویر سلفی در دسترس نیست.")
                                return
                            region = cust.get("region", "—")
                            req_time = cust.get("request_time", "—")
                            name = cust.get("name", "—")
                            note = cust.get("note", "")  # Internal implementation note: legacy behavior is preserved during modernization.
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            caption_lines = [
                                f"👤 نام: {name}",
                                f"🌍 منطقه: {region}",
                                f"🕒 زمان درخواستی: {req_time}"
                            ]
                            if note:
                                caption_lines.append(f"📝 توضیحات: {note}")
                            caption = "\n".join(caption_lines)
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            keyboard = InlineKeyboardMarkup(row_width=2)
                            keyboard.add(
                                InlineKeyboardButton("✅ تأیید", callback_data=f"request_drafts:accept:{request_id}"),
                                InlineKeyboardButton("❌ رد", callback_data=f"request_drafts:reject:{request_id}")
                            )
                            # Internal implementation note: legacy behavior is preserved during modernization.
                            code_row = self.db.select_dict("codes", "code = ?", (cust.get("staff_code"),))
                            if not code_row:
                                self.bot.send_message(chat_id, "❌ کد پرسنل مربوطه نامعتبر است.")
                                return
                            target_telegram_id = code_row[0].get("telegram_id")
                            if not target_telegram_id:
                                self.bot.send_message(chat_id, "❌  شناسه تلگرام پرسنل یافت نشد. درخواست توسط ادمین مدیریت میشود")
                                adminreq = True
                            if not adminreq:
                                # Internal implementation note: legacy behavior is preserved during modernization.
                                try:
                                    # Internal implementation note: legacy behavior is preserved during modernization.
                                    file_info = self.bots["staff"].get_file(photo_id)
                                    file_path = file_info.file_path
                                    download_url = f"https://api.telegram.org/file/bot{self.bots['staff'].token}/{file_path}"
                                    # Internal implementation note: legacy behavior is preserved during modernization.
                                    photo_response = requests.get(download_url)
                                    photo_response.raise_for_status()  # Internal implementation note: legacy behavior is preserved during modernization.
                                    photo_file = f"verification_photo_{request_id}.jpg"
                                    with open(photo_file, "wb") as f:
                                        f.write(photo_response.content)
                                    log.debug(f"عکس با موفقیت دانلود شد: {photo_file}")
                                except Exception as e:
                                    log.error(f"خطا در دانلود عکس برای درخواست {request_id}: {str(e)}")
                                    return
                                # Internal implementation note: legacy behavior is preserved during modernization.
                                try:
                                    intro_message = (
                                        "📩 یک درخواست جدید برای شما ثبت شده است.\n"
                                        "لطفاً تصویر و اطلاعات مشتری را بررسی کرده و با استفاده از دکمه‌های زیر اقدام کنید ✨\n"
                                        "❗️ در صورت رد درخواست، لطفاً دلیل آن را مشخص کنید تا ادمین بتواند بررسی کند 💬\n"
                                        "با تشکر از دقت و همکاری شما 😇"
                                    )
                                    log.debug(f"ارسال پیام اطلاع‌رسانی به پرسنل (telegram_id: {target_telegram_id}, request_id: {request_id})")
                                    self.bots["staff"].send_message(
                                        chat_id=target_telegram_id,
                                        text=intro_message,
                                        parse_mode="Markdown"
                                    )
                                    log.info(f"پیام اطلاع‌رسانی با موفقیت به {target_telegram_id} برای درخواست {request_id} ارسال شد")
                                except Exception as e:
                                    log.error(f"خطا در ارسال پیام اطلاع‌رسانی به {target_telegram_id} برای درخواست {request_id}: {str(e)}")
                                    return
                                # Internal implementation note: legacy behavior is preserved during modernization.
                                try:
                                    log.debug(f"ارسال عکس به پرسنل (telegram_id: {target_telegram_id}, request_id: {request_id})")
                                    with open(photo_file, "rb") as photo:
                                        self.bots["staff"].send_photo(
                                            chat_id=target_telegram_id,
                                            photo=photo,
                                            caption=caption,
                                            reply_markup=keyboard,
                                            parse_mode="HTML"
                                        )
                                    log.info(f"عکس با موفقیت به {target_telegram_id} برای درخواست {request_id} ارسال شد")
                                except Exception as e:
                                    log.error(f"خطا در ارسال عکس به {target_telegram_id} برای درخواست {request_id}: {str(e)}")
                                    return
                                finally:
                                    # Internal implementation note: legacy behavior is preserved during modernization.
                                    if os.path.exists(photo_file):
                                        os.remove(photo_file)
                                        log.debug(f"فایل ویژه {photo_file} حذف شد")
                        except Exception as e:
                            log.error(f"خطا در پردازش درخواست {request_id}: {str(e)}")
                    try:
                        self.db.update(
                            table, {status_column: "approved"}, "id = ?", (request_id,)
                        )
                        self.bot.send_message(chat_id, MESSAGES["request_accepted_admin"])
                        if adminreq or not table == "request_drafts":
                            self.notify_user(table, request_id, "approved")
                        log.info(f"[accept] Request ID {request_id} in table `{table}` approved.")
                        approved_successfully = True
                    except Exception as e:
                        log.error(f"[accept] DB update error: table={table}, id={request_id} → {e}")
                        self.bot.send_message(chat_id, "❌ خطا در تأیید درخواست.")
                elif dbtype == 3:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    table, request_id, review_column = current
                    if action == BUTTONS["submit_request"]:
                        self.current_request.pop(chat_id, None)
                        self.handle_submit_request(
                            message, chat_id, table, review_column)
                    elif action.startswith("✅") or action.startswith("❌"):
                        self.toggle_review_checkbox(message, chat_id)
                    elif action == BUTTONS["view_more_details"]:
                        self.send_full_details(chat_id, table, request_id)
                    elif action == BUTTONS["view_less_ditails"]:
                        self.bot.edit_message_text(
                            text=self.current_ditails[chat_id]["text"],
                            chat_id=chat_id,
                            message_id=self.current_ditails[chat_id]["id"],
                            reply_markup=keyboard,
                            parse_mode="HTML"
                        )
                        pass
                    else:
                        self.bot.send_message(
                            chat_id, MESSAGES["invalid_option"])
                    return
                # Internal implementation note: legacy behavior is preserved during modernization.
                elif dbtype == 4:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    ad_row = self.db.select_dict(
                        table, "id = ?", (request_id,))[0]
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.current_publish_selection[chat_id] = {
                        "ad_row": ad_row,
                        "table": table,
                        "request_id": request_id
                    }
                    self.prompt_publish_time_option(chat_id, ad_row)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.update(
                        table, {status_column: "approved"}, "id = ?", (request_id,))
                    return
                elif dbtype == 5:
                    # """
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # """
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    rows = self.db.select_dict(table, "id = ?", (request_id,))
                    if not rows:
                        log.warning(
                            f"[TYPE5] درخواست با id={request_id} یافت نشد.")
                        return
                    req = rows[0]
                    ad_id = req.get("ad_id")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    ad_row = self.db.select_dict("ads", "id = ?", (ad_id,))
                    ad_row = ad_row[0] if ad_row else {}
                    # --------------------------------------------------------------
                    slot_time = req.get("slot_time")
                    extra_times = req.get("extra_times")
                    extra_times = json.loads(extra_times or "[]")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    status_col = self.settings[table]["status_column"]
                    self.db.update(
                        table, {status_col: "approved"}, "id = ?", (request_id,))
                    try:
                        alltimes = extra_times + [slot_time]
                        placeholders = ",".join("?" for _ in alltimes)
                        query = f"U_code != ? AND ad_id = ? AND slot_time IN ({placeholders})"
                        params = (req.get("U_code"), ad_id, *alltimes)
                        the_clientwithsameord = self.db.select_dict(
                            table, query, params)
                        plocholder = {row["U_code"]: row["telegram_id"]
                                      for row in the_clientwithsameord}
                        ucodes = list(plocholder.keys())
                        placeholders = ",".join("?" for _ in ucodes)
                        self.db.update(
                            table, {status_col: "expired"}, f"U_code IN ({placeholders})", ucodes)
                        for u in plocholder.values():
                            self.bot.send_message(
                                u, "❌ درخواست شما برای این ساعت و آگهی لغو شد زیرا ظرفیت پر شد. لطفاً ساعت یا آگهی دیگری را امتحان کنید.")
                    except:
                        pass
                    self.bot.send_message(
                        chat_id, MESSAGES["request_accepted_admin"])
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    for parent_table, tg_id in self.target_request[chat_id][request_id].items():
                        if not tg_id:
                            continue
                        # bot = getattr(self, f"{parent_table}_bot", self.bot)
                        key = f"request_approved_{parent_table}"
                        # #print(self.target_request[chat_id][request_id].items())
                        # print(f"bot : {parent_table} | t_id : {tg_id} | message : {key}")
                        self.bots[parent_table].send_message(
                            tg_id, MESSAGES[key])
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    live = self.db.select_dict(
                        "live_ads", "ad_id = ?", (ad_id,)
                    )
                    if not live:
                        log.warning(
                            f"[TYPE5] live_ads for  ad_id={ad_id} not founded!  .")
                        return
                    live = live[0]
                    msg_id = live.get("channel_message_id")
                    slots = json.loads(live.get("time_slots", "{}"))
                    # print(extra_times)
                    # print(slots)
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if slot_time in slots:
                        slots[slot_time] = False
                    for extra_time in extra_times:
                        # print(extra_time)
                        if extra_time in slots:
                            slots[extra_time] = False
                    keyboard = InlineKeyboardMarkup(row_width=4)
                    buttons = []
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    link_base = f"https://t.me/{html.escape(CLIENT_BOT_ID)}?start"
                    for slot, available in slots.items():
                        if available:
                            # param = f"reserve_{table}_{ad_id}_{slot.replace(':', '_')}"
                            slot_time_fmt = datetime.strftime(
                                datetime.strptime(slot, "%H:%M"), "%H_%M")
                            param = f"reserve_ads_{ad_id}_{slot_time_fmt}"
                            # url = f"https://t.me/{CLIENT_BOT_ID}?start={param}"
                            buttons.append(InlineKeyboardButton(
                                slot, url=f"{link_base}={param}"))
                        else:
                            # url = f"https://t.me/{CLIENT_BOT_ID}?start={param}"
                            buttons.append(InlineKeyboardButton(
                                "رزوشده🕰", url=f"{link_base}=ShowAvalabelCodes"))
                    rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
                    if len(rows) >= 2 and len(rows[-1]) == 1:
                        flat = sum(rows, [])
                        rows = [flat[i:i+3] for i in range(0, len(flat), 3)]
                    rows.append([
                        InlineKeyboardButton(
                            text=BUTTONS["Goto_Cutsomer_bot"], url=f"https://t.me/{CLIENT_BOT_ID}?start"),
                        InlineKeyboardButton(
                            text=BUTTONS["Add_toFavoris"], callback_data=f"AddToFavorits_{ad_row.get('U_code')}")
                    ])
                    client_bot = self.notification_manager.bots["client"]
                    keyboard = InlineKeyboardMarkup()
                    for r in rows:
                        keyboard.row(*r)
                    try:
                        # if any(slots.values()):
                        #     client_bot.edit_message_reply_markup(
                        #         chat_id=CHANNEL_ID,
                        #         message_id=msg_id,
                        #         reply_markup=keyboard
                        #     )
                        #     log.info(MESSAGES["log_update_buttons"].format(ad_id=ad_id))
                        # else:
                        #     client_bot.delete_message(
                        #         chat_id=CHANNEL_ID, message_id=msg_id
                        #     )
                        #     log.info(MESSAGES["log_delete_message"].format(ad_id=ad_id))
                        client_bot.edit_message_reply_markup(
                            chat_id=CHANNEL_ID,
                            message_id=msg_id,
                            reply_markup=keyboard
                        )
                        log.info(
                            MESSAGES["log_update_buttons"].format(ad_id=ad_id))
                    except Exception as e:
                        log.warning(f"{MESSAGES['log_error_edit']}: {e}")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.db.update(
                        "live_ads", {
                            "time_slots": json.dumps(slots, ensure_ascii=False)
                        },
                        "id = ?", (live["id"],)
                    )
                else:
                    self.bot.send_message(chat_id, MESSAGES["invalid_option"])
                    return
            elif action == BUTTONS["reject"]:
                if self.rejection_reason_menu(chat_id):
                    self.bot.register_next_step_handler(
                        message, self.handle_rejection_reason_selection, table, request_id)
                if dbtype == 5:
                    for parent_table, tg_id in self.target_request[chat_id][request_id].items():
                        if not tg_id:
                            continue
                        # bot = getattr(self, f"{parent_table}_bot", self.bot)
                        key = f"request_rejected_{parent_table}"
                        # #print(self.target_request[chat_id][request_id].items())
                        # print(f"bot : {parent_table} | t_id : {tg_id} | message : {key}")
                        if parent_table == "clients":
                            self.bots[parent_table].send_message(
                                tg_id, MESSAGES[key])
                return
            elif action == BUTTONS["block"]:
                self.current_request.pop(chat_id, None)
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.update(
                    table,
                    {status_column: "blocked"},
                    "id = ?",
                    (request_id,)
                )
                self.bot.send_message(chat_id, MESSAGES["request_blocked"])
                self.notify_user(table, request_id, "blocked")
                # Internal implementation note: legacy behavior is preserved during modernization.
                # Internal implementation note: legacy behavior is preserved during modernization.
                if table == "request_drafts":
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    row = self.db.select_dict(
                        "request_drafts",
                        "id = ?",
                        (request_id,)
                    )
                    if row:
                        tg_id = row[0]["telegram_id"]
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        self.db.update(
                            "clients",
                            {"status": "blocked"},
                            "telegram_id = ?",
                            (tg_id,)
                        )
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        self.bots["client"].send_message(
                            tg_id,
                            MESSAGES["user_blocked_by_admin"]
                        )
            elif action == BUTTONS["view_more_details"]:
                self.send_full_details(chat_id, table, request_id)
                return
            elif action == BUTTONS["view_less_ditails"]:
                # yadetbasheviewless
                pass
            elif action == BUTTONS["edit"]:
                # line 1804
                # edit_label = BUTTONS["edit"]
                # print(f"clicked on the {edit_label}")
                self.edit_request_fields(message)
                return
            else:
                self.bot.send_message(chat_id, MESSAGES["invalid_option"])
                return
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.requests_menu(message, chat_id, table)
            log.info(
                f"Action '{action}' processed for request #{request_id} in table {table} (type {dbtype}).")
        except Exception as e:
            log.exception(f"[handle_request_action] ❌ Error: {e}")
            self.bot.send_message(chat_id, MESSAGES["error_processing_action"])
            self.requests_menu(message, chat_id, table)
    def backfromedittseerec(self,message):
        chat_id = message.chat.id
        message = self.ifuserwantedit[chat_id][1]
        message.text = self.ifuserwantedit[chat_id][0]
        self.current_request[chat_id] = self.ifuserwantedit[chat_id][2]
        current = self.current_request[chat_id]
        table = current[0]
        # request_id = current[1]
        self.current_ditails[chat_id] = [chat_id,]
        self.handle_request_selection(message , table )
        return
    def edit_request_fields(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        # from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
        chat_id = message.chat.id
        # -----------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -----------------------------
        try:
            table, request_id = self.current_request[chat_id]
        except (KeyError, ValueError):
            self.bot.send_message(chat_id, MESSAGES["request_not_found"], reply_markup=ReplyKeyboardRemove())
            return
        # -----------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -----------------------------
        row = next(iter(self.db.select_dict(table, "id = ?", (request_id,))), None)
        if not row:
            self.bot.send_message(chat_id, MESSAGES["request_info_absent"], reply_markup=ReplyKeyboardRemove())
            return
        # -----------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -----------------------------
        editable_fields = [
            f for f in row.keys()
            if f not in EDITABLE_FIELDS_EXCLUDE           # Internal implementation note: legacy behavior is preserved during modernization.
            and f not in MEDIA_FIELDS                     # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
                           # Internal implementation note: legacy behavior is preserved during modernization.
        ]
        # Internal implementation note: legacy behavior is preserved during modernization.
        editable_fields.sort(key=lambda fld: field_labels.get(fld, fld))
        # -----------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -----------------------------
        self.temp_data[chat_id] = {
            "edit_row": row,
            "table": table,
            "request_id": request_id,
            "fild_list":list(row.keys())
        }
        # -----------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -----------------------------
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        # Internal implementation note: legacy behavior is preserved during modernization.
        for fld in editable_fields:
            label = field_labels.get(fld, fld)
            buttons.append(f"{EMOJI['edit']} {label}")
        markup.add(*buttons)
        # Internal implementation note: legacy behavior is preserved during modernization.
        for media_fld in MEDIA_FIELDS:
            if media_fld in row:
                label = field_labels.get(media_fld, media_fld)
                markup.add(f"{EMOJI['media']} {label}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.add_back_buttons(markup)
        # -----------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -----------------------------
        self.bot.send_message(
            chat_id,
            MESSAGES["choice_a_field_for_edit"],
            reply_markup=markup,
        )
        self.bot.register_next_step_handler(message, self.handle_edit_field_choice)
    def handle_edit_field_choice(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return   
        if self.is_back(message):
            # Internal implementation note: legacy behavior is preserved during modernization.
            return 
        label = text.replace(EMOJI['edit'], "").replace(EMOJI['media'], "").strip()
        inv = self.invert_dict(field_labels)
        field = inv.get(label, label)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if field not in self.temp_data[chat_id]["fild_list"]:
            self.bot.send_message(
                chat_id,
                "⚠️ فیلدی که وارد کردید در لیست گزینه‌های قابل ویرایش وجود ندارد.\nلطفاً یکی از گزینه‌های موجود را انتخاب کنید یا بازگردید.",
            )
            message = self.ifuserwantedit[chat_id][1]
            self.current_request[chat_id] = self.ifuserwantedit[chat_id][2]
            self.handle_request_action(message)
            return
        inv =self.invert_dict(field_labels)
        field = inv.get(label, label)
        row = self.temp_data[chat_id]["edit_row"]
        current_value = row.get(field, "نامشخص")
        # Internal implementation note: legacy behavior is preserved during modernization.
        meta = EDITABLE_FIELD_TYPES.get(field, {})
        field_type = meta.get("type", "text")
        self.temp_data[chat_id].update({
            "editing_field": field,
            "editing_field_type": field_type,
            "editing_field_meta": meta
        })
        # Internal implementation note: legacy behavior is preserved during modernization.
        if field_type == "media":
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(
                chat_id, MESSAGES["please_send_new_file_for_edit"].format(label=label))
            return self.bot.register_next_step_handler(message, self.handle_edit_media_field)
        elif field_type == "media_group":
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.temp_data[chat_id]["editing_media_group_field"] = field
            self.temp_data[chat_id]["media_group"] = []
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.handle_edit_media_group_request(message)
        elif field_type == "json" and self.is_json_dict(current_value):
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                obj = json.loads(current_value)
                self.temp_data[chat_id].update({
                    "json_object": obj,
                    "json_edit_stack": []
                })
                return self.show_json_keys(message, obj)
            except:
                return self.bot.send_message(chat_id, MESSAGES["data_format_error"])
        elif field_type == "enum":
            # Internal implementation note: legacy behavior is preserved during modernization.
            choices = meta.get("choices", [])
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            for c in choices:
                markup.add(c)
            self.add_back_buttons(markup)
            self.bot.send_message(
                chat_id,
                f"🔘 مقدار فعلی: {current_value}\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=markup
            )
            return self.bot.register_next_step_handler(message, self.handle_edit_text_field)
        elif field_type == "bool":
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add("✅ هست", "❌ نیست")
            self.add_back_buttons(markup)
            current_label = "✅ هست" if str(
                current_value) in ("1", "True") else "❌ نیست"
            self.bot.send_message(
                chat_id,
                f"🔘 مقدار فعلی: {current_label}\nلطفاً وضعیت جدید را انتخاب کنید:",
                reply_markup=markup
            )
            return self.bot.register_next_step_handler(message, self.handle_edit_bool_value)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            intro = f"🔘 مقدار فعلی: {current_value}\n\n"
            if field_type == "int":
                prompt = intro + "لطفاً یک عدد صحیح وارد کنید:"
            elif field_type == "time":
                prompt = intro + \
                    "⏰ فرمت زمان HH:MM را رعایت کنید (مثلاً 21:30):"
            elif field_type == "date":
                fmt = meta.get("format", "%Y-%m-%d")
                prompt = intro + f"📅 تاریخ را به فرمت {fmt} وارد کنید:"
            else:
                prompt = intro + "✏️ مقدار جدید را وارد کنید:"
            self.bot.send_message(chat_id, prompt)
            return self.bot.register_next_step_handler(message, self.handle_edit_text_field)
    def handle_edit_bool_value(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return
        if self.is_back(message):
            # Internal implementation note: legacy behavior is preserved during modernization.
            return 
        if text == "✅ هست":
            value = 1
        elif text == "❌ نیست":
            value = 0
        else:
            self.bot.send_message(
                chat_id, "❌ گزینه نامعتبر! دوباره انتخاب کنید.")
            return self.bot.register_next_step_handler(message, self.handle_edit_bool_value)
        self._save_field_update(message, value)
    def show_json_keys(self, message, current_dict):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for k in current_dict.keys():
            markup.add(f"{EMOJI['key']} {k}")
        markup.add(KeyboardButton(BUTTONS["back"]))
        self.bot.send_message(
            chat_id, MESSAGES["json_key_prompt"], reply_markup=markup)
        return self.bot.register_next_step_handler(message, self.handle_json_key_selection)
    def handle_json_key_selection(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return
        if self.is_back(message):
            # Internal implementation note: legacy behavior is preserved during modernization.
            return 
        key = text.replace(EMOJI['key'], "").strip()
        stack = self.temp_data[chat_id]["json_edit_stack"]
        obj = self.temp_data[chat_id]["json_object"]
        current = obj
        for k in stack:
            current = current.get(k, {})
        if key not in current:
            self.bot.send_message(chat_id, MESSAGES["invalid_key"])
            return self.show_json_keys(message, current)
        value = current[key]
        if isinstance(value, dict):
            stack.append(key)
            return self.show_json_keys(message, value)
        else:
            stack.append(key)
            prompt = MESSAGES["edit_text_prompt"].format(current_value=value)
            self.bot.send_message(chat_id, prompt)
            return self.bot.register_next_step_handler(message, self.handle_json_value_input)
    def handle_json_value_input(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        new_val = message.text.strip()
        stack = self.temp_data[chat_id]["json_edit_stack"]
        obj = self.temp_data[chat_id]["json_object"]
        cur = obj
        for k in stack[:-1]:
            cur = cur[k]
        cur[stack[-1]] = new_val
        self._save_field_update(message, json.dumps(obj, ensure_ascii=False))
    def handle_edit_text_field(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text
        meta = self.temp_data[chat_id]["editing_field_meta"]
        ftype = self.temp_data[chat_id]["editing_field_type"]
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return
        if self.is_back(message):
            # Internal implementation note: legacy behavior is preserved during modernization.
            return 
        # Internal implementation note: legacy behavior is preserved during modernization.
        if ftype == "int":
            if not text.isdigit():
                self.bot.send_message(
                    chat_id, "❌ لطفاً یک عدد صحیح وارد کنید.")
                return self.bot.register_next_step_handler(message, self.handle_edit_text_field)
            value = int(text)
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif ftype == "time":
            try:
                datetime.strptime(text, "%H:%M")
                value = text
            except:
                self.bot.send_message(chat_id, "❌ فرمت صحیح HH:MM نیست.")
                return self.bot.register_next_step_handler(message, self.handle_edit_text_field)
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif ftype == "date":
            fmt = meta.get("format", "%Y-%m-%d")
            try:
                datetime.strptime(text, fmt)
                value = text
            except:
                self.bot.send_message(chat_id, f"❌ تاریخ باید طبق {fmt} باشد.")
                return self.bot.register_next_step_handler(message, self.handle_edit_text_field)
        # Internal implementation note: legacy behavior is preserved during modernization.
        elif ftype == "enum":
            choices = meta.get("choices", [])
            if text not in choices:
                self.bot.send_message(
                    chat_id, "❌ گزینه نامعتبر! یکی از موارد زیر را انتخاب کنید.")
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                for c in choices:
                    markup.add(c)
                self.add_back_buttons(markup)
                self.bot.send_message(
                    chat_id, MESSAGES["choice_a_field_for_edit"], reply_markup=markup)
                return self.bot.register_next_step_handler(message, self.handle_edit_text_field)
            value = text
        else:
            value = text
        self._save_field_update(message, value)
    def handle_edit_media_field(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text.strip()
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return   
        if self.is_back(message):
            # Internal implementation note: legacy behavior is preserved during modernization.
            return 
        log.debug(f"[handle_edit_media_field] start for chat_id={chat_id}")
        # Retrieve which field we're editing
        data = self.temp_data.get(chat_id, {})
        field = data.get("editing_field")
        if not field:
            log.error(f"[handle_edit_media_field] no 'editing_field' in temp_data for {chat_id}")
            self.bot.send_message(chat_id, "❌ An internal error occurred. Please try again.")
            return
        expected_type = MEDIA_FIELDS.get(field)
        if not expected_type:
            log.error(f"[handle_edit_media_field] Unknown media field '{field}'")
            self.bot.send_message(chat_id, "❌ Invalid media field. Operation aborted.")
            return
        # Map Telegram message to file_id
        try:
            if expected_type == "photo" and message.photo:
                new_file_id = self.save_media_to_channel(message, "photo")
            elif expected_type == "video" and message.video:
                new_file_id = self.save_media_to_channel(message, "video")
            elif expected_type == "document" and message.document:
                new_file_id = self.save_media_to_channel(message, "document")
            elif expected_type == "video_note" and message.video_note:
                new_file_id = self.save_media_to_channel(message, "video_note")
            elif expected_type == "voice" and message.voice:
                new_file_id = self.save_media_to_channel(message, "voice")
            else:
                raise ValueError("Media type mismatch or no media provided")
            if not new_file_id:
                raise RuntimeError("Forwarding succeeded but returned empty file_id")
            # Persist the updated media field through the existing compatibility database adapter.
            self.db.update(self.current_request[chat_id][0],
                           {field: new_file_id},
                           "id = ?",
                           (self.current_request[chat_id][1],))
            log.info(f"[handle_edit_media_field] Saved new {field} for {chat_id}, file_id={new_file_id}")
            self.bot.send_message(chat_id, "✅ File saved successfully.")
        except Exception as e:
            log.exception(f"[handle_edit_media_field] Error handling media for {chat_id}: {e}")
            self.bot.send_message(chat_id, "❌ Failed to process the file. Please send a valid media.")
            # re-ask for the same step
            self.bot.register_next_step_handler(message, self.handle_edit_media_field)
    def save_media_to_channel(self, message, media_type="photo") -> str:
        """
        Forward the incoming media to STORAGE_CHANNEL and return the new file_id.
        :param message: the incoming Telegram message
        :param media_type: one of 'photo', 'video', 'document', 'video_note', 'voice'
        :return: the new file_id in STORAGE_CHANNEL, or empty string on failure
        """
        chat_id = message.chat.id
        try:
            forwarded = self.bot.forward_message(
                STORAGE_CHANNEL,
                chat_id,
                message.message_id
            )
            log.debug(f"[save_media_to_channel] forwarded message_id={message.message_id} as {media_type}")
            # Extract the correct file_id from the forwarded message
            if media_type == "photo" and forwarded.photo:
                return forwarded.photo[-1].file_id
            if media_type == "video" and forwarded.video:
                return forwarded.video.file_id
            if media_type == "document" and forwarded.document:
                return forwarded.document.file_id
            if media_type == "video_note" and getattr(forwarded, "video_note", None):
                return forwarded.video_note.file_id
            if media_type == "voice" and forwarded.voice:
                return forwarded.voice.file_id
            # If we reach here, the forwarded message had no matching media
            log.error(f"[save_media_to_channel] No {media_type} found in forwarded message")
            return ""
        except Exception as e:
            log.exception(f"[save_media_to_channel] Failed to forward media: {e}")
            return ""
    def handle_edit_media_group_request(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        data = self.temp_data.setdefault(chat_id, {})
        field = data.get("editing_media_group_field")
        text = message.text
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return
        if self.is_back(message):
            return
        if not field:
            self.bot.send_message(chat_id, "❌ فیلد مدنظر مشخص نیست.")
            return
        row = self.db.select_dict(self.current_request[chat_id][0], "id = ?", (self.current_request[chat_id][1],))
        row = row[0] if row else {}
        photos = json.loads(row.get(field, "[]")) if isinstance(row.get(field), str) else row.get(field, [])
        if not photos:
            self.bot.send_message(chat_id, "❌ هیچ عکسی برای این فیلد ثبت نشده است.")
            return
        self.temp_data[chat_id]["media_groups"] = {}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for i, photo_id in enumerate(photos):
            label = f"عکس شماره ({i + 1})"
            try:
                self.bot.send_photo(chat_id, photo_id, caption=label)
                self.temp_data[chat_id]["media_groups"][label] = photo_id
                buttons.append(label)
            except Exception as e:
                log.warning(f"[handle_edit_media_group_request] Failed to send photo {photo_id}: {e}")
        markup.add(*buttons)
        markup = self.add_back_buttons(markup)
        self.bot.send_message(chat_id, "لطفاً عکس مورد نظر برای ویرایش را انتخاب کنید:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self._handle_media_select_id)
    def _handle_media_select_id(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        # text = message.text.stri
        medias = self.temp_data.get(chat_id, {}).get("media_groups", {})
        text = message.text
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return
        if self.is_back(message):
            return
        if text not in medias:
            self.bot.send_message(chat_id, "⚠️ لطفاً یکی از گزینه‌های معتبر را انتخاب کنید.")
            return self.bot.register_next_step_handler(message, self._handle_media_select_id)
        self.bot.send_message(chat_id, f"📤 لطفاً عکس جایگزین برای {text} را ارسال کنید:")
        self.bot.register_next_step_handler(message, self._handle_media_replace_ment, text)
    def _handle_media_replace_ment(self, message, label):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        text = message.text
        if text == BUTTONS["back_to_previous"]:
            self.backfromedittseerec(message)
            return
        if self.is_back(message):
            return
        if not message.photo:
            self.bot.send_message(chat_id, "⚠️ فقط عکس ارسال کنید.")
            return self.bot.register_next_step_handler(message, self._handle_media_replace_ment, label)
        file_id = self.save_media_to_channel(message, "photo")
        if file_id:
            self.temp_data[chat_id]["media_groups"][label] = file_id
            self.bot.send_message(chat_id, "✅ عکس با موفقیت جایگزین شد.")
            self._save_media_group_to_db(chat_id)
        else:
            self.bot.send_message(chat_id, "❌ خطا در ذخیره عکس جدید.")
            self.bot.register_next_step_handler(message, self._handle_media_replace_ment, label)
    def _save_media_group_to_db(self, chat_id):
        """Legacy-compatible behavior preserved for this callable."""
        data = self.temp_data.get(chat_id, {})
        table = data.get("table")
        req_id = data.get("request_id")
        field = data.get("editing_media_group_field")
        media_map = data.get("media_groups", {})
        media_list = list(media_map.values())
        if not (table and req_id and field and media_list):
            self.bot.send_message(chat_id, "❌ اطلاعات ذخیره ناقص است.")
            return
        self.db.update(table, {field: json.dumps(media_list, ensure_ascii=False)}, "id = ?", (req_id,))
        self.bot.send_message(chat_id, MESSAGES["changes_saved"])
        log.info(f"[_save_media_group_to_db] Updated field '{field}' with {len(media_list)} photos for chat_id={chat_id}")
        if chat_id in self.ifuserwantedit:
            original_message = self.ifuserwantedit[chat_id][1]
            self.current_request[chat_id] = self.ifuserwantedit[chat_id][2]
            table, request_id = self.current_request[chat_id]
            self.send_full_details(chat_id, table, request_id)
            self.handle_request_action(original_message)
