from typing import List, Dict, Any, Tuple
from telebot import TeleBot, types
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
# from telegram_bot_platform.compat.handlers.admin.request_manager import RequestManager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from  datetime import datetime 
from io import BytesIO
from datetime import date, datetime
import pandas as pd
from telebot.types import InputFile, InlineQuery, CallbackQuery, Message
from io import BytesIO
from datetime import date
from telebot.types import InputFile
from telegram_bot_platform.compat.config.settings import MEDIA_FIELDS




log = CustomLogger("INLINE_USER_SEARCHER")
class InlineUserSearcher:
    """Legacy-compatible behavior preserved for this callable."""

    SEARCH_COLUMNS: List[str] = [
        "telegram_id", "username", "first_name", "last_name", "phone_number",
    ]
    MAX_RESULTS: int = 10  # Internal implementation note: legacy behavior is preserved during modernization.

    def __init__(self, db: DatabaseManager, bot: TeleBot) -> None:
        self.db = db
        self.bot = bot
        
    def get_admins(self):
        
        admins = self.db.select_dict("admins")
        
        telegram_ids = [admin["telegram_id"]  for admin in admins]
        return telegram_ids
    def register_handlers(self) -> None:
        admins = self.get_admins()
        @self.bot.inline_handler(func=lambda q: True)
        def _inline_handler(inline_query: types.InlineQuery):
            try:
                user_id = inline_query.from_user.id
                if user_id not in admins:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    return
                query = (inline_query.query or "").strip()
                results = self._search_users(query)
                self.bot.answer_inline_query(inline_query.id, results, cache_time=1)
            except Exception as e:
                log.error(f"[inline_handler] {e}")
                self.bot.answer_inline_query(
                    inline_query.id,
                    [],
                    switch_pm_text="خطا در جستجو",
                    switch_pm_parameter="start"
                )

        # Internal implementation note: legacy behavior is preserved during modernization.
        @self.bot.callback_query_handler(
            func=lambda call: call.data in ("export_all_users", "export_today_users", "export_one_user")
        )
        def _export_callback(call: CallbackQuery):
            user_id = call.from_user.id
            if user_id not in admins:
                return self.bot.answer_callback_query(
                    call.id,
                    "❌ شما اجازهٔ دسترسی به این بخش را ندارید.",
                    show_alert=True
                )
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id)

            # Internal implementation note: legacy behavior is preserved during modernization.
            if call.data == "export_all_users":
                rows = self.db.select_dict("users")
                df = pd.DataFrame(rows)

                buf = BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name="All Users", index=False)
                buf.seek(0)
                buf.name = "all_users.xlsx"

                self.bot.send_document(
                    chat_id,
                    InputFile(buf, file_name=buf.name),
                    caption="📊 فایل اکسل کامل کاربران"
                )
            elif call.data == "export_today_users":
                today_str = date.today().isoformat()
            
                # Internal implementation note: legacy behavior is preserved during modernization.
                users = self.db.select_dict(
                    "users",
                    "date(last_interaction) = ?",
                    (today_str,)
                )
            
                # Internal implementation note: legacy behavior is preserved during modernization.
                for u in users:
                    clicks_today = self.db.select_dict(
                        "clicks",
                        "telegram_id = ? AND date(created_at) = ?",
                        (u["telegram_id"], today_str)
                    )
                    u["today_clicks"] = clicks_today[0]["clicks"] if clicks_today else 0
            
                # Internal implementation note: legacy behavior is preserved during modernization.
                df = pd.DataFrame(users)
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name="Today's Users", index=False)
                buf.seek(0)
                buf.name = "today_users.xlsx"
            
                self.bot.send_document(
                    chat_id,
                    InputFile(buf, buf.name),
                    caption=f"📅 اکسل کاربران فعال امروز (+ تعداد کلیک) {today_str}"
                )
            

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif call.data == "export_one_user":
                msg = self.bot.send_message(
                    chat_id,
                    "🔍 لطفاً آیدی عددی کاربر را ارسال کنید:"
                )
                self.bot.register_next_step_handler(msg, self._handle_export_one)


    def _handle_export_one(self, message: Message):
        chat_id = message.chat.id
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            user_id = int(message.text.strip())
        except ValueError:
            return self.bot.send_message(chat_id, "❌ آیدی نامعتبر است. لطفاً فقط عدد وارد کنید.")
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        users = self.db.select_dict("users", "telegram_id = ?", (user_id,))
        if not users:
            return self.bot.send_message(chat_id, "⚠️ کاربری با این آیدی یافت نشد.")
        user = users[0]
        df_user = pd.DataFrame([user])
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        clicks = self.db.select_dict("clicks", "telegram_id = ?", (user_id,))
        df_raw = pd.DataFrame(clicks)
        if not df_raw.empty and "created_at" in df_raw.columns:
            df_raw["created_at"] = pd.to_datetime(df_raw["created_at"])
            df_raw["date"] = df_raw["created_at"].dt.date
            df_daily = df_raw[["date", "clicks"]].sort_values("date")
        else:
            df_daily = pd.DataFrame(columns=["date", "clicks"])
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        df_all, medias = self._collect_user_rows_across_tables(user_id)
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        if medias:
            for media_type, file_id in medias[:10]:
                try:
                    if media_type == "photo":
                        self.bot.send_photo(chat_id, file_id)
                    else:
                        self.bot.send_document(chat_id, file_id)
                except Exception as exc:
                    log.debug(f"[media_send] failed {file_id} | {exc}")
        else:
            self.bot.send_message(chat_id, "ℹ️ هیچ رسانه‌ای برای ارسال یافت نشد.")
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        buf_profile = BytesIO()
        with pd.ExcelWriter(buf_profile, engine="xlsxwriter") as writer:
            df_user.to_excel(writer, sheet_name="Profile", index=False)
        buf_profile.seek(0)
        buf_profile.name = f"user_{user_id}_profile.xlsx"
        self.bot.send_document(
            chat_id,
            InputFile(buf_profile, buf_profile.name),
            caption=f"👤 اکسل پروفایل کاربر {user_id}"
        )
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        buf_clicks = BytesIO()
        with pd.ExcelWriter(buf_clicks, engine="xlsxwriter") as writer:
            df_daily.to_excel(writer, sheet_name="Daily Clicks", index=False)
        buf_clicks.seek(0)
        buf_clicks.name = f"user_{user_id}_clicks.xlsx"
        self.bot.send_document(
            chat_id,
            InputFile(buf_clicks, buf_clicks.name),
            caption=f"📊 اکسل کلیک‌های کاربر {user_id}"
        )
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not df_all.empty:
            buf_all = BytesIO()
            with pd.ExcelWriter(buf_all, engine="xlsxwriter") as writer:
                df_all.to_excel(writer, sheet_name="All Tables", index=False)
            buf_all.seek(0)
            buf_all.name = f"user_{user_id}_all_tables.xlsx"
            self.bot.send_document(
                chat_id,
                InputFile(buf_all, buf_all.name),
                caption=f"📁 تمام رکوردهای کاربر {user_id} در همهٔ جداول"
            )
        else:
            self.bot.send_message(
                chat_id,
                "ℹ️ هیچ رکورد دیگری برای این کاربر در جداول یافت نشد."
            )
    
    def _collect_user_rows_across_tables(
            self,
            user_id: int
    ) -> Tuple[pd.DataFrame, List[Tuple[str, str]]]:
        """Legacy-compatible behavior preserved for this callable."""
        dataframes: List[pd.DataFrame] = []
        medias: List[Tuple[str, str]] = []

        for table in self.db.list_tables():
            try:
                cols = self.db.get_columns(table)
            except Exception as e:
                log.debug(f"[collect] skip table {table}: {e}")
                continue

            if "telegram_id" not in cols:
                continue

            rows = self.db.select_dict(table, "telegram_id = ?", (user_id,))
            if not rows:
                continue

            df = pd.DataFrame(rows)
            df.insert(0, "table", table)        # Internal implementation note: legacy behavior is preserved during modernization.
            dataframes.append(df)

            # Internal implementation note: legacy behavior is preserved during modernization.
            
            for r in rows:
                for mc in list(MEDIA_FIELDS.keys()):
                    file_id = r.get(mc)
                    if file_id:
                        # Internal implementation note: legacy behavior is preserved during modernization.
                        media_type = MEDIA_FIELDS.get(mc , "photo")
                        
                        medias.append((media_type, file_id))

        if dataframes:
            df_all = pd.concat(dataframes, ignore_index=True)
        else:
            df_all = pd.DataFrame()

        return df_all, medias

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
        
    def _search_users(self, query: str) -> List[types.InlineQueryResultArticle]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            all_rows = self.db.select_dict("users")
        except Exception as e:
            log.error(f"[_search_users] load failed: {e}")
            return []

        # Internal implementation note: legacy behavior is preserved during modernization.
        if query:
            query_lower = query.strip().lower()
            filtered_rows = []

            for row in all_rows:
                for col in self.SEARCH_COLUMNS:
                    val = row.get(col)
                    if val is not None and query_lower in str(val).lower():
                        filtered_rows.append(row)
                        break
        else:
            filtered_rows = all_rows

        rows = filtered_rows[: self.MAX_RESULTS]

        results: List[types.InlineQueryResultArticle] = []
        for u in rows:
            try:
                tid = str(u["telegram_id"])
                title = (
                    f"{u.get('first_name','')} {u.get('last_name','')} "
                    f"{('@'+u['username']) if u.get('username') else ''}"
                ).strip() or tid
                desc = f"ID: {tid} | 📞 {u.get('phone_number','—')}"
                content = types.InputTextMessageContent(
                    self._format_profile(u), parse_mode="HTML"
                )
                results.append(
                    types.InlineQueryResultArticle(
                        id=tid,
                        title=title[:128],
                        description=desc[:256],
                        input_message_content=content,
                    )
                )
            except Exception as e:
                log.debug(f"[inline_row] skip row: {e}")
        return results

    def _format_profile(self, u: Dict[str, Any]) -> str:
        fs = self.convert_to_shamsi(u.get("created_at") or "—")
        li = self.convert_to_shamsi(u.get("last_updated") or "—")
        tc = u.get("clicks", 0)

        # Internal implementation note: legacy behavior is preserved during modernization.
        today_date = datetime.now().date().isoformat()
        today_clicks = 0
        try:
            row = self.db.select_dict(
                "clicks",
                "telegram_id = ? AND date(created_at) = ?",
                (u["telegram_id"], today_date)
            )
            if row:
                today_clicks = row[0]["clicks"] if isinstance(row, list) else row["clicks"]
        except Exception as exc:
            log.debug(f"[format_profile] fetch today's clicks failed | {exc}")

        return (
            f"🆔 <b>آیدی عددی:</b> <code>{u['telegram_id']}</code>\n"
            f"👤 <b>نام:</b> {u.get('first_name','')} {u.get('last_name','')}\n"
            f"🔗 <b>یوزرنیم:</b> {(('@'+u['username']) if u.get('username') else '—')}\n"
            f"📞 <b>شماره تماس:</b> {u.get('phone_number','—')}\n"
            f"🕓 <b>اولین ورود:</b> {fs}\n"
            f"🕓 <b>آخرین تعامل:</b> {li}\n"
            f"📊 <b>تعداد استارت‌ها:</b> {tc} مرتبه\n"
            f"📅 <b>کلیک‌های امروز:</b> {today_clicks} مرتبه\n"
        )
    # Internal implementation note: legacy behavior is preserved during modernization.
