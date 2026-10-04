from dotenv import load_dotenv
import os
from pathlib import Path
ADD_FAVORITES_FOR_NORMAL_USERS = True
load_dotenv()


ADD_TO_FAVORITES_PREFIX = "AddToFavorits"

ADS_TABLE = "ads"

AD_TABLES = [
    "ads"
]

APPLY_FILTERS = "apply_filters"

AUTH_MESSAGES = {
    "required_error": "این مرحله اجباری است و باید اطلاعات را وارد کنید.",
    "skipped": "این مرحله غیرفعال شده است و از آن صرف نظر می‌شود."
}

AUTH_PROMPTS = {
    "contact": "لطفاً شماره تلفن را ارسال کنید:",
    "document": "لطفاً فایل را ارسال کنید:",
    "location": "لطفاً موقعیت مکانی را ارسال کنید:",
    "otp": "لطفاً کد تایید دریافتی را وارد کنید:",
    "photo": "لطفاً عکس را ارسال کنید:",
    "text": "لطفاً متن را وارد کنید:",
    "video": "لطفاً ویدئو را ارسال کنید:",
    "voice": "لطفاً صدا را ارسال کنید:"
}

AUTO_CONFIG = {
    "default_auto_check_interval": 20,
    "default_auto_threshold": 1,
    "default_auto_timer": 120,
    "hash_line": "########################################################################################################################################################################################################",
    "hash_subline": "##################################################",
    "log_error_parsing_permissions": "❌ خطا در تجزیه دسترسی‌ها برای مدیر {id}: {error}",
    "log_error_threshold": "\nخطا در بررسی آستانه برای جدول {table}: {error}\n{hash_subline}\n",
    "log_error_timer": "\nخطا در بررسی تایمر برای جدول {table}: {error}\n{hash_subline}\n",
    "log_file": "automatical.log",
    "log_global_interval": "\nفاصله زمانی بررسی خودکار جهانی به {interval} دقیقه تنظیم شد. در حال انتظار...\n{hash_line}\n",
    "log_notification_failed": "❌ ارسال اطلاعیه به {name} | شناسه تلگرام: {chat_id} با خطا مواجه شد: {error}",
    "log_notification_sent": "✅ اطلاعیه‌ها برای مدیر {name} | شناسه تلگرام: {chat_id} ارسال شدند",
    "log_start_approver": "\n{hash_line}\nشروع تایید خودکار << {table} >> درخواست‌های در انتظار << {count} >>\n{hash_subline}\n",
    "log_threshold_not_met": "\nآستانه برای جدول {table} برآورده نشد. تاییدی بر اساس تعداد صورت نگرفت.\n{hash_subline}\n",
    "log_update_error": "ما نمی‌توانیم وضعیت را به‌روز کنیم به دلیل: {error}",
    "status_active": "✅ فعال",
    "status_approved": "تایید شده",
    "status_inactive": "❌ غیرفعال",
    "status_pending": "در انتظار"
}


HAND_VERFIY = {
    "✋🏻": "fullhand",
    "👍🏻": "likehand",
    "👌🏻": "nicehand",
    "👆🏻": "onefinger",
    "👊🏻": "punch",
    "🤟🏻": "spiderhand",
    "🤙🏻": "telephonefinger",
    "✌🏻": "twofinger",
}

VERIFICATION_PHOTO_TIMEOUT = 180
BOT_ADMIN_TOKEN = os.getenv("BOT_ADMIN_TOKEN", "")
BOT_CLIENT_TOKEN = os.getenv("BOT_CLIENT_TOKEN") or os.getenv("BOT_CUSTOMER_TOKEN", "")
BOT_STAFF_TOKEN = os.getenv("BOT_STAFF_TOKEN") or os.getenv("BOT_PERSONNEL_TOKEN", "")
BOT_AUTO_RESPONDER_TOKEN = os.getenv("BOT_AUTO_RESPONDER_TOKEN") or os.getenv("BOT_AUTOREPONSER_TOKEN", "")
BOT_AUTOREPONSER_TOKEN = BOT_AUTO_RESPONDER_TOKEN

CHANNEL_ID = _env_int("CHANNEL_ID")
STORAGE_CHANNEL = _env_int("ARCHIVE_CHANNEL")
PHOTOS_CHANNEL = _env_int("PHOTOS_CHANNEL")
CLIENT_BOT_ID = os.getenv("CLIENT_BOT_ID") or os.getenv("CUSTOMER_BOT_ID")
CLIENT_BOT_USERNAME = os.getenv("CLIENT_BOT_USERNAME") or (CLIENT_BOT_ID or "")
if not CLIENT_BOT_ID:
    CLIENT_BOT_ID = CLIENT_BOT_USERNAME
STAFF_BOT_ID = os.getenv("STAFF_BOT_ID") or os.getenv("PERSTONNEL_BOT_ID")
STAFF_BOT_USERNAME = os.getenv("STAFF_BOT_USERNAME") or (STAFF_BOT_ID or "")
if not STAFF_BOT_ID:
    STAFF_BOT_ID = STAFF_BOT_USERNAME
ADMIN_BOT_ID = os.getenv("ADMIN_BOT_ID")
PROFILE_CHANNEL_TAGS = os.getenv("PROFILE_CHANNEL_TAGS", "")
PROFILE_CHANNEL_TAGS = PROFILE_CHANNEL_TAGS.split("|") if PROFILE_CHANNEL_TAGS else []
DURATION_TIME  = 20
BETWIN_TIME = 30      # minutes  (on-site)
MULTIPLIER_DISPATCH = 2  
DB_PARAMS = {
    "db_type": "mysql",
    'host': os.getenv('DB_HOST'),
    "db_name": os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    "port": os.getenv("DB_PORT"),
}

# BOT_GROUP_ID = -4707606339
# BOT_TOKEN = "BOT_TOKEN_FROM_ENV"

BUTTONS = {
    "auto_answer": "پاسخ دهی خودکار",
    "manage_messages": "مدیریت پیام ها",
    "search_users": "👥 مشاهده کاربران",
    "Add_toFavoris": " ➕علاقه مندی ها💌",
    "Change_to_active": "فعال کردن مدیر🔛",
    "Goto_Cutsomer_bot": "➡️ رفتن به بات مشتری",
    "GropAndChannel": "تنظمیات کانال/گروه📢⚙",
    "BotAndChannel":"کانال/ربات",
    "Manage_members": "👥 مدیریت اعضا",
    "Send_my_phone": "📱 ارسال شماره من",
    "accept": "✅ تایید",
    "accounting": "💰 حسابداری",
    "add_card": "➕ افزودن کارت",
    "add_new_admin": "➕ افزودن مدیر جدید",
    "add_reason": "➕ افزودن دلیل",
    "add_request": "➕ افزودن درخواست",
    "add_wallet": "➕ افزودن کیف پول",
    "admins": "👥 مدیران",
    "ads": "آگهی",
    "approved": "✅ تایید شده",
    "approved_list": "✅ پرسنل تایید شده",
    "auto": "📍 تشخیص خودکار",
    "auto_help": "ℹ️ راهنمای خودکار",
    "auto_operations": "⚙️ عملیات خودکار",
    "back": "🔙 بازگشت",
    "back_to_pannel"      :"🔙 بازگشت به پنل",
    "back_to_accounting": "🔙 بازگشت به حسابداری",
    "back_to_add_wallet": "🔙 بازگشت به افزودن کیف پول",
    "back_to_admin_main": "⬅️ بازگشت به منوی مدیر",
    "back_to_bank_accounts": "🔙 بازگشت به حساب‌های بانکی",
    "back_to_crypto_wallets": "🔙 بازگشت به کیف پول‌های کریپتو",
    "back_to_main": "🔙 بازگشت به منوی اصلی",
    "back_to_main_menu": "🏠 منوی اصلی",
    "back_to_pervious_menu": "🔙 بازگشت",
    "back_to_previous": "↩️ بازگشت",
    "back_to_requests": "بازگشت به منوی درخواست🧾",
    "back_to_settings": "🔙 بازگشت به تنظیمات",
    "bank_accounts": "🏦 حساب‌های بانکی",
    "block": "🚫 مسدودسازی",
    "blocked": "🚫 مسدود شده",
    "blocked_list": "🚫 پرسنل بلاک شده",
    "cancel": "❌ لغو",
    "change_address": "📍 تغییر آدرس",
    "change_status": "🔄 تغییر وضعیت",
    "change_to_approved": "🔄 تغییر به تایید شده",
    "change_to_blocked": "🔄 تغییر به مسدود شده",
    "change_to_rejected": "🔄 تغییر به رد شده",
    "channel_settings": "📢 تنظیمات کانال",
    "complete_identity_verification": "✅ تکمیل احراز هویت",
    "complete_profile": "📝 تکمیل پروفایل",
    "configure_settings": "⚙️ پیکربندی تنظیمات",
    "confirm": "✅ تایید",
    "confirm_extra_time": "✔️ تایید زمان اضافه",
    "confirm_services": "✔️ تایید خدمات",
    "continue_without_premium": "❌ ادامه بدون PREMIUM",
    "create_ad": "📢 ایجاد آگهی",
    "crypto_wallets": "💰 کیف پول‌های کریپتو",
    "client_ads": "🛍 آگهی‌های مشتریان",
    "daily_update": "⏰ به‌روزرسانی روزانه",
    "delete": "🗑️ حذف",
    "delete_card": "🗑️ حذف کارت",
    "delete_reason": "🗑️ حذف دلیل",
    "delete_wallet": "🗑️ حذف کیف پول",
    "disqualified": "❌ عدم صلاحیت",
    "edit": "✏️ ویرایش",
    "edit_ad_desc": "📄 متن آگهی",
    "edit_ad_title": "📝 عنوان آگهی",
    "edit_admin": "✏️ ویرایش مدیر",
    "edit_card": "✏️ ویرایش کارت",
    "edit_card_number": "🔢 ویرایش شماره کارت",
    "edit_cardholder_name": "👤 ویرایش نام دارنده کارت",
    "edit_crypto_wallet": "💰 ویرایش کیف پول کریپتو",
    "edit_client": "✏️ ویرایش مشتری",
    "edit_name": "✏️ ویرایش نام",
    "edit_network_only": "🌐 ویرایش فقط شبکه",
    "edit_network_wallet": "🌐 ویرایش شبکه کیف پول",
    "edit_reason": "✏️ ویرایش دلیل",
    "edit_services": "✏️ ویرایش خدمات",
    "edit_username": "💬 ویرایش آیدی",
    "edit_wallet": "✏️ ویرایش کیف پول",
    "edit_wallet_address": "📇 ویرایش آدرس کیف پول",
    "edit_wallet_address_option": "📇 ویرایش آدرس کیف پول",
    "fake_ads": "آگهی فیک",
    "filter_by_ad_type": "📂 نوع آگهی",
    "filter_by_age": "🎂 سطح تجربه",
    "filter_by_appearance": "🪞 سبک خدمت",
    "filter_by_score": "⭐ امتیاز",
    "filter_by_services": "🧾 خدمات انتخابی",
    "first_name": "📝 نام",
    "forgot_password": "🔑 فراموشی رمز عبور",
    "goto_permanent_codes": "📌 نمایش کدهای دائم",
    "goto_show_codes": "🧾 نمایش کدها",
    "goto_today_codes": "📅 نمایش کدهای امروز",
    "goto_premium": "👑 ورود به مشتریان ویژه",
    "group_settings": "👥 تنظیمات گروه",
    "help": "ℹ️ راهنما",
    "help_accounting": "❓ راهنما - حسابداری",
    "help_bank_accounts": "❓ راهنما - حساب‌های بانکی",
    "help_crypto_wallets": "❓ راهنما - کیف پول‌های کریپتو",
    "history": "🕰 تاریخچه",
    "i_dont_have": "🚫 ندارم",
    "incomplete_info": "⚠️ اطلاعات ناقص",
    "invalid_option": "⚠️ لطفاً گزینه‌ای معتبر انتخاب کنید",
    "identity_verification_later": "❌ بعداً",
    "identity_verification_verification": "🪪 احراز هویت",
    "last_name": "📝 نام خانوادگی",
    "latest_request": "📑 آخرین درخواست",
    "list_admins": "📋 لیست تمام مدیران",
    "login": "🔑 ورود",
    "manage_admins": "🗣 مدیریت مدیران",
    "manage_clients": "👤 مدیریت مشتریان",
    "manage_staff": "👷 مدیریت پرسنل",
    "manage_rejection_reasons": "🛑 مدیریت دلایل رد",
    "manage_requests": "📌 مدیریت درخواست‌ها",
    "manual": "🛠️ انتخاب دستی",
    "manual_address": "🗺️ انتخاب دستی آدرس",
    "messages": "💬 پیام‌ها",
    "my_discounts": "🎁 تخفیف‌ها",
    "my_invites": "📨 دعوتی‌های من",
    "name": "📝 نام",
    "next": "بعدی ➡️",
    "no": "❌ خیر",
    "none": "🚫 هیچ",
    "not_now": "❌ فعلاً نه",
    # Internal implementation note: legacy behavior is preserved during modernization.
    "old_admins": "📋 مدیران قبلی",
    "pay_card": "💳 پرداخت کارت به کارت",
    "pay_cash": "💵 پرداخت نقدی",
    "pending": "⏳ در انتظار",
    "permanent_codes": "📌 کدهای دائم",
    "permissions": "🔐 دسترسی‌ها",
    "staff_ads": "📢 آگهی‌های پرسنل",
    "staff_requests": "👷 درخواست‌های پرسنل",
    "phone_number": "📞 شماره تلفن",
    "prev": "⬅️ قبلی",
    "previous": "⬅️ قبلی",
    "profile": "👤 پروفایل",
    "profile_view": "👤 مشاهده پروفایل",
    "publish_at_ad_time": "🕒 انتشار در زمان آگهی",
    "publish_list": "📅 انتخاب از لیست",
    "publish_manual": "📝 وارد کردن دستی",
    "publish_now": "🚀 انتشار فوری",
    "recent_requests_24h": "📈 ۲۴ ساعته اخیر",
    "register": "📝 ثبت پرسنل",
    "register_premium": "👑 ثبت‌نام PREMIUM",
    "reject": "❌ رد",
    "reject_extra_time": "❌ عدم نیاز به زمان اضافه",
    "rejected": "❌ رد شده",
    "rejected_list": "❌ پرسنل رد شده",
    "remove_admin": "🗑️ حذف مدیر",
    "reports": "📊 گزارش‌ها",
    "reports_menu": "📊 منوی گزارش‌ها",
    "request_settings": "⚙️ تنظیمات درخواست",
    "requests": "📂 درخواست‌ها",
    "requests_details": "🔎 ریز جزئیات",
    "search": "🔍 جستجوی پرسنل",
    "search_entire_city": "🌍 جستجو در کل شهر",
    "see_requests": "📨 مدیریت درخواست ها",
    "select_default_card": "✅ انتخاب کارت پیش‌فرض",
    "select_default_wallet": "✅ انتخاب کیف پول پیش‌فرض",
    "select_location": "🌍 انتخاب موقعیت مکانی",
    "select_specific_area": "📍 انتخاب منطقه خاص",
    "select_wallet": "👝 انتخاب کیف پول",
    "send_contact": "📱 ارسال شماره تماس",
    "send_gps": "📍 ارسال مکان",
    "send_location": "📤 ارسال مکان",
    "send_message": "📨 ارسال پیام",
    "set_auto_check_interval": "⏱ تنظیم فاصله زمانی بررسی خودکار",
    "set_categorization_column": "📚 تنظیم ستون دسته‌بندی",
    "set_display_columns": "🧩 تنظیم ستون‌های نمایش",
    "set_ignored_columns": "🚫 تنظیم ستون‌های نادیده‌گرفته‌شده",
    "set_max_requests_per_row": "🔢 تنظیم حداکثر درخواست‌ها در هر ردیف",
    "set_permissions": "🔐 تنظیم دسترسی‌ها",
    "set_request_details": "🔍 تنظیم جزئیات درخواست",
    "set_request_overview": "📝 تنظیم نمای کلی درخواست",
    "settings": "⚙️ تنظیمات",
    "show_codes": "🧾 نمایش کدها",
    "show_permanent_codes": "📌 کدهای دائم",
    "show_today_codes": "📅 کدهای امروز",
    "skip_custom_fantasy": "⏭️ رد شدن",
    "skip_gps": "⏭️ رد کردن مرحله GPS",
    "skip_send_gps": "⏭️ رد کردن مرحله GPS",
    "submit_favorits": "🎭 ثبت گزینه‌های سفارشی",
    "submit_order": "✅ ثبت سفارش",
    "submit_request": "ثبت",
    "submit_premium_request": "✨ ویژه شدن",
    "telegram_username": "🆔 نام کاربری تلگرام",
    "to_be_premium": "✅ ویژه شدن",
    "today_codes": "📅 نمایش کدهای امروز",
    "update": "🔄 به‌روزرسانی",
    "update_requests": "🔄 به‌روزرسانی درخواست‌ها",
    "user_requests": "👤 درخواست‌های مشتریان",
    "view_all": "👥 مشاهده همه",
    "view_by_date": "📅 مشاهده بر اساس تاریخ",
    "view_latest_request": "🆕 مشاهده آخرین درخواست",
    "view_less_ditails": "🔽 جزئیات کمتر",
    "view_more_details": "🔍 جزئیات بیشتر",
    "view_pending_requests": "📋 مشاهده درخواست‌های در انتظار",
    "view_requests": "👀 مشاهده درخواست‌ها",
    "view_today_requests": "📋 مشاهده درخواست‌های امروز",
    "premium_active_codes": "📊 کدهای فعال",
    "premium_ads": "🗂️ آگهی‌ها",
    "premium_code_invalid": "❌ کد اشتباه است",
    "premium_code_sent": "📨 کد ارسال شد",
    "premium_favorites": "💎 علاقه‌مندی‌ها",
    "premium_filter": "⚙️ فیلتر",
    "premium_forgot_prompt": "📞 شماره تلفن خود را وارد کنید",
    "premium_history": "📜 تاریخچه فعالیت",
    "premium_login": "👑 ورود به مشتری ویژه",
    "premium_login_info": "🔐 لطفاً کد ورود خود را وارد کنید",
    "premium_panel_welcome": "👤 پنل مشتریان ویژه",
    "premium_purchase": "🛒 خرید عکس/فیلم",
    "premium_search_all": "🔎 جستجو براساس شهر",
    "premium_search_all_codes": "🔎 نمایش تمام کدها",
    "premium_search_same_city": "🏠 جستجو بین همشهری‌ها",
    "write_reason": "📝 نوشتن دلیل",
    "yes": "✅ بله"
}
# -1002357768003
PROFILE_CATEGORY = ["دسته‌بندی","دسته‌بندی","عضو","عضو"]
COLUMN_NAMES = {
    "receipt":     "رسید",
    "U_code": "کد کاربر",
    "U_refC": "کد معرف",
    "age": "سطح تجربه",
    "city": "شهر",
    "created_at": "تاریخ ایجاد",
    "service_requests": "مشتریان",
    "height": "ظرفیت",
    "id": "شناسه",
    "name": "نام",
    "phone_number": "شماره تلفن",
    "province": "استان",
    "ref_code": "کد ارجاع",
    "profile_category": "پروفایلت",
    "status": "وضعیت",
    "telegram_id": "شناسه تلگرام",
    "username": "نام کاربری",
    "video_message": "پیام ویدیویی",
    "weight": "حجم خدمات"
}

