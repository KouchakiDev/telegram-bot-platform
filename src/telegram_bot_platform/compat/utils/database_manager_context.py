from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
import sqlite3
import mysql.connector
import psycopg2
import pyodbc
import csv
import json
import os
import logging
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
import sys
import time
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Setup logging with CustomLogger
logger = CustomLogger()  # log_file='database.log', log_level=logging.DEBUG)

__all__=[n for n in globals() if not n.startswith("__")]
