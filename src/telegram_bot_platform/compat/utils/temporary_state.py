# utils/cb_state_utils.py
import json
from typing import Dict, Any
from telegram_bot_platform.compat.database.database_manager import DatabaseManager

import json


def clean_state_for_json(state: dict) -> dict:
    """Legacy-compatible behavior preserved for this callable."""
    if isinstance(state, dict):
        cleaned = {}
        for k, v in state.items():
            if isinstance(v, set):
                cleaned[k] = list(v)
            elif isinstance(v, dict):
                cleaned[k] = clean_state_for_json(v)
            else:
                cleaned[k] = v
        return cleaned
    else:
        return state


def save_filter_snapshot(
    db: DatabaseManager,
    chat_id: int,
    state: Dict[str, Any],
    retention_days: int = 3,
) -> int:
    """Legacy-compatible behavior preserved for this callable."""
    # Internal implementation note: legacy behavior is preserved during modernization.
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS cb_state (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            chat_id       VARCHAR(255) UNIQUE,  
            json_state    JSON,                    
            last_updated  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)


    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    db.execute_query(
        "DELETE FROM cb_state "
        "WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)",
        (retention_days,)          # Internal implementation note: legacy behavior is preserved during modernization.
    )
    
    state = clean_state_for_json(state)
    # Internal implementation note: legacy behavior is preserved during modernization.
    db.upsert(
        "cb_state",
        {"chat_id": chat_id, "json_state": json.dumps(
            state, ensure_ascii=False)},
        "chat_id"        # Internal implementation note: legacy behavior is preserved during modernization.
    )
    return chat_id        # Internal implementation note: legacy behavior is preserved during modernization.


def load_filter_snapshot(db: DatabaseManager, chat_id: int) -> Dict[str, Any]:
    """Legacy-compatible behavior preserved for this callable."""
    rows = db.select_dict("cb_state", "chat_id = ?", (chat_id,))
    if rows:
        return json.loads(rows[0]["json_state"])
    return {}
