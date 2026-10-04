from __future__ import annotations

from .database_manager_context import *
from .database_manager_core import DatabaseManagerCoreMixin
from .database_manager_flows import DatabaseManagerFlowsMixin
from .database_manager_data import DatabaseManagerDataMixin
from .database_manager_integrations import DatabaseManagerIntegrationsMixin


class DatabaseManager(DatabaseManagerCoreMixin, DatabaseManagerFlowsMixin, DatabaseManagerDataMixin, DatabaseManagerIntegrationsMixin):
    def __init__(self, db_type: str, db_name: str, host: Optional[str] = None,
                 user: Optional[str] = None, password: Optional[str] = None,
                 column_types: Optional[Dict[str, str]] = None,
                 column_types_file: Optional[str] = None):
        """
        DatabaseManager class for managing multiple database types:
        - SQLite
        - MySQL
        - PostgreSQL
        - Microsoft SQL Server
        Features:
        - Table creation, deletion, and modification
        - Column management (add, rename, delete)
        - Data insertion, update, and deletion
        - Transaction handling with commit/rollback
        - Backup and restore (SQL and CSV)
        - Performance optimization
        - User and permission management
        - Index, view, trigger, sequence, function, and procedure management
        Args:
            db_type (str): Type of database ('sqlite', 'mysql', 'postgresql', 'mssql')
            db_name (str): Database name
            host (str, optional): Server host (for non-SQLite databases)
            user (str, optional): Database username
            password (str, optional): Database password
            column_types (Dict[str, str], optional): Column type dictionary
            column_types_file (str, optional): Path to JSON file for column types
        """
        self.db_type = db_type.lower()
        self.db_name = db_name
        self.host = host
        self.user = user
        self.password = password
        self.column_types = column_types or {}
        self.column_types_file = column_types_file
        self.connection = None
        self.cursor = None
        self.transaction_level = 0
        self.query_cache = {}
        self.lock = threading.Lock()
        self._load_column_types_from_file()
        self._initialize_connection()
        logger.info(
            f"Database {self.db_type} with name {self.db_name} initialized.")


if __name__ == "__main__":
    db = DatabaseManager(db_type="sqlite", db_name="test.db")
    db.create_table(
        "users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})
    db.insert("users", {"name": "Ali", "age": 30})
    db.update("users", {"age": 31}, "name = ?", ("Ali",))
    db.delete("users", "name = ?", ("Ali",))
    db.close()
