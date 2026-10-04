from __future__ import annotations

from .database_manager_context import *
from .database_manager_lifecycle import M_DatabaseManagerLifecycleMixin
from .database_manager_schema import M_DatabaseManagerSchemaMixin
from .database_manager_data import M_DatabaseManagerDataMixin
from .database_manager_settings import M_DatabaseManagerSettingsMixin
from .database_manager_transactions import M_DatabaseManagerTransactionsMixin
from .database_manager_advanced import M_DatabaseManagerAdvancedMixin


class M_DatabaseManager(M_DatabaseManagerLifecycleMixin, M_DatabaseManagerSchemaMixin, M_DatabaseManagerDataMixin, M_DatabaseManagerSettingsMixin, M_DatabaseManagerTransactionsMixin, M_DatabaseManagerAdvancedMixin):
    def __init__(self, db_type: str, db_name: str, host: Optional[str] = None,
                 user: Optional[str] = None, password: Optional[str] = None, port=None
                 ):
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db_type = db_type.lower()
        self.db_name = db_name
        self.host = host
        self.user = user
        self.port = port or 3306
        self.inferer = TypeInferer()
        self.password = password
        self.create_database_if_not_exists(db_name)
        self.query_cache = {}
        self.local = threading.local()  # Internal implementation note: legacy behavior is preserved during modernization.
        self.lock = threading.Lock()
        self.transaction_level = 0
        self.placeholder = MYSQL_PLACEHOLDER if self.db_type == "mysql" else SQLITE_PLACEHOLDER
    # Internal implementation note: legacy behavior is preserved during modernization.
        self.column_types: Dict[str, str] = {}
    
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db_name
        )
    
        # self.cursor = self.connection.cursor()
        logger.info(
            f"Database {self.db_type} with name {self.db_name} initialized.")

def replace_placeholders_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = [
            arg.replace("?", "%s") if isinstance(arg, str) else arg
            for arg in args
        ]
        new_kwargs = {
            k: v.replace("?", "%s") if isinstance(v, str) else v
            for k, v in kwargs.items()
        }
        return func(*new_args, **new_kwargs)
    return wrapper


