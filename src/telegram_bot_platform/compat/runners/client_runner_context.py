# -*- coding: utf-8 -*-
"""Legacy-compatible behavior preserved for this callable."""
from __future__ import annotations
import os
from pathlib import Path
import sys
import re
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, '..'))

import inspect
from typing import Any, Callable, Dict, Optional
import random
import io, threading
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import TeleBot, types 
from telebot.types import ReplyKeyboardMarkup , ReplyKeyboardRemove , KeyboardButton ,InlineKeyboardButton , InlineKeyboardMarkup
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.utils.workflow_engine import WorkstationEngine, StepExecutionError
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import HAND_VERFIY , STORAGE_CHANNEL , BOT_ADMIN_TOKEN   
from telegram_bot_platform.compat.runners.starter import Starter   
import time               # Internal implementation note: legacy behavior is preserved during modernization.
import threading          # Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
import json
PHOTO_DELAY = 10        # Internal implementation note: legacy behavior is preserved during modernization.

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
BACK_BTN        = '🔙 بازگشت'
CONFIRM_BTN     = '✅ همینو میخوام'
OTHER_CODES_BTN = '👀 کدهای دیگر'
IMAGES_DIR     = os.getenv("IMAGES_DIR", str(Path(__file__).resolve().parents[5] / "resources" / "images"))
VNT      = str(Path(__file__).resolve().parents[5] / "resources" / "training" / "VideoNoteTrain.mp4")
CANCEL_BTN = "از درخواست خود منصرف شدم 🚫"
admin_username = os.getenv("ADMIN_SUPPORT_USERNAME", "").strip()
# ---------------------------------------------------------------------------
# Helper decorator to flag handler methods
# ---------------------------------------------------------------------------
HandlerFn = Callable[[str, Any], Any]

def step_handler(step_name: str) -> Callable[[HandlerFn], HandlerFn]:
    """Decorator that marks a method as the *handler* for **step_name**."""

    def decorator(fn: HandlerFn) -> HandlerFn:
        setattr(fn, "_step_name", step_name)
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

__all__=[n for n in globals() if not n.startswith('__')]
