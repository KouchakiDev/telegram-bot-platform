from __future__ import annotations

from .workflow_engine_context import *


class WorkstationEngineNavigationMixin:
    def _previous_active_step(self, current_step: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if current_step not in self._flow:
                logger.error("Current step '%s' not found in flow.", current_step)
                raise StepConfigError("مرحله فعلی در جریان کاری تعریف نشده است.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            cur_pos: int = self._flow[current_step].get("position", 0)

            # Internal implementation note: legacy behavior is preserved during modernization.
            prev_steps = [
                (name, cfg)
                for name, cfg in self._flow.items()
                if cfg.get("active", True) and cfg.get("position", 0) < cur_pos
            ]

            if not prev_steps:
                logger.info("No previous active step before '%s'.", current_step)
                raise StepConfigError("مرحلهٔ قبلی فعّالی وجود ندارد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            return max(prev_steps, key=lambda item: item[1].get("position", 0))[0]

        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error in _previous_active_step: %s", exc)
            raise

    def execute_prev(self, user_id: str, message: Any):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            step: Optional[str] = self._user_states.get(user_id, {}).get("current_step")
            while True:
                prev_step = self._previous_active_step(step)
                prev_conf = self._flow[prev_step]
                # Internal implementation note: legacy behavior is preserved during modernization.
                if prev_conf.get("skippable") and \
                   not self._evaluate_condition(prev_conf.get("display_condition"), user_id):
                    self._skip_step(user_id, prev_step, reason="auto-back-skip")
                    step = prev_step
                    continue
                break                     # Internal implementation note: legacy behavior is preserved during modernization.

            self._persist(user_id, "current_step", prev_step)
            return self.execute_step(user_id, prev_step, message)

        except StepConfigError:
            # Internal implementation note: legacy behavior is preserved during modernization.
            raise

        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to execute previous step for user %s: %s", user_id, exc)
            raise

    def get_missing_steps(self) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        return [name for name in self._flow if name not in self._contract]

    def get_unconfigured_steps(self) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        return [name for name in self._contract if name not in self._flow]

    def get_step_summary(self) -> List[Dict[str, Any]]:
        """Legacy-compatible behavior preserved for this callable."""
        summary: List[Dict[str, Any]] = []
        for name, conf in sorted(self._flow.items(), key=lambda item: item[1].get("position", 0)):
            summary.append(
                {
                    "name": name,
                    "active": conf.get("active", True),
                    "skippable": conf.get("skippable", False),
                    "position": conf.get("position"),
                    "implemented": name in self._contract,
                }
            )
        return summary
