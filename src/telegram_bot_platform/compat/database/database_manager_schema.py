from __future__ import annotations

from .database_manager_context import *


class M_DatabaseManagerSchemaMixin:
    def _get_column_type(self, column_name: str, provided_type: Optional[str] = None) -> str:
        """Determine column type with specified priority."""
        if provided_type:
            return provided_type
        if column_name in self.column_types:
            return self.column_types[column_name]
        return "TEXT"

    def create_database_if_not_exists(self, db_name):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if not self.host or self.host in [".", "localhost"]:
                self.host = "127.0.0.1"

            attempt = 0
            max_attempts = 10
            while attempt < max_attempts:
                try:
                    temp_connection = mysql.connector.connect(
                        host=self.host or "127.0.0.1",
                        user=self.user,
                        password=self.password,
                        port=self.port or 3306
                    )
                    break
                except mysql.connector.Error as e:
                    attempt += 1
                    logger.warning(
                        f"MySQL connection attempt {attempt} failed: {e}")
                    time.sleep(3)
            else:
                logger.error(
                    f"Failed to connect to MySQL after {max_attempts} attempts.")
                raise Exception(
                    f"Could not connect to MySQL after {max_attempts} attempts.")

            temp_cursor = temp_connection.cursor()
            temp_cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            temp_connection.commit()
            temp_cursor.close()
            temp_connection.close()

            logger.info(
                f"Database '{db_name}' created or already exists.")

        except Exception as e:
            logger.error(f"Error creating database '{db_name}': {str(e)}")
            raise

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create a table with specified columns."""
        try:
            self.ensure_table_and_columns(table_name, column_types=columns)
            logger.info(f"Table {table_name} created or already exists.")
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            raise

    def drop_table(self, table_name: str):
        """Legacy-compatible behavior preserved for this callable."""
        sql = f"DROP TABLE IF EXISTS {self.qname(table_name)}"
        self.execute_query(sql)

    def rename_table(self, old_name: str, new_name: str):
        """Rename a table."""
        try:
            if self.table_exists(new_name):
                new_name = f"{new_name}_{int(datetime.timestamp(datetime.now()))}"
                logger.warning(f"{new_name} exists, renaming to {new_name}.")
            query = (f"ALTER TABLE {self.qname(old_name)} "
                     f"RENAME TO {self.qname(new_name)}")
            self.execute_query(query)
            logger.info(f"Renamed {old_name} to {new_name}.")
        except Exception as e:
            logger.error(f"Error renaming {old_name}: {e}")

    def add_column(self,
                   table_name: str,
                   column_name: str,
                   column_type: str):
        """Add a column to a table."""
        try:
            query = (f"ALTER TABLE {self.qname(table_name)} "
                     f"ADD COLUMN {self.qname(column_name)} {column_type}")
            self.execute_query(query)
            logger.info(f"Added column {column_name} to {table_name}.")
        except Exception as e:
            logger.error(f"Error adding column {column_name}: {e}")

    def rename_column(self,
                      table_name: str,
                      old_name: str,
                      new_name: str):
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            sql = (
                f"ALTER TABLE {self.qname(table_name)} "
                f"RENAME COLUMN {old_name} TO {new_name}"
            )
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            col_type = dict(self.get_table_schema(table_name)).get(old_name)
            sql = (
                f"ALTER TABLE {self.qname(table_name)} "
                f"CHANGE {self.qname(old_name)} {self.qname(new_name)} {col_type}"
            )
        self.execute_query(sql)

    def remove_column(self,
                      table_name: str,
                      column_name: str):
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            raise NotImplementedError(
                "SQLite does not support DROP COLUMN directly")
        else:
            sql = (
                f"ALTER TABLE {self.qname(table_name)} "
                f"DROP COLUMN {self.qname(column_name)}"
            )
        self.execute_query(sql)

    def _is_column_unique(self, table_name: str, column: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type != "mysql":
            return False
        sql = (
            "SELECT COUNT(*) FROM information_schema.statistics "
            "WHERE table_schema = %s AND table_name = %s "
            "AND column_name = %s AND non_unique = 0"
        )
        return self.fetch_data(sql, (self.db_name, table_name, column))[0][0] > 0

    def _sanitize_mysql_types(self, columns: Dict[str, str]) -> Dict[str, str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            fixed: Dict[str, str] = {}
            for col, sql_type in columns.items():
                low = sql_type.lower()

                # Internal implementation note: legacy behavior is preserved during modernization.
                must_fix = (
                    ("text" in low or "blob" in low)
                    and
                    ("unique" in low or col in INDEX_SAFE_COLUMNS)
                )

                if must_fix:
                    safe_type = INDEX_SAFE_COLUMNS.get(col, "VARCHAR(191)")
                    if "unique" in low and "unique" not in safe_type.lower():
                        safe_type += " UNIQUE"
                    fixed[col] = safe_type
                    logger.info(f"[Fix] Column {col} converted {sql_type} → {safe_type} for MySQL.")
                else:
                    fixed[col] = sql_type
            return fixed
        except Exception as exc:
            logger.exception(f"[Fix] _sanitize_mysql_types failed: {exc}")
            return columns

    def _convert_column_to_varchar(self, table_name: str, column_name: str, value: Any):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            size = len(str(value)) + 10
            alter_sql = (
                f"ALTER TABLE {self.qname(table_name)} "
                f"MODIFY COLUMN {self.qname(column_name)} VARCHAR({size})"
            )
            logger.warning(f"[AutoFix] Upgrading column '{column_name}' in '{table_name}' → VARCHAR({size})")
            self.execute_query(alter_sql)
            logger.info   (f"[AutoFix] Column '{column_name}' in '{table_name}' upgraded to VARCHAR({size})")
        except Exception as exc:
            logger.error  (f"[AutoFix] Failed to upgrade column '{column_name}' in '{table_name}': {exc}")

    def ensure_table_and_columns(
        self,
        table_name: str,
        data: Optional[Dict[str, Any]] = None,
        column_types: Optional[Dict[str, str]] = None,
        columns: Optional[Dict[str, str]] = None
    ):
        """Legacy-compatible behavior preserved for this callable."""
        logger.info(f"[Ensure] Starting ensure_table_and_columns for '{table_name}'")

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            if columns is not None:
                column_types = columns
            elif data:
                column_types = column_types or {}
                for key, val in data.items():
                    if key in column_types:
                        continue
                    column_types[key] = self.inferer.infer(val)
                    if key == "telegram_id":
                        column_types[key] = "varchar(50)"

        except Exception as exc:
            logger.exception(f"[Ensure] Failed while inferring column types: {exc}")

        if not column_types and not data:
            logger.info(f"[Ensure] No column info for '{table_name}'; skipping")
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.db_type == "mysql":
            default_columns = {
                "id": "INT AUTO_INCREMENT PRIMARY KEY",
                "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "last_updated": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP "
                                "ON UPDATE CURRENT_TIMESTAMP"
            }
        else:
            default_columns = {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "created_at": "TEXT",
                "last_updated": "TEXT"
            }

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            existing_columns = self.get_table_column_types(table_name)
            if not isinstance(existing_columns, dict):
                logger.warning(f"[Ensure] get_table_column_types returned non-dict for '{table_name}'")
                existing_columns = {}
        except Exception as exc:
            logger.warning(f"[Ensure] Could not fetch schema for '{table_name}': {exc}")
            existing_columns = {}

        # Internal implementation note: legacy behavior is preserved during modernization.
        if not existing_columns:
            try:
                logger.info(f"[Ensure] Table '{table_name}' not found; creating")

                final_columns = default_columns.copy()
                final_columns.update(column_types or {})

                # Internal implementation note: legacy behavior is preserved during modernization.
                if self.db_type == "mysql":
                    final_columns = self._sanitize_mysql_types(final_columns)

                cols_def = ", ".join(f"{self.qname(c)} {t}" for c, t in final_columns.items())
                sql = f"CREATE TABLE IF NOT EXISTS {self.qname(table_name)} ({cols_def})"
                if self.db_type == "mysql" and "MYSQL_TABLE_OPTIONS" in globals():
                    sql += " " + MYSQL_TABLE_OPTIONS

                logger.debug(f"[Ensure] Executing CREATE TABLE: {sql}")
                self.execute_query(sql)
                logger.info(f"[Ensure] Table '{table_name}' created with columns: {list(final_columns.keys())}")
            except Exception as exc:
                logger.error(f"[Ensure] Failed to create '{table_name}': {exc}")
                raise
            return

        # Internal implementation note: legacy behavior is preserved during modernization.
        for col, sql_type in (column_types or {}).items():
            if col not in existing_columns:
                try:
                    alter = (
                        f"ALTER TABLE {self.qname(table_name)} "
                        f"ADD COLUMN {self.qname(col)} {sql_type}"
                    )
                    logger.debug(f"[Ensure] Executing ALTER: {alter}")
                    self.execute_query(alter)
                    logger.info(f"[Ensure] Column '{col}' added to '{table_name}'")
                except Exception as exc:
                    logger.warning(f"[Ensure] Failed to add column '{col}' to '{table_name}': {exc}")
            else:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if col == "telegram_id" and self.db_type == "mysql":
                    try:
                        existing_type = existing_columns[col].lower()
                        if "bigint" not in existing_type:
                            alter = (
                                f"ALTER TABLE {self.qname(table_name)} "
                                f"MODIFY COLUMN {self.qname(col)} BIGINT"
                            )
                            logger.debug(f"[Ensure] Executing MODIFY: {alter}")
                            self.execute_query(alter)
                            logger.info(f"[Ensure] telegram_id modified to BIGINT in '{table_name}'")
                    except Exception as exc:
                        logger.warning(f"[Ensure] Failed to modify telegram_id in '{table_name}': {exc}")
                else:
                    logger.debug(f"[Ensure] Column '{col}' already exists; skipping")

        logger.info(f"[Ensure] Completed ensure_table_and_columns for '{table_name}'")

    def get_table_column_types(self, table_name: str) -> Dict[str, str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            rows = self.fetch_data(f"SHOW COLUMNS FROM {self.qname(table_name)};")

            if not rows or not isinstance(rows, list):
                logger.warning(f"[Schema] No rows returned from SHOW COLUMNS for '{table_name}'")
                return {}

            result = {row[0]: row[1] for row in rows}  # Field: Type
            logger.info(f"[Schema] Column types for table '{table_name}': {result}")
            return result

        except Exception as e:
            logger.error(f"[Schema] Failed to get columns for table '{table_name}': {e}")
            return {}

    def create_index(self,
                     table_name: str,
                     index_name: str,
                     column_name: str,
                     unique: bool = False):
        """Legacy-compatible behavior preserved for this callable."""
        uniq = "UNIQUE " if unique else ""
        sql = (
            f"CREATE {uniq}INDEX {self.qname(index_name)} "
            f"ON {self.qname(table_name)} ({self.qname(column_name)})"
        )
        self.execute_query(sql)

    def _maybe_create_index(self, table: str, condition: str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type != "mysql" or not condition:
            return

        m = re.match(r"\s*([A-Za-z0-9_]+)\s+(=|IN)\b", condition)
        if not m:
            return
        col = m.group(1)

        # Internal implementation note: legacy behavior is preserved during modernization.
        sql = (
            "SELECT COUNT(*) FROM information_schema.statistics "
            "WHERE table_schema=%s AND table_name=%s AND column_name=%s"
        )
        if self.fetch_data(sql, (self.db_name, table, col))[0][0]:
            return

        if self.count_rows(table) < 5_000:
            return

        idx = f"auto_{col}"
        logger.info(f"Creating auto‑index {idx} ON {table}({col}) …")
        self.create_index(table, idx, col)

    def create_composite_index(self,
                               table_name: str,
                               index_name: str,
                               columns: List[str],
                               unique: bool = False):
        """Legacy-compatible behavior preserved for this callable."""
        uniq = "UNIQUE " if unique else ""
        cols = ','.join(self.qname(c) for c in columns)
        sql = (
            f"CREATE {uniq}INDEX {self.qname(index_name)} "
            f"ON {self.qname(table_name)} ({cols})"
        )
        self.execute_query(sql)

    def drop_index(self, table_name: str, index_name: str):
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            sql = f"DROP INDEX IF EXISTS {self.qname(index_name)}"
        else:
            sql = (
                f"DROP INDEX {self.qname(index_name)} "
                f"ON {self.qname(table_name)}"
            )
        self.execute_query(sql)

    def table_exists(self, table_name: str, schema: str = 'public') -> bool:
        """Check if a table exists."""
        return table_name in self.list_tables()

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        cols = self.get_columns(table_name)
        return column_name in cols

    def get_columns(self, table_name: str) -> List[str]:
        """Get list of columns in a table."""
        try:
            if self.db_type == "sqlite":
                query = f"PRAGMA table_info({table_name})"
                return [row[1] for row in self.fetch_data(query)]
            else:
                query = (
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = %s AND table_name = %s"
                )
                return [
                    row[0]
                    for row in self.fetch_data(query, (self.db_name, table_name))
                ]
        except Exception as e:
            logger.error(f"Error fetching columns for {table_name}: {e}")
            return []

    def get_table_schema(self, table_name: str) -> List[Tuple[str, str]]:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            rows = self.fetch_data(
                f"PRAGMA table_info({self.qname(table_name)})")
            # row format: (cid, name, type, notnull, dflt_value, pk)
            return [(r[1], r[2]) for r in rows]
        else:
            sql = (
                "SELECT column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s "
                "ORDER BY ordinal_position"
            )
            rows = self.fetch_data(sql, (self.db_name, table_name))
            return [(r[0], r[1]) for r in rows]

    def list_tables(self) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        tables: List[str] = []

        if self.db_type == "sqlite":
            try:
                rows = self.fetch_data(
                    "SELECT name FROM sqlite_option_a WHERE type='table';"
                )
                tables = [r[0] for r in rows]
            except Exception as e:
                logger.error(f"Error listing SQLite tables: {e}")
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                sql = (
                    "SELECT table_name "
                    "FROM information_schema.tables "
                    "WHERE table_schema = %s AND table_type = 'BASE TABLE';"
                )
                rows = self.fetch_data(sql, (self.db_name,))
                tables = [r[0] for r in rows]
            except Exception as e:
                logger.error(f"Error listing MySQL tables: {e}")

        return tables

    def get_tables_with_status(self) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        return [
            table
            for table in self.list_tables()
            if self.column_exists(table, "status")
        ]

    def get_tables_with_parm(self, parm: str) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        return [
            table
            for table in self.list_tables()
            if self.column_exists(table, parm)
        ]
