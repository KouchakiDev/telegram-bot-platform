from __future__ import annotations

from .database_manager_context import *


class M_DatabaseManagerSettingsMixin:
    def create_bot_settings_table(self):
        """Create bot_settings table for configuration."""
        try:
            conn = self._get_connection()
            cursor = self._get_cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT ,
                    request_type TEXT UNIQUE,
                    categorization_column TEXT,
                    sorting_columns TEXT
                )
            ''')

            conn.commit()

            logger.info("Table bot_settings created or already exists.")
        except Exception as e:
            logger.error(f"Error creating bot_settings table: {e}")
        finally:
            cursor.close()
            self.close()

    def get_settings(self, key: str) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        sql = (
            f"SELECT {self.qname('value')} "
            f"FROM {self.qname('bot_settings')} "
            f"WHERE {self.qname('key')} = {self.placeholder}"
        )
        rows = self.fetch_data(sql, (key,))
        return rows[0][0] if rows else None

    def create_auto_settings_table(self):
        """Legacy-compatible behavior preserved for this callable."""
        columns = {
            "table_name": "VARCHAR(191) UNIQUE",  # Internal implementation note: legacy behavior is preserved during modernization.
            "auto_approval_enabled": "INTEGER DEFAULT 0",
            "auto_threshold": "INTEGER",
            "auto_timer": "INTEGER",
            "auto_check_interval": "INTEGER DEFAULT 20"
        }
        self.ensure_table_and_columns("auto_settings", columns=columns)

    def get_auto_settings(self, table_name: str) -> dict:
        """Legacy-compatible behavior preserved for this callable."""
        result = self.select_dict(
            "auto_settings", "table_name = ?", (table_name,))
        if result:
            return result[0]
        else:
            return {
                "table_name": table_name,
                "auto_approval_enabled": 0,
                "auto_threshold": None,
                "auto_timer": None,
                "auto_check_interval": 20
            }

    def set_auto_settings(self, table_name: str, settings: dict) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        data = {
            "table_name": table_name,
            "auto_approval_enabled": settings.get("auto_approval_enabled", 0),
            "auto_threshold": settings.get("auto_threshold"),
            "auto_timer": settings.get("auto_timer"),
            "auto_check_interval": settings.get("auto_check_interval", 20)

        }
        self.upsert("auto_settings", data, key="table_name")

    def set_settings(self, key: str, value: str):
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            sql = (
                f"INSERT OR REPLACE INTO {self.qname('bot_settings')} "
                f"({self.qname('key')},{self.qname('value')}) "
                f"VALUES ({self.placeholder},{self.placeholder})"
            )
        else:
            sql = (
                f"INSERT INTO {self.qname('bot_settings')} "
                f"({self.qname('key')},{self.qname('value')}) "
                f"VALUES ({self.placeholder},{self.placeholder}) "
                f"ON DUPLICATE KEY UPDATE "
                f"{self.qname('value')} = VALUES({self.qname('value')})"
            )
        self.execute_query(sql, (key, value))

    def get_bot_settings(self, table_name):
        query = """
            SELECT categorization_column, display_columns, max_requests_per_row, request_overview, request_details, ignored_columns 
            FROM bot_settings 
            WHERE table_name = ?
        """
        # conn = self._get_connection()
        cursor = self._get_cursor()
        cursor.execute(query, (table_name,))
        result = cursor.fetchone()
        cursor.close()
        self.close()
        if result:
            cat_col, disp_cols, max_per_row, overview, details, ignored_cols = result
            disp_cols = disp_cols.split(",") if disp_cols else []
            ignored = ignored_cols.split(",") if ignored_cols else []
            return {
                "categorization_column": cat_col,
                "display_columns": disp_cols,
                "max_requests_per_row": max_per_row,
                "request_overview": overview or "",
                "request_details": details or "",
                "ignored_columns": ignored
            }
        else:
            return None

    def create_rejection_reasons_table(self):
        """Create rejection_reasons table for storing rejection reasons."""
        try:
            conn = self._get_connection()
            cursor = self._get_cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rejection_reasons (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT ,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            cursor.close()
            logger.info("Table rejection_reasons created or already exists.")
        except Exception as e:
            logger.error(f"Error creating rejection_reasons table: {e}")
        finally:
            cursor.close()
            self.close()

    def get_current_user(self) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            return "sqlite_user"
        else:
            row = self.fetch_data("SELECT CURRENT_USER()", ())
            return row[0][0]
