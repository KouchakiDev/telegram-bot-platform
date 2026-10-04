from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import DB_PARAMS

import json


class DatabaseSetup:
    def __init__(self):
        """Initial setup for the database and constant definitions."""
        self.db = DatabaseManager(**DB_PARAMS)  # *DB_PARAMS)
        self.all_permissions = {
            "manage_requests": True,
            "auto_answer" : True,
            "manage_users":True,
            "manage_admins": True,
            "bot_settings": True,
            "add_admin": True,
            "remove_admin": True,
            "edit_admin": True,
            "request_settings": True,
            "view_reports": True,
            "manage_clients": True,
            "manage_staff": True,
            "channel_settings": True,
            "group_settings": True,
            "create_ad": True,
            "ads_settins": True,
            "manage_messages": True,
            "manage_codes": True,
            "accounting": True,
            "automatical": True,  # New line to activate the accounting module
        }

    def setup_admin(self):
        """Add the primary admin if not already present."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        admins_columns = {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "telegram_id": "VARCHAR(191) UNIQUE",
            "username": "VARCHAR(191) UNIQUE",
            "name": "TEXT",
            "phone_number": "VARCHAR(20) UNIQUE",
            "A_status": "TEXT",
            "permissions": "TEXT"
        }

        admin_data = {
            'telegram_id': os.getenv("PRIMARY_ADMIN_ID", ""),
            'username': os.getenv("PRIMARY_ADMIN_USERNAME", ""),
            'name': os.getenv("PRIMARY_ADMIN_NAME", "Platform Owner"),
            'phone_number': os.getenv("PRIMARY_ADMIN_PHONE", ""),
            "A_status": "active",
            'permissions': json.dumps(self.all_permissions)
        }
        # Internal implementation note: legacy behavior is preserved during modernization.
        # self.db.drop_table("admins")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.create_table("admins", admins_columns)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.upsert("admins", admin_data, "telegram_id",
                       column_types=admins_columns)
        print("✅ Primary admin has been added.")
