"""Legacy-compatible behavior preserved for this callable."""

from __future__ import annotations
from pathlib import Path
import random
import re
from io import BytesIO
from typing import Callable, Dict, List, Optional
import secrets
import pandas as pd
from telebot import TeleBot, types
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.config.settings import CHANNEL_ID , CLIENT_BOT_ID , STORAGE_CHANNEL , PHOTOS_CHANNEL
from html import escape
import threading
import time
from telegram_bot_platform.compat.utils.watermark import watermark_image
import json
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
logger = CustomLogger("codesManager")

BACK_BTN: str = "🔙 بازگشت"
VIEW_BTN: str = "👁 مشاهده"
EXPORT_BTN: str = "📤 خروجی اکسل"
NO_USERNAME_BTN: str = "🚫 ندارم"
PHOTO_ASK_TEXT = (
    "آیا ارسال عکس‌های شما تمام شد؟\n"
    "اگر همچنان قصد ارسال عکس دارید، عکس را با نادیده گرفتن این پیغام ارسال کنید."
)
WATERMARK_PATH = os.getenv("WATERMARK_PATH", str(Path(__file__).resolve().parents[5] / "resources" / "images" / "H_waterMark.png"))

_HOURS_LINE_RE = re.compile(
     r"^(?:⏰|🕒)?\s*\d{1,2}\s*(?:تا|-)\s*\d{1,2}.*$", re.MULTILINE
)

__all__=[n for n in globals() if not n.startswith("__")]
