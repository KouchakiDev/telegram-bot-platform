from __future__ import annotations

from .database_manager_context import *


class M_DatabaseManagerDataMixin:
    def normalize_data_by_table_type(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy-compatible behavior preserved for this callable."""
        normalized = {}
        try:
            types_map = self.get_table_column_types(table_name)
            logger.info(f"[Normalize] Start type conversion for table '{table_name}'")

            for column, value in data.items():
                sql_type = types_map.get(column)
                if sql_type:
                    try:
                        normalized[column] = self.convert_value_to_sql_type(sql_type, value)
                    except Exception as convert_err:
                        logger.warning(f"[Normalize] Failed to convert '{column}' → {sql_type} (value: {value}): {convert_err}")
                        normalized[column] = value  # Internal implementation note: legacy behavior is preserved during modernization.
                else:
                    logger.info(f"[Normalize] Column '{column}' not found in schema of table '{table_name}' — kept as-is.")
                    normalized[column] = value  # Internal implementation note: legacy behavior is preserved during modernization.

            logger.info(f"[Normalize] Data normalized for table '{table_name}': {normalized}")
            return normalized

        except Exception as e:
            logger.error(f"[Normalize] Failed to normalize data for table '{table_name}': {e}")
            return data  # Internal implementation note: legacy behavior is preserved during modernization.

    def convert_value_to_sql_type(self, sql_type: str, value: Any) -> Any:
        """Legacy-compatible behavior preserved for this callable."""
        if value is None:
            return None

        sql_type = sql_type.lower()

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if "int" in sql_type:
                return int(value)

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif "float" in sql_type or "double" in sql_type or "decimal" in sql_type:
                return float(value)

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif "char" in sql_type or "text" in sql_type:
                str_val = str(value)
                match = re.search(r'\((\d+)\)', sql_type)
                if match:
                    max_len = int(match.group(1))
                    if len(str_val) > max_len:
                        logger.warning(f"[Convert] Trimming value '{str_val}' to {max_len} characters for type {sql_type}")
                        str_val = str_val[:max_len]
                return str_val

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif "bool" in sql_type:
                return bool(value)

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif "date" in sql_type or "time" in sql_type:
                return value

            # Internal implementation note: legacy behavior is preserved during modernization.
            else:
                return str(value)

        except Exception as e:
            logger.warning(f"[Convert] Failed to convert value '{value}' to SQL type '{sql_type}': {e}")
            return value

    def insert(self,
               table_name: str,
               data: Dict[str, Any],
               column_types: Optional[Dict[str, str]] = None):
        """Insert data into a table."""
        try:

            # data = self.normalize_data_by_table_type(table_name, data)

            data["created_at"] = datetime.now()
            data["last_updated"] = datetime.now()
            self.ensure_table_and_columns(table_name, data, column_types)

            cols = ', '.join(self.qname(c) for c in data.keys())
            # Internal implementation note: legacy behavior is preserved during modernization.
            placeholders = ', '.join([self.placeholder] * len(data))

            query = (f"INSERT INTO {self.qname(table_name)} "
                     f"({cols}) VALUES ({placeholders})")
            self.execute_query(query, tuple(data.values()))
            self.clear_query_cache()

            logger.info(f"Data inserted into table {table_name}.")
        except Exception as e:
            logger.error(f"Error inserting into {table_name}: {e}")

    def upsert( self, table_name: str, data: Dict[str, Any], key: Optional[str] = None,   column_types: Optional[Dict[str, str]] = None,unique_column: Optional[str] = None, schema: Optional[Dict[str, str]] = None,
    ) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        # data = self.normalize_data_by_table_type(table_name, data)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if unique_column is not None:
            key = unique_column
        if schema is not None:
            column_types = schema
        if key is None:
            raise ValueError("key (یا unique_column) نباید None باشد.")

        # Internal implementation note: legacy behavior is preserved during modernization.
        now = datetime.now()
        data["last_updated"] = now

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.ensure_table_and_columns(table_name, data, column_types)

        # Internal implementation note: legacy behavior is preserved during modernization.
        columns = list(data.keys())
        col_names = ", ".join(self.qname(c) for c in columns)
        placeholders = ", ".join([self.placeholder] * len(columns))
        values = tuple(data[c] for c in columns)

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.db_type == "mysql":
            # Internal implementation note: legacy behavior is preserved during modernization.
            if not self._is_column_unique(table_name, key):
                self.create_index(table_name, f"uq_{key}", key, unique=True)

            update_clause = ", ".join(
                f"{self.qname(c)} = VALUES({self.qname(c)})"
                for c in columns if c != key
            )
            sql = (
                f"INSERT INTO {self.qname(table_name)} ({col_names}) "
                f"VALUES ({placeholders}) "
                f"ON DUPLICATE KEY UPDATE {update_clause}"
            )

        else:  # Internal implementation note: legacy behavior is preserved during modernization.
            update_clause = ", ".join(
                f"{self.qname(c)} = excluded.{c}"
                for c in columns if c != key
            )
            sql = (
                f"INSERT INTO {self.qname(table_name)} ({col_names}) "
                f"VALUES ({placeholders}) "
                f"ON CONFLICT({self.qname(key)}) DO UPDATE SET {update_clause}"
            )

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            self.execute_query(sql, values)
            self.clear_query_cache()
            logger.info(f"Upsert into {table_name} succeeded.")
        except Exception as exc:
            logger.error(f"Error during upsert in {table_name}: {exc}")
            raise

    def update(self,
               table_name: str,
               data: Dict[str, Any],
               condition: str,
               params: Tuple):
        """Update data in a table."""
        # data = self.normalize_data_by_table_type(table_name, data)

        try:
            data["last_updated"] = datetime.now()
            self.ensure_table_and_columns(table_name, data)

            # Internal implementation note: legacy behavior is preserved during modernization.
            set_clause = ', '.join(
                f"{self.qname(k)} = {self.placeholder}"
                for k in data.keys()
            )
            if self.db_type == "mysql":
                condition = self.adapt_condition_placeholders(condition)

            query = (f"UPDATE {self.qname(table_name)} SET {set_clause} "
                     f"WHERE {condition}")
            self.execute_query(query, tuple(data.values()) + params)
            self.clear_query_cache()

            logger.info(f"Data updated in {table_name}.")
        except Exception as e:
            logger.error(f"Error upsocial_service {table_name}: {e}")

    def delete(self,
               table_name: str,
               condition: str = "",
               params: Tuple = ()):
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "mysql":
            condition = self.adapt_condition_placeholders(condition)
        where = f"WHERE {condition}" if condition else ""
        sql = f"DELETE FROM {self.qname(table_name)} {where}"
        self.execute_query(sql, params)
        self.clear_query_cache()

    def select(self,
               table_name: str,
               columns: List[str] = None,
               condition: str = "",
               params: Tuple = ()) -> List[Tuple]:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "mysql":
            condition = self.adapt_condition_placeholders(condition)
        cols = '*' if not columns else ','.join(self.qname(c) for c in columns)
        where = f"WHERE {condition}" if condition else ""
        sql = f"SELECT {cols} FROM {self.qname(table_name)} {where}"
        self._maybe_create_index(table_name, condition)

        return self.fetch_data(sql, params)

    def select_dict(
        self,
        table: str,
        condition: str = "",
        params: Tuple = (),
        order_by: str = "",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Legacy-compatible behavior preserved for this callable."""
        table_q = self.qname(table)
        sql_base = f"SELECT * FROM {table_q}"
        # Internal implementation note: legacy behavior is preserved during modernization.
        where_clause = ""
        if condition:
            cond = condition
            if self.placeholder != "?":
                cond = cond.replace("?", self.placeholder)
            if self.placeholder != "%s":
                cond = cond.replace("%s", self.placeholder)
            where_clause = f" WHERE {cond}"
        if self.db_type == "mysql":
            condition = self.adapt_condition_placeholders(condition)
        # Internal implementation note: legacy behavior is preserved during modernization.
        order_clause = f" ORDER BY {order_by}" if order_by else ""
        limit_clause = f" LIMIT {limit}" if limit is not None else ""

        full_sql = sql_base + where_clause + order_clause + limit_clause

        try:
            # conn = self._get_connection()
            cursor = self._get_cursor()
            self._maybe_create_index(table, condition)

            cursor.execute(full_sql, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            msg = str(e).lower()
            if "unknown column" in msg:
                logger.warning(
                    f"Unknown column in WHERE for table '{table}': {condition!r}. Retrying without WHERE.")
                # Internal implementation note: legacy behavior is preserved during modernization.
                fallback_sql = sql_base + order_clause + limit_clause
                try:
                    # conn = self._get_connection()
                    cursor = self._get_cursor()
                    self._maybe_create_index(table, condition)

                    cursor.execute(fallback_sql)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    cursor.close()
                    return [dict(zip(columns, row)) for row in rows]
                except Exception as e2:
                    logger.error(
                        f"Failed to fetch '{table}' without WHERE: {e2}")
                    return []
            else:
                logger.error(f"Error in select_dict for table {table}: {e}")
                return []
        finally:
            cursor.close()
            self.close()

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        conn   = self._get_connection()
        cursor = self._get_cursor()

        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            cursor.execute(query, params)
            conn.commit()
            logger.debug(f"[DataBaseManager.execute_query] | Query executed: {query}")

        except Exception as exc:
            # Internal implementation note: legacy behavior is preserved during modernization.
            conn.rollback()
            msg = str(exc)
            logger.error(
                f"[DataBaseManager.execute_query] | Error executing query: {query} | {msg}"
            )

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                if "Out of range value for column" in msg and "at row" in msg:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    col_name = msg.split("'")[1]

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    table_match = re.search(r"INTO\s+`?(\w+)`?", query, re.IGNORECASE)
                    table_name  = table_match.group(1) if table_match else None

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    values_part = query.split("VALUES")[-1]
                    long_num    = re.search(r"\b\d{11,}\b", values_part)

                    if table_name and long_num:
                        long_value = long_num.group(0)

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        self._convert_column_to_varchar(table_name, col_name, long_value)

                        # Internal implementation note: legacy behavior is preserved during modernization.
                        cursor.execute(query, params)
                        conn.commit()
                        logger.info(
                            "[AutoFix] Re-executed query successfully after VARCHAR upgrade."
                        )
                        return  # Internal implementation note: legacy behavior is preserved during modernization.

            except Exception as autofix_exc:
                # Internal implementation note: legacy behavior is preserved during modernization.
                logger.warning(
                    f"[AutoFix] Failed to handle overflow auto-fix: {autofix_exc}"
                )

            # Internal implementation note: legacy behavior is preserved during modernization.
            raise

        finally:
            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                cursor.close()
            except Exception as exc:
                logger.debug(f"[DataBaseManager.execute_query] | Cursor close failed: {exc}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            try:
                self.close()
            except Exception as exc:
                logger.debug(f"[DataBaseManager.execute_query] | Connection close failed: {exc}")

    def fetch_data(self, query: str, params: Tuple = ()) -> List[Tuple]:
        # conn = self._get_connection()
        cursor = self._get_cursor()
        try:
            if self.db_type == "mysql":
                query = self.adapt_condition_placeholders(query)
            cursor.execute(query, params)
            rows = cursor.fetchall()  # Internal implementation note: legacy behavior is preserved during modernization.
            return rows
            # return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching data: {query} | Error: {e}")
            return []
        finally:
            cursor.close()
            self.close()

    def count_rows(self, table_name: str, condition: str = "", params: Tuple = ()):
        """Count rows in a table."""
        if not self.table_exists(table_name):
            logger.warning(
                f"⚠️ Table {table_name} does not exist; returning 0")
            return 0

        query = f"SELECT COUNT(*) FROM {self.qname(table_name)}"
        # print(condition)
        if self.db_type == "mysql":
            condition = self.adapt_condition_placeholders(condition)
        if condition:
            query += f" WHERE {condition}"

        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.db_type == "sqlite":
            placeholder_count = condition.count("?")
        elif self.db_type == "mysql":
            placeholder_count = condition.count("%s")
        else:
            placeholder_count = condition.count("?")  # Internal implementation note: legacy behavior is preserved during modernization.

        if placeholder_count != len(params):
            logger.warning(
                f"⚠️ Mismatch between placeholders ({placeholder_count}) and params ({len(params)}) in count_rows query: {query}"
            )
            return 0

        try:
            result = self.fetch_data(query, params)
            return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"❌ Error in count_rows for table {table_name}: {e}")
            return 0

    def get_table_size(self, table_name: str) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            # page_count * page_size
            pc = self.fetch_data("PRAGMA page_count")[0][0]
            ps = self.fetch_data("PRAGMA page_size")[0][0]
            return pc * ps
        else:
            sql = (
                "SELECT IFNULL(SUM(data_length + index_length),0) "
                "FROM information_schema.tables "
                "WHERE table_schema = %s AND table_name = %s"
            )
            return int(self.fetch_data(sql, (self.db_name, table_name))[0][0])

    def get_database_size(self) -> int:
        """Legacy-compatible behavior preserved for this callable."""
        if self.db_type == "sqlite":
            pc = self.fetch_data("PRAGMA page_count")[0][0]
            ps = self.fetch_data("PRAGMA page_size")[0][0]
            return pc * ps
        else:
            sql = (
                "SELECT IFNULL(SUM(data_length + index_length),0) "
                "FROM information_schema.tables "
                "WHERE table_schema = %s"
            )
            return int(self.fetch_data(sql, (self.db_name,))[0][0])

    def optimize_table(self, table_name: str):
        """Optimize a table."""
        try:
            if self.db_type == "sqlite":
                query = "VACUUM"
            else:
                query = f"ANALYZE {table_name}"
            self.execute_query(query)
            self.clear_query_cache()

            logger.info(f"Table {table_name} optimized.")
        except Exception as e:
            logger.error(f"Error optimizing table {table_name}: {e}")

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
