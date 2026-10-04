"""Legacy-compatible behavior preserved for this callable."""

from __future__ import annotations

import inspect
import logging
import os
import re
import sys
import traceback
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from types import FrameType
from typing import Optional

# Internal implementation note: legacy behavior is preserved during modernization.
try:
    import arabic_reshaper  # type: ignore
    from bidi.algorithm import get_display  # type: ignore
except ImportError:  # pragma: no cover
    arabic_reshaper = None  # type: ignore
    get_display = None  # type: ignore

try:
    from colorama import Fore, Style, init as color_init  # type: ignore

    color_init(autoreset=True)
except ImportError:  # pragma: no cover
    Fore = Style = None  # type: ignore

# Internal implementation note: legacy behavior is preserved during modernization.
BASE_DIR: str = os.path.abspath(os.path.join(os.getcwd(), "Logs"))
LOG_ROOT: str = os.path.join(BASE_DIR, "logs")
CRASH_ROOT: str = os.path.join(BASE_DIR, "crash")
RETENTION_DAYS: int = 7  # Internal implementation note: legacy behavior is preserved during modernization.
MAX_BYTES: int = 2 * 1024 * 1024  # Internal implementation note: legacy behavior is preserved during modernization.
BACKUP_COUNT: int = 3  # Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
_INVALID_CHARS_PATTERN = r"[<>:\\\"/|?*]"


def _sanitize_filename(name: str) -> str:
    """Legacy-compatible behavior preserved for this callable."""
    return re.sub(_INVALID_CHARS_PATTERN, "_", name)

# Internal implementation note: legacy behavior is preserved during modernization.


class _ExactLevelFilter(logging.Filter):
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, level: int):
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        return record.levelno == self._level


