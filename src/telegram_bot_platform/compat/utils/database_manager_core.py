from __future__ import annotations

from .database_manager_context import *


class DatabaseManagerCoreMixin:
    def _load_column_types_from_file(self):
        """Load column types from a JSON file."""
        if self.column_types_file and os.path.exists(self.column_types_file):
            try:
                with open(self.column_types_file, 'r', encoding='utf-8') as f:
                    self.column_types.update(json.load(f))
                logger.info(
                    f"Column types loaded from file {self.column_types_file}.")
            except Exception as e:
                logger.error(f"Error loading column types from file: {e}")
    def _initialize_connection(self):
        """Initialize database connection."""
        try:
            self.connection = self._connect()
            self.cursor = self.connection.cursor()
            logger.info(f"Connection to {self.db_type} database established.")
        except Exception as e:
            logger.error(f"Error during initial connection to database: {e}")
            raise
    def _connect(self):
        """Create a connection based on database type."""
        try:
            if self.db_type == "sqlite":
                return sqlite3.connect(self.db_name, check_same_thread=False)
            elif self.db_type == "mysql":
                return mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.db_name)
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
    def close(self):
        """Close the database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed.")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    def _get_column_type(self, column_name: str, provided_type: Optional[str] = None) -> str:
        """Determine column type with specified priority."""
        if provided_type:
            return provided_type
        if column_name in self.column_types:
            return self.column_types[column_name]
        return "TEXT"
    def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create a table with specified columns."""
        try:
            self.ensure_table_and_columns(table_name, column_types=columns)
            logger.info(f"Table {table_name} created or already exists.")
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            raise
    def drop_table(self, table_name: str):
        """Drop a table."""
        try:
            query = f"DROP TABLE IF EXISTS {table_name}"
            self.execute_query(query)
            logger.info(f"Table {table_name} dropped.")
        except Exception as e:
            logger.error(f"Error dropping table {table_name}: {e}")
    def rename_table(self, old_name: str, new_name: str):
        """Rename a table, generating a unique name if the target exists."""
        try:
            if self.table_exists(new_name):
                new_name = f"{new_name}_{int(datetime.timestamp(datetime.now()))}"
                logger.warning(
                    f"Table {new_name} already exists. Renamed to {new_name}.")
            query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
            self.execute_query(query)
            logger.info(f"Table renamed from {old_name} to {new_name}.")
        except Exception as e:
            logger.error(
                f"Error renaming table from {old_name} to {new_name}: {e}")
    def add_column(self, table_name: str, column_name: str, column_type: str):
        """Add a column to a table."""
        try:
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            self.execute_query(query)
            logger.info(f"Column {column_name} added to table {table_name}.")
        except Exception as e:
            logger.error(
                f"Error adding column {column_name} to table {table_name}: {e}")
    def rename_column(self, table_name: str, old_name: str, new_name: str):
        """Rename a column in a table."""
        try:
            if self.db_type == "sqlite":
                schema = self.get_table_schema(table_name)
                new_columns = [(new_name if col == old_name else col, dtype[1])
                               for col, dtype in schema]
                column_defs = ', '.join(
                    [f"{col} {dtype}" for col, dtype in new_columns])
                self.execute_query(
                    f"ALTER TABLE {table_name} RENAME TO temp_table")
                self.create_table(table_name, dict(new_columns))
                self.execute_query(
                    f"INSERT INTO {table_name} SELECT * FROM temp_table")
                self.drop_table("temp_table")
            else:
                query = f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"
                self.execute_query(query)
            logger.info(
                f"Column {old_name} renamed to {new_name} in table {table_name}.")
        except Exception as e:
            logger.error(
                f"Error renaming column from {old_name} to {new_name}: {e}")
    def remove_column(self, table_name: str, column_name: str):
        """Remove a column from a table."""
        try:
            if self.db_type == "sqlite":
                columns = self.get_columns(table_name)
                new_columns = [col for col in columns if col != column_name]
                column_defs = ', '.join(new_columns)
                self.execute_query(
                    f"CREATE TABLE temp_table AS SELECT {column_defs} FROM {table_name}")
                self.drop_table(table_name)
                self.execute_query(
                    f"ALTER TABLE temp_table RENAME TO {table_name}")
            else:
                query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
                self.execute_query(query)
            logger.info(
                f"Column {column_name} removed from table {table_name}.")
        except Exception as e:
            logger.error(
                f"Error removing column {column_name} from table {table_name}: {e}")
    def ensure_table_and_columns(self, table_name: str, data: dict = None, column_types: dict = None):
        """Legacy-compatible behavior preserved for this callable."""
        default_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "created_at": "TIMESTAMP",
            "last_updated": "TIMESTAMP"
        }
        # Internal implementation note: legacy behavior is preserved during modernization.
        # 1. column_types
        # Internal implementation note: legacy behavior is preserved during modernization.
        final_columns = default_columns.copy()
        if data:
            for key in data.keys():
                if key not in final_columns:
                    if column_types and key in column_types:
                        final_columns[key] = column_types[key]
                    else:
                        final_columns[key] = "TEXT"
        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(f'{col} {dtype}' for col, dtype in final_columns.items())}
                )
            """)
        except Exception as e:
            print(f"❌ خطا در ساخت جدول {table_name}: {e}")
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(f'{col} {dtype}' for col, dtype in default_columns.items())}
                )
            """)
        # Internal implementation note: legacy behavior is preserved during modernization.
        existing_columns = self.get_columns(table_name)
        # Internal implementation note: legacy behavior is preserved during modernization.
        for col, dtype in final_columns.items():
            if col not in existing_columns:
                try:
                    self.cursor.execute(
                        f"ALTER TABLE {table_name} ADD COLUMN {col} {dtype}")
                except Exception as e:
                    print(
                        f"❌ خطا در افزودن ستون {col} به جدول {table_name}: {e}")
    def insert(self, table_name: str, data: Dict[str, Any], column_types: Optional[Dict[str, str]] = None):
        """Insert data into a table."""
        try:
            data["created_at"] = datetime.now()
            data["last_updated"] = datetime.now()
            self.ensure_table_and_columns(table_name, data, column_types)
            columns = ', '.join(data.keys())
            placeholders = ', '.join(
                ['?' if self.db_type == "sqlite" else '%s' for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.execute_query(query, tuple(data.values()))
            logger.info(f"Data inserted into table {table_name}.")
        except Exception as e:
            logger.error(f"Error inserting data into table {table_name}: {e}")
    def insert_batch(self, table_name: str, data_list: List[Dict[str, Any]], column_types: Optional[Dict[str, str]] = None):
        """Batch insert data into a table."""
        try:
            if not data_list:
                logger.warning("No data provided for batch insert.")
                return
            self.ensure_table_and_columns(
                table_name, data_list[0], column_types)
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(
                ['?' if self.db_type == "sqlite" else '%s' for _ in data_list[0]])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.executemany(
                query, [tuple(d.values()) for d in data_list])
            self.connection.commit()
            logger.info(
                f"{len(data_list)} rows inserted into table {table_name}.")
        except Exception as e:
            self.connection.rollback()
            logger.error(
                f"Error during batch insert into table {table_name}: {e}")
    def upsert(self, table_name: str, data: Dict[str, Any], key: str, column_types: Optional[Dict[str, str]] = None):
        """Insert or update data based on a key."""
        try:
            data["last_updated"] = datetime.now()
            createat = data.get("created_at", 0)
            if not createat:
                data["created_at"] = datetime.now()
            self.ensure_table_and_columns(table_name, data, column_types)
            columns = ', '.join(data.keys())
            placeholders = ', '.join(
                ['?' if self.db_type == "sqlite" else '%s' for _ in data])
            if self.db_type == "sqlite":
                updates = ', '.join(
                    [f"{col} = excluded.{col}" for col in data.keys() if col != key])
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT({key}) DO UPDATE SET {updates}"
            elif self.db_type == "mysql":
                updates = ', '.join(
                    [f"{col} = VALUES({col})" for col in data.keys()])
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"
            else:
                updates = ', '.join(
                    [f"{col} = excluded.{col}" for col in data.keys() if col != key])
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT ({key}) DO UPDATE SET {updates}"
            self.execute_query(query, tuple(data.values()))
            logger.info(f"Data inserted or updated in table {table_name}.")
        except Exception as e:
            logger.error(f"Error during upsert in table {table_name}: {e}")
    def update(self, table_name: str, data: Dict[str, Any], condition: str, params: Tuple):
        """Update data in a table."""
        try:
            data["last_updated"] = datetime.now()
            self.ensure_table_and_columns(table_name, data)
            set_clause = ', '.join(
                [f"{key} = ?" if self.db_type == "sqlite" else f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            self.execute_query(query, tuple(data.values()) + params)
            logger.info(f"Data updated in table {table_name}.")
        except Exception as e:
            logger.error(f"Error upsocial_service table {table_name}: {e}")
    def delete(self, table_name: str, condition: str, params: Tuple):
        """Delete data from a table."""
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            self.execute_query(query, params)
            logger.info(f"Data deleted from table {table_name}.")
        except Exception as e:
            logger.error(f"Error deleting data from table {table_name}: {e}")
    def select(self, table_name: str, condition: str = "", params: Tuple = ()) -> List[Tuple]:
        """Select data from a table."""
        try:
            query = f"SELECT * FROM {table_name}"
            if condition:
                query += f" WHERE {condition}"
            return self.fetch_data(query, params)
        except Exception as e:
            logger.error(f"Error selecting data from table {table_name}: {e}")
            return []
    def select_dict(self, table: str, condition: str = "", params: Tuple = (), order_by: str = "", limit: int = None):
        try:
            query = f"SELECT * FROM {table}"
            if condition:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if self.db_type != "sqlite":
                    condition = condition.replace("?", "%s")
                query += f" WHERE {condition}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit is not None:
                query += f" LIMIT {limit}"
            self.cursor.execute(query, params)
            columns = [column[0] for column in self.cursor.description]
            results = self.cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error(f"Error in select_dict for table {table}: {e}")
            return []
    def execute_query(self, query: str, params: Tuple = ()):
        """Execute a SQL query."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            logger.debug(f"Query executed: {query}")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error executing query: {query} | Error: {e}")
    def fetch_data(self, query: str, params: Tuple = ()) -> List[Tuple]:
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching data: {query} | Error: {e}")
            return []
    def get_columns(self, table_name: str, schema: str = 'public') -> List[str]:
        """Get list of columns in a table."""
        try:
            if self.db_type == "sqlite":
                query = f"PRAGMA table_info({table_name})"
                return [row[1] for row in self.fetch_data(query)]
            else:
                query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = %s AND table_name = %s"
                return [row[0] for row in self.fetch_data(query, (schema, table_name))]
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            return []