CRYPTO_CURRENCY = {
    "Binance Coin (BNB)": [
        "BEP20 (BSC)",
        "BEP2"
    ],
    "Bitcoin (BTC)": [
        "Bitcoin"
    ],
    "Dogecoin (DOGE)": [
        "Dogecoin"
    ],
    "Ethereum (ETH)": [
        "ERC20 (Ethereum)"
    ],
    "Tether (USDT)": [
        "TRC20 (Tron)",
        "ERC20 (Ethereum)",
        "BEP20 (BSC)"
    ],
    "Tron (TRX)": [
        "TRC20 (Tron)"
    ]
}

CLIENTS_TABLE = "premium_clients"


# DATABASE_URL = "\\\\hpzbook\\share\\database\\database.db"



DATE_FIELDS = [
    "created_at",
    "last_updated",
    "updated_at",
    "timestamp",
    "date",
    "birth_date",
    "start_date",
    "end_date"
]

DAY_NAMES_PERSIAN = {
    "0": "دوشنبه",
    "1": "سه‌شنبه",
    "2": "چهارشنبه",
    "3": "پنج‌شنبه",
    "4": "جمعه",
    "5": "شنبه",
    "6": "یک‌شنبه"
}

DB_LOCATIONS = os.getenv("DB_LOCATIONS", str(Path(__file__).resolve().parents[5] / "resources" / "locations.db"))

# DB_PATH = "\\\\hpzbook\\share\\database\\database.db"

DB_TABLE_NORMAL = "clients"

DB_TABLE_STAFF = "staff"

DB_TABLE_SERVICES = "services"

DB_TABLE_PREMIUM = "premium_clients"

DEFAULT_REASONS = [
    "❗ اطلاعات ناقص",
    "✍ دلیل را بنویسید"
]

DEFAULT_REQUIRED = True

DYNAMIC_NOTIFICATION_CONFIG = {
    "admin.alert": {
        "bot": "admin",
        "table": "admin_alerts",
        "template": {
            "approved": "⚠️ هشدار سیستم: {message}"
        }
    },
    "staff.receipts": {
        "bot": "staff",
        "table": "receipts",
        "template": {
            "approved": "✅ رسید واریزی شما توسط ادمین بررسی و تایید شد.",
            "rejected": "❌ رسید شما رد شد.\n📌 دلیل: {extra}\nلطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید."
        }
    },
    "client.request_drafts": {
        "bot": "client",
        "table": "request_drafts",
        "template": {
            "approved": "✅ سفارش شما توسط کد موردنظر تأیید شده است. لطفاً منتظر تماس بمانید و گوشی خود را در دسترس نگه دارید.",
            "rejected": "❌ درخواست شما رد شد.\nعلت رد درخواست: {extra}"
        }
    },



    "admin.system_update": {
        "bot": "admin",
        "table": "system_updates",
        "template": {
            "approved": "🔄 سیستم به‌روزرسانی شد. جزئیات: {update_details}"
        }
    },
    "client.complaint": {
        "bot": "client",
        "table": "complaints",
        "template": {
            "approved": "✅ شکایت شما ثبت شد. پیگیری: {complaint_id}",
            "rejected": "❌ ثبت شکایت شما با مشکل مواجه شد. دلیل: {extra}"
        }
    },
    "client.feedback": {
        "bot": "client",
        "table": "feedback",
        "template": {
            "approved": "✅ بازخورد شما دریافت شد. ممنون از نظرتان."
        }
    },
    "client.identity_verification_request": {
        "bot": "client",
        "table": "identity_verification_requests",
        "template": {
            "approved": "📋 احراز هویت شما بررسی شد.{extra}",
            "rejected": ""
        }
    },
    "client.order": {
        "bot": "client",
        "table": "orders",
        "template": {
            "approved": "✅ سفارش شما تایید شد. شماره سفارش: {order_number}",
            "blocked": "🚫 سفارش شما مسدود شده است.",
            "rejected": "❌ سفارش شما رد شد. دلیل: {extra}"
        }
    },
    "client.order_approved": {
        "bot": "client",
        "table": "orders",
        "template": {
            "approved": "✅ سفارش شما به تایید نهایی رسید."
        }
    },
    "client.order_cancel": {
        "bot": "client",
        "table": "orders",
        "template": {
            "approved": "ℹ️ سفارش شما با موفقیت لغو شد.",
            "rejected": "❌ لغو سفارش شما ناموفق بود. دلیل: {extra}"
        }
    },
    "client.order_rejected": {
        "bot": "client",
        "table": "orders",
        "template": {
            "rejected": "❌ سفارش شما رد شد. دلیل: {extra}"
        }
    },
    "client.password_reset": {
        "bot": "client",
        "table": "password_resets",
        "template": {
            "approved": "🔑 درخواست تغییر رمز عبور شما تایید شد. کد تغییر: {reset_code}",
            "rejected": "❌ درخواست تغییر رمز عبور شما رد شد. دلیل: {extra}"
        }
    },
    "client.register": {
        "bot": "client",
        "table": "clients",
        "template": {
            "approved": "✅ ثبت‌نام شما با موفقیت انجام شد. کد ورود: {U_code}",
            "blocked": "🚫 ثبت‌نام شما مسدود شده است.",
            "rejected": "❌ ثبت‌نام شما رد شد. دلیل: {extra}"
        }
    },
    "client.premium_request": {
        "bot": "client",
        "table": "client_requests",
        "template": {
            "approved": "✨ درخواست PREMIUM شما تایید شد.",
            "rejected": "❌ درخواست PREMIUM شما رد شد. علت: {extra}"
        }
    },
    "service_requests": {
        "bot": "client",
        "table": "service_requests",
        "template": {
            "approved": "✅ درخواست جذب مشتری شما تایید شد.",
            "rejected": "❌ درخواست جذب مشتری شما رد شد. دلیل: {extra}"
        }
    },
    "staff.ad_request": {
        "bot": "staff",
        "table": "ads",
        "template": {
            "approved": "📢 آگهی شما تایید شد و منتشر خواهد شد.",
            "rejected": "❌ آگهی شما رد شد. دلیل: {extra}"
        }
    },
    "staff.change_password": {
        "bot": "staff",
        "table": "staff",
        "template": {
            "approved": "✅ تغییر رمز عبور شما انجام شد.",
            "rejected": "❌ تغییر رمز عبور شما ناموفق بود. دلیل: {extra}"
        }
    },
    "staff.edit_profile": {
        "bot": "staff",
        "table": "staff",
        "template": {
            "approved": "✅ پروفایل شما با موفقیت به‌روزرسانی شد.",
            "rejected": "❌ به‌روزرسانی پروفایل شما ناموفق بود. دلیل: {extra}"
        }
    },
    "staff.identity_verification_request": {
        "bot": "staff",
        "table": "identity_verification_data",
        "template": {
            "approved": "📋 احراز هویت شما بررسی شد.{extra}",
            "rejected": ""
        }
    },
    "staff.register": {
        "bot": "staff",
        "table": "staff",
        "template": {
            "approved": "✅ ثبت‌نام شما تایید شد.\nکد پرسنلی: `{U_code}`\nبرای دعوت دوستان خود از: `{U_refC}` استفاده کنید",
            "blocked": "🚫 ثبت‌نام شما مسدود شده است.",
            "rejected": "❌ ثبت‌نام شما رد شد. دلیل: {extra}"
        }
    },
    "staff.support": {
        "bot": "staff",
        "table": "support_requests",
        "template": {
            "approved": "✅ درخواست پشتیبانی شما در حال بررسی است.",
            "rejected": "❌ درخواست پشتیبانی شما رد شد. دلیل: {extra}"
        }
    },
    "staff.premium_upgrade": {
        "bot": "staff",
        "table": "premium_staff",
        "template": {
            "approved": "🎉 درخواست ارتقا به PREMIUM شما تایید شد.",
            "rejected": "❌ درخواست PREMIUM شما رد شد. دلیل: {extra}"
        }
    },
    "service.request": {
        "bot": "client",
        "table": "service_requests",
        "template": {
            "approved": "✅ درخواست خدمات شما تایید شد. جزئیات: {service_details}",
            "rejected": "❌ درخواست خدمات شما رد شد. دلیل: {extra}"
        }
    },
    "premium.approval": {
        "bot": "client",
        "table": "premium_requests",
        "template": {
            "approved": "✨ شما به عنوان PREMIUM تایید شدید."
        }
    },
    "premium.request": {
        "bot": "client",
        "table": "premium_requests",
        "template": {
            "approved": "✨ درخواست PREMIUM شما تایید شد.",
            "rejected": "❌ درخواست PREMIUM شما رد شد. دلیل: {extra}"
        }
    }
}

EDITABLE_FIELDS_EXCLUDE = [
    "U_code",
    "phone_number",
    "phone",
    "created_at",
    "last_updated",
    "creation_date",
    "publish_time",
    "PU_code",
    "id",
    "status",
    "telegram_id"
]

EDITABLE_FIELD_TYPES = {
    "PREMIUM_services_price": {
        "type": "int"
    },
    "profile_photos": {
        "type": "media_group",
        "label": "عکس های پروفایل"
    },
    "ad_description": {
        "type": "str"
    },
    "ad_id": {
        "type": "str"
    },
    "ad_photo": {
        "type": "media"
    },
    "video_message":{
        "type": "media"
    },
    "ad_price": {
        "type": "int"
    },
    "address_video": {
        "type": "str"
    },
    "age": {
        "type": "str"
    },
    "appearance": {
        "type": "str"
    },
    "auto_approval_enabled": {
        "type": "str"
    },
    "auto_check_interval": {
        "type": "str"
    },
    "balance_status": {
        "type": "str"
    },
    "base_price": {
        "type": "int"
    },
    "cancel_paid": {
        "type": "str"
    },
    "cancel_reason": {
        "type": "str"
    },
    "card": {
        "type": "str"
    },
    "city": {
        "type": "str"
    },
    "creation_date": {
        "format": "%Y-%m-%d %H:%M",
        "type": "date"
    },
    "created_at": {
        "format": "%Y-%m-%d %H:%M",
        "type": "date"
    },
    "service_requests": {
        "type": "str"
    },
    "description": {
        "type": "str"
    },
    "dispatch_mode": {
        "choices": [
            "در محل",
            "ارائه در محل مشتری"
        ],
        "type": "enum"
    },
    "end_time": {
        "type": "time"
    },
    "extra_time_cost": {
        "type": "str"
    },
    "extra_times": {
        "type": "str"
    },
    "first_name": {
        "type": "str"
    },
    "gallery_photos": {
        "type": "media"
    },
    "health_card": {
        "type": "str"
    },
    "height": {
        "type": "str"
    },
    "id_card": {
        "type": "str"
    },
    "id_card_back": {
        "type": "media"
    },
    "id_card_front": {
        "type": "media"
    },
    "invoice": {
        "type": "str"
    },
    "is_premium": {
        "type": "str"
    },
    "identity_verification_status": {
        "type": "str"
    },
    "last_name": {
        "type": "str"
    },
    "last_updated": {
        "type": "str"
    },
    "level": {
        "type": "str"
    },
    "location": {
        "type": "str"
    },
    "manual_address": {
        "type": "str"
    },
    "name": {
        "type": "str"
    },
    "payment_method": {
        "type": "str"
    },
    "phone": {
        "type": "str"
    },
    "phone_number": {
        "type": "str"
    },
    "prepayment_amount": {
        "type": "int"
    },
    "profile_photo": {
        "type": "media"
    },
    "province": {
        "type": "str"
    },
    "publish_time": {
        "type": "str"
    },
    "razon_reason": {
        "type": "str"
    },
    "ref_code": {
        "type": "str"
    },
    "region": {
        "type": "str"
    },
    "regular_services": {
        "type": "str"
    },
    "regular_services_price": {
        "type": "int"
    },
    "reject_reason": {
        "type": "str"
    },
    "rejection_reason": {
        "type": "str"
    },
    "selected_services": {
        "type": "str"
    },
    "verification_photo_with_id": {
        "type": "media"
    },
    "service_count": {
        "type": "int"
    },
    "service_price": {
        "type": "str"
    },
    "services": {
        "type": "json"
    },
    "services_price": {
        "type": "str"
    },
    "slot_time": {
        "type": "str"
    },
    "start_time": {
        "type": "time"
    },
    "status": {
        "choices": [
            "pending",
            "approved",
            "rejected",
            "cancelled",
            "expired",
            "done",
            "finalized",
            "blocked",
            "draft",
            "waiting_payment",
            "waiting_user",
            "waiting_service",
            "in_progress",
            "failed"
        ],
        "type": "enum"
    },
    "telegram_id": {
        "type": "str"
    },
    "timestamp": {
        "type": "str"
    },
    "token": {
        "type": "str"
    },
    "updated_at": {
        "type": "str"
    },
    "user_name": {
        "type": "str"
    },
    "premium": {
        "type": "bool"
    },
    "premium_services": {
        "type": "json"
    },
    "premium_services_price": {
        "type": "int"
    },
    "visit_client_home": {
        "type": "str"
    },
    "wallet": {
        "type": "str"
    },
    "wallet_network": {
        "type": "str"
    },
    "weight": {
        "type": "str"
    }
}

EMOJI = {
    "edit": "✏️",
    "key": "🔑",
    "media": "🖼️"
}

FIELD_PREFIX = "field_"

FILTER_CONFIG = {
    "age": {
        "emoji": "📊",
        "label": "📊 سطح تجربه",
        "range": {
            "max": 80,
            "min": 20,
            "step": 10
        },
        "type": "range"
    },
    "appearance": {
        "emoji": "🧍‍♂️",
        "label": "🧍‍♂️ سبک خدمت",
        "options": [
            "استاندارد",
            "اقتصادی",
            "ویژه",
            "سازمانی",
            "تخصصی",
            "سفارشی"
        ],
        "type": "checkbox"
    },
    "dispatch_mode": {
        "emoji": "🏠",
        "label": "👣 نوع مراجعه",
        "options": [
            "مکان دار",
            "ارائه در محل مشتری"
        ],
        "type": "single_choice"
    },
    "eye_color": {
        "emoji": "👁️",
        "label": "👁️ تخصص اصلی",
        "options": [],
        "type": "checkbox"
    },
    "hair_color": {
        "emoji": "🧩",
        "label": "🧩 روش ارائه",
        "options": [
            "حضوری",
            "آنلاین",
            "ترکیبی",
            "ساعتی",
            "زمان‌بندی‌شده",
            "درخواستی",
            "سفارشی"
        ],
        "type": "checkbox"
    },
    "height": {
        "emoji": "📏",
        "label": "📏 ظرفیت",
        "range": {
            "max": 200,
            "min": 140,
            "step": 20
        },
        "type": "range"
    },
    "service_price": {
        "emoji": "💵",
        "label": "💵 قیمت پایه سرویس",
        "range": {
            "max": 0,
            "min": 0,
            "step": 200000
        },
        "type": "range"
    },
    "services": {
        "emoji": "🛎",
        "label": "🛎 خدمات",
        "options": [],
        "type": "checkbox"
    },
    "skin_color": {
        "emoji": "🎨",
        "label": "🎨 دسته‌بندی خدمات",
        "options": [
            "عمومی",
            "استاندارد",
            "ویژه",
            "حرفه‌ای",
            "سازمانی"
        ],
        "type": "checkbox"
    },
    "weight": {
        "emoji": "⚖️",
        "label": "⚖️ حجم خدمات",
        "range": {
            "max": 100,
            "min": 30,
            "step": 15
        },
        "type": "range"
    }
}

