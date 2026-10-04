from __future__ import annotations

from .accounting_handler_context import *


class AccountingHandlerCoreMixin:
    def is_back(self, message: Message) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if not isinstance(message, Message):
                return False
            if getattr(message, "content_type", None) != "text":
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            text = message.text
            if not text:
                return False
            # Internal implementation note: legacy behavior is preserved during modernization.
            back_buttons = {
                BUTTONS["back_to_previous"],
                BUTTONS["back_to_main"],
                BUTTONS["back_to_accounting"],
                BUTTONS["back_to_bank_accounts"],
                BUTTONS["back_to_crypto_wallets"],
            }
            if text.startswith("/start"):
                self.send_welcome(message)
                return True
            elif text == BUTTONS["back_to_previous"]:
                self.back_to_settings(message)
                return True
            elif text == BUTTONS["back_to_main"]:
                self.send_welcome(message)
                return True
            elif text in back_buttons:
                log.info(f"Received back command: {text}")
                self.back_to_settings(message)
                return True
            return False
        except Exception as e:
            log.error(f"Error in is_back: {e}")
            return False
    def get_bottom_row(self, context, back_button=None):
        """Create the bottom row of buttons including help, back, and main menu."""
        buttons = [types.KeyboardButton(BUTTONS[f"help_{context}"])]
        back_btn = back_button if back_button else BUTTONS["back_to_previous"]
        buttons.extend([types.KeyboardButton(back_btn),
                        types.KeyboardButton(BUTTONS["back_to_main"])])
        return buttons
    def get_menu_keyboard(self, buttons, context, back_button=None):
        """Create a menu keyboard with custom buttons and the bottom row."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*[types.KeyboardButton(btn) for btn in buttons])
        markup.add(*self.get_bottom_row(context, back_button))
        return markup
    def handle_settings_menu(self, message):
        user_id = message.from_user.id
        self.cleanup_temp_data(user_id)
        self.active_sessions.discard(user_id)
        self.back_to_settings(message)
        return True
    def cleanup_temp_data(self, user_id):
        """Clean up temporary data for the user."""
        if user_id in self.temp_data:
            del self.temp_data[user_id]
    def handle_back_buttons(self, message, context):
        text = message.text.strip()
        user_id = message.chat.id
        log.debug(f"{text} => {context}")
        # Handle help button
        if text == BUTTONS.get(f"help_{context}"):
            help_message = MESSAGES.get(
                f"help_{context}", "📌 راهنمایی موجود نیست.")
            self.bot.send_message(user_id, help_message)
            return "HELP"
        # Back to main menu
        if text == BUTTONS.get("back_to_main"):
            self.cleanup_temp_data(user_id)
            self.active_sessions.discard(user_id)
            self.send_welcome(message)
            return True
        # Back to settings menu
        if text == BUTTONS.get("back_to_previous"):
            self.cleanup_temp_data(user_id)
            self.active_sessions.discard(user_id)
            self.back_to_settings(message)
            return True
        # Back to a specific submenu
        if text in self.back_targets:
            target = self.back_targets[text]
            # Internal implementation note: legacy behavior is preserved during modernization.
            if target == context:
                parent = self.parent_menu.get(context)
                if parent and hasattr(self, f"handle_{parent}_menu"):
                    message.text = MESSAGES["back_message"]
                    getattr(self, f"handle_{parent}_menu")(message)
                else:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    self.bot.send_message(
                        user_id, MESSAGES["main_menu_message"])
                return True
            else:
                getattr(self, f"handle_{target}_menu")(message)
                return True
        return False
    def handle_accounting_menu(self, message):
        result = self.handle_back_buttons(message, "accounting")
        if result is True:
            return
        buttons = [
            BUTTONS["bank_accounts"],
            BUTTONS["crypto_wallets"],
        ]
        markup = self.get_menu_keyboard(buttons, "accounting")
        self.bot.send_message(
            message.chat.id, MESSAGES["accounting_menu"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.route_accounting)
    def handle_bank_accounts_menu(self, message):
        buttons = [
            BUTTONS["add_card"],
            BUTTONS["edit_card"],
            BUTTONS["delete_card"],
            BUTTONS["select_default_card"],
        ]
        markup = self.get_menu_keyboard(
            buttons, "bank_accounts", BUTTONS["back_to_accounting"])
        self.bot.send_message(
            message.chat.id, MESSAGES["bank_accounts_menu"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.route_accounting)
    def handle_add_card(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True or result == "HELP":
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.get_bottom_row("bank_accounts",
                   BUTTONS["back_to_bank_accounts"]))
        self.bot.send_message(
            message.chat.id, MESSAGES["enter_card_number"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_card_number)
    def process_card_number(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        card_number = message.text.strip()
        if not re.match(r"^\d{16}$", card_number):
            self.bot.send_message(user_id, MESSAGES["invalid_card_number"])
            self.bot.register_next_step_handler(
                message, self.process_card_number)
            return
        if self.db.select_dict('cards', 'user_id = ? AND card_number = ?', (user_id, card_number)):
            self.bot.send_message(
                user_id, MESSAGES["card_exists"])
            self.handle_bank_accounts_menu(message)
            return
        self.temp_data[user_id] = {'card_number': card_number}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.get_bottom_row("bank_accounts",
                   BUTTONS["back_to_bank_accounts"]))
        self.bot.send_message(
            user_id, MESSAGES["enter_cardholder_name"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_cardholder_name)
    def process_cardholder_name(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_bank_accounts_menu(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        cardholder_name = message.text.strip()
        self.temp_data[user_id]['cardholder_name'] = cardholder_name
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(BUTTONS["yes"], BUTTONS["no"])
        self.bot.send_message(
            user_id, MESSAGES["do_you_want_set_default_card"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_card_default_choice)
    def process_card_default_choice(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data or 'cardholder_name' not in self.temp_data[user_id]:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_bank_accounts_menu(message)
            return
        card_number = self.temp_data[user_id]['card_number']
        cardholder_name = self.temp_data[user_id]['cardholder_name']
        # Internal implementation note: legacy behavior is preserved during modernization.
        choice = message.text.strip().lower()
        if choice == BUTTONS["yes"].lower() or choice == "yes":
            is_default = 1
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.update('cards', {'is_default': 0},
                               'user_id = ?', (user_id,))
            except Exception as e:
                log.error(f"Error upsocial_service cards to non-default: {e}")
        else:
            is_default = 0
        try:
            self.db.insert('cards', {
                'user_id': user_id,
                'card_number': card_number,
                'cardholder_name': cardholder_name,
                'is_default': is_default
            })
            self.bot.send_message(user_id, MESSAGES["card_added_successfully"])
        except Exception as e:
            log.error(f"خطا در افزودن کارت: {e}")
            self.bot.send_message(user_id, MESSAGES["error_adding_card"])
        self.cleanup_temp_data(user_id)
        self.handle_bank_accounts_menu(message)
    def handle_edit_card(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        cards = self.db.select_dict('cards', 'user_id = ?', (user_id,))
        if not cards:
            self.bot.send_message(user_id, MESSAGES["no_cards_found"])
            self.handle_bank_accounts_menu(message)
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for card in cards:
            label = f"Card {card['card_number'][-4:]} ({card['cardholder_name']})"
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("bank_accounts",
                   BUTTONS["back_to_bank_accounts"]))
        self.bot.send_message(
            user_id, MESSAGES["select_card_to_edit"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_card_to_edit)
    def select_currency_for_edit_wallet(self, message):
        """Legacy-compatible behavior preserved for this callable."""
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        wallets = self.db.select_dict('wallets', 'user_id = ?', (user_id,))
        if not wallets:
            self.bot.send_message(user_id, MESSAGES["no_wallets_found"])
            self.handle_crypto_wallets_menu(message)
            return
        currencies = list({w['crypto'] for w in wallets})
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for currency in currencies:
            count = sum(1 for w in wallets if w['crypto'] == currency)
            label = f"{currency} - ({count} wallets)"
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_crypto_wallet_edit"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_currency_for_edit_wallet)
    def process_select_currency_for_edit_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        currency = message.text.split(" - ")[0]
        self.temp_data[user_id] = {'currency': currency}
        self.select_network_for_edit_wallet(message)
