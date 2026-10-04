from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    "fa": {
        "welcome": "سلام! به پلتفرم خوش آمدید. از منوی زیر یک بخش را انتخاب کنید.",
        "help": "راهنما:\\n/start شروع\\n/content نمایش محتوای منتشرشده\\n/app باز کردن Mini App\\n/help نمایش این راهنما",
        "app": "باز کردن Mini App",
        "content": "محتوا",
        "no_content": "هنوز محتوایی منتشر نشده است.",
        "admin_required": "دسترسی مدیریتی لازم است.",
        "admin_summary": "کاربران: {users}\\nچت‌ها: {chats}\\nمحتوا: {content}",
        "unknown": "پیام شما دریافت شد؛ برای شروع از /help استفاده کنید.",
    },
    "en": {
        "welcome": "Welcome. Choose a module from the menu below.",
        "help": "Help:\\n/start start\\n/content show published content\\n/app open the Mini App\\n/help show this help",
        "app": "Open Mini App",
        "content": "Content",
        "no_content": "No published content is available yet.",
        "admin_required": "Administrator access is required.",
        "admin_summary": "Users: {users}\\nChats: {chats}\\nContent: {content}",
        "unknown": "Message received. Use /help to see available commands.",
    },
}


def locale_for(language_code: str | None, default: str = "fa") -> str:
    candidate = (language_code or default).split("-")[0].lower()
    return candidate if candidate in MESSAGES else default


def text(key: str, locale: str, **values: object) -> str:
    template = MESSAGES.get(locale, MESSAGES["en"]).get(key, key)
    return template.format(**values)