FILTER_PREFIX = "filter_"

FILTER_SEARCH_PREFIX = "filter_search"

IGNORED_COLUMNS_CONFIG = [
    "id",
    "created_at",
    "last_updated"
]

KEYWORD = "آگهی کد کاربر"

IDENTITY_VERIFICATION_FIELD_TYPES = {
    "id_card": "photo",
    "name": "text",
    "phone": "contact",
    "photo_id": "photo",
    "photo_verification_photo": "photo",
    "video_message": "video_note",
    "video_note": "video_note"
}

IDENTITY_VERIFICATION_PROMPTS = {
    "name": "📝 لطفاً نام مستغار خود را وارد کنید:",
    "phone": "📱 لطفاً شماره تلفن خود را ارسال کنید:",
    "photo_id": "🆔 لطفاً تصویر مدرک شناسایی خود را ارسال کنید:",
    "video_message": "📹 لطفاً یک ویدئوی تأیید کوتاه از خود ارسال کنید:"
}

IDENTITY_VERIFICATION_STATUS_ICONS = {
    "approved": "✅",
    "not_submitted": "❔",
    "pending": "⏳",
    "rejected": "❌"
}

MEDIA_FIELDS = {
    
    "verification_photo_1_file_id":"photo",
    "verification_photo_2_file_id":"photo",
    "receipt":"photo",
    "ad_photo": "photo",
    "profile_photos":"media_group",
    "address_video": "video_note",
    "video_file_id": "video_note",
    "animation": "animation",
    "archive_file": "document",
    "attachment_file": "document",
    "attachment_image": "photo",
    "audio_message": "voice",
    "audio_note": "voice",
    "avatar": "photo",
    "banner": "photo",
    "chat_video_note": "video_note",
    "circular_video": "video_note",
    "clip": "video",
    "cover_image": "photo",
    "doc_file": "document",
    "document": "document",
    "file_attachment": "document",
    "gallery_image": "photo",
    "gif": "animation",
    "health_card": "photo",
    "id_card": "photo",
    "id_card_back": "photo",
    "id_card_front": "photo",
    "image": "photo",
    "inline_video_note": "video_note",
    "inline_voice": "voice",
    "intro_video": "video",
    "location": "location",
    "media_video": "video",
    "microphone_audio": "voice",
    "movie": "video",
    "pdf_file": "document",
    "photo": "photo",
    "photo_field": "photo",
    "photo_id": "photo",
    "photo_verification_photo": "photo",
    "picture": "photo",
    "preview_video": "video",
    "profile_pic": "photo",
    "profile_video": "video",
    "recorded_video": "video",
    "recorded_video_note": "video_note",
    "recorded_voice": "voice",
    "round_video": "video_note",
    "verification_photo_video_note": "video_note",
    "verification_photo_with_id": "photo",
    "short_video_note": "video_note",
    "speech_note": "voice",
    "sticker": "sticker",
    "thumbnail": "photo",
    "trailer": "video",
    "uploaded_video": "video",
    "video": "video",
    "video_field": "video",
    "video_message": "video_note",
    "video_note": "video_note",
    "video_note_field": "video_note",
    "video_note_message": "video_note",
    "voice": "voice",
    "voice_clip": "voice",
    "voice_message": "voice",
    "voice_recording": "voice",
    "zip_file": "document"
}

BASE_PRICE_FILTER = [1_500_000 , 3_100_000]

