from __future__ import annotations

from .database_manager_context import *


class M_DatabaseManagerLifecycleMixin:
    def _get_connection(self):
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        if hasattr(self.local, "connection"):
            try:
                if self.local.connection.is_connected():
                    return self.local.connection
            except Exception as e:
                logger.warning(f"[Connection] Detected broken connection: {e}")
                self.reset_all_connections()


        # Internal implementation note: legacy behavior is preserved during modernization.
        self.local.connection = self._connect()

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not self.local.connection.autocommit:
            self.local.connection.autocommit = True

        return self.local.connection

    def _get_cursor(self):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            conn = self._get_connection()
            if conn is None:
                raise ConnectionError("Connection is None")
            return conn.cursor(buffered=True)
        except Exception as e:
            logger.error(f"[Cursor] Error getting cursor: {e}")
            self.reset_all_connections()
            conn = self._get_connection()
            return conn.cursor(buffered=True)

    def _connect(self):
        """Create a connection based on database type."""
        try:
            if self.db_type == "sqlite":
                return sqlite3.connect(self.db_name, check_same_thread=False)
            elif self.db_type == "mysql":
                conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.db_name,
                    autocommit=True,
                    pool_name="lotus_pool",
                    pool_size=8,
                    charset="utf8mb4",
                    use_unicode=True
                )
                # Internal implementation note: legacy behavior is preserved during modernization.
                conn.cursor().execute(
                    "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"
                )
                return conn

            elif self.db_type == "postgresql":
                return psycopg2.connect(dbname=self.db_name, user=self.user, password=self.password, host=self.host)
            elif self.db_type == "mssql":
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host};DATABASE={self.db_name};UID={self.user};PWD={self.password}"
                return pyodbc.connect(conn_str)
            else:
                raise ValueError(
                    f"Database type {self.db_type} is not supported.")
        except Exception as e:
            logger.error(f"Error creating connection: {e}")
            raise

    def adapt_condition_placeholders(self, condition: str) -> str:
        if self.placeholder == "%s":
            if isinstance(condition, str):
                return condition.replace("?", "%s")
            else:
                return condition
        return condition

    def close(self):
        """Legacy-compatible behavior preserved for this callable."""
        if hasattr(self.local, "connection"):
            try:
                self.local.connection.close()
                logger.info(
                    f"Connection closed for thread {threading.current_thread().name}")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                del self.local.connection

    def reset_all_connections(self):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if hasattr(self.local, "connection"):
                try:
                    self.local.connection.close()
                    logger.warning("[Reset] Closed current thread connection due to reset.")
                except Exception as e:
                    logger.warning(f"[Reset] Error closing connection during reset: {e}")
                finally:
                    del self.local.connection
            logger.info("[Reset] All thread-local connections reset.")
        except Exception as e:
            logger.error(f"[Reset] Failed to reset connections: {e}")

    def is_connected(self) -> bool:
        """Check if the connection is active."""
        try:
            self.connection.cursor().execute("SELECT 1")
            return True
        except Exception:
            return False

    def reconnect(self):
        """Legacy-compatible behavior preserved for this callable."""

        # Internal implementation note: legacy behavior is preserved during modernization.
        conn = self._get_connection()
        return conn

    def ping(self) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            conn = self._get_connection()
            if self.db_type == "mysql":
                conn.ping(reconnect=True)
            return True
        except Exception:
            return False

    def __enter__(self):
        """Support context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close connection on context exit."""
        self.close()

    def __del__(self):
        """Close connection in destructor."""
        self.close()
