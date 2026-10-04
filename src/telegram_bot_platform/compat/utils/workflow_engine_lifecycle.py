from __future__ import annotations

from .workflow_engine_context import *


class WorkstationEngineLifecycleMixin:
    def __init__(
        self,
        flow_config: Dict[str, Dict[str, Any]],
        target_object: Any,
        *,
        persistence_adapter: Optional[Callable[[str, str, Any], None]] = None,
    ) -> None:
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not hasattr(target_object, "workstation_contract"):
                raise AttributeError("Target object must implement 'workstation_contract()')")

            self._flow: Dict[str, Dict[str, Any]] = flow_config
            self._target = target_object
            self._contract: Dict[str, Dict[str, Any]] = self._target.workstation_contract()
            self._normalize_positions()          # Internal implementation note: legacy behavior is preserved during modernization.

            self._persist = persistence_adapter or self._memory_persistence
            self._user_states: Dict[str, str] = {}  # user_id -> current step

            # Internal implementation note: legacy behavior is preserved during modernization.
            self._validate_flow_and_contract()
            logger.info("WorkstationEngine initialized successfully.")
        except Exception as exc:  # noqa: BLE001
            logger.error("Engine initialization failed: %s", exc, exc_info=True)
            raise

    def reset_state(self, user_id: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            previous_state = self._user_states.pop(user_id, None)
            logger.debug("State reset for user %s (previous: %s)", user_id, previous_state)

        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to reset state for user %s: %s", user_id, exc)
            raise

    def on_start(self, user_id: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        logger.info("Flow started for user '%s'", user_id)

    def on_finish(self, user_id: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        logger.info("Flow finished for user '%s'", user_id)

    def on_cancel(self, user_id: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        logger.info("Flow cancelled for user '%s'", user_id)
