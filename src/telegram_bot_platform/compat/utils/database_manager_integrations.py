from __future__ import annotations

from .database_manager_context import *


class DatabaseManagerIntegrationsMixin:
    def drop_sequence(self, sequence_name: str):
        """Drop a sequence."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support sequences.")
                return
            query = f"DROP SEQUENCE IF EXISTS {sequence_name}"
            self.execute_query(query)
            logger.info(f"Sequence {sequence_name} dropped.")
        except Exception as e:
            logger.error(f"Error dropping sequence {sequence_name}: {e}")
    def get_next_sequence_value(self, sequence_name: str) -> Optional[int]:
        """Get the next value from a sequence."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support sequences.")
                return None
            query = f"SELECT nextval('{sequence_name}')"
            result = self.fetch_data(query)
            return result[0][0] if result else None
        except Exception as e:
            logger.error(
                f"Error getting next sequence value for {sequence_name}: {e}")
            return None
    def set_sequence_value(self, sequence_name: str, value: int):
        """Set the value of a sequence."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support sequences.")
                return
            query = f"SELECT setval('{sequence_name}', {value})"
            self.execute_query(query)
            logger.info(f"Sequence {sequence_name} value set to {value}.")
        except Exception as e:
            logger.error(
                f"Error setting sequence value for {sequence_name}: {e}")
    def create_trigger(self, trigger_name: str, table_name: str, timing: str, event: str, function: str):
        """Create a trigger."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite has limited trigger support.")
                return
            query = f"""
            CREATE TRIGGER {trigger_name}
            {timing} {event} ON {table_name}
            FOR EACH ROW
            EXECUTE PROCEDURE {function}();
            """
            self.execute_query(query)
            logger.info(
                f"Trigger {trigger_name} created for table {table_name}.")
        except Exception as e:
            logger.error(f"Error creating trigger {trigger_name}: {e}")
    def drop_trigger(self, trigger_name: str, table_name: str):
        """Drop a trigger."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite has limited trigger support.")
                return
            query = f"DROP TRIGGER {trigger_name} ON {table_name}"
            self.execute_query(query)
            logger.info(
                f"Trigger {trigger_name} dropped from table {table_name}.")
        except Exception as e:
            logger.error(f"Error dropping trigger {trigger_name}: {e}")
    def get_triggers(self, table_name: str) -> List[str]:
        """Get list of triggers for a table."""
        try:
            if self.db_type == "sqlite":
                query = f"SELECT name FROM sqlite_option_a WHERE type='trigger' AND tbl_name='{table_name}'"
                return [row[0] for row in self.fetch_data(query)]
            else:
                query = f"SELECT trigger_name FROM information_schema.triggers WHERE event_object_table = %s"
                return [row[0] for row in self.fetch_data(query, (table_name,))]
        except Exception as e:
            logger.error(f"Error getting triggers for table {table_name}: {e}")
            return []
    def create_function(self, function_name: str, params: str, return_type: str, body: str):
        """Create a stored function."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support stored functions.")
                return
            query = f"""
            CREATE FUNCTION {function_name}({params}) RETURNS {return_type} AS $$
            {body}
            $$ LANGUAGE plpgsql;
            """
            self.execute_query(query)
            logger.info(f"Function {function_name} created.")
        except Exception as e:
            logger.error(f"Error creating function {function_name}: {e}")
    def drop_function(self, function_name: str, params: str):
        """Drop a stored function."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support stored functions.")
                return
            query = f"DROP FUNCTION IF EXISTS {function_name}({params})"
            self.execute_query(query)
            logger.info(f"Function {function_name} dropped.")
        except Exception as e:
            logger.error(f"Error dropping function {function_name}: {e}")
    def get_functions(self, schema: str = 'public') -> List[str]:
        """Get list of stored functions."""
        try:
            if self.db_type == "sqlite":
                return []
            else:
                query = f"SELECT routine_name FROM information_schema.routines WHERE routine_schema = %s AND routine_type = 'FUNCTION'"
                return [row[0] for row in self.fetch_data(query, (schema,))]
        except Exception as e:
            logger.error(f"Error getting functions: {e}")
            return []
    def create_procedure(self, procedure_name: str, params: str, body: str):
        """Create a stored procedure."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support stored procedures.")
                return
            query = f"""
            CREATE PROCEDURE {procedure_name}({params}) AS $$
            {body}
            $$ LANGUAGE plpgsql;
            """
            self.execute_query(query)
            logger.info(f"Procedure {procedure_name} created.")
        except Exception as e:
            logger.error(f"Error creating procedure {procedure_name}: {e}")
    def drop_procedure(self, procedure_name: str, params: str):
        """Drop a stored procedure."""
        try:
            if self.db_type == "sqlite":
                logger.warning("SQLite does not support stored procedures.")
                return
            query = f"DROP PROCEDURE IF EXISTS {procedure_name}({params})"
            self.execute_query(query)
            logger.info(f"Procedure {procedure_name} dropped.")
        except Exception as e:
            logger.error(f"Error dropping procedure {procedure_name}: {e}")
    def get_procedures(self, schema: str = 'public') -> List[str]:
        """Get list of stored procedures."""
        try:
            if self.db_type == "sqlite":
                return []
            else:
                query = f"SELECT routine_name FROM information_schema.routines WHERE routine_schema = %s AND routine_type = 'PROCEDURE'"
                return [row[0] for row in self.fetch_data(query, (schema,))]
        except Exception as e:
            logger.error(f"Error getting procedures: {e}")
            return []
    def cache_query(self, query: str, params: Tuple = (), ttl: int = 300) -> List[Tuple]:
        """Cache query results for performance."""
        cache_key = (query, params)
        try:
            with self.lock:
                if cache_key in self.query_cache:
                    cached_time, result = self.query_cache[cache_key]
                    if time.time() - cached_time < ttl:
                        logger.info(
                            f"Returning cached result for query: {query}")
                        return result
                result = self.fetch_data(query, params)
                self.query_cache[cache_key] = (time.time(), result)
                logger.info(f"Query result cached: {query}")
                return result
        except Exception as e:
            logger.error(f"Error caching query {query}: {e}")
            return []
    def clear_query_cache(self):
        """Clear the query cache."""
        try:
            with self.lock:
                self.query_cache.clear()
            logger.info("Query cache cleared.")
        except Exception as e:
            logger.error(f"Error clearing query cache: {e}")
    def get_current_user(self) -> str:
        """Get the current database user."""
        try:
            if self.db_type == "sqlite":
                return "sqlite_user"
            else:
                query = "SELECT current_user"
                result = self.fetch_data(query)
                return result[0][0] if result else None
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    def create_rejection_reasons_table(self):
        """Create rejection_reasons table for storing rejection reasons."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS rejection_reasons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.connection.commit()
            logger.info("Table rejection_reasons created or already exists.")
        except Exception as e:
            logger.error(f"Error creating rejection_reasons table: {e}")
    def get_database_version(self) -> str:
        """Get the database version."""
        try:
            if self.db_type == "sqlite":
                query = "SELECT sqlite_version()"
            elif self.db_type == "mysql":
                query = "SELECT VERSION()"
            elif self.db_type == "postgresql":
                query = "SELECT version()"
            else:
                query = "SELECT @@VERSION"
            result = self.fetch_data(query)
            return result[0][0] if result else "Unknown"
        except Exception as e:
            logger.error(f"Error getting database version: {e}")
            return "Unknown"
    def is_connected(self) -> bool:
        """Check if the connection is active."""
        try:
            self.connection.cursor().execute("SELECT 1")
            return True
        except Exception:
            return False
    def reconnect(self):
        """Reconnect to the database."""
        try:
            self.close()
            self._initialize_connection()
            logger.info("Reconnected to database.")
        except Exception as e:
            logger.error(f"Error reconnecting: {e}")
    def ping(self):
        """Ping the database to check connectivity."""
        try:
            if self.db_type == "sqlite":
                self.execute_query("SELECT 1")
            elif self.db_type == "mysql":
                self.connection.ping(reconnect=True)
            else:
                self.execute_query("SELECT 1")
            logger.info("Database ping successful.")
        except Exception as e:
            logger.error(f"Error pinging database: {e}")
            self.reconnect()
    def __enter__(self):
        """Support context manager."""
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        """Close connection on context exit."""
        self.close()
    def __del__(self):
        """Close connection in destructor."""
        self.close()
