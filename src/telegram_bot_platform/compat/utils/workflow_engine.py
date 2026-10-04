from __future__ import annotations

from .workflow_engine_context import *
from .workflow_engine_lifecycle import WorkstationEngineLifecycleMixin
from .workflow_engine_execution import WorkstationEngineExecutionMixin
from .workflow_engine_navigation import WorkstationEngineNavigationMixin
from .workflow_engine_persistence import WorkstationEnginePersistenceMixin


class WorkstationEngine(WorkstationEngineLifecycleMixin, WorkstationEngineExecutionMixin, WorkstationEngineNavigationMixin, WorkstationEnginePersistenceMixin):
    """Legacy-compatible behavior preserved for this callable."""

# ---------------------------------------------------------------------------
# TEST CLASS - WRITE BY $O5hA/\/
# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------

WORKSTATION_FLOW_EXAMPLE: Dict[str, Dict[str, Any]] = {
    "get_code": {
        "label": "Staff Code",
        "position": 1,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": [],
        "dependencies": [],
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "handle_get_code",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "🧾",
            "input_type": "text",
            "description": "Ask the user for a valid staff code.",
        },
    },
    "verify_code": {
        "label": "Verify Code",
        "position": 2,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": ["get_code"],
        "dependencies": ["get_code"],
        "on_skip": "fail",
        "on_fail": "notify_admin",
        "handler_fn": "handle_verify_code",
        "validation_fn": None,
        "display_condition": "True",
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "✅",
            "input_type": "text",
            "description": "Verify the staff code provided by user.",
        },
    },
}


# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------


class SampleBotHandler:
    """Legacy-compatible behavior preserved for this callable."""

    def workstation_contract(self) -> Dict[str, Dict[str, Any]]:  # noqa: D401
        """Legacy-compatible behavior preserved for this callable."""
        return {
            "get_code": {
                "handler": self._handle_get_code,
                "input_type": "text",
                "description": "Receives the staff code from the user.",
                "preview_fn": None,
            },
            "verify_code": {
                "handler": self._handle_verify_code,
                "input_type": "text",
                "description": "Verifies the staff code with backend.",
                "preview_fn": None,
            },
        }

    # Internal implementation note: legacy behavior is preserved during modernization.

    def _handle_get_code(self, user_id: str, message: Any) -> str:  # noqa: ANN401
        """Legacy-compatible behavior preserved for this callable."""
        logger.debug("Handling 'get_code' for user '%s' with message '%s'", user_id, message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        return "dummy_code"

    def _handle_verify_code(self, user_id: str, message: Any) -> bool:  # noqa: ANN401
        """Legacy-compatible behavior preserved for this callable."""
        logger.debug("Handling 'verify_code' for user '%s' with message '%s'", user_id, message)
        # Internal implementation note: legacy behavior is preserved during modernization.
        return True


# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    bot = SampleBotHandler()
    engine = WorkstationEngine(flow_config=WORKSTATION_FLOW_EXAMPLE, target_object=bot)
    user = "u123"
    engine.on_start(user)
    engine.execute_step(user, "get_code", message="123456")
    engine.execute_step(user, "verify_code", message="123456")
    engine.on_finish(user)
