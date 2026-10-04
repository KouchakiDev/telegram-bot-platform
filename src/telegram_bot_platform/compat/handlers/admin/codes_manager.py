from __future__ import annotations

from .codes_manager_context import *
from .codes_manager_core import CodesManagerCoreMixin
from .codes_manager_flows import CodesManagerFlowsMixin
from .codes_manager_data import CodesManagerDataMixin
from .codes_manager_integrations import CodesManagerIntegrationsMixin


class CodesManager(CodesManagerCoreMixin, CodesManagerFlowsMixin, CodesManagerDataMixin, CodesManagerIntegrationsMixin):
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(
        self,
        bot: TeleBot,
        db: DatabaseManager,
        back_callback: Callable,
        start_callback: Callable,
    ) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.db = db
        self.start_callback = start_callback
        self.back_callback = back_callback
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._state: Dict[int, Dict[str, str]] = {}
        self.user_state: Dict[int, Dict[str, str]] = {}
        self._photo_timers: Dict[int, threading.Timer] = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._STATE_MAP: Dict[str, Callable] = {
            "start": self.start_callback,
            "root": self.show_root_menu,
            "add": self._start_add,
            "edit": self._start_edit,
            "delete": self._start_delete,
            "activity": self._start_activity,
            "view": self._start_view,  # Internal implementation note: legacy behavior is preserved during modernization.
        }
        self._kb_timer: Optional[threading.Timer] = None
              # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_message_handler(self._on_new_photo, content_types=["photo"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_callback_query_handler(self._on_photos_done, func=lambda c: c.data == "photos_done")
        try:
            self.db.execute_query("ALTER TABLE codes ADD COLUMN username varchar(100);")
        except Exception as exc:
            logger.warning("ALTER TABLE skipped · err=%s", exc)


