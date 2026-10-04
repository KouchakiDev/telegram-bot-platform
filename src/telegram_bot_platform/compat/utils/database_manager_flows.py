from __future__ import annotations

from .database_manager_context import *


class DatabaseManagerFlowsMixin:
    def get_table_schema(self, table_name: str, schema: str = 'public') -> List[Tuple]:
        """Get table schema."""
        try:
            if self.db_type == "sqlite":
                query = f"PRAGMA table_info({table_name})"
                return [(row[1], row[2]) for row in self.fetch_data(query)]
            else:
                query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = %s AND table_name = %s"
                return self.fetch_data(query, (schema, table_name))
        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {e}")
            return []
    def list_tables(self, schema: str = 'public') -> List[str]:
        """List all tables in the database."""
        try:
            if self.db_type == "sqlite":
                query = "SELECT name FROM sqlite_option_a WHERE type='table'"
                return [row[0] for row in self.fetch_data(query)]
            else:
                query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
                return [row[0] for row in self.fetch_data(query, (schema,))]
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []
    def table_exists(self, table_name: str, schema: str = 'public') -> bool:
        """Check if a table exists."""
        return table_name in self.list_tables(schema)
    def column_exists(self, table_name: str, column_name: str, schema: str = 'public') -> bool:
        """Check if a column exists."""
        return column_name in self.get_columns(table_name, schema)
    def count_rows(self, table_name: str, condition: str = "", params: Tuple = ()):
        """Count rows in a table."""
        if self.table_exists(table_name):
            query = f"SELECT COUNT(*) FROM {table_name}"
        else:
            return 0
        if condition:
            query += f" WHERE {condition}"
        result = self.fetch_data(query, params)
        return result[0][0] if result else 0
    def get_table_size(self, table_name: str) -> int:
        """Get table size in bytes."""
        try:
            if self.db_type == "sqlite":
                query = f"SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
                result = self.fetch_data(query)
                return result[0][0] if result else 0
            else:
                query = f"SELECT pg_total_relation_size('{table_name}')"
                result = self.fetch_data(query)
                return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"Error getting size of table {table_name}: {e}")
            return 0
    def get_database_size(self) -> int:
        """Get total database size in bytes."""
        try:
            if self.db_type == "sqlite":
                return os.path.getsize(self.db_name)
            else:
                query = "SELECT pg_database_size(current_database())"
                result = self.fetch_data(query)
                return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0
    def optimize_table(self, table_name: str):
        """Optimize a table."""
        try:
            if self.db_type == "sqlite":
                query = "VACUUM"
            else:
                query = f"ANALYZE {table_name}"
            self.execute_query(query)
            logger.info(f"Table {table_name} optimized.")
        except Exception as e:
            logger.error(f"Error optimizing table {table_name}: {e}")
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
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics."""
        try:
            stats = {
                "row_count": self.count_rows(table_name),
                "size_bytes": self.get_table_size(table_name),
                "column_count": len(self.get_columns(table_name)),
                "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            logger.info(f"Table {table_name} stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting stats for table {table_name}: {e}")
            return {}
    def create_bot_settings_table(self):
        """Create bot_settings table for configuration."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_type TEXT UNIQUE,
                    categorization_column TEXT,
                    sorting_columns TEXT
                )
            ''')
            self.connection.commit()
            logger.info("Table bot_settings created or already exists.")
        except Exception as e:
            logger.error(f"Error creating bot_settings table: {e}")
    def get_settings(self, request_type):
        """Get settings for a specific request type."""
        try:
            self.cursor.execute(
                "SELECT categorization_column, sorting_columns FROM bot_settings WHERE request_type = ?", (request_type,))
            result = self.cursor.fetchone()
            if result:
                categorization_column, sorting_columns = result
                sorting_columns = sorting_columns.split(
                    ",") if sorting_columns else ["created_at DESC"]
                return {
                    "categorization_column": categorization_column,
                    "sorting_columns": sorting_columns
                }
            return None
        except Exception as e:
            logger.error(f"Error getting settings for {request_type}: {e}")
            return None
    def create_auto_settings_table(self):
        """Legacy-compatible behavior preserved for this callable."""
        columns = {
            "table_name": "TEXT UNIQUE",
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
    def set_settings(self, request_type, categorization_column, sorting_columns):
        """Set settings for a specific request type."""
        try:
            sorting_columns_str = ",".join(sorting_columns)
            self.cursor.execute('''
                INSERT OR REPLACE INTO bot_settings (request_type, categorization_column, sorting_columns)
                VALUES (?, ?, ?)
            ''', (request_type, categorization_column, sorting_columns_str))
            self.connection.commit()
            logger.info(f"Settings saved for {request_type}.")
        except Exception as e:
            logger.error(f"Error saving settings for {request_type}: {e}")
    def create_index(self, table_name: str, column_name: str, index_name: Optional[str] = None, unique: bool = False):
        """Create an index on a column."""
        try:
            if index_name is None:
                index_name = f"idx_{table_name}_{column_name}"
            unique_str = "UNIQUE" if unique else ""
            query = f"CREATE {unique_str} INDEX {index_name} ON {table_name} ({column_name})"
            self.execute_query(query)
            logger.info(f"Index {index_name} created on column {column_name}.")
        except Exception as e:
            logger.error(f"Error creating index for {column_name}: {e}")
    def get_user_data(self, chat_id):
        """Fetches user data by chat_id from the premium_clients table."""
        results = self.select_dict(
            "premium_clients", "telegram_id = ? AND C_status = 'approved'", (chat_id,))
        return results[0] if results else {}
    def update_user_field(self, chat_id, field, value):
        """Updates a specific field for a user."""
        self.update("premium_clients", {field: value},
                    "telegram_id = ?", (chat_id,))
    def insert_complete_profile_request(self, chat_id, data, status="pending"):
        """Inserts a complete profile request."""
        request_data = {"U_Code": chat_id,
                        "data": json.dumps(data), "status": status}
        self.insert("complete_profile_requests", request_data)
