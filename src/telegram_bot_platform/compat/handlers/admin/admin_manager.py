import telebot
import json
import re
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
from telegram_bot_platform.compat.config.settings import MESSAGES, BUTTONS, PERMISSIONS, PER_CONV

# Initialize logger
log = CustomLogger("admin_management.log")

# Regex patterns for validation
NAME_PATTERN = r"^(?:[a-zA-Z]{2,25}(?: [a-zA-Z]{2,25})?|[\u0600-\u06FF]{2,25}(?:[\s‌][\u0600-\u06FF]{2,25})?)$"

PHONE_PATTERN = r'^09\d{9}$'
USERNAME_PATTERN = r'^@[a-zA-Z0-9_]{5,}$'


def validate_name(name):
    return bool(re.match(NAME_PATTERN, name))


def validate_phone(phone):
    return bool(re.match(PHONE_PATTERN, phone))


def validate_username(username):
    return bool(re.match(USERNAME_PATTERN, username))


def extract_username(button_text):
    """Extract username from button text like 'First Last (@username)'."""
    match = re.search(r'\(@(.+?)\)', button_text)
    return match.group(1) if match else None


class AdminManager:
    """Class to manage admin operations within the Telegram bot."""

    def __init__(self, bot, db, back_to_main, back_to_settings):
        self.bot = bot
        self.db = db
        self.back_to_main = back_to_main
        self.back_to_settings = back_to_settings
        self.temp_permissions = {}  # Temporary storage for permission toggling
        log.info("✅ AdminManager initialized.")
        self.previous_menus = self.back_to_settings

    def navigation_markup(self):
        """Legacy-compatible behavior preserved for this callable."""
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        return markup

    def register_handlers(self):
        """Register message handlers for admin management."""
        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["manage_admins"])
        def MANAGE_ADMINS_handler(message):
            self.MANAGE_ADMINS_menu(message)

        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["old_admins"])
        def old_admins_handler(message):
            self.show_old_admins(message)

        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["list_admins"])
        def list_admins_handler(message):
            self.view_all_admins(message)

        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["add_new_admin"])
        def add_admin_handler(message):
            self.start_add_admin(message)

        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["edit_admin"])
        def edit_admin_handler(message):
            self.start_edit_admin(message)

        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["remove_admin"])
        def remove_admin_handler(message):
            self.start_remove_admin(message)

        @self.bot.message_handler(func=lambda message: message.text == BUTTONS["back_to_main"])
        def back_handler(message):
            self.back_to_main(message)

    def show_old_admins(self, message):
        """Display admins that have been deactivated (status changed from active to deactive)."""
        admins = self.db.select_dict("admins", "")
        old_admins = [admin for admin in admins if admin.get(
            "A_status", "active").lower() == "deactive"]
        if old_admins:
            response = "\n".join(
                [f"{admin['name']} - (@{admin['username']})" for admin in old_admins])
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            # Split the response into individual items
            for res in response.split('\n'):
                markup.add(KeyboardButton(res))  # Add each admin as a button
            markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
                BUTTONS["back_to_main"]))
            self.bot.send_message(
                message.chat.id, f"مدیران غیر فعال:", reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.select_old_admin)
        else:
            self.bot.send_message(
                message.chat.id, "مدیر غیر فعالی یافت نشد.", reply_markup=self.navigation_markup())
            self.MANAGE_ADMINS_menu(message)

    def select_old_admin(self, message):
        print(message.text)
        if message.text in (BUTTONS["back_to_main"], BUTTONS["back_to_previous"]):
            self.route_adming_manger(message)
            return
        username = extract_username(message.text)
        if not username:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        adam = None

        admin = self.db.select_dict("admins", "username = ?", (username,))
        if not admin:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        print(admin)
        adam = admin[0]
        markup.add(KeyboardButton(BUTTONS["Change_to_active"]))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]), KeyboardButton(
            BUTTONS["back_to_previous"]))
        self.bot.send_message(
            message.chat.id, MESSAGES["doyowanechange"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.Change_or_no, adam)

    def Change_or_no(self, message, admin):
        if message.text in (BUTTONS["back_to_main"], BUTTONS["back_to_previous"]):
            self.route_adming_manger(message)
            return
        print(admin)

        if message.text == BUTTONS["Change_to_active"]:
            self.db.update("admins", {"A_status": "active"},
                           "username = ?", (admin["username"],))
            log.info(f"Admin {admin['username']} activated (set to active).")
            self.bot.send_message(
                message.chat.id, f"ادمین {admin['username']} به وضعیت فعال تغییر یافت.", reply_markup=self.navigation_markup())
            self.MANAGE_ADMINS_menu(message)

            log.info(f"Admin {admin["username"]} activated (set to deactive).")

        ############################

    def route_adming_manger(self, message):

        text = message.text.strip()
        if text == BUTTONS["manage_admins"]:
            self.previous_menus = self.back_to_settings
            self.MANAGE_ADMINS_menu(message)

# SUB Menu of the admin manager
        elif text == BUTTONS["old_admins"]:
            self.previous_menus = self.MANAGE_ADMINS_menu
            self.show_old_admins(message)

        elif text == BUTTONS["list_admins"]:
            self.previous_menus = self.MANAGE_ADMINS_menu
            self.view_all_admins(message)

        elif text == BUTTONS["add_new_admin"]:
            self.previous_menus = self.MANAGE_ADMINS_menu
            self.start_add_admin(message)
        elif text == BUTTONS["edit_admin"]:
            self.previous_menus = self.MANAGE_ADMINS_menu
            self.start_edit_admin(message)
        elif text == BUTTONS["remove_admin"]:
            self.previous_menus = self.MANAGE_ADMINS_menu
            self.start_remove_admin(message)
# Back Func
        elif text == BUTTONS["back_to_main"]:
            self.back_to_main(message)
        elif text == BUTTONS["back_to_previous"]:
            self.previous_menus(message)
        else:
            self.bot.send_message(
                message.chat.id, MESSAGES["invalid_choice"])
            self.back_to_settings(message)

    def MANAGE_ADMINS_menu(self, message):
        """Display the admin management menu."""
        self.previous_menus = self.back_to_settings

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(BUTTONS["list_admins"]), KeyboardButton(
            BUTTONS["add_new_admin"]))
        markup.add(KeyboardButton(BUTTONS["edit_admin"]), KeyboardButton(
            BUTTONS["remove_admin"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["old_admins"]))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(message.chat.id, "منوی مدیریت ادمین‌ها:\n" +
                              MESSAGES.get("admin_management_guide", ""), reply_markup=markup)
        self.bot.register_next_step_handler(message, self.route_adming_manger)

    def view_all_admins(self, message):
        """List all active admins with their details."""

        admins = self.db.select_dict("admins")
        if not admins:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        admin_list = "\n".join(
            [f"{admin['name']}  (@{admin['username']})" for admin in admins if admin.get(
                "A_status", "active").lower() == "active"]
        )
        self.bot.send_message(
            message.chat.id, f"لیست ادمین‌های فعال:\n{admin_list}", reply_markup=self.navigation_markup())
        self.bot.register_next_step_handler(message, self.route_adming_manger)

    # Core Admin Operations
    def add_admin(self, data):
        """Add a new admin to the database."""
        username = data["username"].lstrip('@')
        phone_number = data["phone_number"]
        if self.db.select_dict("admins", "username = ?", (username,)):
            raise ValueError(MESSAGES["admin_exists"])
        if self.db.select_dict("admins", "phone_number = ?", (phone_number,)):
            raise ValueError(MESSAGES["admin_exists"])
        # Internal implementation note: legacy behavior is preserved during modernization.
        data["A_status"] = "active"
        self.db.insert("admins", data)
        log.info(
            f"Admin {username} added with permissions {data['permissions']}.")

    def remove_admin(self, username):
        """Deactivate an admin by changing status to deactive."""
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db.update("admins", {"A_status": "deactive"},
                       "username = ?", (username,))
        log.info(f"Admin {username} deactivated (set to deactive).")

    def edit_admin_field(self, username, field, value):
        """Edit a specific field for an admin by username."""
        if field == "telegram_username":
            field = "username"
            value = value.lstrip('@')
        self.db.update("admins", {field: value}, "username = ?", (username,))
        log.info(f"Field {field} updated for admin {username} to {value}.")

    def edit_admin_permissions(self, username, permissions):
        """Edit an admin's permissions by username."""
        permissions_json = json.dumps(permissions)
        self.db.update(
            "admins", {"permissions": permissions_json}, "username = ?", (username,))
        log.info(f"permissions updated for admin {username}.")

    # Add Admin Workflow
    def start_add_admin(self, message):
        """Start the process to add a new admin."""

        self.bot.send_message(
            message.chat.id, MESSAGES["enter_admin_username"], reply_markup=self.navigation_markup())
        self.bot.register_next_step_handler(message, self.get_username_for_add)

    def get_username_for_add(self, message):
        """Get and validate username for new admin."""
        if message.text in (BUTTONS["back_to_main"], BUTTONS["back_to_previous"]):
            self.route_adming_manger(message)
            return
        username = message.text.strip()
        if not validate_username(username):
            self.bot.send_message(
                message.chat.id, MESSAGES["invalid_username"], reply_markup=self.navigation_markup())
            self.bot.register_next_step_handler(
                message, self.get_username_for_add)
            return
        if self.db.select_dict("admins", "username = ?", (username.lstrip('@'),)):
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_exists"], reply_markup=self.navigation_markup())
            self.bot.register_next_step_handler(
                message, self.get_username_for_add)
            return
        self.bot.send_message(
            message.chat.id, MESSAGES["enter_name"], reply_markup=self.navigation_markup())
        self.bot.register_next_step_handler(
            message, self.get_name_for_add, username)

    def get_name_for_add(self, message, username):
        """Get and validate first name for new admin."""
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        name = message.text.strip()
        if not validate_name(name):
            self.bot.send_message(
                message.chat.id, MESSAGES["invalid_name"], reply_markup=self.navigation_markup())
            self.bot.register_next_step_handler(
                message, self.get_name_for_add, username)
            return
        self.bot.send_message(
            message.chat.id, MESSAGES["enter_phone_number"], reply_markup=self.navigation_markup())
        self.bot.register_next_step_handler(
            message, self.get_phone_number_for_add, username, name)

    def get_phone_number_for_add(self, message, username, name):
        """Get and validate phone number for new admin."""
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        phone_number = message.text.strip()
        if not validate_phone(phone_number):
            self.bot.send_message(
                message.chat.id, MESSAGES["invalid_phone"], reply_markup=self.navigation_markup())
            self.bot.register_next_step_handler(
                message, self.get_phone_number_for_add, username, name)
            return
        if self.db.select_dict("admins", "phone_number = ?", (phone_number,)):
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_exists"], reply_markup=self.navigation_markup())
            self.bot.register_next_step_handler(
                message, self.get_phone_number_for_add, username, name)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        chat_id = message.chat.id
        self.temp_permissions[chat_id] = {
            PER_CONV[per]: False for per in PERMISSIONS}
        self.show_permission_menu(message, username, name, phone_number)

    def show_permission_menu(self, message, username, name, phone_number):
        """Show permission toggling menu for adding admin."""
        chat_id = message.chat.id
        permissions = self.temp_permissions.get(chat_id, {})
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for perm in permissions:
            status = "✅" if permissions[perm] else "❌"
            buttons.append(KeyboardButton(f"{status} {perm}"))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(BUTTONS["back_to_main"]))
        self.bot.send_message(chat_id, MESSAGES["set_permissions"] +
                              "\n(برای تغییر هر گزینه، روی دکمه مربوطه کلیک کنید)", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.toggle_permissions, username, name, phone_number)

    def toggle_permissions(self, message, username, name, phone_number):
        """Handle permission toggling for adding admin."""
        chat_id = message.chat.id
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        text :str = message.text
        if text == BUTTONS["confirm"]:
            self.temp_permissions[chat_id] = {perm_key: self.temp_permissions[chat_id][perm_value]
                                              for perm_key, perm_value in PER_CONV.items() if perm_value in self.temp_permissions[chat_id]}

            admin_data = {
                "telegram_id": None,
                "username": username.lstrip('@'),
                "name": name,
                "phone_number": phone_number,
                "permissions": json.dumps(self.temp_permissions[chat_id])


            }
            try:
                self.add_admin(admin_data)
                self.bot.send_message(chat_id, MESSAGES["admin_added"].format(
                    username=username), reply_markup=self.navigation_markup())
            except ValueError as e:
                self.bot.send_message(chat_id, str(
                    e), reply_markup=self.navigation_markup())
            self.temp_permissions.pop(chat_id, None)
            self.MANAGE_ADMINS_menu(message)
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            perm = self.remove_leading_emoji(text)# Internal implementation note: legacy behavior is preserved during modernization.
            if perm in self.temp_permissions[chat_id]:
                self.temp_permissions[chat_id][perm] = not self.temp_permissions[chat_id][perm]
            self.show_permission_menu(
                message, username, name, phone_number)

    # Edit Admin Workflow
    def start_edit_admin(self, message):
        """Start the process to edit an admin."""

        admins = self.db.select_dict("admins")
        if not admins:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for admin in admins:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if admin.get("A_status", "active").lower() == "active":
                button_text = f"{admin['name']}  (@{admin['username']})"
                buttons.append(KeyboardButton(button_text))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["back_to_main"]), KeyboardButton(
            BUTTONS["back_to_previous"]))
        self.bot.send_message(message.chat.id, MESSAGES["choose_admin_to_edit"].format(
            username=""), reply_markup=markup)
        self.bot.register_next_step_handler(message, self.select_admin_to_edit)

    def select_admin_to_edit(self, message):
        """Select admin to edit and provide editable fields."""
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        username = extract_username(message.text)
        if not username:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        admin = self.db.select_dict("admins", "username = ?", (username,))
        if not admin:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(KeyboardButton(BUTTONS["name"]),
                   KeyboardButton(BUTTONS["telegram_username"]),
                   KeyboardButton(BUTTONS["phone_number"]),
                   KeyboardButton(BUTTONS["permissions"]))

        markup.add(KeyboardButton(BUTTONS["back_to_main"]), KeyboardButton(
            BUTTONS["back_to_previous"]))
        self.bot.send_message(message.chat.id, MESSAGES["choose_field_to_edit"].format(
            username=username), reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.edit_admin_field_handler, username)

    def edit_admin_field_handler(self, message, username):
        """Handle field selection for editing."""
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        field = message.text
        chat_id = message.chat.id
        if field == BUTTONS["permissions"]:
            admin = self.db.select_dict(
                "admins", "username = ?", (username,))[0]
            self.temp_permissions[chat_id] = {PER_CONV[per]: s for per, s in (
                dict(json.loads(admin["permissions"]))).items() if per in PER_CONV}

            self.show_permission_menu_for_edit(message, username)
        else:
            self.bot.send_message(chat_id, MESSAGES["enter_new_value"].format(
                field=field), reply_markup=self.navigation_markup())
            self.bot.register_next_step_handler(
                message, self.update_admin_field, username, field)

    def update_admin_field(self, message, username, field):
        """Update the selected admin field."""
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        value = message.text.strip()
        field_mapping = {
            BUTTONS["name"]: "name",
            BUTTONS["telegram_username"]: "telegram_username",
            BUTTONS["phone_number"]: "phone_number"
        }
        field_key = field_mapping.get(field)
        if field == BUTTONS["telegram_username"]:
            if not validate_username(value):
                self.bot.send_message(
                    message.chat.id, MESSAGES["invalid_username"], reply_markup=self.navigation_markup())
                self.bot.register_next_step_handler(
                    message, self.update_admin_field, username, field)
                return
            if self.db.select_dict("admins", "username = ? AND username != ?", (value.lstrip('@'), username)):
                self.bot.send_message(
                    message.chat.id, MESSAGES["admin_exists"], reply_markup=self.navigation_markup())
                self.bot.register_next_step_handler(
                    message, self.update_admin_field, username, field)
                return
        elif field == BUTTONS["phone_number"]:
            if not validate_phone(value):
                self.bot.send_message(
                    message.chat.id, MESSAGES["invalid_phone"], reply_markup=self.navigation_markup())
                self.bot.register_next_step_handler(
                    message, self.update_admin_field, username, field)
                return
            if self.db.select_dict("admins", "phone_number = ? AND username != ?", (value, username)):
                self.bot.send_message(
                    message.chat.id, MESSAGES["admin_exists"], reply_markup=self.navigation_markup())
                self.bot.register_next_step_handler(
                    message, self.update_admin_field, username, field)
                return
        elif field in [BUTTONS["name"]]:
            if not validate_name(value):
                self.bot.send_message(
                    message.chat.id, MESSAGES["invalid_name"], reply_markup=self.navigation_markup())
                self.bot.register_next_step_handler(
                    message, self.update_admin_field, username, field)
                return
        self.edit_admin_field(username, field_key, value)
        self.bot.send_message(message.chat.id, MESSAGES["admin_updated"].format(
            username=username), reply_markup=self.navigation_markup())
        self.MANAGE_ADMINS_menu(message)

    def show_permission_menu_for_edit(self, message, username):
        """Show permission toggling menu for editing."""
        chat_id = message.chat.id
        permissions = self.temp_permissions.get(chat_id, {})
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for perm in permissions:
            status = "✅" if permissions[perm] else "❌"
            buttons.append(KeyboardButton(f"{status} {perm}"))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["confirm"]))
        markup.add(KeyboardButton(BUTTONS["back_to_main"]), KeyboardButton(
            BUTTONS["back_to_previous"]))
        self.bot.send_message(
            chat_id, MESSAGES["set_permissions"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.toggle_permissions_for_edit, username)

    def remove_leading_emoji(self , text: str) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            cleaned = re.sub(r'^\s*[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+\s*', '', text).strip()
            return cleaned
        except Exception as e:
            print(f"remove_leading_emoji failed: {e}")
            return text

    def toggle_permissions_for_edit(self, message, username):
        """Handle permission toggling for editing."""
        chat_id = message.chat.id
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        text = message.text
        if text == BUTTONS["confirm"]:
            # inj
            self.temp_permissions[chat_id] = {perm_key: self.temp_permissions[chat_id][perm_value]
                                              for perm_key, perm_value in PER_CONV.items() if perm_value in self.temp_permissions[chat_id]}

            self.edit_admin_permissions(
                username, self.temp_permissions[chat_id])
            self.bot.send_message(chat_id, MESSAGES["admin_updated"].format(
                username=username), reply_markup=self.navigation_markup())
            self.temp_permissions.pop(chat_id, None)
            self.MANAGE_ADMINS_menu(message)
        else:
            perm = self.remove_leading_emoji(text)# Internal implementation note: legacy behavior is preserved during modernization.
            if perm in self.temp_permissions[chat_id]:
                self.temp_permissions[chat_id][perm] = not self.temp_permissions[chat_id][perm]
            self.show_permission_menu_for_edit(message, username)

    # Remove Admin Workflow
    def start_remove_admin(self, message):
        """Start the process to remove (deactivate) an admin."""

        admins = self.db.select_dict("admins")
        if not admins:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for admin in admins:
            if admin.get("A_status", "active").lower() == "active":
                button_text = f"{admin['name']}  (@{admin['username']})"
                buttons.append(KeyboardButton(button_text))
        markup.add(*buttons)
        markup.add(KeyboardButton(BUTTONS["back_to_main"]), KeyboardButton(
            BUTTONS["back_to_previous"]))
        self.bot.send_message(
            message.chat.id, MESSAGES["choose_admin_to_remove"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.confirm_remove_admin)

    def confirm_remove_admin(self, message):
        """confirm admin removal with full details."""
        if message.text in [BUTTONS["back_to_main"], BUTTONS["back_to_previous"]]:
            self.route_adming_manger(message)
            return
        username = extract_username(message.text)
        if not username:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        admin = self.db.select_dict("admins", "username = ?", (username,))
        if not admin:
            self.bot.send_message(
                message.chat.id, MESSAGES["admin_not_found"], reply_markup=self.navigation_markup())
            return
        admin = admin[0]
        admin['permissions'] = {PER_CONV[per]: s for per,
                                s in dict(json.loads(admin["permissions"])).items() if per in PER_CONV}

        details = (
            f"نام: {admin['name']} \n"
            f"نام کاربری: @{admin['username']}\n"
            f"شماره تلفن: {admin['phone_number']}\n"
            f"دسترسی‌ها:\n" + "\n".join([f"{key} {'✔' if value else '❌'}" for key,
                                        value in admin['permissions'].items()])
        )
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(BUTTONS["delete"]))
        markup.add(KeyboardButton(BUTTONS["back_to_previous"]), KeyboardButton(
            BUTTONS["back_to_main"]))
        self.bot.send_message(
            message.chat.id, f"جزئیات ادمین:\n{details}\n\nآیا مطمئن هستید که می‌خواهید این ادمین را غیر فعال کنید؟", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.remove_admin_final, username)

    def remove_admin_final(self, message, username):
        """Finalize admin removal (set status to deactive)."""
        if message.text == BUTTONS["delete"]:
            self.remove_admin(username)
            self.bot.send_message(message.chat.id, MESSAGES["admin_deleted"].format(
                username=username), reply_markup=self.navigation_markup())
        else:
            self.bot.send_message(
                message.chat.id, MESSAGES["request_canceled"], reply_markup=self.navigation_markup())
        self.MANAGE_ADMINS_menu(message)
