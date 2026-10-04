from telegram_bot_platform.compat.config.settings import *

from telebot import types

from datetime import datetime
from telegram_bot_platform.compat.handlers.admin.request_manager import RequestManager
from telebot import types

import json

import re

from datetime import datetime
import jdatetime
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="requests.log")

_P2E = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")   # Persian-to-English

log = logger

__all__=[n for n in globals() if not n.startswith("__")]
