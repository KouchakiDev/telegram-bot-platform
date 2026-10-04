# Internal implementation note: legacy behavior is preserved during modernization.
import json
from datetime import datetime, timedelta

# Internal implementation note: legacy behavior is preserved during modernization.
from telebot import TeleBot

# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.


# Database Manager
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

# Logger
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
log = CustomLogger()  # log_file="see_r_r.log")


class SeeRequestsHandler:
    def __init__(self, bot: TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db

    def counter_of_requests_results(self, message):
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id

            # Internal implementation note: legacy behavior is preserved during modernization.
            try :
                rows = self.db.select_dict('clients', 'telegram_id = ?', (user_id,))
            except :
                return 0
            if not rows:
                try:
                    count = self.db.count_rows('clients')
                except :
                    return 0
                U_code = f'c{count + 1421}'
                data = {'telegram_id': user_id, 'U_code': U_code}
                if message.from_user.username:
                    data['username'] = message.from_user.username
                try:
                    self.db.upsert(
                        'clients',
                        data,
                        unique_column='telegram_id',
                        schema={'telegram_id': 'INTEGER UNIQUE', 'U_code': 'TEXT UNIQUE'}
                    )
                except :
                    return 0

            else:
                U_code = rows[0]['U_code']

            # Internal implementation note: legacy behavior is preserved during modernization.
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            requests = self.db.select_dict(
                'service_requests',
                'U_code = ? AND created_at >= ? AND created_at < ?',
                (U_code, today, tomorrow)
            )
            if requests:
                return len(requests)
            else:
                return 0
        except :
                return 0

    def handle(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = self.db.select_dict('clients', 'telegram_id = ?', (user_id,))
        if not rows:
            count = self.db.count_rows('clients')
            U_code = f'c{count + 1421}'
            data = {'telegram_id': user_id, 'U_code': U_code}
            if message.from_user.username:
                data['username'] = message.from_user.username
            self.db.upsert(
                'clients', data, 'telegram_id',
                {'telegram_id': 'INTEGER UNIQUE', 'U_code': 'TEXT UNIQUE'}
            )
        else:
            U_code = rows[0]['U_code']

        # Internal implementation note: legacy behavior is preserved during modernization.
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        requests = self.db.select_dict(
            'service_requests',
            'U_code = ? AND created_at >= ? AND created_at < ?',
            (U_code, today, tomorrow)
        )

        if not requests:
            self.bot.send_message(chat_id, MESSAGES["not_requests_found"])
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        for req in requests:
            try:
                text = self._compose_message(req)
                self.bot.send_message(chat_id, text, parse_mode="HTML")
            except Exception as e:
                # Internal implementation note: legacy behavior is preserved during modernization.
                print(f"Error sending message for req {req.get('id')}: {e}")
        return

    def convert_to_shamsi(self, date_str: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        from datetime import datetime
        from persiantools.jdatetime import JalaliDateTime

        if not date_str:
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

    def normalize_phone_number(self, number: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        number = str(number).strip().replace(" ", "").replace("-", "")


        if number.startswith("0098"):
            number = f"+{number[4:]}"
        elif number.startswith("098"):
            number = f"+{number[3:]}"
        elif number.startswith("0"):
            number = f"+98{number[1:]}"
        elif not number.startswith("98"):
            number = f"+98{number}"  # Internal implementation note: legacy behavior is preserved during modernization.
        return number

    def _compose_message(self, req: dict) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        req_id = req.get('id')
        status = req.get('status')
        raw_pu_code = req.get('PU_code')
        PU_code = f"/{raw_pu_code}" if raw_pu_code else '—'

        # Internal implementation note: legacy behavior is preserved during modernization.
        created = req.get('created_at')
        # Internal implementation note: legacy behavior is preserved during modernization.
        created_dt = None
        if isinstance(created, str):
            try:
                if '.' in created:
                    created = created.split('.')[0]
                created_dt = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        elif isinstance(created, datetime):
            created_dt = created

        # Internal implementation note: legacy behavior is preserved during modernization.
        if created_dt:

            date_str = self.convert_to_shamsi(
                created_dt.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            date_str = "نامشخص"

        # Internal implementation note: legacy behavior is preserved during modernization.
        invoice = {}
        if req.get('invoice'):
            try:
                invoice = json.loads(req['invoice'])
            except Exception:
                invoice = {}
        total_price = invoice.get('total_price', '—')
        prepayment = invoice.get('prepayment', '—')

        # Internal implementation note: legacy behavior is preserved during modernization.
        services = '—'
        svc = invoice.get('services', {})
        if isinstance(svc, dict) and svc:
            selected = [name for name, used in svc.items() if used]
            services = '، '.join(selected) if selected else '—'

        # Internal implementation note: legacy behavior is preserved during modernization.
        phone_number = '—'
        if raw_pu_code and status == 'finalized':
            per = self.db.select_dict(
                'staff', 'U_code = ?', (raw_pu_code,))
            if per:
                phone_number = per[0].get('phone_number', '—')

        # Internal implementation note: legacy behavior is preserved during modernization.
        if status == 'approved':
            return MESSAGES['see_requests_approved'].format(
                req_id=req_id, date=date_str,
                total_price=total_price, PU_code=PU_code
            )
        if status == 'pending':
            return MESSAGES['see_requests_pending'].format(
                req_id=req_id, date=date_str,
                total_price=total_price, PU_code=PU_code
            )
        if status == 'expired':
            return MESSAGES['see_requests_expired'].format(
                req_id=req_id, date=date_str,
                total_price=total_price, PU_code=PU_code
            )
        if status == 'finalized':
            return MESSAGES['see_requests_finalized1'].format(
                req_id=req_id,
                date=date_str,
                total_price=total_price,
                PU_code=PU_code,
                # phone_number=self.normalize_phone_number(
                #     phone_number),
                # Internal implementation note: legacy behavior is preserved during modernization.
            )
        if status == 'done':
            return MESSAGES['see_requests_done'].format(
                req_id=req_id, date=date_str,
                total_price=total_price, PU_code=PU_code,
                services=services
            )
        if status == 'cancelled':
            return MESSAGES['see_requests_cancelled'].format(
                req_id=req_id, date=date_str,
                total_price=total_price, PU_code=PU_code
            )
        if status == 'rejected':
            return MESSAGES.get('see_requests_rejected', MESSAGES['not_requests_found']).format(
                req_id=req_id,
                date=date_str,
                total_price=total_price,
                PU_code=PU_code,
                reject_reason=req.get("reject_reason", "ذکر نشده")
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        return MESSAGES['not_requests_found']
