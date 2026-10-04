from __future__ import annotations

from .database_manager_context import *


class M_DatabaseManagerAdvancedMixin:
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

    def get_views(self) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            rows = self.fetch_data(
                "SELECT name FROM sqlite_option_a WHERE type='view'")
            return [r[0] for r in rows]
        else:
            sql = (
                "SELECT table_name "
                "FROM information_schema.views "
                "WHERE table_schema = %s"
            )
            rows = self.fetch_data(sql, (self.db_name,))
            return [r[0] for r in rows]

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

    def full_database_backup(self, backup_root: str = "./backups") -> bytes:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            now = datetime.now()
            j_now = JalaliDateTime.to_jalali(now)

            year = str(j_now.year)
            month_num = j_now.month
            month_name = j_now.strftime("%B")  # Internal implementation note: legacy behavior is preserved during modernization.
            month_dir = f"{month_name}_{month_num:02d}"

            day = f"{j_now.day:02d}"
            week_num = ((j_now.day - 1) // 7) + 1  # Internal implementation note: legacy behavior is preserved during modernization.
            week_dir = f"week_{week_num}"
            time_str = now.strftime("%H-%M-%S")

            backup_dir = os.path.join(backup_root, year, month_dir, week_dir, day)
            os.makedirs(backup_dir, exist_ok=True)

            filename = f"{time_str}.sql"
            backup_path = os.path.join(backup_dir, filename)

            if self.db_type == "sqlite":
                with open(backup_path, 'w', encoding='utf-8') as f:
                    for line in self.connection.iterdump():
                        f.write(f"{line}\n")
                logger.info(f"[Backup] SQLite backup created at: {backup_path}")

            elif self.db_type == "mysql":
                cmd = f"mysqldump -h {self.host} -u {self.user} -p'{self.password}' {self.db_name} > \"{backup_path}\""
                result = os.system(cmd)
                if result == 0:
                    logger.info(f"[Backup] MySQL backup created at: {backup_path}")
                else:
                    logger.error(f"[Backup] Failed to create MySQL backup with command: {cmd}")
                    raise Exception("MySQL backup failed.")

            else:
                logger.warning(f"[Backup] Backup not supported for db_type: {self.db_type}")
                raise NotImplementedError(f"Backup not implemented for {self.db_type}")

            with open(backup_path, "rb") as f:
                binary_data = f.read()

            return binary_data

        except Exception as e:
            logger.exception(f"[Backup] Error during full backup: {e}")
            raise

    def backup_to_sql(self, backup_file: str):
        """Backup database to an SQL file."""
        try:
            if self.db_type == "sqlite":
                with open(backup_file, 'w', encoding='utf-8') as f:
                    for line in self.connection.iterdump():
                        f.write(f"{line}\n")
                logger.info(f"Backup created to file {backup_file}.")
            else:
                logger.warning(
                    "SQL backup for this database requires external tools.")
        except Exception as e:
            logger.error(f"Error during SQL backup: {e}")

    def restore_from_sql(self, sql_file: str):
        """Restore database from an SQL file."""
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith("CREATE TABLE"):
                        table_name = line.split()[2]
                        if self.table_exists(table_name):
                            logger.warning(
                                f"Table {table_name} already exists. Skipping creation.")
                            continue
                    self.execute_query(line)
            logger.info(f"Database restored from file {sql_file}.")
        except Exception as e:
            logger.error(f"Error restoring from file {sql_file}: {e}")

    def backup_to_csv(self, table_name: str, csv_file: str):
        """Backup a table to a CSV file."""
        try:
            data = self.select(table_name)
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.get_columns(table_name))
                writer.writerows(data)
            logger.info(f"Table {table_name} backed up to {csv_file}.")
        except Exception as e:
            logger.error(f"Error backing up table {table_name} to CSV: {e}")

    def qname(self, name: str) -> str:
        """Quote identifiers (table/column names) for MySQL."""
        return f"`{name}`" if self.db_type == "mysql" else name