class DatabaseManager(M_DatabaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(
            f"CustomDatabaseManager initialized for database: {self.db_name}")

        # Internal implementation note: legacy behavior is preserved during modernization.
        for attr_name in dir(self):
            if attr_name.startswith("__"):
                continue  # Internal implementation note: legacy behavior is preserved during modernization.
            attr = getattr(self, attr_name)
            if isinstance(attr, types.MethodType):
                wrapped = replace_placeholders_decorator(attr)
                setattr(self, attr_name, wrapped)


def Test():
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    """Legacy-compatible behavior preserved for this callable."""

    # Internal implementation note: legacy behavior is preserved during modernization.
    DB_PARAMS = {
        "db_type": "mysql",
        "db_name": "testing",            # Internal implementation note: legacy behavior is preserved during modernization.
        "host":    "127.0.0.1",        # Internal implementation note: legacy behavior is preserved during modernization.
        "user":    "root",
        # Internal implementation note: legacy behavior is preserved during modernization.
        "password": os.getenv("DB_PASSWORD")
    }

    TABLE = "test_humans"
    LOG_FILE = "db_test_results.log"

    COLUMNS = {
        "first_name":      "VARCHAR(50)",
        "last_name":       "VARCHAR(50)",
        "age":             "INT",
        "height_cm":       "FLOAT",
        "weight_kg":       "FLOAT",
        "email":           "VARCHAR(100)",
        "phone":           "VARCHAR(20)",
        "birth_date":      "DATE",
        "is_active":       "BOOLEAN",
        "score":           "DECIMAL(5,2)",
        "bio":             "TEXT",
        "country":         "VARCHAR(50)",
        "city":            "VARCHAR(50)",
        "zip_code":        "VARCHAR(10)",
        "join_time":       "TIME",
        "last_login":      "DATETIME",
        "profile_picture": "BLOB",
        "preferences":     "JSON",
        "rating":          "DOUBLE",
        "nickname":        "CHAR(20)",
    }

    def write_header(path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write("DATABASE MANAGER TEST RESULTS\n")
            f.write(f"Started: {datetime.now()}\n")
            f.write("=" * 60 + "\n")

    def log_result(path: str, name: str, ok: bool, details: str = ""):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{'PASS' if ok else 'FAIL'}] {name}\n")
            if details:
                f.write(f"       {details}\n")

    def main():
        write_header(LOG_FILE)

        db = DatabaseManager(**DB_PARAMS)  # **DB_PARAMS)

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            db.drop_table(TABLE)
            log_result(LOG_FILE, "drop_table", True)
        except Exception as e:
            log_result(LOG_FILE, "drop_table", False, str(e))

        try:
            db.create_table(TABLE, COLUMNS)
            log_result(LOG_FILE, "create_table", True)
        except Exception as e:
            log_result(LOG_FILE, "create_table", False, str(e))

        # Internal implementation note: legacy behavior is preserved during modernization.
        for i in range(1, 11):
            test_name = f"insert_row_{i}"
            try:
                db.insert(
                    TABLE,
                    {
                        "first_name":  f"First{i}",
                        "last_name":   f"Last{i}",
                        "age":         20 + i,
                        "height_cm":   160 + i,
                        "weight_kg":   60 + i,
                        "email":       f"user{i}@test.com",
                        "phone":       f"+1234567890{i}",
                        "birth_date":  f"199{i}-01-01",
                        "is_active":   i % 2 == 0,
                        "score":       round(50 + i * 1.1, 2),
                        "bio":         f"Test bio {i}",
                        "country":     "CountryX",
                        "city":        f"City{i}",
                        "zip_code":    f"ZIP{i:04}",
                        "join_time":   "12:00:00",
                        "last_login":  "2025-05-01 12:00:00",
                        "profile_picture": b"",
                        "preferences": json.dumps({"theme": "dark"}),
                        "rating":      4.5 + i / 10,
                        "nickname":    f"Nick{i}",
                    },
                )
                log_result(LOG_FILE, test_name, True)
            except Exception as e:
                log_result(LOG_FILE, test_name, False, str(e))

        # Internal implementation note: legacy behavior is preserved during modernization.
        read_tests = [
            ("count_rows", lambda: str(db.count_rows(TABLE))),
            ("get_columns", lambda: str(db.get_columns(TABLE))),
            ("list_tables", lambda: str(db.list_tables())),       # Internal implementation note: legacy behavior is preserved during modernization.
            ("select", lambda: str(db.select(TABLE))),
            ("select_dict", lambda: str(db.select_dict(TABLE))),
            ("column_exists", lambda: str(db.column_exists(TABLE, "age"))),
            ("get_table_schema", lambda: str(db.get_table_schema(TABLE))),
            ("get_table_size", lambda: str(db.get_table_size(TABLE))),
            ("get_database_size", lambda: str(db.get_database_size())),
            ("get_current_user", lambda: db.get_current_user()),
        ]
        for name, fn in read_tests:
            try:
                result = fn()
                log_result(LOG_FILE, name, True, result)
            except Exception as e:
                log_result(LOG_FILE, name, False, str(e))

        # Internal implementation note: legacy behavior is preserved during modernization.
        try:
            db.update(TABLE, {"city": "UpdatedCity"}, "id = %s", (1,))
            log_result(LOG_FILE, "update", True, "row#1 city → UpdatedCity")
        except Exception as e:
            log_result(LOG_FILE, "update", False, str(e))

        try:
            db.upsert(TABLE, {"first_name": "First1",
                      "age": 99}, key="first_name")
            log_result(LOG_FILE, "upsert", True, "First1 age → 99")
        except Exception as e:
            log_result(LOG_FILE, "upsert", False, str(e))

        try:
            db.add_column(TABLE, "new_column", "VARCHAR(100)")
            log_result(LOG_FILE, "add_column", True, "new_column added")
        except Exception as e:
            log_result(LOG_FILE, "add_column", False, str(e))

        try:
            db.create_index(TABLE, "idx_first_name", "first_name")
            log_result(LOG_FILE, "create_index",
                       True, "idx_first_name created")
        except Exception as e:
            log_result(LOG_FILE, "create_index", False, str(e))

        try:
            db.drop_index(TABLE, "idx_first_name")
            log_result(LOG_FILE, "drop_index", True, "idx_first_name dropped")
        except Exception as e:
            log_result(LOG_FILE, "drop_index", False, str(e))

        try:
            stats = str(db.get_table_stats(TABLE))
            log_result(LOG_FILE, "get_table_stats", True, stats)
        except Exception as e:
            log_result(LOG_FILE, "get_table_stats", False, str(e))

        try:
            ping = str(db.ping())
            log_result(LOG_FILE, "ping", True, ping)
        except Exception as e:
            log_result(LOG_FILE, "ping", False, str(e))

        try:
            conn = str(db.is_connected())
            log_result(LOG_FILE, "is_connected", True, conn)
        except Exception as e:
            log_result(LOG_FILE, "is_connected", False, str(e))

        try:
            db.create_composite_index(
                TABLE, "idx_name_age", ["first_name", "age"])
            log_result(LOG_FILE, "create_composite_index",
                       True, "idx_name_age created")
        except Exception as e:
            log_result(LOG_FILE, "create_composite_index", False, str(e))

        try:
            db.drop_index(TABLE, "idx_name_age")
            log_result(LOG_FILE, "drop_composite_index",
                       True, "idx_name_age dropped")
        except Exception as e:
            log_result(LOG_FILE, "drop_composite_index", False, str(e))

        try:
            db.delete(TABLE, "id = %s", (1,))
            remaining = db.count_rows(TABLE)
            log_result(LOG_FILE, "delete(id=1)", True,
                       f"remaining rows={remaining}")
        except Exception as e:
            log_result(LOG_FILE, "delete(id=1)", False, str(e))

        # Internal implementation note: legacy behavior is preserved during modernization.
        db.close()
        log_result(LOG_FILE, "CLOSE_CONNECTION", True)
        print(f"\n📑Test completed and saved in: «{os.path.abspath(LOG_FILE)}»")

    if __name__ == "__main__":
        main()
