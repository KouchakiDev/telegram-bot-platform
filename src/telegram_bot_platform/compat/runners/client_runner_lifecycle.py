from __future__ import annotations

from .client_runner_context import *


class ClientRunnerLifecycleMixin:
    def run(self, skip_pending: bool = True) -> None:  # noqa: D401
        """Start the *infinite* polling loop."""
        self.bot.infinity_polling(skip_pending=skip_pending)
    def workstation_contract(self) -> Dict[str, Dict[str, Any]]:  # noqa: D401
        """Legacy-compatible behavior preserved for this callable."""
        return self._contract
    def user_blocked(self , message ):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if message:
                telegram_id = message.from_user.id
                rows = self.db.select_dict(
                    table="clients",
                    condition="telegram_id = ? AND status = 'blocked'",
                    params=(telegram_id,)
                )
                if rows:
                    self.log.info(f"[CHECK_PENDING] chat={telegram_id} has pending request")
                    return True
                else:
                    return False
            else:
                return False
        except Exception as exc:
            self.log.exception(f"[CHECK_PENDING] failed: {exc}")
            return False
