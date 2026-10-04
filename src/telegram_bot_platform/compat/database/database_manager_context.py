# from logs.log import CustomLogger
# from DataBase_Manager import DatabaseManager
# from DataBase_Manager import DatabaseManager
# from typing import Any, Dict, List, Tuple
import types
from functools import wraps
import re
import sqlite3
import mysql.connector
import psycopg2
import pyodbc
import csv
import json
import re
import sys

import os
import logging
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
# import sys
import time
import threading
from persiantools.jdatetime import JalaliDateTime

import sys
import io
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if path not in sys.path:
    sys.path.append(path)
from datetime import datetime
from typing import Any, Dict, Optional

MYSQL_PLACEHOLDER = "%s"
SQLITE_PLACEHOLDER = "?"
# config.py
# Internal implementation note: legacy behavior is preserved during modernization.
# ----------------  Constants & Helpers  ----------------
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
INDEX_SAFE_COLUMNS: Dict[str, str] = {
    "telegram_id": "VARCHAR(191)",
    "chat_id": "VARCHAR(191)",
    "username": "VARCHAR(191)",
    "phone_number": "VARCHAR(20)",
    "U_code": "VARCHAR(191)",          # Internal implementation note: legacy behavior is preserved during modernization.
}
# Internal implementation note: legacy behavior is preserved during modernization.
DEFAULT_COLUMNS = {
    "id": {
        "sqlite": "INTEGER PRIMARY KEY AUTO_INCREMENT ",
        "mysql": "INT AUTO_INCREMENT PRIMARY KEY"
    },
    "created_at": {
        "sqlite": "TIMESTAMP",
        "mysql": "DATETIME"
    },
    "last_updated": {
        "sqlite": "TIMESTAMP",
        "mysql": "DATETIME"
    }
}
logger = CustomLogger()

# Internal implementation note: legacy behavior is preserved during modernization.
# MYSQL_TABLE_OPTIONS = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

# logger_manager.py
#########################
# Internal implementation note: legacy behavior is preserved during modernization.
#########################

# Internal implementation note: legacy behavior is preserved during modernization.
MYSQL_TABLE_OPTIONS = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

# Internal implementation note: legacy behavior is preserved during modernization.
DEFAULT_SQLITE_TYPE = "TEXT"

# Internal implementation note: legacy behavior is preserved during modernization.
DEFAULT_MYSQL_TYPE = "VARCHAR(255)"

# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
INDEX_SAFE_COLUMNS = {
    "telegram_id": "VARCHAR(191)",
    "username":    "VARCHAR(191)",
    "phone_number": "VARCHAR(20)"
}

# Internal implementation note: legacy behavior is preserved during modernization.
LOG_MESSAGES = {
    "table_created":       "✅ Table {table} successfully created",
    "table_exists":        "📄 Table {table} already exists",
    "column_added":        "➕ New column {column} (type: {dtype}) added",
    "column_skipped":      "⏭️ Column {column} already exists; skipping addition",
    "alias_applied":       "⚙️ Using alias parameter: columns → column_types",
    "mysql_type_warning":  "⚠️ Column {column} cannot be TEXT when indexed; please use VARCHAR"
}

# Internal implementation note: legacy behavior is preserved during modernization.
# ...

REGEX_PATTERNS = {
    "UUID": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    "EMAIL": r"^[\w\.-]+@[\w\.-]+\.\w+$",
    "URL": r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
    "IPV4": r"^(?:\d{1,3}\.){3}\d{1,3}$",
    "IPV6": r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
    "JSON": r"^(?:\{.*\}|\[.*\])$",
    "XML": r"^<\?xml.*\?>",
}

# Internal implementation note: legacy behavior is preserved during modernization.
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
]
TIME_FORMATS = [
    "%H:%M:%S",
    "%H:%M",
]
DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M",
]