MESSAGES = {
    "pleace_enter_base_price": \
    "💰 لطفاً مبلغ سرویس را وارد کنید:\n" \
    "بین {min_price} تا {max_price} تومان\n\n" \
    "می‌توانید یکی از روش‌های زیر مقدار را بنویسید:\n" \
    "• عدد کامل: ۱۲۰۰۰۰۰\n" \
    "• عدد هزارتایی: ۱۲۰۰\n" \
    "• عدد اعشاری: ۱.۲\n" \
    "در مثال بالا، به هر روشی که وارد کنید\n" \
    "عدد نهایی برابر با یک میلیون و دویست هزار تومان می‌باشد.",
    "invalid_price": \
    "❌ مبلغ نامعتبر است.\n"
    "لطفاً عددی بین {min_price} تا {max_price} تومان وارد کنید\n"
    "و دقت کنید که عدد واردشده مضرب ۱٬۰۰۰ باشد.",

    "Restart_bots": "⚠️ به دلایل فنی، ربات از سمت سرور ریستارت شده است.\n"
    "منوهای داخلی شما نیز به همین دلیل ریست شده‌اند.\n\n"
    "با عرض پوزش از شما کاربر گرامی 🙏\n"
    "لطفاً برای ادامه عملیات:\n\n"
    "🔹 یا از منوی اصلی استفاده کنید\n"
    "🔹 یا با ارسال /start ربات را مجدداً راه‌اندازی کنید\n\n"
    "ℹ️ به همین دلیل ممکن است اختلالاتی ویژه در عملکرد برخی بخش‌ها مشاهده شود.\n"
    "توصیه می‌شود یک‌بار ربات را ریستارت نمایید.",
    "ASK_EXTRA_SLOTS_PROMPT": "⏱ مدت زمان سرویس فعلی: {duration_text}\nآیا نیاز به تایم بیشتری دارید؟\n💸 مبلغ هر اسلات اضافه: {price_str}\nلطفاً در صورت نیاز، تایم‌های دلخواه را انتخاب و سپس تأیید نمایید:",
    "Choice_Favorites": "🎭 لطفاً گزینه‌های سفارشی خود را از منوی زیر انتخاب کنید:",
    "GropAndChannellSettings": "لطفا تظیمات مربوطه را انتخاب کنید",
    "INVALID_INPUT_ERROR": "❌ لطفاً اطلاعات معتبر وارد کنید.",
    "INVALID_PAYMENT_METHOD_ERROR": "❌ لطفاً یکی از گزینه‌های موجود را از بین دکمه‌ها انتخاب کن.",
    "INVALID_SERVICE_SELECTION": "❌ لطفاً یکی از گزینه‌های معتبر را انتخاب کن.",
    "IDENTITY_VERIFICATION_AUTO_COMPLETE_MSG": "✅ مراحل احراز هویت شما به صورت اتوماتیک انجام شد.\nدر حال انتقال به مرحله بعدی...",
    "IDENTITY_VERIFICATION_INCOMPLETE_PROMPT": "🔎 شما هنوز احراز هویت خود را کامل نکرده‌اید.\nمی‌خواید همین الان کاملش کنید تا همیشه راحت باشید؟ 😉",
    "IDENTITY_VERIFICATION_PREMIUM_OFFER_PROMPT": "🔐 برای هر سفارش نیاز به احراز هویت دارید.\nاما می‌تونید همین الان به صورت کاملاً رایگان ویژه بشید و فقط یکبار برای همیشه احراز هویت کنید. 😇",
    "MEDIA_INVALID_ERROR": "❌ مدیا معتبر یافت نشد.",
    "NAME_INVALID_ERROR": "❌ نام باید فقط شامل حروف فارسی یا انگلیسی باشد، بدون عدد یا علامت، و حداکثر ۴ بخش.",
    "NAME_TOO_LONG_ERROR": "❌ نام وارد شده بیش از ۷۲ کاراکتر است.",
    "NO_PAYMENT_METHOD_ERROR": "❌ روش پرداختی برای این آگهی ثبت نشده است.",
    "P_select_Address": "لطفاً آدرس کیف پول را انتخاب کنید:",
    "P_select_network": "🌐 لطفاً یک شبکه انتخاب کنید:",
    "Pchoice_manage_member_m": "یک منو جهت مدیریت اعضا انتخابکنید 🔰",
    "Pchoice_setting_m": "🛠 یک منوی تنظیمات را انتخاب کنید:",
    "Please_enter_Checking_time": "⏱ لطفاً زمان بررسی خودکار درخواست‌ها را بین 5 تا 10100 دقیقه تنظیم کنید!\n📌 در ادامه چند مثال برای راهنمایی آمده است:\n▫️ 1 ساعت = 60 دقیقه\n▫️ 2 ساعت = 120 دقیقه\n▫️ 5 ساعت = 300 دقیقه\n▫️ 10 ساعت = 600 دقیقه\n▫️ 1 روز = 1440 دقیقه\n▫️ 2 روز = 2880 دقیقه\n▫️ 3 روز = 4320 دقیقه\n▫️ 5 روز = 7200 دقیقه\n🔄 10100 دقیقه تقریباً یک هفته است.",
    "BOOKING_SUCCESS_MSG": "✅ رزرو شما با موفقیت ثبت شد!\n🧾 مبلغ کل: {total_price} تومان\nدر اسرع وقت با شما تماس خواهیم گرفت.",
    "SELECT_PAYMENT_METHOD_PROMPT": "💳 لطفاً روش پرداخت مورد نظر را انتخاب کن:",
    "SERVICE_SELECTION_PROMPT": "✅ لطفاً خدمات مورد نظر را انتخاب کن:\n(فقط خدماتی که قیمت دارند نمایش داده می‌شوند)",
    "SUMMARY_PROMPT": "📋 خلاصه درخواست شما:\n🔸 خدمات انتخابی: {services_str}\n🕓 زمان شروع سرویس: {start_time}\n🕔 زمان پایان سرویس: {end_time}\n⏱ مجموع مدت‌زمان سرویس: {duration_str}\n➕ تعداد اسلات‌های اضافه: {num_extra_slots} (هر اسلات: {base_price:,} تومان)\n💰 هزینه خدمات: {services_cost:,} تومان\n🧾 مبلغ کل: {total_price:,} تومان",
    "You_selected_this_w": "🔐 شما آدرس زیر را برای دریافت {coin} در شبکه {net} انتخاب کرده‌اید:\n🔗 آدرس: {address}",
    "accounting_menu": "📊 منوی حسابداری: لطفاً یک گزینه انتخاب کنید.",
    "activity_history_prompt": "🕘 موردی برای مشاهده تاریخچه فعالیت انتخاب کنید:",
    "ad_desc_updated": "✅ متن آگهی با موفقیت بروزرسانی شد.",
    "ad_title_updated": "✅ عنوان آگهی به «{ad_title}» تغییر یافت.",
    "add_rejection_reason_message": "📌 توضیحات دلیل رد را وارد کنید:",
    "add_rejection_reason_title": "📝 عنوان دلیل رد را وارد کنید:",
    "address_confirmed": "✅ آدرس شما ({province}، {city}) ثبت شد.",
    "address_display": "📌 آدرس شما: استان {province}، شهر {city}",
    "admin_added": "✅ مدیر '{username}' با موفقیت اضافه شد!",
    "admin_deleted": "🗑️ مدیر '{username}' با موفقیت حذف شد.",
    "admin_exists": "⚠️ مدیری با این نام کاربری یا شماره تلفن قبلاً موجود است.",
    "admin_not_found": "❌ مدیر یافت نشد.",
    "admin_updated": "✅ مدیر '{username}' با موفقیت به‌روز شد!",
    "ads_confrimed": "✅ آگهی تایید شد و به کانال ارسال گردید.",
    "ads_navigation": "📌 از هر آگهی‌ای که خوشتون اومد، می‌تونید اون رو به لیست علاقه‌مندی‌هاتون اضافه کنید.\n➕ دکمه «افزودن به علاقه‌مندی‌ها» زیر هر آگهی قرار داره.\n\n🔁 برای مرور سایر آگهی‌ها، از دکمه‌های «⬅️ قبلی» و «➡️ بعدی» استفاده کنید.",
    "all_pending_requests": "📌 همه درخواست‌های در انتظار:",
    "apply_filters": "✔️ اعمال فیلترها",
    "auto_approved_threshold": "✅ درخواست شما به صورت خودکار تایید شد (به دلیل رسیدن به آستانه درخواست تنظیم شده).",
    "auto_approved_timer": "✅ درخواست شما به صورت خودکار تایید شد (زمان تایمر از زمان ثبت درخواست گذشته است).",
    "auto_enabled_changed": "✅ وضعیت تایید خودکار برای جدول {table} به {status} تغییر یافت.",
    "auto_help_text": "ℹ️ **راهنما: عملیات خودکار**\n\nتنظیمات تایید خودکار را در اینجا مدیریت کنید! وضعیت را تغییر دهید، آستانه درخواست را تعیین کنید یا تایمر را با استفاده از دکمه‌ها تنظیم کنید.\nبرای بازگشت، از '⬅️ بازگشت به قبلی' یا '🔙 بازگشت به منوی اصلی' استفاده کنید.",
    "auto_settings_for_table": "⚙️ تنظیمات عملیات خودکار برای جدول {table}:",
    "auto_threshold_set": "✅ آستانه درخواست برای تایید خودکار به {threshold} تنظیم شد.",
    "auto_timer_set": "⏱ تایمر تایید خودکار به {timer} دقیقه تنظیم شد.",
    "back_message": "⬅️ به منوی قبلی بازگشت.",
    "back_to_main": "🔙 بازگشت به منوی اصلی.",
    "bank_accounts_menu": "🏦 منوی حساب‌های بانکی: یک گزینه انتخاب کنید.",
    "bot_running": "🤖 ربات در حال اجرا است!",
    "card_added_successfully": "✅ کارت با موفقیت افزوده شد!",
    "card_deleted": "✅ کارت با موفقیت حذف شد.",
    "card_exists": "❌ این شماره کارت قبلاً ثبت شده است.",
    "card_number_updated": "✅ شماره کارت با موفقیت به‌روز شد.",
    "cardholder_name_updated": "✅ نام دارنده کارت با موفقیت به‌روز شد.",
    "categorization_column_set": "✅ ستون دسته‌بندی با موفقیت تنظیم شد: {text}",
    "category_list": "📋 لیست پرسنل «{status_title}»:",
    "changes_saved": "✅ تغییرات با موفقیت ذخیره شد.",
    "choice_a_field_for_edit": "🔧 یکی از فیلدهای زیر را برای ویرایش انتخاب کنید:",
    "choose_admin_to_edit": "✏️ مدیر مورد نظر برای ویرایش را انتخاب کنید:",
    "choose_admin_to_remove": "🗑️ مدیر مورد نظر برای حذف را انتخاب کنید:",
    "choose_area_or_all": "🏙 لطفاً انتخاب کنید:\n📍 انتخاب منطقه خاص\n🌍 یا جستجو در کل شهر",
    "choose_category": "📋 دسته‌بندی '{category}' را انتخاب کنید:",
    "choose_field_to_edit": "✏️ کدام فیلد برای '{username}' را می‌خواهید ویرایش کنید:",
    "choose_filter_value": "🔎 لطفاً مقدار فیلتر را انتخاب کنید:",
    "choose_new_status": "🔄 لطفاً وضعیت جدید را انتخاب کنید:",
    "choose_request": "📝 لطفاً یک درخواست را انتخاب کنید:",
    "choose_request_category": "📋 لطفاً دسته‌بندی مورد نظر را انتخاب کنید:",
    "choose_skill": "🛠 لطفاً مهارت را انتخاب کنید:",
    "choose_status": "لطفاً وضعیت مورد نظر را انتخاب کنید:",
    "choose_table": "📋 لطفاً نوع درخواست را انتخاب کنید:",
    "choose_user": "لطفاً مشتری مورد نظر را انتخاب کنید:",
    "clear_keyboard": "",
    "prompt_manual_time": "⌨️ لطفاً زمان را در فرمت صحیح ارسال کنید (مثلاً: ۱۴:۳۰)",

    "code_menu_prompt": "🌐 لطفاً برای مشاهده کدها، موقعیت مکانی خود را انتخاب کنید.",
    "codes_list_info": "📋 لیست کدهای پیدا شده (صفحه {current} از {total})",
    "configure_sorting": "⚙️ نوع درخواست را برای پیکربندی مرتب‌سازی و دسته‌بندی انتخاب کنید:",
    "confirm_address_prompt": "❓ آیا این آدرس صحیح است؟",
    "confirm_delete": "❓ آیا مطمئن هستید که می‌خواهید این مشتری را حذف کنید؟",
    "crypto_wallets_menu": "💰 منوی کیف پول‌های کریپتو: یک گزینه انتخاب کنید.",
    "custom_reason_lost": "❌ خطا: دلیل سفارشی از دست رفت. لطفاً دوباره تلاش کنید.",
    "data_format_error": "❌ فرمت داده مشکل دارد و قابل ویرایش نیست.",
    "default_card_selected": "✅ کارت پیش‌فرض با موفقیت تنظیم شد!",
    "default_wallet_selected": "✅ کیف پول پیش‌فرض با موفقیت تنظیم شد!",
    "delete_rejection_reason_select": "🗑️ دلیل مورد نظر برای حذف را انتخاب کنید:",
    "display_columns_set": "✅ ستون‌های نمایش تنظیم شدند: {columns}",
    "do_you_want_set_default": "🔐 آیا می‌خواهید این کیف پول را برای دریافت پرداخت‌ها به عنوان پیش‌فرض تنظیم کنید؟",
    "do_you_want_set_default_card": "❓ آیا می‌خواهید این کارت را به عنوان کارت پیش‌فرض تنظیم کنید؟",
    "doyowanechange": "آیا میخواهید این مدیر را فعال کنید؟",
    "edit_rejection_reason_select": "📌 دلیل مورد نظر برای ویرایش را انتخاب کنید:",
    "edit_text_prompt": "✏️ مقدار فعلی: {current_value}\n\nلطفاً مقدار جدید را وارد کنید:",
    "enter_admin_username": "🆔 لطفا نام کاربری مدیر را وارد کنید \n(@UserName)",
    "enter_card_number": "🔢 لطفاً شماره 16 رقمی کارت را وارد کنید:",
    "enter_cardholder_name": "👤 لطفاً نام دارنده کارت را وارد کنید:",
    "enter_categorization": "📋 ستون دسته‌بندی را وارد کنید (برای هیچ چیزی خالی بگذارید) - موجود: {columns}:",
    "enter_custom_reason": "✍ لطفاً دلیل سفارشی خود را وارد کنید:",
    "enter_ignored_columns": "🚫 لطفاً ستون‌های نادیده گرفته شده را به صورت جداشده با کاما وارد کنید:",
    "enter_last_name": "📝 لطفاً نام خانوادگی مدیر را وارد کنید:",
    "enter_message_text": "💌 لطفاً پیام مورد نظر خود را برای پرسنل تایپ کنید:",
    "enter_name": "📝 لطفاً نام مدیر را وارد کنید:",
    "enter_new_ad_desc": "📄 لطفاً متن جدید آگهی را وارد کنید:",
    "enter_new_ad_title": "📝 لطفاً عنوان جدید آگهی را وارد کنید:",
    "enter_new_card_number": "🔢 شماره کارت جدید را وارد کنید:",
    "enter_new_cardholder_name": "👤 نام دارنده کارت جدید را وارد کنید:",
    "enter_new_crypto_wallet": "💰 ارز دیجیتال جدید را انتخاب کنید:",
    "enter_new_name": "✏️ لطفاً نام جدید را وارد کنید:",
    "enter_new_network_wallet": "🌐 شبکه جدید را انتخاب کنید:",
    "enter_new_phone_number": "لطفاً شماره تلفن جدید را وارد کنید:",
    "enter_new_reason": "✍ لطفاً دلیل جدید را وارد کنید:",
    "enter_new_username": "💬 لطفاً آیدی جدید را وارد کنید:",
    "enter_new_value": "🔄 مقدار جدید برای '{field}' را وارد کنید:",
    "enter_new_wallet_address": "📇 آدرس جدید کیف پول را وارد کنید:",
    "enter_new_wallet_address_currency": "📇 آدرس جدید کیف پول را وارد کنید:",
    "enter_new_wallet_address_network": "📇 آدرس جدید کیف پول را وارد کنید:",
    "enter_number": "🔢 عدد جدید برای «{field}» را وارد کنید:",
    "enter_phone_number": "📞 لطفاً شماره تلفن مدیر را وارد کنید:",
    "enter_rejection_reason": "✍ لطفاً دلیل رد را وارد کنید:",
    "enter_request_details": "لطفاً عبارت جستجو را وارد کنید:",
    "enter_request_overview": "📝 لطفاً متن نمای کلی درخواست را وارد کنید:",
    "enter_search": "🔎 لطفاً نام یا آیدی پرسنل را وارد کنید:",
    "enter_sorting": "🔧 ستون‌های مرتب‌سازی (با کاما جدا شده) را وارد کنید - موجود: {columns}:",
    "enter_text": "🔡 مقدار جدید برای «{field}» را وارد کنید:",
    "enter_threshold": "لطفاً تعداد درخواست‌های مورد نیاز برای تایید خودکار را وارد کنید:",
    "enter_timer": "لطفاً مدت زمان تایمر (به فرمت HH:MM یا به دقیقه) را وارد کنید:",
    "enter_wallet_address": "📇 آدرس کیف پول را وارد کنید:",
    "error": "❌ خطایی رخ داده است. لطفاً دوباره تلاش کنید.",
    "error_adding_card": "❌ خطا در افزودن کارت. لطفاً دوباره تلاش کنید.",
    "error_adding_wallet": "❌ خطا در افزودن کیف پول. لطفاً دوباره تلاش کنید.",
    "error_deleting_wallet": "❌ خطا در حذف کیف پول.",
    "error_displaying_details": "❌ خطا در نمایش جزئیات.",
    "error_displaying_reasons": "❌ خطا در نمایش دلایل.",
    "error_invalid_option": "⚠️ گزینهٔ نامعتبر است.\nلطفاً یکی از گزینه‌های منو را انتخاب کنید.",
    "error_invalid_time": "⚠️ ساعت واردشده نامعتبر است.\n⏱ لطفاً یک ساعت با فرمت `HH:MM` وارد کنید که حداقل %(min)d دقیقه جلوتر باشد.",
    "error_processing_action": "❌ خطا در پردازش عملیات لطفا دوباره تلاش کنید🔁.",
    "error_selecting_default": "❌ خطا در تنظیم کارت پیش‌فرض.",
    "error_upsocial_service_card": "❌ خطا در به‌روز کردن کارت. لطفاً دوباره تلاش کنید.",
    "error_upsocial_service_wallet": "❌ خطا در به‌روز کردن کیف پول.",
    "favorites_list_message": "⭐ لیست آگهی‌های علاقه‌مندیتان:",
    "file_not_received": "❌ فایل دریافت نشد.",
    "filter_prompt": "🛠 لطفاً فیلتر مورد نظر را انتخاب کنید:",
    "filtered_list_info": "نمایش نتایج: صفحه {current} از {total}",
    "global_interval_set": "⏱ فاصله زمانی بررسی جهانی به {interval} دقیقه تنظیم شد.",
    "goto_permanent_codes": "📌 به بخش نمایش کدهای دائم منتقل شدید.",
    "goto_show_codes": "🧾 به بخش نمایش کدها منتقل شدید.",
    "goto_today_codes": "📅 به بخش نمایش کدهای امروز منتقل شدید.",
    "goto_premium": "👑 به بخش مشتریان ویژه منتقل شدید.",
    "gps_prompt": "📍 برای تعیین دقیق‌تر محل شما، آیا تمایلی به ارسال موقعیت مکانی خود دارید؟\n(اختیاری)",
    "help_accounting": "❓ **راهنما: حسابداری**\n\nاین بخش به شما امکان مدیریت حساب‌های بانکی و کیف پول‌های کریپتو را می‌دهد. می‌توانید اضافه، ویرایش، حذف یا تنظیم پیش‌فرض را انجام دهید تا گزینه‌های پرداخت شما به‌روز باشند.\n\n### مثال ساده:\nبرای افزودن کارت بانکی، به بخش 'حساب‌های بانکی' بروید، روی 'افزودن کارت' کلیک کنید و جزئیات را وارد کنید!",
    "help_ads": "📢 **راهنما: تبلیغات**\n\nدر این بخش می‌توانید آگهی‌هایی برای خدمات خود ایجاد کنید تا دیگران آن را ببینند و با شما تماس بگیرند. این مانند درج آگهی در روزنامه است!\n\n### در اینجا چه کاری می‌توانید انجام دهید؟\n- **🆕 ایجاد آگهی جدید**: آگهی جدیدی ایجاد کنید.\n- **✏️ ویرایش آگهی**: در صورت نیاز، آگهی را تغییر دهید.\n- **🗑️ حذف آگهی**: آگهی‌هایی که دیگر نیاز ندارید را حذف کنید.\n\n### مثال ساده:\nمی‌توانید آگهی‌ای ایجاد کنید که عنوان آن 'طراحی وب مقرون به صرفه' باشد و نحوه کار خود را توضیح دهید.",
    "help_bank_accounts": "📘 **راهنما: مدیریت حساب‌های بانکی**\n\nسلام! این بخش جایی است که می‌توانید حساب‌های بانکی خود را مدیریت کنید. آن را مانند یک دفترچه دیجیتال برای کارت‌های بانکی خود در نظر بگیرید که تنها برای مدیران قابل مشاهده است. این به شما کمک می‌کند تا به راحتی پرداخت‌ها را دریافت کنید.\n\n### در اینجا چه کاری می‌توانید انجام دهید؟\n- **🆕 افزودن کارت جدید**: یک کارت بانکی جدید اضافه کنید. برای مثال، اگر کارت جدیدی دریافت کرده‌اید، شماره آن را وارد کنید.\n- **✏️ ویرایش کارت**: در صورت تغییر شماره کارت یا نام دارنده، آن را به‌روز کنید.\n- **🗑️ حذف کارت**: کارت‌هایی که دیگر استفاده نمی‌کنید را حذف کنید.\n- **⭐ تنظیم کارت پیش‌فرض**: تعیین کنید کدام کارت به عنوان کارت اصلی برای دریافت پرداخت‌ها باشد.\n\n### مثال ساده:\nبرای افزودن کارت جدید، کافیست بر روی 'افزودن کارت' کلیک کنید، شماره 16 رقمی کارت را وارد کنید و نام دارنده کارت را وارد کنید. همین!",
    "help_crypto_wallets": "💰 **راهنما: مدیریت کیف پول‌های کریپتو**\n\nدر اینجا می‌توانید کیف پول‌های کریپتو خود را مدیریت کنید. کیف پول مانند یک حساب بانکی برای ارزهای دیجیتال مانند تتر یا بیت‌کوین است. شما می‌توانید ارز دیجیتال را ارسال یا دریافت کنید.\n\n### در اینجا چه کاری می‌توانید انجام دهید؟\n- **🆕 افزودن کیف پول**: یک کیف پول کریپتو جدید اضافه کنید.\n- **✏️ ویرایش کیف پول**: جزئیات کیف پول را تغییر دهید.\n- **🗑️ حذف کیف پول**: کیف پولی که دیگر نیاز ندارید را حذف کنید.\n- **⭐ تنظیم کیف پول پیش‌فرض**: تعیین کنید کدام کیف پول برای دریافت ارز دیجیتال اصلی باشد.\n\n### مثال ساده:\nاگر می‌خواهید یک کیف پول تتر در شبکه TRON (TRC20) اضافه کنید، بر روی 'افزودن کیف پول' کلیک کنید، تتر را انتخاب کنید، TRC20 را برگزینید و آدرس کیف پول خود را وارد کنید. تمام!",
    "help_edit_cards": "✏️ **راهنما: ویرایش کارت‌های بانکی**\n\nگاهی جزئیات کارت شما تغییر می‌کند، مانند شماره کارت یا نام دارنده کارت. در اینجا می‌توانید این جزئیات را به‌روز کنید.\n\n### چگونه انجام شود؟\n- روی 'ویرایش کارت' کلیک کنید.\n- کارت مورد نظر خود را انتخاب کنید.\n- انتخاب کنید که چه چیزی را می‌خواهید ویرایش کنید (شماره کارت یا نام).\n- اطلاعات جدید را وارد کنید.\n\n### مثال ساده:\nاگر شماره کارت شما تغییر کرده است، به این بخش بروید، کارت را پیدا کنید و شماره جدید را وارد کنید. خیلی ساده!",
    "help_identity_verification": "🆔 **راهنما: شناسایی مشتری (IDENTITY_VERIFICATION)**\n\nIDENTITY_VERIFICATION روشی است که ما هویت شما را تأیید می‌کنیم تا اطمینان حاصل شود که حساب شما امن است و فقط شما به آن دسترسی دارید.\n\n### چه چیزی لازم است؟\n- **📷 عکس شناسنامه یا گذرنامه**: عکسی واضح از مدرک شناسایی شما.\n- **🤳 سلفی با مدرک**: عکسی از خودتان که مدرک شناسایی را در دست دارید.\n\n### چرا این کار را انجام می‌دهیم؟\n- برای اطمینان از اینکه حساب شما متعلق به شماست.\n- برای مطابقت با الزامات قانونی.\n\n### مثال ساده:\nمانند زمانی که حساب بانکی افتتاح می‌کنید، مدرک شناسایی خود را نشان می‌دهید. در اینجا، عکس مدرک شناسایی و سلفی با آن را بارگذاری می‌کنید تا هویت خود را تأیید کنید.",
    "help_payment_methods": "💳 **راهنما: روش‌های پرداخت**\n\nدر این بخش می‌توانید مشخص کنید مشتریان چگونه به شما پرداخت کنند، مانند کارت بانکی یا کیف پول کریپتو. این امر دریافت پول را برای مشتریان آسان‌تر می‌کند.\n\n### چرا این موضوع اهمیت دارد؟\n- مشتریان می‌توانند روشی را که برایشان مناسب‌تر است انتخاب کنند.\n- می‌توانید گزینه‌های متعددی را ارائه دهید تا نیازهای همه برآورده شود.\n\n### مثال ساده:\nاگر هم کارت بانکی و هم کیف پول تتر دارید، می‌توانید هر دو را اینجا فهرست کنید تا مشتریان روش مورد نظر خود را انتخاب کنند.",
    "help_registration": "📝 **راهنما: ثبت نام**\n\nبرای استفاده از خدمات ما، ابتدا باید ثبت نام کنید. این به معنای ایجاد یک حساب با جزئیات شماست.\n\n### چرا ثبت نام کنیم؟\n- برای دسترسی به تمامی خدمات ما.\n- تا بدانیم شما کی هستید و بتوانیم حساب شما را امن نگه داریم.\n\n### چگونه ثبت نام کنیم؟\n- نام کامل خود را وارد کنید.\n- ایمیل خود را ارائه دهید.\n- شماره تلفن خود را وارد کنید.\n\n### مثال ساده:\nمانند ثبت نام در یک باشگاه، نام و شماره خود را ارائه می‌دهید تا عضو شوید. در اینجا نیز همین کار را انجام دهید!",
    "help_requests": "📬 **راهنما: درخواست‌ها**\n\nدر این بخش می‌توانید درخواست‌های مشتریانی که به خدمات شما علاقه‌مند هستند را مشاهده و مدیریت کنید.\n\n### در اینجا چه کاری می‌توانید انجام دهید؟\n- **📥 مشاهده درخواست‌ها**: ببینید چه کسی چه درخواستی دارد.\n- **✅ پذیرش درخواست**: اگر قادر به انجام کار هستید، درخواست را تایید کنید.\n- **❌ رد درخواست**: اگر نمی‌توانید، درخواست را رد کنید.\n\n### مثال ساده:\nاگر کسی درخواست طراحی وبسایت داشته باشد، می‌توانید درخواست او را مشاهده کرده و در صورت در دسترس بودن بگویید 'بله، انجام می‌دهم!'",
    "help_select_network": "🌐 **راهنما: انتخاب شبکه برای ارزهای دیجیتال**\n\nهنگام کار با ارزهای دیجیتال، باید 'راه' مناسب برای تراکنش خود را انتخاب کنید. این راه به عنوان شبکه شناخته می‌شود. هر شبکه دارای سرعت و هزینه‌های متفاوتی است، مانند انتخاب بین پست عادی یا پست اکسپرس!\n\n### چرا انتخاب شبکه مناسب اهمیت دارد؟\n- هر شبکه به صورت متفاوت عمل می‌کند: برای مثال، TRC20 ارزان‌تر و سریع‌تر است، در حالی که ERC20 گران‌تر و کندتر است.\n- اگر شبکه اشتباهی را انتخاب کنید، مانند فرستادن پول به مسیر اشتباه است — ممکن است آن را از دست بدهید!\n\n### مثال ساده:\nمی‌توانید تتر (USDT) را از طریق TRC20 ارسال کنید، که سریع و کم‌هزینه است. اگر به اشتباه ERC20 را انتخاب کنید، ممکن است پول خود را از دست بدهید. پس دقت کنید!",
    "help_services": "🛠️ **راهنما: خدمات**\n\nدر این بخش می‌توانید خدماتی که ارائه می‌دهید مانند طراحی وب یا ترجمه را فهرست کنید. این به دیگران نشان می‌دهد که چه کاری انجام می‌دهید.\n\n### در اینجا چه کاری می‌توانید انجام دهید؟\n- **🆕 افزودن سرویس جدید**: سرویس جدیدی که ارائه می‌دهید را اضافه کنید.\n- **✏️ ویرایش سرویس**: در صورت تغییر جزئیات، سرویس را به‌روز کنید.\n- **🗑️ حذف سرویس**: سرویس‌هایی که دیگر ارائه نمی‌دهید را حذف کنید.\n\n### مثال ساده:\nاگر طراح وب هستید، می‌توانید خدمتی مانند 'طراحی وب‌سایت شرکتی' را اضافه کرده و توضیح دهید چه کاری انجام می‌دهید.",
    "help_set_categorization": "ℹ️ **راهنما: تنظیم ستون دسته‌بندی**\n\nدر اینجا تصمیم می‌گیرید چگونه درخواست‌های خود را گروه‌بندی کنید (مثلاً بر اساس وضعیت یا استان). فقط ستون‌هایی که نادیده گرفته نشده‌اند قابل استفاده هستند.\n\n### مثال ساده:\nستون 'استان' را برای مرتب‌سازی درخواست‌ها بر اساس موقعیت انتخاب کنید!",
    "help_set_display_columns": "ℹ️ **راهنما: تنظیم ستون‌های نمایش**\n\nتا 3 ستون را برای نمایش در نمای اولیه درخواست‌ها انتخاب کنید. این کار صفحه را ساده و واضح نگه می‌دارد.\n\n### مثال ساده:\nستون‌های 'نام'، 'سطح تجربه' و 'شهر' را انتخاب کنید تا جزئیات آن‌ها بلافاصله نمایش داده شوند!",
    "help_set_ignored_columns": "ℹ️ **راهنما: تنظیم ستون‌های نادیده گرفته شده**\n\nستون‌هایی را که می‌خواهید در تمام نماهای درخواست پنهان شوند انتخاب کنید تا صفحه مرتب بماند.\n\n### مثال ساده:\nستون 'تاریخ ایجاد' را نادیده بگیرید اگر نیازی به مشاهده زمان‌بندی ندارید!",
    "help_set_request_details": "ℹ️ **راهنما: تنظیم جزئیات درخواست**\n\nاین متن زمانی که روی 'مشاهده جزئیات بیشتر' کلیک می‌کنید نمایش داده می‌شود.\n\n### مثال ساده:\nآن را به 'تلفن: {phone_number}' تنظیم کنید تا در صورت نیاز اطلاعات تماس را مشاهده کنید!",
    "help_set_request_overview": "ℹ️ **راهنما: تنظیم نمای کلی درخواست**\n\nاین متن کوتاه است که برای هر درخواست در نگاه اول نمایش داده می‌شود.\n\n### مثال ساده:\nآن را به 'نام: {name}' تنظیم کنید تا به سرعت ببینید چه کسی درخواست کرده است!",
    "help_table_settings": "ℹ️ **راهنما: تنظیمات درخواست**\n\nاین بخش به شما امکان سفارشی‌سازی نحوه نمایش و مدیریت درخواست‌ها را می‌دهد. شما می‌توانید دسته‌بندی‌ها را تنظیم کنید، ستون‌های نمایش را انتخاب کنید و جزئیاتی که باید نادیده گرفته شوند را تعیین کنید.\n\n### مثال ساده:\nبرای نمایش فقط 'نام' و 'وضعیت' در درخواست‌ها، به 'تنظیم ستون‌های نمایش' بروید و آن دو را انتخاب کنید!",
    "help_text": "ℹ️ این ربات به شما در مدیریت درخواست‌ها و تنظیمات به راحتی کمک می‌کند!",
    "ignored_columns_set": "✅ ستون‌های نادیده گرفته شده تنظیم شدند: {columns}",
    "invalid_card_number": "❌ شماره کارت نامعتبر است. لطفاً 16 رقم وارد کنید.",
    "invalid_choice": "❌ گزینه نامعتبر. لطفاً گزینه معتبر را انتخاب کنید.",
    "invalid_city": "⚠️ شهر وارد شده معتبر نیست.",
    "invalid_column": "❌ ستون نامعتبر: {column}",
    "invalid_contact": "❗ لطفاً شماره تماس خود را با دکمه مخصوص ارسال کنید.",
    "invalid_crypto": "❌ ارز دیجیتال انتخاب شده نامعتبر است.",
    "invalid_details": "⚠️ جزئیات غیرفعال شده‌اند.",
    "invalid_info": "❌ اطلاعات نامعتبر.",
    "invalid_input": "❌ ورودی نامعتبر. لطفاً دوباره تلاش کنید.",
    "invalid_interval": "❌ ورودی نامعتبر. مقدار باید بین 5 تا 10100 دقیقه باشد.",
    "invalid_key": "❌ کلید نامعتبر است.",
    "invalid_name": "❌ نام نامعتبر! فقط از حروف (انگلیسی یا فارسی) استفاده کنید.",
    "invalid_network": "❌ شبکه انتخاب شده نامعتبر است.",
    "invalid_number": "⚠️ لطفاً یک عدد معتبر وارد کنید.",
    "invalid_option": "❗️ گزینه نامعتبر است. لطفاً یکی از گزینه‌های موجود را انتخاب کنید.",
    "invalid_phone": "⚠️ شماره تلفن باید با 09 آغاز شود.",
    "invalid_photo": "❌ لطفاً یک تصویر معتبر ارسال کنید.",
    "invalid_province": "⚠️ استان وارد شده معتبر نیست.",
    "invalid_region_selection": "❌ لطفاً یکی از مناطق مشخص شده را انتخاب کن.",
    "invalid_selection": "❌ انتخاب نامعتبر. لطفاً دوباره تلاش کنید.",
    "invalid_table": "❌ جدول انتخاب شده نامعتبر است.",
    "invalid_user_details": "❌ جزئیات کاربر نامعتبر است.",
    "invalid_username": "❌ نام کاربری نامعتبر! از نام کاربری معتبر تلگرام استفاده کنید (مثلاً @username).",
    "invalid_video": "❌ لطفاً یک ویدئوی معتبر ارسال کنید.",
    "invalid_wallet_address": "❌ آدرس کیف پول نامعتبر است.",
    "json_invalid_format": "❌ فرمت JSON نامعتبر است. لطفاً دوباره امتحان کنید.",
    "json_key_prompt": "🧭 لطفاً یکی از کلیدهای زیر را برای ویرایش انتخاب کنید:",
    "identity_verification_complete": "✅ احراز هویت شما با موفقیت ثبت شد. در انتظار بررسی توسط ادمین هستید.",
    "identity_verification_completed_success": "✅ احراز هویت با موفقیت انجام شد.",
    "identity_verification_incomplete_prompt": "🛂 برخی مدارک شما هنوز کامل نشده.\n\nآیا می‌خواهید مدارک ناقص را تکمیل کنید؟",
    "identity_verification_now_prompt": "🛂 شما PREMIUM هستید ولی هنوز احراز هویت نکردید.\n\nالان می‌خواهید احراز هویت کنید؟",
    "identity_verification_progress": "🛂 وضعیت احراز هویت: {approved} از {total} مورد تأیید شده ({percent:.0f}٪)",
    "identity_verification_required_info_missing": "⚠️ اطلاعات کافی برای ثبت سفارش وجود ندارد.",
    "identity_verification_step_skipped": "⏭️ این مرحله از احراز هویت رد شد.",
    "link_expired": "🚫 لینک منقضی شده است.",
    "loc_address": "📍 **بررسی مکان خودکار**\n\n🗺 آدرس از مکان:\n🌍 استان: {pro}\n🏙 شهر: {cit}\n📌 منطقه: {are}",
    "log_delete_message": "🗑 پیام آگهی #{ad_id} حذف شد (تمام اسلات‌ها پر شدند).",
    "log_error_edit": "❗ خطا در ویرایش یا حذف پیام آگهی",
    "log_update_buttons": "🎯 دکمه‌های آگهی #{ad_id} بروزرسانی شدند.",
    "login_prompt": "🔑 لطفاً اطلاعات ورود خود را وارد کنید:",
    "main_menu": "🛠 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "main_menu_message": "لطفاً یک گزینه از منوی زیر انتخاب کنید:",
    "main_menu_welcome": "👋 به منوی اصلی خوش آمدید.",
    "manage_reasons": "⚙️ لطفاً یک گزینه برای مدیریت دلایل رد انتخاب کنید:",
    "manage_requests_activated": "📌 مدیریت درخواست فعال شد!",
    "message_sent": "📬 پیام با موفقیت ارسال شد. ✅",
    "name_updated": "✅ نام پرسنل به «{name}» بروزرسانی شد.",
    "no_ads": "⚠️ امروز هیچ آگهی‌ای یافت نشد.",
    "no_areas_found": "❗️ در این شهر منطقه‌ای یافت نشد.",
    "no_cards_found": "⚠️ هیچ کارتی یافت نشد.",
    "no_codes": "❗️ هیچ کدی مطابق با فیلترهای انتخابی یافت نشد.",
    "no_codes_to_this_city_today": "امروز هیچ آگهی‌ای برای این شهر ثبت نشده 😕 لطفاً شهر یا منطقه دیگه‌ای رو امتحان کن.",
    "no_fields_to_edit": "✏️ موردی برای ویرایش وجود ندارد. از بخش «تکمیل پروفایل» استفاده کنید.",
    "no_pending_requests": "📭 هیچ درخواست در انتظاری وجود ندارد",
    "no_staff": "⚠️ هیچ پرسنلی برای نمایش یافت نشد.",
    "no_provinces": "⛔ دریافت لیست استان‌ها ممکن نیست.",
    "no_reasons_available": "⚠️ هیچ دلیلی برای رد موجود نیست.",
    "no_requests": "هیچ مشتری با وضعیت {status} یافت نشد.",
    "not_requests_found": "هیچ درخواستی یافت نشد",
    "no_requests_24h": "در ۲۴ ساعت گذشته درخواستی ثبت نشده است.",
    "no_requests_for_day": "📭 در آن روز درخواستی ثبت نشده است.",
    "no_requests_for_skill": "🚫 هیچ درخواستی برای این مهارت یافت نشد.",
    "no_requests_today": "📭 امروز درخواستی ثبت نکرده‌اید.",
    "no_results": "🚫 نتیجه‌ای برای جستجو یافت نشد.",
    "no_wallets_found": "⚠️ هیچ کیف پولی یافت نشد.",
    "not_found_address": "❌ برای {coin} در شبکه {net} آدرسی یافت نشد.",
    "not_found_network": "❌ برای {coin} شبکه‌ای یافت نشد.",
    "not_premium": "⚠️ شما هنوز به عنوان مشتری PREMIUM تایید نشده‌اید.",
    "notif_approved_to_admins": "✅ {count} درخواست در جدول {table} به صورت خودکار تایید شدند.",
    "page_info": "📄 صفحه {current} از {total}",
    "permanent_code_menu_prompt": "📌 برای مشاهده کدهای دائم، موقعیت مکانی را انتخاب کنید.",
    "person_detail": "👤 ارائه‌دهنده:\n🆔 کد: {id}\n👥 نام: {name}\n💬 آیدی: {username}\n📄 وضعیت: {status_title}\n\n📢 آگهی:\n🏷 عنوان: {ad_title}\n📝 متن: {ad_desc}",
    "please_choice_a_menu_for_Edit_showing": "⚙️ لطفاً یک منوی زیر را برای ویرایش تنظیمات انتخاب کنید:\n📌 مثال: برای تنظیم تنظیمات 'پرسنل'، روی دکمه 'پرسنل' کلیک کنید.",
    "please_fisrt_register": "❗ شما ویژه نیستید.\n👑 همین الان به‌صورت کاملاً رایگان PREMIUM شوید!",
    "please_send_field": "📝 لطفاً {prompt} را وارد کنید:",
    "please_send_new_file_for_edit": "📤 لطفاً فایل جدید برای «{label}» را ارسال کنید:",
    "please_send_yor_id_photo": "🆔 لطفاً تصویر مدرک شناسایی رو بفرست:",
    "please_send_your_phone": "📱 لطفاً شماره موبایل خود را ارسال کنید:",
    "plese_send_video_note": "📹 لطفاً ویدئو نوت ارسال کن:",
    "profile_complete": "✅ پروفایل شما کامل است.",
    "profile_menu": "👤 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "prompt_list_time": "🕑 لطفاً یک گزینه از لیست زیر انتخاب کنید تا آگهی در آن ساعت منتشر شود:",
    "prompt_manual_time": "🕓 لطفاً ساعت دلخواه خود را وارد کنید.\n📌 فرمت: `HH:MM`\n⏳ زمان انتخابی باید حداقل ۵ دقیقه از زمان فعلی جلوتر باشد\n مثال 12:45",
    "prompt_publish_time": "📅 لطفاً زمان انتشار آگهی را انتخاب کنید:",
    "publish_immediate": "✅ آگهی شماره #%(id)s بدون زمان‌بندی و به‌صورت فوری منتشر شد. 🚀",
    "publish_scheduled": "✅ آگهی شماره #%(id)s با موفقیت زمان‌بندی شد.\n🕒 زمان انتشار: %(time)s",
    "reason_added": "✅ دلیل '{reason}' با موفقیت اضافه شد!",
    "reason_deleted": "🗑️ دلیل '{reason}' با موفقیت حذف شد.",
    "reason_exists": "⚠️ این دلیل قبلاً موجود است.",
    "reason_not_found": "❌ دلیل یافت نشد.",
    "reason_too_short": "❌ دلیل باید حداقل 3 کاراکتر باشد. دوباره تلاش کنید:",
    "reason_updated": "✅ دلیل از '{old_reason}' به '{new_reason}' به‌روز شد.",
    "registering_staff": "📋 در حال ثبت پرسنل...",
    "registration_prompt": "📋 لطفاً اطلاعات اولیه خود را برای ثبت‌نام ارسال کنید.",
    "rejection_stopped": "⏹ روند رد درخواست متوقف شد.",
    "reports_view": "📊 مشاهده گزارش‌های مالی و آماری",
    "request_accepted_admin": "✅ درخواست با موفقیت تایید شد!",
    "request_accepted_user": "✅ درخواست شما تایید شد!",
    "request_approved": "✅ درخواست شما تأیید شد.",
    "request_approved_clients": "✅ درخواست شما توسط ادمین بررسی و تأیید شد.\n📬 اطلاعات سفارش برای پرسنل ارسال شده است.\n⏳ لطفاً منتظر پاسخ نهایی از طرف پرسنل بمانید.",
    "request_approved_staff": "🆕 یک سفارش جدید برای شما ثبت شده است.\n📥 این درخواست توسط ادمین بررسی و تأیید شده است.\n🔎 لطفاً هرچه سریع‌تر آن را بررسی و پاسخ دهید.",
    "request_blocked": "🚫 درخواست با موفقیت مسدود شد.",
    "request_canceled": "❌ عملیات لغو شد.",
    "request_deleted": "✅ درخواست با موفقیت حذف شد.",
    "request_details": "کلیات درخواست:\n{details}",
    "request_details_set": "✅ جزئیات درخواست تنظیم شد: {text}",
    "request_details_set_columns": "✅ تنظیمات جزئیات درخواست ذخیره شد: {columns}",
    "request_failure": "⚠️ خطا در ثبت درخواست. لطفاً مجدد تلاش کنید.",
    "request_forward_success": "📤 درخواست شما به پرسنل ارسال شد.",
    "request_info_absent": "❌ اطلاعات درخواست موجود نیست.",
    "request_not_found": "❌ درخواست یافت نشد.",
    "request_overview_set": "✅ نمای کلی درخواست تنظیم شد: {text}",
    "request_overview_set_columns": "✅ تنظیمات نمای کلی درخواست ذخیره شد: {columns}",
    "request_rejected": "❌ درخواست با موفقیت رد شد. دلیل: {reason}",
    "request_rejected_admin": "❌ درخواست با موفقیت رد شد.",
    "request_rejected_clients": "❌ درخواست شما توسط ادمین رد شد.\nℹ️ لطفاً برای اطلاعات بیشتر با پشتیبانی تماس بگیرید یا درخواست جدیدی ثبت کنید.",
    "request_rejected_user": "❌ درخواست شما رد شد. دلیل: {reason}",
    "request_settings_main_menu": "⚙️ تنظیمات درخواست",
    "request_submit_prompt": "📋 لطفاً اطلاعات خود را به فرمت 'شماره تلفن، کارت ملی، رسانه' ارسال کنید.",
    "request_submitted": "✅ فایل ارسال شد و در حال بررسی است.",
    "request_success": "✅ درخواست شما ثبت شد. پس از بررسی، نتیجه اعلام می‌شود.",
    "requests_for_skill": "📌 درخواست‌های این مهارت:",
    "requests_menu": "🕹 به منوی مدیریت درخواست خوش آمدید!",
    "requests_menu_prompt": "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "save_reason_prompt": "💾 آیا '{reason}' را به لیست پیش‌فرض ذخیره کنم؟",
    "search_entire_city": "🌍 جستجو در کل شهر",
    "search_results": "🔍 نتایج جستجو برای: «{query}»",
    "see_requests_approved": "✅ درخواست شماره: {req_id}\n📅 تاریخ درخواست: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n\nدرخواست شما توسط ادمین بررسی و تأیید اولیه شده و در انتظار تأیید نهایی پرسنل است.\n🙏 با سپاس از صبر و شکیبایی شما.",
    "see_requests_cancelled": "🚫 درخواست شما لغو شد.\n\n🔸 شماره درخواست: {req_id}\n📅 تاریخ درخواست: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n\n🔄 در صورت نیاز می‌توانید درخواست جدیدی ثبت نمایید.",
    "see_requests_done": "🎉 درخواست شما با موفقیت انجام شد!\n\n🔸 شماره درخواست: {req_id}\n📅 تاریخ درخواست: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n🛎 خدمات ارائه شده: {services}\n\n🌟 امیدواریم از خدمات دریافتی رضایت کامل داشته باشید.\n🙏 مشتاق دیدار دوباره شما هستیم.",
    "see_requests_expired": "⌛️ متأسفانه درخواست شما منقضی شده است.\n\n🔸 شماره درخواست: {req_id}\n📅 تاریخ درخواست: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n\nاین درخواست در زمان مقرر بررسی نشد و از تاریخ ارائه خدمات گذشته است.\n🔄 در صورت تمایل می‌توانید درخواست جدیدی ثبت کنید.",
    "see_requests_finalized": "🚀 درخواست شما تأیید نهایی شد!\n\n🔸 شماره درخواست: {req_id}\n📅 تاریخ درخواست: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n\n📞 لطفاً برای هماهنگی نهایی با شماره زیر تماس بگیرید:\n{phone_number}",
    "see_requests_finalized1": "🚀 درخواست شما تأیید نهایی شد!\n\n🔸 شماره درخواست: {req_id}\n📅 تاریخ درخواست: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n\n📞 منتظر تماس پرسنل باشید🤙",
    
    "see_requests_on_surd": "🚀 درخواست شما تایید نهایی شده است. لطفاً با پرسنل جهت دریافت خدمات هماهنگ کنید.",
    "see_requests_pending": "⏳ درخواست شما ثبت شد و در حال بررسی است.\n\n🔸 شماره درخواست: {req_id}\n📅 تاریخ: {date}\n💰 مبلغ کل: {total_price} تومان\n🔖 کد ارائه‌دهنده: {PU_code}\n\nلطفاً منتظر تأیید ادمین بمانید.",
    "see_requests_rejected": (
        "❌ درخواست شما رد شد.\n\n"
        "🔸 شماره درخواست: {req_id}\n"
        "📅 تاریخ درخواست: {date}\n"
        "💰 مبلغ کل: {total_price} تومان\n"
        "🔖 کد ارائه‌دهنده: {PU_code}\n"
        "📝 دلیل رد شدن: {reject_reason}\n\n"
        "📞 جهت اطلاعات بیشتر با پشتیبانی تماس بگیرید."
    ),

    "see_requests_unknown": "ℹ️ وضعیت درخواست شما نامشخص است. لطفاً مجدداً بررسی کنید.",
    "select_action_prompt": "لطفاً یکی از عملیات زیر را برای وضعیت {status} انتخاب کنید:",
    "select_area": "📍 انتخاب منطقه خاص",
    "select_area_prompt": "🏘 لطفا منطقه مورد نظر را انتخاب کنید:",
    "select_area_specific": "🏘 لطفا منطقه مورد نظر خود را انتخاب کنید:",
    "select_card_to_delete": "🗑️ کارت مورد نظر برای حذف را انتخاب کنید:",
    "select_card_to_edit": "✏️ کارت مورد نظر برای ویرایش را انتخاب کنید:",
    "select_categorization_column": "📋 نحوه دسته‌بندی درخواست‌ها را انتخاب کنید:",
    "select_choice": "🔘 مقدار جدید برای «{field}» را انتخاب کنید:",
    "select_city": "🏙️ لطفاً شهر خود را انتخاب کنید:",
    "select_complete_field": "لطفاً یک فیلد برای تکمیل انتخاب کنید:",
    "select_crypto": "💰 ارز دیجیتال را انتخاب کنید:",
    "select_crypto_wallet_delete": "💰 کیف پول کریپتو را برای حذف انتخاب کنید:",
    "select_crypto_wallet_edit": "💰 کیف پول کریپتو را برای ویرایش انتخاب کنید:",
    "select_currency": "💱 ارز را انتخاب کنید:",
    "select_curnecy":"💱 ارز را انتخاب کنید:",
    "select_day_title": "روز موردنظر را انتخاب کنید:",
    "select_default_card": "✅ کارت پیش‌فرض خود را انتخاب کنید:",
    "select_default_wallet": "✅ کیف پول پیش‌فرض خود را انتخاب کنید:",
    "select_display_columns": "📝 ستون‌های نمایش (تا 3 ستون) را انتخاب کنید:",
    "select_edit_field": "لطفاً یکی از فیلدهای قابل ویرایش را انتخاب کنید:",
    "select_field_to_edit": "✏️ کدام فیلد را می‌خواهید ویرایش کنید؟",
    "select_field_to_edit_wallet": "✏️ کدام فیلد کیف پول را می‌خواهید ویرایش کنید؟",
    "select_ignored_columns": "🚫 لطفاً ستون‌هایی که می‌خواهید نادیده گرفته شوند را انتخاب کنید:",
    "select_max_requests_per_row": "📌 تعداد درخواست‌ها در هر ردیف (1-5) را انتخاب کنید:",
    "select_month_title": "ماه موردنظر را انتخاب کنید:",
    "select_network": "🌐 شبکه را انتخاب کنید:",
    "select_network_wallet_delete": "🌐 شبکه کیف پول را برای حذف انتخاب کنید:",
    "select_network_wallet_edit": "🌐 شبکه کیف پول را برای ویرایش انتخاب کنید:",
    "select_new_wallet_network": "🌐 شبکه جدید کیف پول را انتخاب کنید:",
    "select_option_edit_wallet": "✏️ گزینه‌ای برای ویرایش کیف پول انتخاب کنید:",
    "select_province": "📍 لطفاً استان خود را انتخاب کنید:",
    "select_region_prompt": "🏙 لطفاً منطقه‌ای که در آن حضور داری را انتخاب کن:",
    "select_rejection_reason": "📌 لطفاً یک دلیل رد را انتخاب کنید:",
    "select_request_details_columns": "🔍 لطفاً ستون‌هایی که در جزئیات درخواست (نمایش جزئیات بیشتر) نمایش داده شوند را انتخاب کنید:",
    "select_request_overview_columns": "📝 لطفاً ستون‌هایی که در نمای کلی درخواست (نمای اولیه) نمایش داده شوند را انتخاب کنید:",
    "select_request_type": "📋 لطفاً نوع درخواست را انتخاب کنید:",
    "select_table_for_auto": "⚙️ لطفاً جدولی را برای پیکربندی عملیات خودکار انتخاب کنید:",
    "select_wallet_address_edit": "📇 آدرس کیف پول مورد نظر برای ویرایش را انتخاب کنید:",
    "select_wallet_delete": "👝 کیف پول را برای حذف انتخاب کنید:",
    "select_wallet_to_delete": "🗑️ کیف پول مورد نظر برای حذف را انتخاب کنید:",
    "select_wallet_to_edit": "✏️ کیف پول مورد نظر برای ویرایش را انتخاب کنید:",
    "send_photo": "لطفاً عکس مورد نظر را ارسال کنید:",
    "send_video": "لطفاً ویدئوی مورد نظر را ارسال کنید:",
    "session_expired": "⏳ جلسه شما منقضی شده است. لطفاً از ابتدا شروع کنید.",
    "set_auto_threshold": "📊 تعیین آستانه درخواست برای تایید خودکار: {threshold}",
    "set_auto_timer": "⏱ تنظیم تایمر: {timer}",
    "set_permissions": "🔐لطفا دسترسی های مدیر را تنظیم  کنید!",
    "settings_menu": "⚙️ منوی تنظیمات",
    "settings_saved": "✅ تنظیمات با موفقیت ذخیره شدند!",
    "settings_under_development": "⚙️ این بخش در حال توسعه است...",
    "start_menu": "سلام!به منوی مشتریان خوش آمدید!",
    "status_actions_title": "انتخاب عملیات برای وضعیت {status}:",
    "status_changed": "وضعیت مشتری به {reason} تغییر یافت.",
    "status_overview_title": "وضعیت درخواست‌های شما:",
    "status_updated": "✅ وضعیت پرسنل به «{status_title}» تغییر یافت.",
    "table_settings_menu": "⚙️ منوی تنظیمات درخواست:\n1. تنظیم دسته‌بندی بر اساس ستون\n2. تنظیم ستون‌های نمایش\n3. تنظیم نمای کلی درخواست\n4. تنظیم جزئیات درخواست\n5. ستون‌های نادیده گرفته شده",
    "today_code_menu_prompt": "📅 برای مشاهده کدهای امروز، موقعیت مکانی خود را انتخاب کنید.",
    "toggle_auto_status": "🔄 تغییر وضعیت تایید خودکار: {status}",
    "update_success": "✅ «{field}» با موفقیت به‌روزرسانی شد.",
    "user_city_not_found": "❗️ اطلاعات شهر شما پیدا نشد. لطفاً مجدداً تلاش کنید.",
    "user_not_found": "❗ کاربر پیدا نشد.",
    "username_updated": "✅ آیدی پرسنل به «{username}» بروزرسانی شد.",
    "view_requests": "درخواست‌های مشتری:",
    "premium_ask_custom_fantasy": "💬 آیا گزینهٔ سفارشی خاصی دارید؟\n(اختیاری، اگر ندارید بدون انتخواب این بخش را رد کنید)",
    "premium_code_invalid": "❌ کد ورود اشتباه است.",
    "premium_code_sent": "📨 کد ورود به شماره شما ارسال شد.",
    "premium_forgot_prompt": "📱 شماره تلفن خود را وارد کنید تا کد ورود ارسال شود.",
    "premium_login_info": "👋 به بخش مشتریان ویژه خوش آمدید. لطفاً کد ورودی خود را وارد کنید.",
    "premium_menu": "🎉 {name}\n عزیز، به منوی مشتریان ویژه خوش آمدید!",
    "premium_panel_welcome": "👤 پنل مشتریان ویژه:",
    "premium_reg_ask_location_auto": "📍 لطفاً مکان خود را ارسال کنید.",
    "premium_reg_ask_name": "📝 لطفاً نام مستعار خود را وارد کنید:",
    "premium_reg_ask_phone": "📞 لطفاً شماره تلفن خود را ارسال کنید.",
    "premium_reg_ask_preferences": "⭐ لطفاً علاقه‌مندی خود را انتخاب کنید:",
    "premium_reg_ask_referral": "📨 کد معرف خود را وارد کنید (در صورت نداشتن، 'ندارم' را انتخاب کنید)",
    "premium_reg_choose_location_mode": "🌍 انتخاب روش مکان: تشخیص خودکار یا دستی؟",
    "premium_reg_confirm_location": "📌 محل انتخابی شما:\n🗺️ استان: {province}\n🏙️ شهر: {city}\n{loc}\n\nآیا تایید می‌کنید یا مایل به ویرایش هستید؟",
    "premium_reg_registration_success": "🎉 ثبت‌نام PREMIUM با موفقیت انجام شد!",
    "premium_reg_request_username": "⚠️ ابتدا در تنظیمات تلگرام، یوزرنیم خود را ست کنید.",
    "premium_required_prompt": "🔐 برای هر سفارش نیاز به احراز هویت دارید.\nاما می‌تونید همین الان به صورت کاملاً رایگان ویژه بشید و فقط یکبار برای همیشه احراز هویت کنید. 😇",
    "premium_search_mode": "✨ لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "wallet_added_successfully": "✅ کیف پول با موفقیت افزوده شد!",
    "wallet_address_updated": "✅ آدرس کیف پول با موفقیت به‌روز شد.",
    "wallet_deleted": "✅ کیف پول با موفقیت حذف شد.",
    "wallet_exists": "❌ این کیف پول قبلاً ثبت شده است.",
    "we_sorry": "کاربر گرامی بدلیل اختلالات سیستمی متاسفانه باید مجددا تلاش کنید",
    "welcome": "🎉 به ربات مدیریت  خوش آمدید! ما اینجا هستیم تا به شما در مدیریت  به صورت کارآمد کمک کنیم.",
    "welcome_location": "👋 خوش آمدید! لطفاً برای تنظیم موقعیت، '📍 انتخاب دستی آدرس' را بزنید.",
    "wrong_name": "لطفا  نام معتبر وارد کنید ",
    "you_dont_have_permision": "⛔ شما اجازه دسترسی به این بخش را ندارید.",
    "you_dont_have_permission": "⛔ شما اجازه دسترسی به این بخش را ندارید!"
}

