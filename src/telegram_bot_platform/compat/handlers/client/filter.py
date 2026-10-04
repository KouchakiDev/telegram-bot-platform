# Internal implementation note: legacy behavior is preserved during modernization.


# Internal implementation note: legacy behavior is preserved during modernization.
# import telebot
import json
from telebot import TeleBot
from telebot.types import (

    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,

)
import pandas as pd  # Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# Client Handlers
# from telegram_bot_platform.compat.handlers.client.filter import FilterHandler

from telegram_bot_platform.compat.utils.temporary_state import save_filter_snapshot, load_filter_snapshot

# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from datetime import datetime

logger = CustomLogger()  # log_file="filter.log")

log = logger
class FilterHandler:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot: TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db
        self.user_state = {}  # chat_id -> state dict
        self.filters = {}
        logger.info('FilterHandler initialized')

    def _make_range_buttons(self, field) -> list:
        """Legacy-compatible behavior preserved for this callable."""

        def format_price_label(val: int, prefix: str = "") -> str:
            """Legacy-compatible behavior preserved for this callable."""
            if val >= 1_000_000:
                val_million = val / 1_000_000
                # Internal implementation note: legacy behavior is preserved during modernization.
                val_str = f"{val_million:.3f}".rstrip('0').rstrip('.')
                return f"{prefix} {val_str} میلیون "
            else:
                return f"{prefix} {val:,} "
        cfg = FILTER_CONFIG[field].get('range')
        # cfg = FILTER_CONFIG[field].get('range')
        if not cfg:
            logger.error(
                f"No numeric range config found for field {field}")
            return []

            # Internal implementation note: legacy behavior is preserved during modernization.
        min_v, max_v, step = cfg.get('min', 0), cfg.get(
            'max', 0), cfg.get('step', 1)
        # Internal implementation note: legacy behavior is preserved during modernization.
        if field == "service_price" and (min_v == 0 or max_v == 0):
            rows = self.db.select_dict(DB_TABLE_STAFF)
            prices = [int(r['service_price'])
                      for r in rows if r.get('service_price') is not None]
            if prices:
                if min_v == 0:
                    min_v = min(prices)
                if max_v == 0:
                    max_v = max(prices)

        buttons = []

        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons.append(
            (
                format_price_label(min_v, "زیر"),
                f"toggle_range_{field}_lt_{min_v}"
            )
        )

        # Internal implementation note: legacy behavior is preserved during modernization.
        val = min_v
        while val < max_v:
            hi = min(val + step, max_v)
            label = f"{format_price_label(val)} تا {format_price_label(hi)}"
            buttons.append(
                (label, f"toggle_range_{field}_{val}_{hi}")
            )
            val += step

        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons.append(
            (
                format_price_label(max_v, "بیشتر از"),
                f"toggle_range_{field}_gt_{max_v}"
            )
        )

        return buttons

    def _make_choice_buttons(self, field: str) -> list:
        """Legacy-compatible behavior preserved for this callable."""

        # Internal implementation note: legacy behavior is preserved during modernization.
        if field in ('visit_client_home', 'has_home'):
            return [
                ('بله', f"toggle_single_{field}_1"),
                ('خیر', f"toggle_single_{field}_0")
            ]

        # Internal implementation note: legacy behavior is preserved during modernization.
        if field == 'services':
            rows = self.db.select_dict(DB_TABLE_SERVICES)
            opts, seen = [], set()
            for r in rows:
                for svc_key, label in SERVICES.items():
                    price = r.get(f"{svc_key}_price")
                    if price and int(price) > 0 and svc_key not in seen:
                        seen.add(svc_key)
                        opts.append(
                            (label, f"toggle_checkbox_services_{svc_key}")
                        )
            return opts

        # Internal implementation note: legacy behavior is preserved during modernization.
        config = FILTER_CONFIG.get(field, {})
        if 'options' in config:
            opt_type = config.get("type", "single_choice")
            toggle_type = "toggle_single" if opt_type == "single_choice" else "toggle_checkbox"
            return [
                (opt, f"{toggle_type}_{field}_{opt}")
                for opt in config["options"]
            ]

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict(DB_TABLE_STAFF)
        values = set()
        for r in rows:
            v = r.get(field)
            if v is not None:
                values.add(v)

        return [
            (v, f"toggle_checkbox_{field}_{v}")
            for v in values
        ]

    # def _show_filter_fields(self, chat_id: int, message_id: int = None):
    # Internal implementation note: legacy behavior is preserved during modernization.
    #     keyboard = []
    #     for i in range(0, len(FILTER_CONFIG.keys()), 3):
    #         row = []
    #         for field in FILTER_CONFIG.keys()[i:i+3]:
    #             label = FILTER_FIELD_LABELS[field]
    #             row.append(InlineKeyboardButton(
    #                 label, callback_data=f'field_{field}'))
    #         keyboard.append(row)
    #     keyboard.append([InlineKeyboardButton(
    #         MESSAGES['apply_filters'], callback_data='apply_filters')])
    #     markup = InlineKeyboardMarkup(keyboard)
    #     if message_id:
    #         try:
    #             self.bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_id,
    #                 text=MESSAGES['filter_prompt'],
    #                 reply_markup=markup
    #             )
    #         except Exception as e:
    #             if 'message is not modified' not in str(e):
    #                 raise
    #     else:
    #         self.bot.send_message(
    #             chat_id, MESSAGES['filter_prompt'], reply_markup=markup)
    #     logger.info(f"Displayed filter fields to chat {chat_id}")

    def _show_filter_options(self, chat_id: int, field: str, message_id: int):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            filters = self.user_state.setdefault(
                chat_id, {}).setdefault('filters_selected', {})
            selected_vals = filters.get(field, set())

            cfg = FILTER_CONFIG[field]
            filter_type = cfg['type']

            # Internal implementation note: legacy behavior is preserved during modernization.
            if filter_type == 'range':
                opts = self._make_range_buttons(field)
            else:
                opts = self._make_choice_buttons(field)

            keyboard = []
            row = []
            row_limit = 3  # Internal implementation note: legacy behavior is preserved during modernization.

            for text, cb in opts:
                # Internal implementation note: legacy behavior is preserved during modernization.
                length = len(text)
                if length <= 3:
                    row_limit = 5
                elif length <= 6:
                    row_limit = 4
                elif length <= 10:
                    row_limit = 3
                elif length <= 15:
                    row_limit = 2
                else:
                    row_limit = 1

                # Internal implementation note: legacy behavior is preserved during modernization.
                cb_val = cb.replace(f"toggle_{filter_type}_{field}_", "")

                is_selected = False
                if filter_type in ('range', 'checkbox'):
                    is_selected = cb_val in selected_vals
                elif filter_type == 'single_choice':
                    is_selected = selected_vals == {cb_val}

                icon = "✅" if is_selected else "☑️"
                button = InlineKeyboardButton(
                    f"{icon} {text}", callback_data=cb)
                row.append(button)

                # Internal implementation note: legacy behavior is preserved during modernization.
                if len(row) >= row_limit:
                    keyboard.append(row)
                    row = []

            # Internal implementation note: legacy behavior is preserved during modernization.
            if row:
                keyboard.append(row)

            # Internal implementation note: legacy behavior is preserved during modernization.
            snapshot_id = save_filter_snapshot(
                self.db, chat_id, self.user_state[chat_id])
            keyboard.append([
                InlineKeyboardButton(
                    '🔙 بازگشت', callback_data=f"filter_search|{snapshot_id}")
            ])

            markup = InlineKeyboardMarkup(keyboard)

            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{MESSAGES['choose_filter_value']}\n\n{cfg['label']}:",
                reply_markup=markup
            )
            logger.info(
                f"Displayed options for filter {field} to chat {chat_id}")

        except Exception:
            logger.exception(f"Error showing filter options for field {field}")

    def _toggle_checkbox_filter(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            data = call.data.replace('toggle_checkbox_', '')
            field = next(
                (f for f in FILTER_CONFIG if data.startswith(f + '_')), None)
            if not field:
                logger.warning(
                    f"⚠️ Field not found in FILTER_CONFIG for data: {data}")
                return

            value = data[len(field)+1:]  # Internal implementation note: legacy behavior is preserved during modernization.

            filters = self.user_state.setdefault(
                chat_id, {}).setdefault('filters_selected', {})
            selected_values = filters.setdefault(field, set())

            if value in selected_values:
                selected_values.remove(value)
                self.bot.answer_callback_query(call.id, text="❌ گزینه حذف شد.")
            else:
                selected_values.add(value)
                self.bot.answer_callback_query(
                    call.id, text="✅ گزینه انتخاب شد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            summary = self._get_filter_summary(chat_id)

            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_filter_options(chat_id, field, message_id)

            logger.info(
                f"Toggled checkbox filter {field}={value} for chat {chat_id}")

        except Exception:
            logger.exception("Error in _toggle_checkbox_filter")

    def _toggle_single_filter(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            data = call.data.replace('toggle_single_', '')
            field = [f for f in FILTER_CONFIG.keys() if f in data][0]
            value = data.replace(f"{field}_", "")

            filters = self.user_state.setdefault(
                chat_id, {}).setdefault('filters_selected', {})

            # Internal implementation note: legacy behavior is preserved during modernization.
            current = filters.get(field)
            if current == {value}:
                filters.pop(field, None)
                self.bot.answer_callback_query(
                    call.id, text="❌ انتخاب برداشته شد.")
            else:
                filters[field] = {value}
                self.bot.answer_callback_query(
                    call.id, text="✅ انتخاب اعمال شد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            summary = self._get_filter_summary(chat_id)

            # Internal implementation note: legacy behavior is preserved during modernization.
            keyboard = []
            for i in range(0, len(FILTER_CONFIG.keys()), 3):
                row = []
                for fld in list(FILTER_CONFIG.keys())[i:i+3]:

                    label = FILTER_CONFIG[fld]['label']

                    row.append(InlineKeyboardButton(
                        label, callback_data=f'field_{fld}'))
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton(
                MESSAGES['apply_filters'], callback_data='apply_filters')])

            markup = InlineKeyboardMarkup(keyboard)

            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{MESSAGES['filter_prompt']}\n\n🎯 فیلترهای انتخاب شده:\n{summary}",
                reply_markup=markup
            )

            logger.info(
                f"Toggled single filter {field}={value} for chat {chat_id}")

        except Exception:
            logger.exception("Error in _toggle_single_filter")

    def _toggle_range_filter(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            data = call.data.replace('toggle_range_', '')
            field = [f for f in FILTER_CONFIG.keys() if f in data][0]
            value = data.replace(f"{field}_", "")  # Internal implementation note: legacy behavior is preserved during modernization.

            print(call.data)
            filters = self.user_state.setdefault(
                chat_id, {}).setdefault('filters_selected', {})
            selected_values = filters.setdefault(field, set())
            # Internal implementation note: legacy behavior is preserved during modernization.
            current = filters.get(field)
            if current == {value}:
                filters.pop(field, None)
                self.bot.answer_callback_query(call.id, text="❌ بازه حذف شد.")
            else:
                filters[field] = {value}
                self.bot.answer_callback_query(
                    call.id, text="✅ بازه انتخاب شد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            summary = self._get_filter_summary(chat_id)

            # Internal implementation note: legacy behavior is preserved during modernization.
            keyboard = []
            for i in range(0, len(FILTER_CONFIG.keys()), 3):
                row = []
                for fld in list(FILTER_CONFIG.keys())[i:i+3]:

                    label = FILTER_CONFIG[fld]['label']

                    if fld in selected_values:
                        label += ' 🔘'
                    row.append(InlineKeyboardButton(
                        label, callback_data=f'field_{fld}'))
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton(
                MESSAGES['apply_filters'], callback_data='apply_filters')])

            markup = InlineKeyboardMarkup(keyboard)

            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{MESSAGES['filter_prompt']}\n\n🎯 فیلترهای انتخاب شده:\n{summary}",
                reply_markup=markup
            )

            logger.info(
                f"Toggled range filter {field}={value} for chat {chat_id}")

        except Exception:
            logger.exception("Error in _toggle_range_filter")

    def _get_filter_summary(self, chat_id: int) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        sel = self.user_state.get(chat_id, {}).get('filters_selected', {})
        parts = []
        for field, vals in sel.items():
            if not vals:
                continue
            cfg = FILTER_CONFIG.get(field)
            if not cfg:
                continue
            label = cfg['label']

            # Internal implementation note: legacy behavior is preserved during modernization.
            emoji = FILTER_CONFIG[field]['emoji']
            filter_type = FILTER_CONFIG[field]['type']
            nice_vals = []

            for v in vals:
                if filter_type == 'range':
                    if v.startswith('lt_'):
                        nice_vals.append(f"کمتر از {v.split('_')[1]}")
                    elif v.startswith('gt_'):
                        nice_vals.append(f"بیشتر از {v.split('_')[1]}")
                    else:
                        lo, hi = v.split('_')
                        nice_vals.append(f"بین {lo} تا {hi}")
                elif field == 'services':
                    nice_vals.append(SERVICES.get(v, v))
                elif field in ('visit_client_home', 'has_home'):
                    nice_vals.append("بله" if v == "1" else "خیر")
                else:
                    nice_vals.append(str(v).replace("_", " "))

            parts.append(f"{label}: {'، '.join(nice_vals)}")
        return "\n".join(parts) if parts else "بدون فیلتر فعال"

    def _apply_filters(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = call.message.chat.id
        msg_id = call.message.message_id
        sel = self.user_state.get(chat_id, {}).get('filters_selected', {})
        where, params = [], []
        for f, vals in sel.items():
            if not vals:
                continue
            if f in ('visit_client_home', 'has_home'):
                where.append(f + ' = ?')
                params.append(int(next(iter(vals))))
            elif FILTER_CONFIG.get(f, {}).get('type') == 'range':

                subs = []
                for v in vals:
                    if v.startswith('lt_'):
                        lim = int(v.split('_')[1])
                        subs.append(f + ' < ?')
                        params.append(lim)
                    elif v.startswith('gt_'):
                        lim = int(v.split('_')[1])
                        subs.append(f + ' > ?')
                        params.append(lim)
                    else:
                        lo, hi = map(int, v.split('_'))
                        subs.append(f + ' BETWEEN ? AND ?')
                        params.extend([lo, hi])
                where.append('(' + ' OR '.join(subs) + ')')
            elif f == "dispatch_mode":
                try:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    db_vals = [DISPATCH_MODE_DB_MAP.get(v, v) for v in vals]
            
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    ph = ",".join("?" for _ in db_vals)
                    ads = self.db.select_dict(
                        ADS_TABLE,
                        f"dispatch_mode IN ({ph})",
                        tuple(db_vals)
                    )
            
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    valid_ucodes = {ad["U_code"] for ad in ads if ad.get("U_code")}
            
                    if not valid_ucodes:
                        self.bot.answer_callback_query(
                            call.id,
                            "❌ هیچ نتیجه‌ای با این نوع مراجعه پیدا نشد."
                        )
                        return
            
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    ph = ",".join("?" for _ in valid_ucodes)
                    where.append(f"U_code IN ({ph})")
                    params.extend(valid_ucodes)
            
                except Exception as exc:
                    logger.exception(f"[Filter] dispatch_mode mapping failed: {exc}")


            elif f == 'services':
                # Internal implementation note: legacy behavior is preserved during modernization.
                conditions = ' OR '.join(
                    [f"{svc_key}_price > 0" for svc_key in vals])

                # Internal implementation note: legacy behavior is preserved during modernization.
                rows = self.db.select_dict(
                    DB_TABLE_SERVICES, condition=conditions)

                # Internal implementation note: legacy behavior is preserved during modernization.
                valid_ucodes = {r['U_code'] for r in rows if r.get('U_code')}

                if not valid_ucodes:
                    self.bot.answer_callback_query(
                        call.id, '❌ هیچ نتیجه‌ای با این سرویس‌ها پیدا نشد.'
                    )
                    return

                # Internal implementation note: legacy behavior is preserved during modernization.
                placeholders = ','.join('?' for _ in valid_ucodes)
                where.append(f"U_code IN ({placeholders})")
                params.extend(valid_ucodes)

            else:
                ph = ','.join('?' for _ in vals)
                where.append(f + f' IN ({ph})')
                params.extend(vals)
        sql_where = ' AND '.join(where)
        where_clause = sql_where if where else ""
        rows = self.db.select_dict(
            DB_TABLE_STAFF, where_clause, tuple(params))
        codes = [r['U_code'] for r in rows]
        self.user_state[chat_id]["all_codes"] = codes.copy()
        self.user_state[chat_id]["today_filter"] = False
        
        existing_codes = self.user_state.get(chat_id, {}).get('codes', [])
        if existing_codes and where:          # Internal implementation note: legacy behavior is preserved during modernization.
           codes = [code for code in codes if code in existing_codes]


        if not codes:
            self.bot.answer_callback_query(call.id, '❌ هیچ نتیجه‌ای پیدا نشد.')
            return
        self.user_state[chat_id]['codes'] = codes
        self.user_state[chat_id]['page'] = 1
        self._show_filtered_codes(chat_id, msg_id, call.id)
        
    def _send_filtered_codes(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id  = call.message.chat.id
        msg_id   = call.message.message_id        # Internal implementation note: legacy behavior is preserved during modernization.
        call_id  = call.id                        # Internal implementation note: legacy behavior is preserved during modernization.

        # -------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -------------------------------------------------
        try:
            try:
                state_id = int(call.data.split('|', 1)[1])
            except (IndexError, ValueError):
                log.exception("[FilteredCodes] Invalid snapshot_id in callback data")
                self.bot.answer_callback_query(call.id, "❌ خطا در بارگذاری فیلتر.")
                return

            loaded_state = load_filter_snapshot(self.db, state_id)
            self.user_state.setdefault(chat_id, {}).update(loaded_state)
        except Exception:
            self.bot.answer_callback_query(call_id, "❌ بارگذاری فیلتر انجام نشد.")
            log.exception("[FilteredCodes] failed to load snapshot")
            return

        # -------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -------------------------------------------------
        PAGE_SIZE = 20
        codes = self.user_state[chat_id].get("codes", [])
        page  = self.user_state[chat_id].get("page", 1)

        total_pages = (len(codes) + PAGE_SIZE - 1) // PAGE_SIZE or 1
        page = max(1, min(page, total_pages))
        self.user_state[chat_id]["page"] = page   # Internal implementation note: legacy behavior is preserved during modernization.

        start, end = (page - 1) * PAGE_SIZE, (page) * PAGE_SIZE
        subset = codes[start:end]

        # -------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -------------------------------------------------
        markup = InlineKeyboardMarkup(row_width=3)

        # Internal implementation note: legacy behavior is preserved during modernization.
        row = []
        for idx, code in enumerate(subset, 1):
            row.append(InlineKeyboardButton(f"🧍‍♀️ کد {code}",
                                            callback_data=f"premium_fav_profile_{code}"))
            if idx % 3 == 0:
                markup.row(*row)
                row = []
        if row:
            markup.row(*row)

        # Internal implementation note: legacy behavior is preserved during modernization.
        snapshot_id = save_filter_snapshot(self.db, chat_id, self.user_state[chat_id])
        btn_filter = InlineKeyboardButton("🛠 فیلتر جستجو",
                                          callback_data=f"filter_search|{snapshot_id}")

        today_on = self.user_state[chat_id].get("today_filter", False)
        btn_today = InlineKeyboardButton(
            "👁 مشاهدهٔ همه" if today_on else "✅ فعال‌های امروز",
            callback_data=f"Actives|{snapshot_id}"
        )
        markup.add(btn_filter, btn_today)

        # Internal implementation note: legacy behavior is preserved during modernization.
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton("⬅️ صفحه قبلی",
                                            callback_data=f"codes_page_{page-1}"))
        if page < total_pages:
            nav.append(InlineKeyboardButton("➡️ صفحه بعدی",
                                            callback_data=f"codes_page_{page+1}"))
        if nav:
            markup.row(*nav)

        # -------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -------------------------------------------------
        summary  = self._get_filter_summary(chat_id)
        text     = MESSAGES['filtered_list_info'].format(current=page,
                                                         total=total_pages)
        text    += "\n\n" + summary

        # -------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # -------------------------------------------------
        try:
            self.bot.copy_message(chat_id=chat_id,
                                  from_chat_id=chat_id,
                                  message_id=msg_id,
                                  caption=text,
                                  reply_markup=markup,
                                  parse_mode="HTML")
        except Exception:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.send_message(chat_id, text, reply_markup=markup)
            log.warning(f"[FilteredCodes] sent new message for chat {chat_id}")

        self.bot.answer_callback_query(call_id)
        log.info(f"[FilteredCodes] page {page}/{total_pages} shown to {chat_id}")

            
    def _show_filtered_codes(self, chat_id: int, msg_id: int = None, call_id: int = None):
        """Legacy-compatible behavior preserved for this callable."""
        codes = self.user_state.get(chat_id, {}).get('codes', [])
        page = self.user_state[chat_id].get('page', 1)
        total = (len(codes) + PAGE_SIZE - 1) // PAGE_SIZE
        start = (page-1)*PAGE_SIZE
        end = start + PAGE_SIZE
        subset = codes[start:end]

        markup = InlineKeyboardMarkup(row_width=4)
        row = []
        for idx, code in enumerate(subset, 1):
            row.append(InlineKeyboardButton(
                text=f"🧍‍♀️ کد {code}",
                callback_data=f"premium_fav_profile_{code}"
            ))
            if idx % 4 == 0:
                markup.row(*row)
                row = []
        if row:
            markup.row(*row)
        snapshot_id = save_filter_snapshot(
            self.db, chat_id, self.user_state[chat_id])
        buttons = [InlineKeyboardButton(
                "🛠 فیلتر جستجو", callback_data=f"filter_search|{snapshot_id}"),]
        
                # Internal implementation note: legacy behavior is preserved during modernization.
        if self.user_state.get(chat_id, {}).get("today_filter"):
            btn_label = "👁 مشاهدهٔ همه"
        else:
            btn_label = "✅ فعال‌های امروز"
        buttons.append(
            InlineKeyboardButton(btn_label, callback_data=f"Actives|{snapshot_id}")
        )
        markup.add(*buttons)

        # Internal implementation note: legacy behavior is preserved during modernization.
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(
                "⬅️ صفحه قبلی", callback_data=f"codes_page_{page-1}"))
        if page < total:
            nav_buttons.append(InlineKeyboardButton(
                "➡️ صفحه بعدی", callback_data=f"codes_page_{page+1}"))
        if nav_buttons:
            markup.row(*nav_buttons)


        summary = self._get_filter_summary(chat_id)
        text = MESSAGES['filtered_list_info'].format(
            current=page, total=total) + "\n\n" + summary

        if msg_id:
            self.bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id, text=text, reply_markup=markup)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.answer_callback_query(call_id, "✅ فهرست به‌روز شد.")
            # Internal implementation note: legacy behavior is preserved during modernization.
            # self.bot.send_message(chat_id, text, reply_markup=markup)


    def _show_filter_fields(self, chat_id: int, message_id: int = None):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            filters = self.user_state.setdefault(
                chat_id, {}).setdefault('filters_selected', {})
            keyboard = []
            selected = []
            for i in range(0, len(FILTER_CONFIG.keys()), 3):
                row = []
                for field in list(FILTER_CONFIG.keys())[i:i+3]:

                    cfg = FILTER_CONFIG.get(field)
                    if not cfg:
                        continue
                    label = cfg['label']

                    if filters.get(field):
                        label += ' 🔘'
                    row.append(InlineKeyboardButton(
                        label, callback_data=f'field_{field}'
                    ))

                keyboard.append(row)

            keyboard.append([InlineKeyboardButton(
                MESSAGES['apply_filters'], callback_data='apply_filters')])
            markup = InlineKeyboardMarkup(keyboard)
            # selected = [fld for in ]
            summary = self._get_filter_summary(chat_id)
            if message_id:
                try:
                    self.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=MESSAGES['filter_prompt'] +
                        "\n\n🎯 فیلترهای انتخاب شده:\n" + summary,
                        reply_markup=markup
                    )
                except Exception as e:
                    if 'message is not modified' not in str(e):
                        raise
            else:
                self.bot.send_message(
                    chat_id, MESSAGES['filter_prompt'], reply_markup=markup)

            logger.info(f"Displayed filter fields to chat {chat_id}")

        except Exception:
            logger.exception("Error showing filter fields")
        # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    def _apply_today_filter(self, call: CallbackQuery):
        chat_id = call.message.chat.id
        msg_id  = call.message.message_id
        call_id = call.id

        self.user_state.setdefault(chat_id, {})
        # Internal implementation note: legacy behavior is preserved during modernization.
        U_codes = self.user_state.get(chat_id, {}).get("codes", [])
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not U_codes:
            self.bot.answer_callback_query(call_id, "❌ هنوز لیستی برای فیلتر کردن نداریم.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.

        
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id]["backup_codes"] = U_codes


        active_today = self._get_today_active_ucodes()
        filtered     = [c for c in U_codes if c in active_today]

        if not filtered:
            self.bot.answer_callback_query(
                call_id,
                "❌ هیچ کد فعالی برای امروز در فیلتر فعلی یافت نشد."
            )
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # if "backup_codes" not in self.user_state[chat_id]:
        #     self.user_state[chat_id]["backup_codes"] = current.copy()


        self.user_state[chat_id]["codes"]        = filtered
        self.user_state[chat_id]["today_filter"] = True
        self.user_state[chat_id]["page"]         = 1
        self._show_filtered_codes(chat_id, msg_id)
        self.bot.answer_callback_query(call_id)

    def _remove_today_filter(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = call.message.chat.id
        msg_id  = call.message.message_id
        call_id = call.id

        self.user_state.setdefault(chat_id, {})  # Internal implementation note: legacy behavior is preserved during modernization.

        prev = self.user_state[chat_id].get("backup_codes")
        if not prev:
            # Internal implementation note: legacy behavior is preserved during modernization.
            prev = self.user_state[chat_id].get("codes", [])

        self.user_state[chat_id]["codes"] = prev
        self.user_state[chat_id].pop("backup_codes", None)  # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id]["today_filter"] = False
        self.user_state[chat_id]["page"] = 1

        self._show_filtered_codes(chat_id, msg_id)
        self.bot.answer_callback_query(call_id)

    def _get_today_active_ucodes(self) -> set:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            today = datetime.now().date().isoformat()  # YYYY-MM-DD
            ads = self.db.select_dict(
                "ads",
                "status = 'approved' AND date(created_at) = ?",
                (today,)
            )

            return {ad['U_code'] for ad in ads if ad.get('U_code')}
        except Exception as exc:
            log.exception(f"[TodayFilter] failed to load today-active ads: {exc}")
            return set()
        
    def _toggle_today_filter(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = call.message.chat.id
        call_id = call.id

        try:
            self.filters.setdefault(chat_id, {})

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                state_id = int(call.data.split('|', 1)[1])
            except Exception as e:
                log.warning(f"[TodayToggle] invalid state ID in callback: {call.data}")
                self.bot.answer_callback_query(call_id, "❌ مشکلی در بارگذاری فیلتر پیش آمد.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            loaded_state = load_filter_snapshot(self.db, state_id)
            if not loaded_state:
                self.bot.answer_callback_query(call_id, "❌ فیلتر موردنظر یافت نشد.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state.setdefault(chat_id, {}).update(loaded_state)

            # Internal implementation note: legacy behavior is preserved during modernization.
            if self.user_state[chat_id].get("today_filter"):
                self._remove_today_filter(call)
            else:
                self._apply_today_filter(call)

            log.info(f"[TodayToggle] toggled today_filter for chat {chat_id}")

        except Exception as e:
            log.exception(f"[TodayToggle] failed for chat {chat_id}: {e}")
            try:
                self.bot.answer_callback_query(call.id, "❌ خطایی رخ داد. لطفاً دوباره امتحان کنید.")
            except:
                pass


    def start_filtering(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            chat_id = call.message.chat.id
            self.filters.setdefault(chat_id, {})  # Internal implementation note: legacy behavior is preserved during modernization.
            state_id = int(call.data.split('|', 1)[1])                
            loaded_state = load_filter_snapshot(self.db, state_id)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.user_state.setdefault(chat_id, {}).update(loaded_state)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self._show_filter_fields(chat_id, call.message.message_id)
            logger.info(
                f"Loaded filter snapshot {state_id} for chat {chat_id}")

        except Exception:
            logger.exception("Error in start_filtering")

    def callback_query(self, call: CallbackQuery):
        """Legacy-compatible behavior preserved for this callable."""
        data = call.data
        try:
            if data.startswith('filter_search'):
                self.start_filtering(call)
            elif data.startswith("Actives"):
                self._toggle_today_filter(call)
            elif data.startswith('toggle_checkbox_'):
                self._toggle_checkbox_filter(call)
            elif data.startswith('toggle_single_'):
                self._toggle_single_filter(call)
            elif data.startswith('toggle_range_'):
                self._toggle_range_filter(call)
            elif data.startswith('field_'):
                field = [f for f in FILTER_CONFIG.keys() if f in data][0]
                # value = data.replace(f"{field}_", "")
                self._show_filter_options(
                    call.message.chat.id, field, call.message.message_id)
            elif data == 'apply_filters':
                self._apply_filters(call)
            else:
                logger.warning(f"Unknown filter callback: {data}")
        except Exception:
            logger.exception("Error in callback_query")

        self.bot.answer_callback_query(call.id)
