from telegram_bot_platform.compat.config.settings import *

from telebot import types

from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from datetime import datetime
import telebot
from telebot.types import Message
import json
from datetime import datetime
import re
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
logger = CustomLogger()  # log_file="services.log")
log = logger
BACK_TO_PANEL     = BUTTONS["back_to_pannel"]   # Internal implementation note: legacy behavior is preserved during modernization.
BACK_GENERIC      = BUTTONS["back"]             # Internal implementation note: legacy behavior is preserved during modernization.
START_CMD_PREFIXES = ("/start",)    
BACK_TEXTS = {BUTTONS["back"],  BUTTONS["back_to_pannel"]}

__all__=[n for n in globals() if not n.startswith("__")]