MONTH_NAMES_PERSIAN = {
    "1": "فروردین",
    "10": "دی",
    "11": "بهمن",
    "12": "اسفند",
    "2": "اردیبهشت",
    "3": "خرداد",
    "4": "تیر",
    "5": "عضواد",
    "6": "شهریور",
    "7": "مهر",
    "8": "آبان",
    "9": "آذر"
}
MESSAGES.update({

    "no_requests_for_month": "درخواستی برای این ماه ثبت نشده است. 👀",
    "slot_already_reserved": "❌ این اسلات قبلاً رزرو شده.\nکدهای فعال الان:\n⬇",

})

MSG_ADDED_FAVORITE = "کد {code} به لیست علاقه‌مندی‌های شما اضافه شد ⭐"

MSG_ALREADY_FAVORITE = "این مورد در حال حاضر هم در لیست علاقه‌مندی‌های شماست ⭐"

MSG_ERROR_GENERIC = "🚫 خطایی رخ داد. لطفاً دوباره تلاش کنید."

MSG_FEATURE_PREMIUM_ONLY = "❌ این قابلیت فقط برای مشتریان ویژه فعال است"

MSG_NO_INFO_FOUND = "❌ اطلاعاتی یافت نشد."

MSG_BOOKING_ERROR = "خطایی رخ داد."

