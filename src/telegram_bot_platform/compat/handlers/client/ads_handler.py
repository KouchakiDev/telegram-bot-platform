from datetime import datetime, timedelta
import html
import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot_platform.compat.config.settings import CHANNEL_ID, BUTTONS, MESSAGES, CLIENT_BOT_ID
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
PAGE_SIZE = 1
log  = CustomLogger("ads_handler")

class AdsHandler:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.today_ads = []
        # Internal implementation note: legacy behavior is preserved during modernization.
        # chat_id -> {"ads": [...], "page": int, "sent_messages": [...], "info_message_id": int, "nav_message_id": int}
        self.user_state = {}

        # Internal implementation note: legacy behavior is preserved during modernization.
        # bot.callback_query_handler(
        #     func=lambda c: c.data.startswith("ads_page_"))(self._on_page)
    def register_handlers(self):
        self.bot.callback_query_handler(
            func=lambda c: c.data.startswith("ads_page_"))(self._on_page)

    def get_today_ads(self):
        """Legacy-compatible behavior preserved for this callable."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        rows = self.db.select_dict(
            'live_ads',
            'created_at >= ? AND created_at < ?',
            (today, tomorrow)
        ) or []
        self.today_ads = rows
        return [row['channel_message_id'] for row in rows]

    def handle_show_ads(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        message_ids = self.get_today_ads()
        ads = [{'message_id': mid} for mid in message_ids]
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.user_state[chat_id] = {
            'ads': ads,
            'page': 1,
            'sent_messages': [],
            'info_message_id': None,
            'nav_message_id': None
        }
        self._send_page(chat_id)

    def _on_page(self, call):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = call.message.chat.id
        state = self.user_state.get(chat_id)
        if not state:
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        new_page = int(call.data.split('_')[-1] or 1)
        state['page'] = new_page
        # Internal implementation note: legacy behavior is preserved during modernization.
        for mid in state['sent_messages']:
            try:
                self.bot.delete_message(chat_id, mid)
            except:
                pass
        state['sent_messages'].clear()
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._send_page(chat_id)

    def _send_page(self, chat_id):
        """Legacy-compatible behavior preserved for this callable."""
        state = self.user_state.get(chat_id, {})
        ads = state.get('ads', [])
        page = state.get('page', 1)
        total = len(ads)

        if total == 0:
            self.bot.send_message(chat_id, MESSAGES['no_ads'])
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        page = max(1, min(page, pages))
        state['page'] = page
        if total > 1:
            # Internal implementation note: legacy behavior is preserved during modernization.
            page_text = MESSAGES['page_info'].format(current=page, total=pages)
            # Internal implementation note: legacy behavior is preserved during modernization.
            if state.get('info_message_id'):
                try:
                    self.bot.edit_message_text(
                        page_text, chat_id, state['info_message_id'])
                except:
                    state['info_message_id'] = None
            if not state.get('info_message_id'):
                msg = self.bot.send_message(chat_id, page_text)
                state['info_message_id'] = msg.message_id

        # Internal implementation note: legacy behavior is preserved during modernization.
        start, end = (page - 1) * PAGE_SIZE, page * PAGE_SIZE
        for ad in ads[start:end]:
            # Internal implementation note: legacy behavior is preserved during modernization.
            msg = self.bot.copy_message(chat_id, CHANNEL_ID, ad['message_id'])
            state['sent_messages'].append(msg.message_id)
            # Internal implementation note: legacy behavior is preserved during modernization.
            ad_row = next(
                (r for r in self.today_ads if r['channel_message_id']
                 == ad['message_id']),
                None
            )
            if ad_row:
                markup = self._build_ad_markup(ad_row)
                self.bot.edit_message_reply_markup(
                    chat_id, msg.message_id, reply_markup=markup)

        # Internal implementation note: legacy behavior is preserved during modernization.
        nav = InlineKeyboardMarkup()
        if page > 1:
            nav.add(InlineKeyboardButton(
                BUTTONS['prev'], callback_data=f"ads_page_{page-1}"))
        if page < pages:
            nav.add(InlineKeyboardButton(
                BUTTONS['next'], callback_data=f"ads_page_{page+1}"))
        # Internal implementation note: legacy behavior is preserved during modernization.
        if total > 1:
            if state.get('nav_message_id'):
                try:
                    self.bot.edit_message_reply_markup(
                        chat_id, state['nav_message_id'], reply_markup=nav)
                except:
                    state['nav_message_id'] = None
            if not state.get('nav_message_id'):
                nav_msg = self.bot.send_message(
                    chat_id, MESSAGES['ads_navigation'], reply_markup=nav)
                state['nav_message_id'] = nav_msg.message_id

    def _build_ad_markup(self, ad_row: dict) -> InlineKeyboardMarkup:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        slots = json.loads(ad_row.get('time_slots', '[]'))
        print(slots)
        link_base = f"https://t.me/{html.escape(CLIENT_BOT_ID)}?start"
        buttons = []
        # Internal implementation note: legacy behavior is preserved during modernization.
        for slot, available in slots.items():
            text = slot.replace(':', '_')
            callback = f"reserve_ads_{ad_row['ad_id']}_{text}"
            if available:
                # param = f"reserve_{table}_{ad_id}_{slot.replace(':', '_')}"

                # url = f"https://t.me/{CLIENT_BOT_ID}?start={param}"
                buttons.append(InlineKeyboardButton(
                    slot.replace('_', ':'), callback_data=callback))
            else:
                # url = f"https://t.me/{CLIENT_BOT_ID}?start={param}"
                buttons.append(InlineKeyboardButton(
                    "رزوشده🕰", url=f"{link_base}"))

        # Internal implementation note: legacy behavior is preserved during modernization.
        rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
        if len(rows) >= 2 and len(rows[-1]) == 1:
            flat = sum(rows, [])
            rows = [flat[i:i+3] for i in range(0, len(flat), 3)]
        try:
    # Internal implementation note: legacy behavior is preserved during modernization.
            ad_list = self.db.select_dict("ads", "id = ?", (ad_row.get("ad_id"),))

            if not ad_list:
                log.warning(f"[UI] No ad found for ad_id={ad_row.get('ad_id')}")
            else:
                ad = ad_list[0]

                # Internal implementation note: legacy behavior is preserved during modernization.
                fav_button = InlineKeyboardButton(
                    text=BUTTONS["Add_toFavoris"],
                    callback_data=f"AddToFavorits_{ad.get('U_code')}"
                )
                rows.append([fav_button])
                log.debug(f"[UI] Added favorite button for ad U_code={ad.get('U_code')}")

        except Exception as e:
            log.exception(f"[UI] Failed to add favorite button for ad_id={ad_row.get('ad_id')}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        keyboard = InlineKeyboardMarkup()
        for r in rows:
            keyboard.row(*r)
        return keyboard

    def send_single_ad_by_ad_id(self, chat_id, ad_id):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        row = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
        if not row:
            self.bot.send_message(
                chat_id, "❌ آگهی مورد نظر در لیست آگهی‌های فعال یافت نشد.")
            return

        ad_row = row[0]
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            msg = self.bot.copy_message(
                chat_id, CHANNEL_ID, ad_row["channel_message_id"])

            # Internal implementation note: legacy behavior is preserved during modernization.
            markup = self._build_ad_markup(ad_row)
            self.bot.edit_message_reply_markup(
                chat_id, msg.message_id, reply_markup=markup)
        except Exception as e:
            print("❌ Error sending ad:", e)
            self.bot.send_message(chat_id, "❌ مشکلی در ارسال آگهی رخ داد.")

    def handle_show_ads_for_ucode(self, message, u_code):
        """Legacy-compatible behavior preserved for this callable."""
        chat_id = message.chat.id
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        # Internal implementation note: legacy behavior is preserved during modernization.
        ads_rows = self.db.select_dict(
            "ads",
            "U_code = ? AND status = 'approved' AND created_at >= ? AND created_at < ?",
            (u_code, today, tomorrow)
        )
        print(u_code)
        if not ads_rows:
            self.bot.send_message(
                chat_id, "📭 این کد امروز هیچ آگهی فعالی ندارد.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        live_ads = []
        for ad in ads_rows:
            ad_id = ad["id"]
            row = self.db.select_dict("live_ads", "ad_id = ?", (ad_id,))
            if row:
                live_ads.append(row[0])  # Internal implementation note: legacy behavior is preserved during modernization.

        if not live_ads:
            self.bot.send_message(
                chat_id, "📭 این کد امروز هیچ آگهی فعالی در کانال ندارد.")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.today_ads = live_ads
        ads = [{'message_id': ad['channel_message_id']} for ad in live_ads]
        self.user_state[chat_id] = {
            'ads': ads,
            'page': 1,
            'sent_messages': [],
            'info_message_id': None,
            'nav_message_id': None
        }
        self._send_page(chat_id)
