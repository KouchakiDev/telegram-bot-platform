from __future__ import annotations

import time
from collections import OrderedDict


class SlidingWindowGate:
    def __init__(self, max_entries: int, requests: int, window_seconds: float) -> None:
        self.max_entries = max_entries
        self.requests = requests
        self.window_seconds = window_seconds
        self._history: OrderedDict[int, list[float]] = OrderedDict()

    def allow(self, key: int) -> bool:
        now = time.monotonic()
        history = [stamp for stamp in self._history.get(key, []) if now - stamp < self.window_seconds]
        if len(history) >= self.requests:
            self._history[key] = history
            self._history.move_to_end(key)
            return False
        history.append(now)
        self._history[key] = history
        self._history.move_to_end(key)
        while len(self._history) > self.max_entries:
            self._history.popitem(last=False)
        return True
