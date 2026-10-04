from __future__ import annotations

from .database_manager_context import *


class DatabaseManagerDataMixin:
    def insert_identity_verification_request(self, chat_id, data, status="pending"):
        """Inserts a IDENTITY_VERIFICATION request."""
        request_data = {"U_Code": chat_id,
                        "data": json.dumps(data), "status": status}
        self.insert("identity_verification_requests", request_data)
    def get_latest_identity_verification_request_status(self, chat_id, field):
        """Gets the status of the latest IDENTITY_VERIFICATION request for a field."""
        results = self.select_dict(
            "identity_verification_requests",
            "U_Code = ? AND json_extract(data, ?)",
            (chat_id, f"$.{field}"),
            order_by="id DESC",
            limit=1
        )
        if results and "status" in results[0]:
            return results[0]["status"]
        return None
    def create_composite_index(self, table_name: str, columns: List[str], index_name: Optional[str] = None):
        """Create a composite index on multiple columns."""
        try:
            if index_name is None:
                index_name = f"idx_{table_name}_{'_'.join(columns)}"
            columns_str = ', '.join(columns)
            query = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
            self.execute_query(query)
            logger.info(
                f"Composite index {index_name} created on columns {columns_str}.")
        except Exception as e:
            logger.error(f"Error creating composite index on {columns}: {e}")
    def drop_index(self, index_name: str):
        """Drop an index."""
        try:
            query = f"DROP INDEX {index_name}"
            self.execute_query(query)
            logger.info(f"Index {index_name} dropped.")
        except Exception as e:
            logger.error(f"Error dropping index {index_name}: {e}")
    def begin_transaction(self):
        """Begin a transaction with nested support."""
        try:
            with self.lock:
                if self.transaction_level == 0:
                    if self.db_type == "sqlite":
                        self.execute_query("BEGIN TRANSACTION")
                    else:
                        self.connection.begin()
                self.transaction_level += 1
            logger.info(
                f"Transaction started. Level: {self.transaction_level}")
        except Exception as e:
            logger.error(f"Error starting transaction: {e}")
    def commit_transaction(self):
        """Commit a transaction."""
        try:
            with self.lock:
                self.transaction_level -= 1
                if self.transaction_level == 0:
                    self.connection.commit()
            logger.info(
                f"Transaction committed. Level: {self.transaction_level}")
        except Exception as e:
            logger.error(f"Error committing transaction: {e}")
    def rollback_transaction(self):
        """Rollback a transaction."""
        try:
            with self.lock:
                self.transaction_level -= 1
                if self.transaction_level == 0:
                    if self.db_type == "sqlite":
                        self.execute_query("ROLLBACK")
                    else:
                        self.connection.rollback()
            logger.info(
                f"Transaction rolled back. Level: {self.transaction_level}")
        except Exception as e:
            logger.error(f"Error rolling back transaction: {e}")
    def savepoint(self, name: str):
        """Create a savepoint in a transaction."""
        try:
            self.execute_query(f"SAVEPOINT {name}")
            logger.info(f"Savepoint {name} created.")
        except Exception as e:
            logger.error(f"Error creating savepoint {name}: {e}")
    def rollback_to_savepoint(self, name: str):
        """Rollback to a savepoint."""
        try:
            self.execute_query(f"ROLLBACK TO SAVEPOINT {name}")
            logger.info(f"Rolled back to savepoint {name}.")
        except Exception as e:
            logger.error(f"Error rolling back to savepoint {name}: {e}")
    def release_savepoint(self, name: str):
        """Release a savepoint."""
        try:
            self.execute_query(f"RELEASE SAVEPOINT {name}")
            logger.info(f"Savepoint {name} released.")
        except Exception as e:
            logger.error(f"Error releasing savepoint {name}: {e}")
    def execute_transaction(self, queries: List[Tuple[str, Tuple]]):
        """Execute multiple queries in a transaction."""
        try:
            self.begin_transaction()
            for query, params in queries:
                self.execute_query(query, params)
            self.commit_transaction()
            logger.info("Transaction executed successfully.")
        except Exception as e:
            self.rollback_transaction()
            logger.error(f"Error executing transaction: {e}")
    def create_user(self, username: str, password: str, role: str = "user"):
        """Create a database user."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support user management.")
                return
            query = f"CREATE USER {username} WITH PASSWORD '{password}'"
            if self.db_type == "postgresql" and role:
                query += f" {role.upper()}"
            self.execute_query(query)
            logger.info(f"User {username} created with role {role}.")
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
    def get_tables_with_status(self):
        """Get list of tables that have a 'status' column."""
        tables = self.fetch_data(
            "SELECT name FROM sqlite_option_a WHERE type='table';")
        tables_with_status = []
        for table in tables:
            table_name = table[0]
            columns = [col[1] for col in self.fetch_data(
                f"PRAGMA table_info({table_name});")]
            if "status" in columns:
                tables_with_status.append(table_name)
        return tables_with_status
    def get_tables_with_parm(self, parm):
        """Get list of tables that have a 'status' column."""
        tables = self.fetch_data(
            "SELECT name FROM sqlite_option_a WHERE type='table';")
        tables_with_status = []
        for table in tables:
            table_name = table[0]
            columns = [col[1] for col in self.fetch_data(
                f"PRAGMA table_info({table_name});")]
            if parm in columns:
                tables_with_status.append(table_name)
        return tables_with_status
    def drop_user(self, username: str):
        """Drop a database user."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support user management.")
                return
            query = f"DROP USER {username}"
            self.execute_query(query)
            logger.info(f"User {username} dropped.")
        except Exception as e:
            logger.error(f"Error dropping user {username}: {e}")
    def get_bot_settings(self, table_name):
        query = """
            SELECT categorization_column, display_columns, max_requests_per_row, request_overview, request_details, ignored_columns 
            FROM bot_settings 
            WHERE table_name = ?
        """
        self.cursor.execute(query, (table_name,))
        result = self.cursor.fetchone()
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
    def grant_permission(self, username: str, table_name: str, permission: str):
        """Grant a permission to a user on a table."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support permissions.")
                return
            query = f"GRANT {permission} ON {table_name} TO {username}"
            self.execute_query(query)
            logger.info(f"Granted {permission} on {table_name} to {username}.")
        except Exception as e:
            logger.error(
                f"Error granting {permission} to {username} on {table_name}: {e}")
    def revoke_permission(self, username: str, table_name: str, permission: str):
        """Revoke a permission from a user on a table."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support permissions.")
                return
            query = f"REVOKE {permission} ON {table_name} FROM {username}"
            self.execute_query(query)
            logger.info(
                f"Revoked {permission} on {table_name} from {username}.")
        except Exception as e:
            logger.error(
                f"Error revoking {permission} from {username} on {table_name}: {e}")
    def create_view(self, view_name: str, query: str):
        """Create a database view."""
        try:
            create_query = f"CREATE VIEW {view_name} AS {query}"
            self.execute_query(create_query)
            logger.info(f"View {view_name} created.")
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
    def drop_view(self, view_name: str):
        """Drop a database view."""
        try:
            query = f"DROP VIEW IF EXISTS {view_name}"
            self.execute_query(query)
            logger.info(f"View {view_name} dropped.")
        except Exception as e:
            logger.error(f"Error dropping view {view_name}: {e}")
    def get_views(self, schema: str = 'public') -> List[str]:
        """Get list of views."""
        try:
            if self.db_type == "sqlite":
                query = "SELECT name FROM sqlite_option_a WHERE type='view'"
                return [row[0] for row in self.fetch_data(query)]
            else:
                query = f"SELECT table_name FROM information_schema.views WHERE table_schema = %s"
                return [row[0] for row in self.fetch_data(query, (schema,))]
        except Exception as e:
            logger.error(f"Error getting views: {e}")
            return []
    def create_sequence(self, sequence_name: str, start: int = 1, increment: int = 1):
        """Create a sequence."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support sequences.")
                return
            query = f"CREATE SEQUENCE {sequence_name} START WITH {start} INCREMENT BY {increment}"
            self.execute_query(query)
            logger.info(f"Sequence {sequence_name} created.")
        except Exception as e:
            logger.error(f"Error creating sequence {sequence_name}: {e}")