# Internal implementation note: legacy behavior is preserved during modernization.
DEFAULT_VARCHAR_LENGTH = 255
TEXT_THRESHOLD = 1000  # Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
SQL_TYPE_MAPPING = {
    "UUID": "CHAR(36)",
    "EMAIL": f"VARCHAR({DEFAULT_VARCHAR_LENGTH})",
    "URL": f"VARCHAR({DEFAULT_VARCHAR_LENGTH})",
    "IPV4": "VARCHAR(15)",
    "IPV6": "VARCHAR(45)",
    "JSON": "JSON",
    "XML": "TEXT",
    "INTEGER": "INT",
    "BIGINT": "BIGINT",
    "FLOAT": "FLOAT",
    "DECIMAL": "DECIMAL(38,10)",
    "BOOLEAN": "BOOLEAN",
    "DATE": "DATE",
    "TIME": "TIME",
    "DATETIME": "DATETIME",
    "TIMESTAMP": "TIMESTAMP",
    "VARCHAR": f"VARCHAR({DEFAULT_VARCHAR_LENGTH})",
    "TEXT": "TEXT",
}

# type_inferer.py
# -*- coding: utf-8 -*-
"""
ماژول حرفه‌ای تشخیص نوع داده از رشته و نگاشت به نوع SQL
شامل معماری extensible با استفاده از Chain of Responsibility
"""

# Internal implementation note: legacy behavior is preserved during modernization.


class BaseDetector:
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        raise NotImplementedError


class RegexDetector(BaseDetector):
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        for name, pattern in REGEX_PATTERNS.items():
            if re.match(pattern, text):
                return name
        return None


class JSONDetector(BaseDetector):
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        try:
            if re.match(REGEX_PATTERNS['JSON'], text):
                json.loads(text)
                return 'JSON'
        except json.JSONDecodeError:
            pass
        return None


class NumericDetector(BaseDetector):
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        # Internal implementation note: legacy behavior is preserved during modernization.
        if re.fullmatch(r"^-?\d+$", text):
            val = int(text)
            return 'BIGINT' if abs(val) > 2**31 - 1 else 'INTEGER'
        # Internal implementation note: legacy behavior is preserved during modernization.
        if re.fullmatch(r"^-?\d+\.\d+(?:[eE][-+]?\d+)?$", text):
            return 'DECIMAL'
        return None


class BoolDetector(BaseDetector):
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        if text.lower() in ('true', 'false', '0', '1'):
            return 'BOOLEAN'
        return None


class DateTimeDetector(BaseDetector):
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        # DATETIME
        for fmt in DATETIME_FORMATS:
            try:
                datetime.strptime(text, fmt)
                return 'DATETIME'
            except ValueError:
                continue
        # DATE
        for fmt in DATE_FORMATS:
            try:
                datetime.strptime(text, fmt)
                return 'DATE'
            except ValueError:
                continue
        # TIME
        for fmt in TIME_FORMATS:
            try:
                datetime.strptime(text, fmt)
                return 'TIME'
            except ValueError:
                continue
        return None


class TextDetector(BaseDetector):
    """Legacy-compatible behavior preserved for this callable."""

    def detect(self, text: str) -> Optional[str]:
        length = len(text)
        if length > TEXT_THRESHOLD:
            return 'TEXT'
        return 'VARCHAR'


class TypeInferer:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, detectors: Optional[List[BaseDetector]] = None):
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.detectors: List[BaseDetector] = detectors or [
            JSONDetector(), RegexDetector(), NumericDetector(
            ), BoolDetector(), DateTimeDetector(), TextDetector()
        ]

    def infer(self, value: Any) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if value is None or (isinstance(value, str) and not value.strip()):
            logger.debug("مقدار None یا خالی دریافت شد، پیش‌فرض VARCHAR")
            return SQL_TYPE_MAPPING['VARCHAR']

        text = str(value).strip()
        for detector in self.detectors:
            dtype = detector.detect(text)
            if dtype:
                sql = SQL_TYPE_MAPPING.get(dtype, SQL_TYPE_MAPPING['VARCHAR'])
                logger.info(
                    f"Value '{text}' detected as {dtype}, mapped to {sql}")
                return sql
        # Internal implementation note: legacy behavior is preserved during modernization.
        logger.info(f"Value '{text}' not matched, default VARCHAR")
        return SQL_TYPE_MAPPING['VARCHAR']

    def infer_batch(self, values: List[Any]) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        return [self.infer(v) for v in values]

__all__ = [name for name in globals() if not name.startswith('__')]
