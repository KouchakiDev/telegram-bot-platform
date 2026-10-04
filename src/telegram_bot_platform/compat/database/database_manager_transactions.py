from __future__ import annotations

from .database_manager_context import *


class M_DatabaseManagerTransactionsMixin:
    def begin_transaction(self):
        """Begin a transaction with nested support."""
        try:
            conn = self._get_connection()
            # cursor = self._get_cursor
            with self.lock:
                if self.transaction_level == 0:
                    if self.db_type == "sqlite":
                        self.execute_query("BEGIN TRANSACTION")
                    else:

                        conn.commit()

                self.transaction_level += 1
            logger.info(
                f"Transaction started. Level: {self.transaction_level}")
        except Exception as e:
            logger.error(f"Error starting transaction: {e}")

    def commit_transaction(self):
        """Commit a transaction."""
        try:
            conn = self._get_connection()
            # cursor = self._get_cursor
            with self.lock:
                self.transaction_level -= 1
                if self.transaction_level == 0:

                    conn.commit()

            logger.info(
                f"Transaction committed. Level: {self.transaction_level}")
        except Exception as e:
            logger.error(f"Error committing transaction: {e}")

    def rollback_transaction(self):
        """Rollback a transaction."""
        try:
            conn = self._get_connection()
            with self.lock:
                self.transaction_level -= 1
                if self.transaction_level == 0:
                    if self.db_type == "sqlite":
                        self.execute_query("ROLLBACK")
                    else:

                        conn.rollback()
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
            self.clear_query_cache()

            logger.info("Transaction executed successfully.")
        except Exception as e:
            self.rollback_transaction()
            logger.error(f"Error executing transaction: {e}")