PAGE_SIZE = 20

PERMISSIONS = [
    "bot_settings",
    "manage_requests",
    "auto_answer",
    "manage_admins",
    "manage_clients",
    "channel_settings",
    "manage_users",
    "manage_codes"
]

PER_CONV = {
    "auto_answer" : "پاسخ دهی خودکار",
    "manage_codes": "مدیریت کد ها",
    "manage_users":"مدیریت کاربران",
    "accounting": "مدیریت حساب ها",
    "ads_settins": "تنظیمات آگهی",
    "automatical": "مدیریت تنظیمات خودکار",
    "bot_settings": "منوی تنظیمات",
    "channel_settings": "تنظیمات کانال",
    "create_ad": "ایجاد آگهی",
    "group_settings": "تنظیمات گروه",
    "manage_admins": "مدیریت ادمین‌ها",
    "manage_clients": "مدیریت مشتریان",
    "manage_staff": "مدیریت پرسنل",
    "manage_requests": "مدیریت درخواست‌ها",
    "manage_messages": "مدیریت پیام‌ها",
    "request_settings": "تنظیمات درخواست‌ها",
    "view_reports": "مشاهده گزارش‌ها"
}

# PERMISSIONS = [
#     "bot_settings",
#     "manage_requests",
#     "request_settings",
#     "manage_admins",
#     "view_reports",
#     "manage_clients",
#     "manage_staff",
#     "channel_settings",
#     "group_settings",
#     "create_ad",
#     "manage_messages",
#     "accounting",
#     "automatical",
#     "manage_users",
#     "ads_settins",
#     "manage_codes"
# ]

# PER_CONV = {
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# }



REQUEST_SETTINGS = {
    "ads": {
        "Translate": {
            "table_name": "آگهی ها"
        },
        "categorization_column": None,
        "display_columns": [
            "name",
            "start_time",
            "end_time"
        ],
        "link_field": "U_code",
        "parent_table": "staff",
        "request_details": "",
        "request_overview": [
            "start_time",
            "end_time",
            "service_count",
            "service_price"
        ],
        "status_column": "status",
        "type": 4,
        "user_info_fields": [
            "name",
            "age",
            "city",
            "is_premium"
        ]
    },
    "receipts": {
        "Translate": {
            "table_name": "رسیدها"      # Internal implementation note: legacy behavior is preserved during modernization.
        },
        "categorization_column": None,
        "display_columns": [
            "name",
            "age",
        ],
        "link_field": "U_code",
        "parent_table": "staff",
        "request_details": "",
        "request_overview": ["name","age","city","created_at"],
        "user_info_fields": [
            "name",
            "age",
            "city",
            "phone",
            "phone_number",
            "dispatch_mode",
            "region",
            "profile_photos",
        ],
        "status_column": "status",      # Internal implementation note: legacy behavior is preserved during modernization.
        "type": 2                       # Internal implementation note: legacy behavior is preserved during modernization.
    },

    "service_requests": {
        "Translate": {
            "table_name": "مشتریان"
        },
        "channel_message_config": {
            "ad_id_field": "ad_id",
            "field": "time_slots",
            "table": "live_ads"
        },
        "display_columns": [
            {
                "field": "name",
                "source": "staff"
            },
            {
                "field": "slot_time",
                "source": "self"
            },
            {
                "field": "name",
                "source": "clients"
            }
        ],
        "parent_tables": [
            {
                "column_connect": "U_code",
                "fields": [
                    "name",
                    "U_code"
                ],
                "link_field": "U_code",
                "table": "clients",
                "title_name": "مشتری"
            },
            {
                "column_connect": "U_code",
                "fields": [
                    "name",
                    "age",
                    "U_code"
                ],
                "link_field": "PU_code",
                "table": "staff",
                "title_name": "پرسنل"
            },
            {
                "column_connect": "id",
                "fields": [
                    "id",
                    "start_time",
                    "end_time"
                ],
                "link_field": "ad_id",
                "table": "ads",
                "title_name": "آگهی"
            }
        ],
        "request_overview": [
            {
                "column_connect": "U_code",
                "fields": [
                    "name",
                    "U_code"
                ],
                "link_field": "U_code",
                "table": "clients",
                "title_name": "مشتری"
            },
            {
                "column_connect": "id",
                "fields": [
                    "invoice",
                    "slot_time"
                ],
                "link_field": "id",
                "table": "service_requests",
                "title_name": "سفارش"
            },
            {
                "column_connect": "U_code",
                "fields": [
                    "name",
                    "U_code"
                ],
                "link_field": "PU_code",
                "table": "staff",
                "title_name": "پرسنل"
            },
            {
                "column_connect": "id",
                "fields": [
                    "id",
                    "start_time",
                    "end_time"
                ],
                "link_field": "ad_id",
                "table": "ads",
                "title_name": "آگهی"
            }
        ],
        "status_column": "status",
        "type": 5
    },
    "identity_verification_requests": {
        "Translate": {
            "table_name": "احراز هویت مشتریان"
        },
        "categorization_column": None,
        "dict_column": "identity_verification_docs",
        "display_columns": [
            {
                "field": "name",
                "source": "premium_clients"
            }
        ],
        "link_field": "U_code",
        "parent_table": "premium_clients",
        "request_details": "",
        "request_overview": [
            {
                "column_connect": "U_code",
                "fields": [
                    "name",
                    "U_code"
                ],
                "link_field": "U_code",
                "table": "premium_clients",
                "title_name": "مشتری"
            }
        ],
        "review_header": "لطفاً روی مواردی که مورد تایید نیستند کلیک کنید.",
        "status_column": "status",
        "type": 3
    },
    "identity_verification_data": {
        "Translate": {
            "table_name": "احراز هویت پرسنل"
        },
        "categorization_column": None,
        "dict_column": "identity_verification_docs",
        "display_columns": [
            {
                "field": "name",
                "source": "staff"
            }
        ],
        "link_field": "U_code",
        "parent_table": "staff",
        "request_details": "",
        "request_overview": [
            {
                "column_connect": "U_code",
                "fields": [
                    "name",
                    "U_code"
                ],
                "link_field": "U_code",
                "table": "staff",
                "title_name": "پرسنل"
            }
        ],
        "review_header": "لطفاً روی مواردی که مورد تایید نیستند کلیک کنید.",
        "status_column": "status",
        "type": 3
    },
    
    "staff": {
        "Translate": {
            "table_name": "ثبت نامی پرسنل"
        },
        "categorization_column": "city",
        "display_columns": [
            "name",
            "age"
        ],
        "link_field": None,
        "parent_table": None,
        "request_details": "",
        "request_overview": "name, age, phone_number",
        "status_column": "status",
        "type": 1,
        "user_info_fields": []
    },
    
    "request_drafts": {
        "type": 1,
        "status_column": "status",
        "Translate": {
            "table_name": "مشتری ها"
        },
        "categorization_column": "",
        "display_columns": [
            "name",
            "phone",
        ],
        "link_field": None,
        "parent_table": None,
        "request_details": "",
        "request_overview": "username, phone ,staff_code,region,request_time,",
        "user_info_fields": []
    },
    
    "premium_staff": {
        "Translate": {
            "table_name": "ویژه شدن پرسنل"
        },
        "categorization_column": None,
        "display_columns": [
            "name"
        ],
        "link_field": "U_code",
        "parent_table": "staff",
        "request_details": "",
        "request_overview": ["name","age","city"],
        "status_column": "status",
        "type": 2,
        "user_info_fields": [
            "name",
            "age",
            "city",
            "phone",
            "phone_number",
            "dispatch_mode",
            "region",
            "profile_photos",
        ]
    }
}

