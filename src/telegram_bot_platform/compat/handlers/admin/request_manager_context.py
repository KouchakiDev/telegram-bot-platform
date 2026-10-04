
# -*- coding: utf-8 -*-
"""Legacy-compatible behavior preserved for this callable."""
# from datetime import date
# from time import min
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import json
import sqlite3
from datetime import datetime, timedelta, time, date
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
# from telegram_bot_platform.compat.logging_ext.logger import Customlog
from telegram_bot_platform.compat.config.settings import *
from telegram_bot_platform.compat.utils.media_sender import MediaSender
import random
import inspect    # Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.utils.notification_manager import NotificationManager
from telegram_bot_platform.compat.utils.listing_publish_scheduler import AdPublishScheduler
import json
import html
import re
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot_platform.compat.utils.show_staff_profile import StaffProfileHandler
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.utils.task_manager import ThreadManager
import json
import html
import random
from typing import Dict, List, Optional ,Callable
import requests
import os
from datetime import datetime
# from telegram_bot_platform.compat.runners.admin_runner import AdminBot
# Internal implementation note: legacy behavior is preserved during modernization.
log = CustomLogger("requests.log")
logger = log
import re
import logging
from typing import Union
import json
import re
import telebot.apihelper

MAX_TELEGRAM_CHARS = 3900   
# Mapping for Persian to English digits
# Internal implementation note: legacy behavior is preserved during modernization.
PHONE_PT = re.compile(r"""
    ^\s*                                   # شروع با فاصله اختیاری
    (?:(?:\+|00)?98|0)?                    # پیش‌شماره‌های مجاز  +98 / 0098 / 98 / 0  (اختیاری)
    [\s\-]*                                # جداکنندهٔ اختیاری
    9                                       # همهٔ موبایل‌های ایران با 9 شروع می‌شوند
    (?:\d[\s\-]*){9}                       # 9 رقمِ بعدی با امکان خط تیره یا فاصله
    \s*$                                   # پایان
""", re.VERBOSE)

import re

_P2E = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")   # Persian-to-English

__all__=[n for n in globals() if not n.startswith('__')]
