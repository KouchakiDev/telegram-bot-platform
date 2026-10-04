# -*- coding: utf-8 -*-
"""Legacy-compatible behavior preserved for this callable."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from collections import deque   # Internal implementation note: legacy behavior is preserved during modernization.

# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------

logger = CustomLogger("WorkStationEngine")


# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------


class StepNotImplementedError(NotImplementedError):
    """Legacy-compatible behavior preserved for this callable."""


class StepConfigError(RuntimeError):
    """Legacy-compatible behavior preserved for this callable."""


class StepExecutionError(RuntimeError):
    """Legacy-compatible behavior preserved for this callable."""


# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------

__all__ = [name for name in globals() if not name.startswith('__')]