REQUEST_TABLE_JOINS = {
    "request_drafts":{
        "request_drafts",
        "id"
    },
    "ad_edit_requests": [
        "ads",
        "U_code"
    ],
    "cards": [
        "cards",
        "id"
    ],
    "client_ads": [
        "ads",
        "U_code"
    ],
    "receipts":[
        "staff",
        "U_code"
    ],
    
    "edit_info_requests": [
        "staff",
        "U_code"
    ],
    "identity_verification_data_requests": [
        "identity_verification_data",
        "U_code"
    ],
    "messages": [
        "messages",
        "id"
    ],
    "permanent_ads": [
        "p_ads",
        "U_code"
    ],
    
    "staff_requests": [
        "staff",
        "U_code"
    ],
    "services_requests": [
        "services",
        "U_code"
    ],
    "featured_ads": [
        "ads",
        "U_code"
    ],
    "user_requests": [
        "clients",
        "U_code"
    ],
    "premium_requests": [
        "premium_requests",
        "U_code"
    ],
    "wallets": [
        "wallets",
        "id"
    ]
}

REQUEST_TYPES = {
    "receipts":"receipts",
    "request_drafts":"request_drafts",
    "client_ads": "ads_clients",
    "service_requests": "service_requests",
    "identity_verification_data_requests": "identity_verification_data",
    "permanent_ads": "p_ads",
    "staff_ads": "ads_staff",
    "staff_requests": "staff",
    "featured_ads": "ads",
    "user_requests": "clients"
}

REQUEST_TYPE_MAP = {
    "request_drafts": "client.request_drafts",
    "receipts":"staff.receipts",
    "ads": "staff.ad_request",
    "cards": "staff.card_edit",
    "service_requests": "service_requests",
    "clients": "client.register",
    "identity_verification_requests": "client.identity_verification_request",
    "identity_verification_data": "staff.identity_verification_request",
    "messages": "admin.message_reply",
    "staff": "staff.register",
    "premium_staff": "staff.premium_upgrade",
    "premium_requests": "staff.premium_request",
    "wallets": "staff.wallet_edit"
}

REQUEST_TYPE_NAMES = {
    "request_drafts": "درخواست‌های مشتری ها",
    "receipts":"رسید ها",
    "client_ads": "آگهی‌های مشتریان",
    "service_requests": "مشتریان",
    "edit_info": "درخواست ویرایش اطلاعات",
    "identity_verification_data_requests": "تأیید احراز هویت",
    "new_client": "درخواست مشتری جدید",
    "permanent_ads": "آگهی‌های دائم 🗓",
    "staff_ads": "آگهی‌های پرسنل",
    "staff_requests": "درخواست‌های پرسنل",
    "featured_ads": "آگهی‌های ویژه 📢",
    "user_requests": "مشتریان",
    "premium_staff": "درخواست ارتقا به PREMIUM"
}

RESERVE_PREFIX = "book"

SELECT_PREFIX = "select_"

SERVICES = {
    "special_service_option_a": "⛓️ گزینه A را فعال می‌کنم",
    "special_service_option_b": "⛓️ گزینه B را فعال می‌کنم",
    "candles_music": "🕯🎶 شمع و موزیک و نوشیدنی",
    "custom_outfit": "📦 محصول سفارشی",
    "social_service": "🤝 خدمات تعاملی",
    "service_option_1": "🧰 گزینه خدمات ۱",
    "massage": "خدمت ویژه",
    "service_option_a": "🧩🧩🧩 گزینه خدمات تعاملی",
    "service_option_b": "🧩👤🧩🧩 گزینه خدمات B"
}

STATUS_APPROVED = "approved"

STATUS_INFO = {
    "approved": {
        "emoji": "✅",
        "title": "تایید شده"
    },
    "cancelled": {
        "emoji": "✂️",
        "title": "لغو شده"
    },
    "done": {
        "emoji": "✔️",
        "title": "انجام شده"
    },
    "expired": {
        "emoji": "⌛",
        "title": "منقضی شده"
    },
    "finalized": {
        "emoji": "🎯",
        "title": "نهایی شده"
    },
    "pending": {
        "emoji": "⏳",
        "title": "در انتظار"
    },
    "rejected": {
        "emoji": "🚫",
        "title": "رد شده"
    }
}

STATUS_REJECTED = "rejected"

STATUS_TITLES = {
    "approved": "تایید شده ✅",
    "blocked": "بلاک شده 🚫",
    "rejected": "رد شده ❌"
}


TABLE_NAME = {
    "table_names": {
        "request_drafts":"مشتری ها",
        "receipts":"رسید ها",
        "identity_verification_requests": "احراز هویت مشتریان",
        "admins": "مدیران",
        "ads": "آگهی‌های ویژه",
        "ads_clients": "آگهی‌های مشتریان",
        "ads_staff": "آگهی‌های پرسنل",
        "bot_settings": "تنظیمات ربات",
        "service_requests": "مشتریان",
        "clients": "مشتریان",
        "identity_verification_data": " احراز هویت",
        "p_ads": "آگهی‌های دائم",
        "staff": "پرسنل",
        "rejection_reasons": "دلایل رد",
        "premium_staff": "درخواست ارتقا به PREMIUM"
    }
}

TB_CONV = {
    "request_drafts":"request_drafts",
    "receipts":"receipts",
    "ads": "featured_ads",
    "ads_clients": "client_ads",
    "ads_staff": "staff_ads",
    "service_requests": "service_requests",
    "clients": "user_requests",
    "identity_verification_data": "identity_verification_data_requests",
    "p_ads": "permanent_ads",
    "staff": "staff_requests",
    "premium_staff": "premium_staff"
}

TEMPLATES = {
    "admin_details": "👤 نام: {name}\n🆔 نام کاربری: @{username}\n📞 تلفن: {phone_number}",
    "request_details": {
        "ads": "📢 عنوان آگهی: {ad_title}\n📝 توضیحات: {description}\n🧾 کد کاربر: {U_code}",
        "ads_clients": "📝 توضیحات آگهی: {ad_description}\n📌 وضعیت: {status}",
        "ads_staff": "📝 توضیحات آگهی: {ad_description}\n📌 وضعیت: {status}",
        "clients": "نام: {name}",
        "identity_verification_data": "نام: {name}\n🆔 نام کاربری: @{username}\n🧾 کد کاربر: {U_code}\n📌 وضعیت: {status}",
        "p_ads": "📅 نوع آگهی: دائم\n📢 عنوان: {ad_title}\n💰 قیمت: {price}\n🧾 کد کاربر: {U_code}",
        "permanent_ads": "🗓 آگهی دائم:\n📝 توضیحات: {ad_description}\n📌 وضعیت: {status}",
        "staff": "نام: {name}\n📞 تلفن: {phone_number}\n🆔 نام کاربری: @{username}",
        "featured_ads": "📢 آگهی ویژه:\n📝 توضیحات: {ad_description}\n📌 وضعیت: {status}"
    },
    "skill_category_button": "📌 درخواست‌ها ({count})",
    "user_button_all": "👤 {name} - ",
    "user_button_skill": "👤 {name} | 📶 سطح: {level} | 🎂 سطح تجربه: {age}",
    "user_details": "👤 نام: {name}\n📶 سطح: {level}\n🎂 سطح تجربه: {age}\n🛠 مهارت: {skill}"
}


PREMIUM_FAV_PROFILE_PREFIX = "premium_fav_profile_"

PREMIUM_FAV_TODAY_ADS_PREFIX = "premium_fav_today_ads_"

PREMIUM_REQUESTS_TABLE = "service_requests"

choice_options = {
    "income_range": [
        "کمتر از 20 میلیون",
        "بین 20 تا 50 میلیون",
        "بین 50 تا 80 میلیون",
        "بین 80 تا 100 میلیون",
        "بیشتر از 100 میلیون"
    ],
    "skin_color": [
        "پایه",
        "استاندارد",
        "ویژه",
        "سفارشی"
    ]
}

editable_fields = [
    "name",
    "age",
    "height",
    "weight",
    "skin_color",
    "income_range",
    "bio",
    "profile_photo"
]
EXPIRE_ABLE_TABLE = {"service_requests","ads"}
field_labels = {
    "intro_msg_id":"مسیج آیدی سفارش دهنده",
    "last_order" :"آخرین سفارش",
    "receipt_method":"روش پرداخت",
    "video_sentence": "جمله خواسته شده",
    "video_file_id":  "ویدیو مسیج دریافتی",
    "note":"یاد داشت کاربر",
    "receipt":"رسید",
    "receipts":"رسید ها",
    "profile_photos":"عکس های کاربر",
    "_region_buffer" : "مناطق کاری",
    "selected_region":"نوع مراجعه",
    "skin_color":"دسته‌بندی خدمات 🎨",
    "PU_code": "کد کاربری پرسنل",
    "Reffral_id": "🎯 شناسه ارجاع",
    "U_code": "🧾 کد کاربر",
    "U_refC": "🎯 کد معرف",
    "ad_description": "📝 توضیحات آگهی",
    "ad_id": "شماره آگهی",
    "ad_photo": "🖼 عکس آگهی",
    "ad_price": "💰 قیمت کل آگهی",
    "address_video": "ویدیوی معرفی محل یا خدمت",
    "age": "🎂 سطح تجربه",
    "base_price": "💰 قیمت پایه",
    "cancel_paid": "وضعیت مبلغ کنسلی",
    "cancel_reason": "دلیل کسنلی",
    "card": "💳 شماره کارت",
    "city": "🏙️ شهر",
    "created_at": "🗓 تاریخ ایجاد",
    "creation_date": "🗓 تاریخ ایجاد",
    "service_requests": "📊 سفارشات مشتریان",
    "dispatch_mode": "🏠 نوع مراجعه",
    "end_time": "🕔 زمان پایان",
    "extra_time_cost": "قیمت زمان اضافه",
    "extra_times": "زمان اضافه",
    "first_name": "👤 نام",
    "health_card": "مدرک مجوز/تأیید 🎫",
    "height": "📏 ظرفیت (سانتی‌متر)",
    "id": "🆔 شناسه",
    "id_card": "تصویر مدرک شناسایی",
    "id_card_back": "🖼 پشت مدرک شناسایی",
    "id_card_front": "🖼 جلو مدرک شناسایی",
    "invoice": "فاکتور",
    "is_premium": "🌟 وضعیت ویژه بودن",
    "last_name": "📝 نام خانوادگی",
    "last_updated": "🗓 آخرین به‌روزرسانی",
    "level": "📶 سطح",
    "location": "لوکیشن📍",
    "manual_address": "✍ آدرس دستی",
    "name": "👤 نام",
    "payment_method": "💳 روش های پرداخت",
    "phone": "شماره تلفن",
    "phone_number": "📱 شماره تلفن",
    "photo_id": "تصویر مدرک شناسایی",
    "photo_verification_photo": "تصویر تأیید هویت",
    "prepayment_amount": "💳 مبلغ پیش‌پرداخت",
    "province": "🌍 استان",
    "publish_time": "🕓 زمان انتشار آگهی",
    "ref_code": "🧬 کد ارجاع",
    "region": "📍 منطقه",
    "regular_services": "🧰 خدمات مازاد",
    "regular_services_price": "💸 قیمت خدمات",
    "reject_reason": "دلیل رد",
    "rejection_reason": "🚫 دلیل رد",
    "verification_photo_with_id": "🤳 سلفی با مدرک شناسایی",
    "service_count": "🔢 تعداد سرویس قابل اراعه ",
    "service_price": "💰 قیمت پایه",
    "services": "خدمات",
    "services_price": "قیمت خدمات",
    "profile_category": "🧩 پروفایلت",
    "skill": "🛠️ مهارت",
    "slot_time": "زمان رزروی سفارش",
    "start_time": "🕓 زمان شروع",
    "status": "📌 وضعیت",
    "telegram_id": "🆔 شناسه تلگرام",
    "total_price": "مجموع قیمت ها",
    "username": "👤 نام کاربری",
    "video_message": "پیام ویدیویی",
    "premium": "🌟 ویژه بودن آگهی",
    "premium_services": "⭐ ویژگی‌های افزوده",
    "premium_services_price": "💵 قیمت ویژگی‌های افزوده",
    "weight": "⚖️ حجم خدمات (واحد)"
}
field_labels.update({
    "telegram_id": "🆔 آیدی عددی تلگرام",
    "username": "👤 یوزرنیم تلگرام",
    "staff_code": "🧑‍💼 کد پرسنل انتخابی",
    "region": "📍 محدوده محل مراجعه",
    "phone": "📞 شماره تماس",
    "verification_photo_1_emoji": "🤳 ایموجی سلفی اول",
    "verification_photo_1_file_id": "🖼 فایل سلفی اول",
    "verification_photo_2_emoji": "📸 ایموجی سلفی دوم",
    "verification_photo_2_file_id": "🖼 فایل سلفی دوم",
    "status": "📌 وضعیت درخواست",
    "request_time": "⏰ ساعت درخواستی",
})

field_types = {
    "age": "number",
    "bio": "text",
    "height": "number",
    "income_range": "choice",
    "name": "text",
    "profile_photo": "photo",
    "skin_color": "choice",
    "weight": "number"
}

ignor_labels = [
    "ad_type",
    "request_count",
    "id",
    "completed_services",
    "total_received",
    "telegram_id",
    "status",
    "identity_verification_status",
    "creation_date",
    "last_updated",
    "is_premium",
    "premium"
]

identity_verification_example = {
    "photo_id": [
        "🔖 لطفاً عکس واضحی از روی کارت ملی خود ارسال کنید.\n- کل کارت در قاب باشد\n- همه نوشته‌ها خوانا باشد",
        "https://www.okx.com/cdn/assets/plugins/announcements/contentful/tofttmniq0qv/48cFxY3Lc3LVLV1PcwxA4s/eb5022eddddc0847b18fc7e8d26f8b3c/Guide_ID_and_verification_photo_photos_1.png"
    ],
    "photo_verification_photo": [
        "🤳 لطفاً یک تصویر سلفی ارسال کنید که در آن:\n- کارت ملی در کنار صورت شما باشد\n- روی کارت مشخص باشد\n",
        "https://www.okx.com/cdn/assets/plugins/announcements/contentful/tofttmniq0qv/SAt5m3j3DGXX6PI92aiue/5ec0d0bcfee460ecb0e0eecc81bffc95/Guide_ID_and_verification_photo_photos_4.png"
    ],
    "video_message": [
        "🤳 لطفاً یک ویدیو نوت سلفی ارسال کنید که در آن:\n- کارت ملی در کنار صورت شما باشد\n- روی کارت مشخص باشد\n",
        "https://www.okx.com/cdn/assets/plugins/announcements/contentful/tofttmniq0qv/SAt5m3j3DGXX6PI92aiue/5ec0d0bcfee460ecb0e0eecc81bffc95/Guide_ID_and_verification_photo_photos_4.png"
    ]
}

identity_verification_field_labels = {
    "photo_id": "ارسال تصویر مدرک شناسایی",
    "photo_verification_photo": "ارسال تصویر تأیید هویت",
    "video_message": "ارسال ویدئوی تأیید"
}

identity_verification_fields = [
    "photo_id",
    "photo_verification_photo",
    "video_message"
]

regular_services_config = {
    "back": {
        "category": "regular",
        "price_range": [
            300000,
            500000
        ],
        "requires_price": True,
        "title": "🧰 گزینه خدمات ۱",
        "toggle": True
    },
    "confirm": {
        "category": "system",
        "title": "✔️ ذخیره و بازگشت"
    },
    "service_group": {
        "category": "regular",
        "subtypes": {
            "group_option_a": {
                "requires_participant": True,
                "title": "🧩 گزینه خدمات A"
            },
            "group_option_b": {
                "title": "🧩 گزینه خدمات B",
                "toggle": True
            }
        },
        "title": "🧩 گروه خدمات"
    },
    "view": {
        "category": "system",
        "title": "📝 مشاهده خدمات من"
    }
}

