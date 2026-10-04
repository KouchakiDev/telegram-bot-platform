# booking_ads_requests.py

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import json
from telegram_bot_platform.compat.config.settings import *  # Internal implementation note: legacy behavior is preserved during modernization.
from datetime import datetime ,timedelta 
from telegram_bot_platform.compat.handlers.client.verification.identity_verification import *
import re
from telebot import types , TeleBot
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
# services/identity_verification_service.py
# from database.DataBaseManager import DatabaseManager
import json
# from telegram_bot_platform.compat.handlers.client.premium.premium_profile import PREMIUMProfileH
from telegram_bot_platform.compat.handlers.client.premium.premium_registeration import PREMIUMRegistration
from telegram_bot_platform.compat.handlers.client.premium.premium_profile import PREMIUMProfile
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
log = CustomLogger("booking_ads")
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# from telegram_bot_platform.compat.config.settings import CLIENT_BOT_USERNAME, CHANNEL_ID, BUTTONS
# from datetime import datetime
import html

__all__=[n for n in globals() if not n.startswith("__")]