class _ExceptionFilter(logging.Filter):
    """Legacy-compatible behavior preserved for this callable."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        return bool(record.exc_info)


# Internal implementation note: legacy behavior is preserved during modernization.

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _cleanup_old_logs(root: str) -> None:
    """Legacy-compatible behavior preserved for this callable."""

    threshold = datetime.now() - timedelta(days=RETENTION_DAYS)
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                if datetime.fromtimestamp(os.path.getmtime(fpath)) < threshold:
                    os.remove(fpath)
            except Exception:  # pragma: no cover
                pass


def _get_caller(stack_idx: int = 2) -> tuple[str, str]:
    """Legacy-compatible behavior preserved for this callable."""

    frame: FrameType = inspect.stack()[stack_idx].frame  # type: ignore[index]
    module = inspect.getmodule(frame)
    module_name: str = module.__name__ if module else "unknown_module"
    func_name: str = frame.f_code.co_name or "unknown_function"
    return module_name, func_name


# Internal implementation note: legacy behavior is preserved during modernization.
class CustomLogger(logging.Logger):
    """Legacy-compatible behavior preserved for this callable."""

    LEVEL_DIRS: dict[int | str, str] = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
        "EXCEPTION": "EXCEPTION",
    }

    _cleaned: bool = False
    _hooked: bool = False

    _FMT: str = "%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d - %(funcName)s()] | %(message)s"
    _DATEFMT: str = "%Y-%m-%d %H:%M:%S"

    def __init__(self, name: Optional[str] = None):
        # Internal implementation note: legacy behavior is preserved during modernization.
        module_name, func_name = _get_caller()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if func_name in ("<module>", "<lambda>", "<listcomp>", "<dictcomp>", "<genexpr>"):
            # Internal implementation note: legacy behavior is preserved during modernization.
            func_name = os.path.splitext(os.path.basename(module_name))[0]

        logger_name = name or f'{module_name}.{func_name}'
        super().__init__(logger_name)
        self.setLevel(logging.DEBUG)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not CustomLogger._cleaned:
            _ensure_dir(LOG_ROOT)
            _ensure_dir(CRASH_ROOT)
            _cleanup_old_logs(LOG_ROOT)
            _cleanup_old_logs(CRASH_ROOT)
            CustomLogger._cleaned = True

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not CustomLogger._hooked:
            sys.excepthook = self._crash_handler  # type: ignore[assignment]
            CustomLogger._hooked = True

        # Internal implementation note: legacy behavior is preserved during modernization.
        self._setup_file_handlers(module_name, func_name)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._setup_console_handler()

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _setup_file_handlers(self, module: str, func: str) -> None:
        # Internal implementation note: legacy behavior is preserved during modernization.
        module = _sanitize_filename(module)
        func = _sanitize_filename(func)

        for level_key, folder in CustomLogger.LEVEL_DIRS.items():
            if level_key == "EXCEPTION":
                level_const = logging.ERROR
                the_filter: logging.Filter = _ExceptionFilter()
            else:
                level_const = level_key  # type: ignore[assignment]
                the_filter = _ExactLevelFilter(level_const)

            dir_path = os.path.join(LOG_ROOT, module, func, folder)
            _ensure_dir(dir_path)
            file_path = os.path.join(dir_path, f'{func}.log')

            handler = RotatingFileHandler(
                file_path,
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding="utf-8",
            )
            handler.setLevel(level_const)
            handler.addFilter(the_filter)
            handler.setFormatter(logging.Formatter(
                CustomLogger._FMT, CustomLogger._DATEFMT))
            self.addHandler(handler)

    # Internal implementation note: legacy behavior is preserved during modernization.
    def _setup_console_handler(self) -> None:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(self._get_console_formatter())
        self.addHandler(console)

    def _get_console_formatter(self) -> logging.Formatter:
        if Fore is None or Style is None:
            # Internal implementation note: legacy behavior is preserved during modernization.
            return logging.Formatter(CustomLogger._FMT, CustomLogger._DATEFMT)

        class _Colored(logging.Formatter):
            COLOR_MAP = {
                logging.DEBUG: Fore.BLUE,
                logging.INFO: Fore.GREEN,
                logging.WARNING: Fore.YELLOW,
                logging.ERROR: Fore.RED,
                logging.CRITICAL: Fore.MAGENTA,
            }

            def format(self, record: logging.LogRecord) -> str:  # noqa: D401
                msg = super().format(record)

                # Internal implementation note: legacy behavior is preserved during modernization.
                if arabic_reshaper and get_display and re.search(r"[\u0600-\u06FF]", record.getMessage()):
                    try:
                        reshaped = arabic_reshaper.reshape(record.getMessage())
                        bidi_text = get_display(reshaped)
                        msg = msg.replace(record.getMessage(), bidi_text)
                    except Exception:  # pragma: no cover
                        pass

                color = _Colored.COLOR_MAP.get(record.levelno, "")
                return f'{color}{msg}{Style.RESET_ALL}'

        return _Colored(CustomLogger._FMT, CustomLogger._DATEFMT)

    # ---------------------- Crash Handler ----------------------
    def _crash_handler(self, exc_type, exc_value, exc_traceback):  # noqa: D401, N802
        module_name, func_name = _get_caller(3)  # Internal implementation note: legacy behavior is preserved during modernization.

        # Internal implementation note: legacy behavior is preserved during modernization.
        module_name = _sanitize_filename(module_name)
        func_name = _sanitize_filename(func_name)

        _ensure_dir(CRASH_ROOT)
        crash_file = os.path.join(
            CRASH_ROOT, f'{module_name}_{func_name}_crash.log')

        with open(crash_file, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            traceback.print_exception(
                exc_type, exc_value, exc_traceback, file=f)

        # Internal implementation note: legacy behavior is preserved during modernization.
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


# Internal implementation note: legacy behavior is preserved during modernization.

def get_logger(name: Optional[str] = None) -> CustomLogger:
    """Legacy-compatible behavior preserved for this callable."""

    return CustomLogger(name)