services_config = {
    "special_service": {
        "active": True,
        "category": "premium",
        "sub_roles": {
            "option_a": {
                "price_range": [
                    200000,
                    700000
                ],
                "requires_price": True,
                "title": "🔱 گزینه A را فعال می‌کنم",
                "toggle": True
            },
            "option_b": {
                "price_range": [
                    400000,
                    700000
                ],
                "requires_price": True,
                "title": "🧷 گزینه B را فعال می‌کنم",
                "toggle": True
            }
        },
        "title": "⛓️ گزینهٔ سفارشی ویژه"
    },
    "candles_music": {
        "active": True,
        "adds_price": 100000,
        "category": "premium",
        "drinks": {
            "enabled": True,
            "price_range": [
                100000,
                400000
            ],
            "requires_price": True,
            "toggle": True
        },
        "title": "🎁 بسته افزوده",
        "toggle": True
    },
    "confirm": {
        "active": True,
        "category": "system",
        "title": "✔️ ذخیره و بازگشت"
    },
    "custom_outfit": {
        "active": True,
        "category": "premium",
        "price_range": [
            200000,
            500000
        ],
        "requires_description": True,
        "requires_photo": True,
        "title": "📦 محصول سفارشی"
    },
    "social_service": {
        "active": True,
        "category": "premium",
        "title": "🤝 خدمات تعاملی"
    },
    "massage": {
        "active": True,
        "category": "premium",
        "price_range": [
            200000,
            700000
        ],
        "requires_price": True,
        "title": "⭐ خدمت ویژه",
        "toggle": True
    }
}


# Internal implementation note: legacy behavior is preserved during modernization.
registration_steps = [
    {"name": "get_name",              "active": True,  "position": 1,  "skippable": False},
    {"name": "get_age",               "active": True,  "position": 2,  "skippable": False},
    {"name": "get_gender",               "active": True,  "position": 3,  "skippable": False},
    {"name": "get_phone_number",      "active": True,  "position": 4,  "skippable": False},
    {"name": "get_video_message",     "active": False, "position": 5,  "skippable": False},
    {"name": "get_dispatch_mode",     "active": True,  "position": 6,  "skippable": False},
    {"name": "get_height",            "active": True,  "position": 7,  "skippable": False},
    {"name": "get_weight",            "active": True,  "position": 8,  "skippable": False},
    {"name": "skin_color",            "active": True,  "position": 9,  "skippable": False},
    {"name": "get_province",          "active": True,  "position": 10, "skippable": False},
    {"name": "get_city",              "active": True,  "position": 11, "skippable": False},
    {"name": "get_region",            "active": True,  "position": 12, "skippable": False},
    {"name": "get_photo_pair",        "active": True,  "position": 13, "skippable": False},
    {"name": "ref_code",              "active": True,  "position": 14, "skippable": True},
    {"name": "complete_registration", "active": True,  "position": 15, "skippable": False},
]

# Internal implementation note: legacy behavior is preserved during modernization.
location_type_step = {
    "name":       "get_dispatch_mode",
    "type":       "buttons",
    "field":      "dispatch_mode",          # Internal implementation note: legacy behavior is preserved during modernization.
    "prompt":     "🏠 لطفاً مشخص کنید: مکان دارید یا ارائه در محل مشتری هستید؟",
    "buttons":    ["🏠 محل ثابت دارم", "🚗 ارائه در محل مشتری"],
    "multi_select": False,
    "back_button": "🔙 بازگشت"
}

# Internal implementation note: legacy behavior is preserved during modernization.
region_step = {
    "name":          "get_region",
    "type":          "buttons",
    "field":         "region",
    "prompt":        "🌍 لطفاً منطقه کاری خود را انتخاب کنید:",
    "buttons":       ["منطقه ۱","منطقه ۲","منطقه ۳","منطقه ۴"],
    "multi_select":  True,                 # Internal implementation note: legacy behavior is preserved during modernization.
    "confirm_button":"✔️ تایید",
    "back_button":   "🔙 بازگشت"
}

# Internal implementation note: legacy behavior is preserved during modernization.
photo_pair_step = {
    "name":   "get_photo_pair",
    "type":   "photo",                      # Internal implementation note: legacy behavior is preserved during modernization.
    "field":  "profile_photos",             # Internal implementation note: legacy behavior is preserved during modernization.
    "prompt": "📸 لطفاً *دو عکس* (یک پرتره و یک تمام‌ظرفیت) ارسال کنید.",
    "count":  2
}
# Internal implementation note: legacy behavior is preserved during modernization.
work_settings_steps = [
    {"name": "get_marital_status",        "active": True,  "position": 1,  "skippable": False},
    {"name": "get_appearance",            "active": True,  "position": 2,  "skippable": False},
    {"name": "get_eye_color",             "active": True,  "position": 3,  "skippable": False},
    {"name": "get_health_card_status",    "active": False, "position": 4,  "skippable": False},
    {"name": "get_has_home",              "active": False, "position": 5,  "skippable": False},
    {"name": "get_visit_client_home",   "active": False, "position": 6,  "skippable": False},
    {"name": "get_breast_size",           "active": True,  "position": 7,  "skippable": False},
    {"name": "get_hair_color",            "active": True,  "position": 8,  "skippable": False},
    {"name": "get_profile_photo",         "active": True,  "position": 9,  "skippable": False},
    {"name": "get_photo_list",            "active": True,  "position": 10, "skippable": False},
    {"name": "get_service_price",         "active": False, "position": 11, "skippable": False},
    {"name": "complete_work_settings",    "active": True,  "position": 12, "skippable": False},
]


# Internal implementation note: legacy behavior is preserved during modernization.
province_cities = {
    "آذربایجان شرقی": ["تبریز", "مرند", "مراغه", "میانه", "اهر"],
    "آذربایجان غربی": ["ارومیه", "خوی", "مهاباد", "بوکان", "سلماس"],
    "اردبیل": ["اردبیل", "مشگین‌شهر", "پارس‌آباد", "خلخال", "نمین"],
    "اصفهان": ["اصفهان", "کاشان", "نجف‌آباد", "شاهین‌شهر", "فولادشهر"],
    "البرز": ["کرج", "نظرآباد", "هشتگرد", "فردیس", "ماهدشت"],
    "ایلام": ["ایلام", "دهلران", "مهران", "آبدانان", "سرابله"],
    "بوشهر": ["بوشهر", "دشتستان", "گناوه", "کنگان", "جم"],
    "تهران": ["تهران", "ری", "ورامین", "اسلامشهر", "دماوند"],
    "چهارمحال و بختیاری": ["شهرکرد", "بروجن", "فارسان", "لردگان", "سامان"],
    "خراسان جنوبی": ["بیرجند", "قائن", "فردوس", "طبس", "نهبندان"],
    "خراسان رضوی": ["مشهد", "نیشابور", "سبزوار", "تربت حیدریه", "قوچان"],
    "خراسان شمالی": ["بجنورد", "شیروان", "اسفراین", "مانه و سملقان", "جاجرم"],
    "خوزستان": ["اهواز", "آبادان", "خرمشهر", "دزفول", "بهبهان"],
    "زنجان": ["زنجان", "ابهر", "خدابنده", "ماه‌نشان", "طارم"],
    "سمنان": ["سمنان", "شاهرود", "دامغان", "حرفه‌ایسار", "مهدی‌شهر"],
    "سیستان و بلوچستان": ["زاهدان", "چابهار", "ایرانشهر", "سراوان", "نیک‌شهر"],
    "فارس": ["شیراز", "مرودشت", "جهرم", "لار", "کازرون"],
    "قزوین": ["قزوین", "تاکستان", "آبیک", "البرز", "بوئین‌زهرا"],
    "قم": ["قم"],
    "کردستان": ["سنندج", "سقز", "بانه", "بیجار", "کامیاران"],
    "کرمان": ["کرمان", "سیرجان", "رفسنجان", "جیرفت", "بم"],
    "کرمانشاه": ["کرمانشاه", "اسلام‌آباد غرب", "هرسین", "سرپل ذهاب", "کنگاور"],
    "کهگیلویه و بویراحمد": ["یاسوج", "دهدشت", "گچساران", "سی‌سخت", "باشت"],
    "گلستان": ["گرگان", "گنبد کاووس", "علی‌آباد", "آق‌قلا", "کردکوی"],
    "گیلان": ["رشت", "لاهیجان", "انزلی", "آستارا", "رودبار"],
    "لرستان": ["خرم‌آباد", "بروجرد", "دورود", "الیگودرز", "ازنا"],
    "مازندران": ["ساری", "بابل", "آمل", "قائم‌شهر", "تنکابن"],
    "مرکزی": ["اراک", "ساوه", "خمین", "محلات", "تفرش"],
    "هرمزگان": ["بندرعباس", "میناب", "قشم", "کیش", "بندر لنگه"],
    "همدان": ["همدان", "ملایر", "نهاوند", "تویسرکان", "کبودرآهنگ"],
    "یزد": ["یزد", "میبد", "اردکان", "بافق", "ابرکوه"]
}

# Internal implementation note: legacy behavior is preserved during modernization.

ad_creation_steps = [
    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "select_location_type",
        "type":  "buttons",
        "field": "location_type",
        "prompt": "🏠 لطفاً مشخص کنید که این آگهی برای محل ثابت شماست یا برای ارائه در محل مشتری:",
        "buttons": ["🏠 محل ثابت", "🚗 ارائه در محل مشتری"],
        "back_button": "🔙 بازگشت"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "enter_start_time",
        "type":  "input",
        "field": "start_time",
        "prompt": "⏰ لطفاً ساعت شروع را وارد کنید (مثال: 14:00)",
        "validation": "time"
    },
    {
        "name":  "enter_end_time",
        "type":  "input",
        "field": "end_time",
        "prompt": "⏰ لطفاً ساعت پایان را وارد کنید (مثال: 18:00)",
        "validation": "time",
        "compare_with": "start_time"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":    "ask_service_count",
        "handler": "ask_service_count"      # Internal implementation note: legacy behavior is preserved during modernization.
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "select_services",
        "type":  "buttons",
        "field": "selected_services",
        "prompt": "🛎 لطفاً خدمات مورد نظر را انتخاب کنید:",
        "buttons": ["گزینه خدمات ۲", "گزینه خدمات ۳", "گزینه خدمات ۴"],
        "multi_select": True,
        "confirm_button": "✔️ تایید",
        "back_button":   "🔙 بازگشت"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":    "ask_regular_services",
        "handler": "ask_regular_services"
    },
    {
        "name":      "ask_premium_services",
        "condition": "is_premium_staff",    # Internal implementation note: legacy behavior is preserved during modernization.
        "handler":   "ask_premium_services"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "enter_ad_photo",
        "type":  "photo",
        "field": "ad_photo",
        "prompt": "📸 لطفاً یک عکس برای آگهی خود ارسال کنید.",
        "validation": "photo"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "select_payment_method",
        "type":  "buttons",
        "field": "payment_method",
        "prompt": "💳 لطفاً روش پرداخت را انتخاب کنید:",
        "buttons": [
            "پرداخت کامل قبل از شروع",
            "پرداخت در محل",
            "پیش‌پرداخت + مابقی در محل"
        ],
        "multi_select": False,
        "confirm_button": "✔️ تایید",
        "back_button":   "🔙 بازگشت"
    },
    {
        "name":  "enter_prepayment_amount",
        "type":  "input",
        "field": "prepayment_amount",
        "prompt": "💵 لطفاً مبلغ پیش‌پرداخت را به تومان وارد کنید:",
        "validation": "integer",
        "conditional": {                    # Internal implementation note: legacy behavior is preserved during modernization.
            "field": "payment_method",
            "value": "پیش‌پرداخت + مابقی در محل"
        }
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "select_region",
        "type":  "buttons",
        "field": "region",
        "prompt": "🌍 لطفاً منطقه آگهی را انتخاب کنید:",
        "buttons": ["منطقه ۱", "منطقه ۲", "منطقه ۳", "منطقه ۴"],
        "multi_select": False,              # Internal implementation note: legacy behavior is preserved during modernization.
        "confirm_button": "✔️ تایید",
        "back_button":   "🔙 بازگشت"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "enter_publish_time",
        "type":  "input",
        "field": "publish_time",
        "prompt": "🕔 لطفاً ساعت انتشار آگهی را وارد کنید (مثال: 15:00)",
        "validation": "time"
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    {
        "name":  "preview_and_confirm",
        "type":  "preview",
        "prompt": "📄 پیش‌نمایش آگهی شما:",
        "confirm_button": "✅ تایید نهایی",
        "cancel_button":  "❌ لغو آگهی"
    }
]

moods = [
    "پاسخگو", "منظم", "دقیق", "حرفه‌ای",
    "صبور", "قابل اعتماد", "پیگیر", "خوش‌برخورد",
    "چشمگیر", "سرزنده", "سازمان‌یافته", "پرانرژی", "جسور", "خلاق",
    "اثرگذار", "حرفه‌ای", "پرانرژی", "پیشرو",
    "فعال", "حرفه‌ای", "متخصص", "آماده", "دقیق", "خلاق", "صبور", "آرام",
    "سریع", "منظم", "شفاف", "تازه‌کار", "باانگیزه"
]

styles = [
    "آماده", "چشمگیر", "حرفه‌ای", "پرانرژی",
    "رقابتی", "چشمگیر",
    "سریع", "اثرگذار", "پرانرژی",
    "خاص و سفارشی",
    "تجربه‌محور", "خوش‌ارائه", "چشمگیر",
    "دقیق", "منظم",
]

bodies = [
    "دیجیتال", "حضوری", "ترکیبی", "سیار",
    "سفارشی", "برون‌سپاری", "فنی",
    "سازمانی",
]
# Internal implementation note: legacy behavior is preserved during modernization.
DISPATCH_MODE_DB_MAP = {
    "مکان دار": "🏠 محل ثابت دارم",
    "ارائه در محل مشتری":  "🚗 ارائه در محل مشتری",
}

CLIENT_RUNNER_FLOW = {
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "get_code": {
        "label": "کد پرسنل",
        "position": 1,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": [],
        "dependencies": [],
        "on_skip": "next",          # Internal implementation note: legacy behavior is preserved during modernization.
        "on_fail": "restart",
        # Internal implementation note: legacy behavior is preserved during modernization.
        "handler_fn": "handle_staff_code",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,       # Internal implementation note: legacy behavior is preserved during modernization.
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "🧾",
            "input_type": "text",
            "description": "دریافت کد پرسنلی فعالِ امروز",
        },
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "get_region": {
        "label": "محدوده اعزام",
        "position": 2,
        "active": True,
        "skippable": False,          # Internal implementation note: legacy behavior is preserved during modernization.
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": ["get_code"],
        "dependencies": ["get_code"],
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "handle_region",
        # Internal implementation note: legacy behavior is preserved during modernization.
        "display_condition": None,
        "validation_fn": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "📍",
            "input_type": "text",
            "description": "دریافت محدوده مشتری در صورت ارائه در محل مشتری بودن کد",
        },
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "get_contact": {
        "label": "شماره تماس",
        "position": 5,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": None,
        "dependencies": None,
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "handle_contact",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "📞",
            "input_type": "contact",
            "description": "گرفتن شماره تلفن کاربر به صورت Contact",
        },
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "get_verification_photo_1": {
        "label": "سلفی اول",
        "position": 3,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": VERIFICATION_PHOTO_TIMEOUT,   # Internal implementation note: legacy behavior is preserved during modernization.
        "retries_allowed": 1,
        "required_fields": None,
        "dependencies": None,
        "on_skip": "fail",
        "on_fail": "restart",
        "handler_fn": "handle_verification_photo",      # Internal implementation note: legacy behavior is preserved during modernization.
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "🤳",
            "input_type": "photo",
            "description": "دریافت سلفی با ایموجی تصادفی (مرحله ۱)",
        },
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "get_verification_photo_2": {
        "label": "سلفی دوم",
        "position": 4,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": VERIFICATION_PHOTO_TIMEOUT,
        "retries_allowed": 1,
        "required_fields": None,
        "dependencies": None,
        "on_skip": "fail",
        "on_fail": "restart",
        "handler_fn": "handle_verification_photo",      # Internal implementation note: legacy behavior is preserved during modernization.
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "🤳",
            "input_type": "photo",
            "description": "دریافت سلفی با ایموجی دوم (مرحله ۲)",
        },
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "get_time": {
        "label": "ساعت درخواستی",
        "position": 6,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": ["get_code" , "get_region" , "get_contact"],
        "dependencies": ["get_code" , "get_region" , "get_contact"],
        "on_skip": "fail",
        "on_fail": "restart",
        "handler_fn": "handle_time",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "⏰",
            "input_type": "text",
            "description": "دریافت ساعت موردِ نظر برای سرویس",
        },
    },

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    "finished": {
        "label": "پایان",
        "position": 7,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 0,
        "required_fields": ["get_time" , "get_code"],
        "dependencies": ["get_time" , "get_code"],
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "finished",           # Internal implementation note: legacy behavior is preserved during modernization.
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,               # Internal implementation note: legacy behavior is preserved during modernization.
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "✅",
            "input_type": "system",
            "description": "نمایش پیام اتمام و پاک‌سازی state",
        },
    },
}
# Config/button names
BUTTONS.update({
    "manage_codes": "کدها"
})

# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
