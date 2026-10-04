from __future__ import annotations

from .booking_requests_context import *


class BookingHandlerIntegrationsMixin:
    def _start_identity_verification_steps(self, message, missing_fields: list):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        manager = AuthenticationManager()
        # Internal implementation note: legacy behavior is preserved during modernization.
        manager.skip_step = True
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        for field in missing_fields:
            prompt = IDENTITY_VERIFICATION_PROMPTS[field]
            if field == "name":
                manager.add_step(TextAuthStep(field, prompt))
            elif field == "phone":
                manager.add_step(ContactAuthStep(field, prompt))
            elif field == "photo_id":
                manager.add_step(PhotoAuthStep(field, prompt))
            elif field == "video_message":
                manager.add_step(VideoAuthStep(field, prompt))
        # Internal implementation note: legacy behavior is preserved during modernization.
        manager.on_complete(self._on_identity_verification_complete)
        self.identity_verification_manager = manager
        self.identity_verification_user = chat_id
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.run_next_identity_verification_step(message)
    def run_next_identity_verification_step(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        for step in self.identity_verification_manager.steps:
            if step.enabled and step.response is None:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                if step.step_type == "contact":
                    contact_button = KeyboardButton(
                        text="📱 ارسال شماره من", request_contact=True)
                    markup.add(contact_button)
                markup = self.add_back_buttons(markup)
                self.bot.send_message(
                    chat_id, step.prompt, reply_markup=markup)
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.bot.register_next_step_handler(
                    message, lambda msg, current_step=step: self.handle_identity_verification_response(msg, current_step))
                return
        # Internal implementation note: legacy behavior is preserved during modernization.
        results = {
            s.name: s.response for s in self.identity_verification_manager.steps if s.enabled}
        self.current_request[chat_id].update(results)
        self.finalize_booking(message)
    def handle_identity_verification_response(self, message, step):
        """Legacy-compatible behavior preserved for this callable."""
        if self.is_back(message):
            return
        chat_id = message.chat.id
        if step.step_type == "contact" and message.contact and message.contact.phone_number:
            step.response = message.contact.phone_number
        elif step.name == "name":
            if message.text:
                text = message.text.strip()
                if len(text) > 72:
                    self.bot.send_message(
                        chat_id, "❌ نام وارد شده بیش از ۷۲ کاراکتر است.")
                    return self.run_next_identity_verification_step(message)
                # Internal implementation note: legacy behavior is preserved during modernization.
                valid_name_regex = r'^([a-zA-Z\u0600-\u06FF]{2,})(\s[a-zA-Z\u0600-\u06FF]{2,}){0,3}$'
                if not re.match(valid_name_regex, text):
                    self.bot.send_message(
                        chat_id,
                        "❌ نام باید فقط شامل حروف فارسی یا انگلیسی باشد، بدون عدد یا علامت، و حداکثر ۴ بخش."
                    )
                    return self.run_next_identity_verification_step(message)
                step.response = text
            else:
                self.bot.send_message(
                    chat_id, "❌ لطفاً اطلاعات معتبر وارد کنید.")
                return self.run_next_identity_verification_step(message)
        elif step.step_type == "photo" and message.photo:
            step.response = self.save_media_to_channel(message, "photo")
        elif step.step_type == "video" and hasattr(message, 'video_note') and message.video_note:
            step.response = self.save_media_to_channel(message, "video_note")
        else:
            self.bot.send_message(chat_id, "❌ لطفاً اطلاعات معتبر وارد کنید.")
            return self.run_next_identity_verification_step(message)
        self.run_next_identity_verification_step(message)
    def _on_identity_verification_complete(self, results: dict):
        """Legacy-compatible behavior preserved for this callable."""
        telegram_id = self.identity_verification_user
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.identity_verification_service.save_identity_verification_data(telegram_id, results)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update(
            "premium_clients",
            {"identity_verification_status": "completed"},
            "telegram_id = ?",
            (telegram_id,)
        )
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request[telegram_id]['identity_verification_snapshot'] = results.copy()
        # Internal implementation note: legacy behavior is preserved during modernization.
        fake_message = types.Message()  # Internal implementation note: legacy behavior is preserved during modernization.
        fake_message.chat = types.SimpleNamespace(id=telegram_id)
        self.finalize_booking(fake_message)
    def save_media_to_channel(self, message, media_type="photo") -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            forwarded = self.bot.forward_message(
                STORAGE_CHANNEL,  # Internal implementation note: legacy behavior is preserved during modernization.
                message.chat.id,
                message.message_id
            )
            # Internal implementation note: legacy behavior is preserved during modernization.
            if media_type == "photo" and forwarded.photo:
                return forwarded.photo[-1].file_id
            elif media_type == "video_note" and hasattr(forwarded, 'video_note'):
                return forwarded.video_note.file_id
            elif media_type == "document" and forwarded.document:
                return forwarded.document.file_id
            elif media_type == "video" and forwarded.video:
                return forwarded.video.file_id
            else:
                raise Exception("❌ مدیا معتبر یافت نشد.")
        except Exception as e:
            print(f"❌ خطا در ذخیره مدیا: {e}")
            return ""
    def finalize_booking(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id
        username = user.username or ""
        if self.is_back(message):
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        ad_row = self.temp_data[chat_id].get("ad_row", {})
        staff = self.temp_data[chat_id].get("staff", {})
        slot_row = self.temp_data[chat_id].get("slot", [{}])[0]
        slot_time = self.temp_data[chat_id].get("slot_time", "")
        extra_times = self.current_request[chat_id].get("extra_times", [])
        selected_svcs = self.current_request[chat_id].get(
            "selected_services", {})
        payment_meth = self.current_request[chat_id].get("payment_method", "")
        phone = self.current_request[chat_id].get("phone", "")
        photo_id = self.current_request[chat_id].get("photo_id", "")
        video_note = self.current_request[chat_id].get("video_message", "")
        selected_region = self.current_request[chat_id].get(
            "selected_region", "درمحل")
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            time_slots = json.loads(slot_row.get("time_slots", "{}"))
            times = sorted(time_slots.keys())
            last_slot = extra_times[-1] if extra_times else slot_time
            idx = times.index(last_slot)
            end_time = times[idx + 1] if idx + 1 < len(times) else last_slot
        except Exception:
            end_time = slot_time
        # Internal implementation note: legacy behavior is preserved during modernization.
        base_price = int(staff.get("service_price", 0) or 0)
        svc_defs = {}
        svc_defs.update(json.loads(ad_row.get("services", "{}")))
        svc_defs.update(json.loads(ad_row.get("premium_services", "{}")))
        services_price = sum(
            int(svc_defs.get(k, {}).get("price", 0) or 0)
            for k, v in selected_svcs.items() if v
        )
        extra_cost = len(extra_times) * base_price
        total_price = base_price + services_price + extra_cost
        # Internal implementation note: legacy behavior is preserved during modernization.
        invoice = {
            "base_price":      base_price,
            "services_price":  services_price,
            "extra_time_cost": extra_cost,
            "total_price":     total_price
        }
        print(invoice)
        # Internal implementation note: legacy behavior is preserved during modernization.
        user_exists = self.db.select_dict(
            "clients", "telegram_id = ?", (user_id,)
        )
        if not user_exists:
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_idx = self.db.count_rows(
                "clients") if self.db.table_exists("clients") else 0
            U_code = f"c{next_idx + 1 + 3420}"
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.insert("clients", {
                "telegram_id": user_id,
                "U_code":      U_code,
                "name":        self.current_request[chat_id].get("name", "")
            })
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            U_code = user_exists[0].get("U_code")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # current_name = user_exists[0].get("name", "")
            new_name = self.current_request[chat_id].get("name", "")
            # if not current_name and new_name:
            #     self.db.update("clients", {"name": new_name},
            #                    "telegram_id = ?", (user_id,))
            self.db.update("clients", {"name": new_name},
                           "telegram_id = ?", (user_id,))
        # Internal implementation note: legacy behavior is preserved during modernization.
        status_code, _ = self.identity_verification_service.get_status(chat_id)
        AutoApproval = status_code == "identity_verification_complete"
        # status_code, _ = self.identity_verification_service.get_status(chat_id)
        # status = "approved" if status_code == "identity_verification_complete" and AutoApproval else "pending"
        created_at = datetime.now()
        # Internal implementation note: legacy behavior is preserved during modernization.
        def format_time(val):
            if isinstance(val, datetime):
                return val.strftime("%H:%M")
            elif isinstance(val, timedelta):
                return (datetime.min + val).strftime("%H:%M")
            elif isinstance(val, str) and ":" in val:
                return val[:5]
            return str(val)
        final_data = {
            "created_at":         created_at,
            "U_code":             U_code,
            "PU_code":            staff.get("U_code", ""),
            "ad_id":              ad_row.get("id"),
            # Internal implementation note: legacy behavior is preserved during modernization.
            "slot_time":          format_time(slot_time),
            "start_time":         format_time(slot_time),
            "end_time":           format_time(end_time),
            # Internal implementation note: legacy behavior is preserved during modernization.
            "extra_times":        json.dumps([
                format_time(t) for t in extra_times
            ]),
            "selected_services":  json.dumps(selected_svcs),
            "invoice":            json.dumps(invoice),
            # Internal implementation note: legacy behavior is preserved during modernization.
            "payment_method":     payment_meth,
            "phone":              phone,
            "photo_id":           photo_id,
            "video_note":         video_note,
            "selected_region":    selected_region,
            "status":             "pending"
        }
        log.debug(final_data)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.insert("service_requests", final_data)
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        summary = (
            "✅ رزرو شما با موفقیت ثبت شد!\n"
            f"🧾 مبلغ کل: {total_price:,} تومان\n"
            "در اسرع وقت با شما تماس خواهیم گرفت."
        )
        self.bot.send_message(chat_id, summary)
        if AutoApproval:
            try:
                condition = (
                    "U_code = %s AND "
                    "PU_code = %s AND "
                    "ad_id = %s AND "
                    "slot_time = %s AND "
                    "start_time = %s AND "
                    "end_time = %s AND "
                    "status = %s"
                )
                params = (
                    final_data["U_code"],
                    final_data["PU_code"],
                    final_data["ad_id"],
                    final_data["slot_time"],
                    final_data["start_time"],
                    final_data["end_time"],
                    final_data["status"],
                )
                log.debug(f"[AutoType5] SELECT condition:\n{condition}")
                log.debug("[AutoType5] Parameters:")
                for key, value in zip(
                    ["U_code", "PU_code", "ad_id", "slot_time", "start_time", "end_time", "status"],
                    params
                ):
                    log.debug(f"    {key} = {value}")
                result = self.db.select_dict("service_requests", condition, params)
                log.debug(f"[AutoType5] Query result: {result}")
                if not result:
                    raise ValueError("Record not found for auto-approval")
                last_id = result[0]["id"]
                log.info(f"[AutoType5] Auto-approval record found → ID = {last_id}")
                try:
                    log.info(f"[AutoType5] Trying auto_accept_premium_client for request ID: {last_id}")
                    self.auto_accept_premium_client(message, last_id)
                    log.info(f"[AutoType5] auto_accept_premium_client executed successfully for request ID: {last_id}")
                except Exception as ex:
                    log.warning(f"[AutoType5] auto_accept_premium_client FAILED for request ID: {last_id} | Error: {ex}")
                self.bot.send_message(
                    chat_id,
                    "🌟 به دلیل ویژه بودن حساب شما و تکمیل احراز هویت، درخواستتان به‌صورت خودکار تأیید و برای پرسنل ارسال شد. لطفاً منتظر پاسخ از سمت پرسنل باشید."
                )
            except Exception as ex:
                log.warning(f"[AutoType5] Error in automatic approval: {ex}")
            # Internal implementation note: legacy behavior is preserved during modernization.
        self.back_main(message)
    def auto_accept_premium_client(self, message, request_id):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        log.info(f"[TYPE5] Start auto_accept_premium_client | request_id={request_id}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            table = "service_requests"
            status_column = self.settings.get(table, {}).get("status_column", "status")
            rows = self.db.select_dict(table, "id = ?", (request_id,))
            if not rows:
                log.warning(f"[TYPE5] Request id={request_id} not found.")
                return
            req = rows[0]
            U_code = req.get("U_code")
            PU_code = req.get("PU_code")
            ad_id = req.get("ad_id")
            def normalize_time(val):
                if isinstance(val, timedelta):
                    return (datetime.min + val).strftime("%H:%M")
                if isinstance(val, datetime):
                    return val.strftime("%H:%M")
                if isinstance(val, str):
                    return val[:5] if ":" in val else val
                return str(val)
            slot_time = normalize_time(req.get("slot_time"))
            extra_times = [normalize_time(t) for t in json.loads(req.get("extra_times") or "[]")]
            log.debug(f"[TYPE5] Loaded request data | U_code={U_code}, PU_code={PU_code}, ad_id={ad_id}, slot={slot_time}, extra={extra_times}")
            ad_row = self.db.select_dict("ads", "id = ?", (ad_id,))
            ad_row = ad_row[0] if ad_row else {}
        except Exception as e:
            log.error(f"[TYPE5] Failed to fetch request/ad data: {e}")
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            def normalize_time(val):
                if isinstance(val, timedelta):
                    return (datetime.min + val).strftime("%H:%M")
                elif isinstance(val, datetime):
                    return val.strftime("%H:%M")
                elif isinstance(val, str) and ":" in val:
                    return val[:5]  # Internal implementation note: legacy behavior is preserved during modernization.
                return str(val)
            # Internal implementation note: legacy behavior is preserved during modernization.
            slot_time = normalize_time(req.get("slot_time"))
            extra_times_raw = req.get("extra_times") or "[]"
            extra_times = [normalize_time(t) for t in json.loads(extra_times_raw)]
            all_times = list(set([slot_time] + extra_times))  # Internal implementation note: legacy behavior is preserved during modernization.
            placeholders = ",".join("?" for _ in all_times)
            query = f"U_code != ? AND ad_id = ? AND slot_time IN ({placeholders})"
            params = (U_code, ad_id, *all_times)
            log.debug(f"[TYPE5] Looking for conflicts with times: {all_times}")
            conflicts = self.db.select_dict(table, query, params)
            user_map = {r["U_code"]: r.get("telegram_id") for r in conflicts if r.get("telegram_id")}
            ucodes = list(user_map.keys())
            if ucodes:
                ph = ",".join("?" for _ in ucodes)
                self.db.update(table, {status_column: "expired"}, f"U_code IN ({ph})", ucodes)
                for tg_id in user_map.values():
                    self.bot.send_message(tg_id, "❌ درخواست شما برای این تایم لغو شد؛ ظرفیت پر شده است.")
            log.info(f"[TYPE5] Expired duplicate requests: {ucodes}")
        except Exception as e:
            log.warning(f"[TYPE5] Failed to expire duplicates: {e}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            admins = self.db.select_dict("admins")
            notified = []
            for admin in admins:
                perms = json.loads(admin.get("permissions") or "{}")
                if perms.get("manage_requests") and admin.get("telegram_id"):
                    notified.append(admin["telegram_id"])
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    start_time = datetime.strptime(slot_time, "%H:%M")
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    end_time = start_time + timedelta(minutes=BETWIN_TIME)
                    end_time_str = end_time.strftime("%H:%M")  # Internal implementation note: legacy behavior is preserved during modernization.
                    self.admin_bot.send_message(
                        admin["telegram_id"],
                        f"<b>درخواست یک مشتری ویژه به صورت خودکار تایید شد ✅</b>\n\n"
                        f"<b>جزئیات:</b> 📝\n"
                        f"<b>کد ارائه‌دهنده:</b> /{PU_code} 🧑‍💼\n"
                        f"<b>کد مشتری:</b> {U_code} 👤\n"
                        f"<b>زمان شروع:</b> {slot_time} ⏰\n"
                        f"<b>زمان پایان:</b> {end_time_str} 🕒\n\n",
                        parse_mode="HTML"
                    )
            log.info(f"[TYPE5] Sent admin notifications: {notified}")
        except Exception as e:
            log.error(f"[TYPE5] Failed to notify admins: {e}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.bot.send_message(chat_id, MESSAGES["request_approved_clients"])
            staff = self.db.select_dict("staff", "U_code = ?", (PU_code,))
            if staff:
                self.staff_bot.send_message(
                    staff[0]["telegram_id"],
                    MESSAGES["request_approved_staff"]
                )
            log.info(f"[TYPE5] Sent confirmation messages to client and staff")
        except Exception as e:
            log.error(f"[TYPE5] Failed to notify client/staff: {e}")
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            live = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
            if not live:
                log.warning(f"[TYPE5] live_ads entry not found for ad_id={ad_id}.")
                return
            live = live[0]
            msg_id = live.get("channel_message_id")
            slots = json.loads(live.get("time_slots") or "{}")
            log.debug(f"Slots of live ads takeed ==== {slots}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            normalized_slots = {normalize_time(k): v for k, v in slots.items()}
            slot_time = normalize_time(slot_time)
            extra_times = [normalize_time(t) for t in extra_times]
            if slot_time in normalized_slots:
                normalized_slots[slot_time] = False
            for t in extra_times:
                if t in normalized_slots:
                    normalized_slots[t] = False
            slots = normalized_slots
            log.debug(f"Slots of live ads takeed after change ==== {slots}")
            log.debug(f"Slots of live ads takeed after change ==== {slots}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            keyboard = InlineKeyboardMarkup()
            link_base = f"https://t.me/{html.escape(CLIENT_BOT_USERNAME)}?start"
            buttons = []
            for s, available in slots.items():
                log.debug(f"slot = {s} | status {available}")
                if available:
                    log.debug(f"status  = {available} And this slot avalabel")
                    fmt = datetime.strptime(s, "%H:%M").strftime("%H_%M")
                    buttons.append(InlineKeyboardButton(s, url=f"{link_base}=reserve_ads_{ad_id}_{fmt}"))
                else:
                    log.debug(f"status  = {available} And this slot not avalabel")
                    buttons.append(InlineKeyboardButton("رزرو شده 🕰", url=f"{link_base}=ShowAvalabelCodes"))
            rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
            if len(rows) >= 2 and len(rows[-1]) == 1:
                flat = sum(rows, [])
                rows = [flat[i:i+3] for i in range(0, len(flat), 3)]
            rows.append([
                InlineKeyboardButton(BUTTONS["Goto_Client_bot"], url=f"https://t.me/{CLIENT_BOT_USERNAME}?start"),
                InlineKeyboardButton(BUTTONS["Add_toFavoris"], callback_data=f"AddToFavorites_{ad_row['U_code']}")
            ])
            for r in rows:
                log.debug(f"[TYPE5] Adding row: {[b.text for b in r]}")
                keyboard.row(*r)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.edit_message_reply_markup(chat_id=CHANNEL_ID, message_id=msg_id, reply_markup=keyboard)
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update("live_ads", {"time_slots": json.dumps(slots, ensure_ascii=False)}, "id = ?", (live["id"],))
            self.db.update(table, {status_column: "approved"}, "id = ?", (request_id,))
            log.info(f"[TYPE5] Request {request_id} approved and live_ads updated.")
        except Exception as e:
            log.warning(f"[TYPE5] Failed to update channel or live_ads: {e}")
        log.info(f"[TYPE5] Finished auto_accept_premium_client for request_id={request_id}")
