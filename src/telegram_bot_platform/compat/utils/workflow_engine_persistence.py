from __future__ import annotations

from .workflow_engine_context import *


class WorkstationEnginePersistenceMixin:
    def _memory_persistence(self, user_id: str, key: str, value: Any) -> None:  # noqa: ANN401
        """Legacy-compatible behavior preserved for this callable."""
        state = self._user_states.setdefault(user_id, {})
        state[key] = value
        logger.debug("State saved for user '%s': %s=%s", user_id, key, value)

    def _get_user_role(self, user_id: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        return "guest"

    def _notify_admin(self, step_name: str, user_id: str, exc: Exception | str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        logger.error("Admin notified: step '%s' for user '%s' failed – %s", step_name, user_id, exc)

    def export_contract_json(self) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            export_data: Dict[str, Any] = {}
            for step, meta in self._contract.items():
                export_data[step] = {
                    "input_type": meta.get("input_type"),
                    "description": meta.get("description"),
                    "preview": bool(meta.get("preview_fn")),
                }
            return json.dumps(export_data, ensure_ascii=False, indent=2)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to export contract json: %s", exc, exc_info=True)
            raise
