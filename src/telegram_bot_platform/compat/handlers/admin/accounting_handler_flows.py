from __future__ import annotations

from .accounting_handler_context import *


class AccountingHandlerFlowsMixin:
    def select_network_for_edit_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        currency = self.temp_data[user_id]['currency']
        wallets = self.db.select_dict(
            'wallets', 'user_id = ? AND crypto = ?', (user_id, currency))
        if not wallets:
            self.bot.send_message(user_id, MESSAGES["no_wallets_found"])
            self.handle_crypto_wallets_menu(message)
            return
        networks = list({w['network'] for w in wallets})
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for network in networks:
            count = sum(1 for w in wallets if w['network'] == network)
            label = f"{network} - ({count} wallets)"
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_wallet_address_edit"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_network_for_edit_wallet)
    def process_select_network_for_edit_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        network = message.text.split(" - ")[0]
        self.temp_data[user_id]['network'] = network
        self.select_wallet_address_for_edit_wallet(message)
    def select_wallet_address_for_edit_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        currency = self.temp_data[user_id]['currency']
        network = self.temp_data[user_id]['network']
        wallets = self.db.select_dict(
            'wallets', 'user_id = ? AND crypto = ? AND network = ?', (user_id, currency, network))
        if not wallets:
            self.bot.send_message(user_id, MESSAGES["no_wallets_found"])
            self.handle_crypto_wallets_menu(message)
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for wallet in wallets:
            # Internal implementation note: legacy behavior is preserved during modernization.
            label = f"{wallet['address'][:6]}...{wallet['address'][-6:]}"
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_wallet_address_edit"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_wallet_address_for_edit_wallet)
    def process_select_wallet_address_for_edit_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        selected_label = message.text.strip()
        currency = self.temp_data[user_id]['currency']
        network = self.temp_data[user_id]['network']
        wallets = self.db.select_dict(
            'wallets', 'user_id = ? AND crypto = ? AND network = ?', (user_id, currency, network))
        selected_wallet = next((w for w in wallets if selected_label ==
                               f"{w['address'][:6]}...{w['address'][-6:]}"), None)
        if not selected_wallet:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            self.select_wallet_address_for_edit_wallet(message)
            return
        self.temp_data[user_id]['selected_wallet'] = selected_wallet
        # Internal implementation note: legacy behavior is preserved during modernization.
        buttons = [BUTTONS["edit_crypto_wallet"], BUTTONS["edit_network_only"],
                   BUTTONS["edit_wallet_address"]]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*[types.KeyboardButton(btn) for btn in buttons])
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_option_edit_wallet"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_edit_wallet_field)
    def process_edit_wallet_option(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        selected_wallet = self.temp_data[user_id].get('selected_wallet')
        if not selected_wallet:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        if message.text.strip() == BUTTONS["edit_wallet_address_option"]:
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=2)
            markup.add(*self.get_bottom_row("crypto_wallets",
                       BUTTONS["back_to_crypto_wallets"]))
            self.bot.send_message(
                user_id, MESSAGES["enter_new_wallet_address"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_wallet_address_for_edit)
        elif message.text.strip() == BUTTONS["edit_network_wallet"]:
            # Internal implementation note: legacy behavior is preserved during modernization.
            crypto = selected_wallet['crypto']
            networks = CRYPTO_CURRENCY.get(crypto, [])
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=2)
            for net in networks:
                markup.add(types.KeyboardButton(net))
            markup.add(*self.get_bottom_row("crypto_wallets",
                       BUTTONS["back_to_crypto_wallets"]))
            self.bot.send_message(
                user_id, MESSAGES["select_new_wallet_network"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_network_for_edit)
        else:
            self.bot.send_message(user_id, MESSAGES["invalid_choice"])
            self.select_wallet_address_for_edit_wallet(message)
    def process_new_wallet_address_for_edit(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        new_address = message.text.strip()
        if not re.match(r'^(0x)?[A-Za-z0-9]{20,100}$', new_address):
            self.bot.send_message(user_id, MESSAGES["invalid_wallet_address"])
            self.bot.register_next_step_handler(
                message, self.process_new_wallet_address_for_edit)
            return
        selected_wallet = self.temp_data[user_id].get('selected_wallet')
        if not selected_wallet:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        try:
            self.db.update(
                'wallets', {'address': new_address}, 'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["wallet_address_updated"])
        except Exception as e:
            log.error(f"خطا در به‌روزرسانی کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_upsocial_service_wallet"])
        self.cleanup_temp_data(user_id)
        self.handle_crypto_wallets_menu(message)
    def process_select_card_to_edit(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        cards = self.db.select_dict('cards', 'user_id = ?', (user_id,))
        selected_card = next(
            (card for card in cards if f"Card {card['card_number'][-4:]} ({card['cardholder_name']})" == message.text), None)
        if not selected_card:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_select_card_to_edit)
            return
        self.temp_data[user_id] = {'selected_card': selected_card}
        buttons = [BUTTONS["edit_card_number"],
                   BUTTONS["edit_cardholder_name"]]
        markup = self.get_menu_keyboard(
            buttons, "bank_accounts", BUTTONS["back_to_bank_accounts"])
        self.bot.send_message(
            user_id, MESSAGES["select_field_to_edit"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_edit_card_field)
    def process_edit_card_field(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_bank_accounts_menu(message)
            return
        selected_card = self.temp_data[user_id]['selected_card']
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.get_bottom_row("bank_accounts",
                   BUTTONS["back_to_bank_accounts"]))
        if message.text == BUTTONS["edit_card_number"]:
            self.bot.send_message(
                user_id, MESSAGES["enter_new_card_number"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_card_number, selected_card)
        elif message.text == BUTTONS["edit_cardholder_name"]:
            self.bot.send_message(
                user_id, MESSAGES["enter_new_cardholder_name"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_cardholder_name, selected_card)
        else:
            self.bot.send_message(user_id, MESSAGES["invalid_choice"])
            self.handle_bank_accounts_menu(message)
    def process_new_card_number(self, message, selected_card):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        new_number = message.text.strip()
        if not re.match(r"^\d{16}$", new_number):
            self.bot.send_message(user_id, MESSAGES["invalid_card_number"])
            self.bot.register_next_step_handler(
                message, self.process_new_card_number, selected_card)
            return
        if self.db.select_dict('cards', 'user_id = ? AND card_number = ? AND id != ?', (user_id, new_number, selected_card['id'])):
            self.bot.send_message(
                user_id, MESSAGES["card_exists"])
            self.handle_bank_accounts_menu(message)
            return
        try:
            self.db.update(
                'cards', {'card_number': new_number}, 'id = ?', (selected_card['id'],))
            self.bot.send_message(user_id, MESSAGES["card_number_updated"])
        except Exception as e:
            log.error(f"خطا در به‌روزرسانی شماره کارت: {e}")
            self.bot.send_message(user_id, MESSAGES["error_upsocial_service_card"])
        self.cleanup_temp_data(user_id)
        self.handle_bank_accounts_menu(message)
    def process_new_cardholder_name(self, message, selected_card):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        new_name = message.text.strip()
        try:
            self.db.update(
                'cards', {'cardholder_name': new_name}, 'id = ?', (selected_card['id'],))
            self.bot.send_message(user_id, MESSAGES["cardholder_name_updated"])
        except Exception as e:
            log.error(f"خطا در به‌روزرسانی نام دارنده کارت: {e}")
            self.bot.send_message(user_id, MESSAGES["error_upsocial_service_card"])
        self.cleanup_temp_data(user_id)
        self.handle_bank_accounts_menu(message)
    def handle_delete_card(self, message):
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
            user_id, MESSAGES["select_card_to_delete"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.process_delete_card)
    def process_delete_card(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        cards = self.db.select_dict('cards', 'user_id = ?', (user_id,))
        selected_card = next(
            (card for card in cards if f"Card {card['card_number'][-4:]} ({card['cardholder_name']})" == message.text), None)
        if not selected_card:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_delete_card)
            return
        try:
            self.db.delete('cards', 'id = ?', (selected_card['id'],))
            self.bot.send_message(user_id, MESSAGES["card_deleted"])
        except Exception as e:
            log.error(f"خطا در حذف کارت: {e}")
            self.bot.send_message(user_id, MESSAGES["error_deleting_card"])
        self.handle_bank_accounts_menu(message)
    def handle_select_default_card(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        cards = self.db.select_dict('cards', 'user_id = ?', (user_id,))
        if not cards:
            self.bot.send_message(user_id, MESSAGES["no_cards_found"])
            self.handle_bank_accounts_menu(message)
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for card in cards:
            label = f"کارت - {card['card_number'][-4:]} - {card['cardholder_name']}" + (
                "☑" if int(card['is_default']) else "")
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("bank_accounts",
                   BUTTONS["back_to_bank_accounts"]))
        self.bot.send_message(
            user_id, MESSAGES["select_default_card"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_default_card)
    def process_select_default_card(self, message):
        result = self.handle_back_buttons(message, "bank_accounts")
        if result == True or result == "HELP":
            return
        user_id = message.chat.id
        cards = self.db.select_dict('cards', 'user_id = ?', (user_id,))
        selected_card = next(
            (card for card in cards if message.text.startswith(f"کارت - {card['card_number'][-4:]} - {card['cardholder_name']}")), None)
        if not selected_card:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_select_default_card)
            return
        try:
            self.db.update('cards', {'is_default': 0},
                           'user_id = ?', (user_id,))
            self.db.update('cards', {'is_default': 1},
                           'id = ?', (selected_card['id'],))
            self.bot.send_message(user_id, MESSAGES["default_card_selected"])
        except Exception as e:
            log.error(f"خطا در انتخاب کارت پیش‌فرض: {e}")
            self.bot.send_message(user_id, MESSAGES["error_selecting_default"])
        self.handle_bank_accounts_menu(message)
    def handle_crypto_wallets_menu(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        buttons = [
            BUTTONS["add_wallet"],
            BUTTONS["edit_wallet"],
            BUTTONS["delete_wallet"],
            BUTTONS["select_wallet"],  # New option for dynamic selection
        ]
        markup = self.get_menu_keyboard(
            buttons, "crypto_wallets", BUTTONS["back_to_accounting"])
        self.bot.send_message(
            message.chat.id, MESSAGES["crypto_wallets_menu"], reply_markup=markup)
        self.bot.register_next_step_handler(message, self.route_accounting)
    def handle_add_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*[types.KeyboardButton(crypto)
                   for crypto in CRYPTO_CURRENCY.keys()])
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            message.chat.id, MESSAGES["select_crypto"], reply_markup=markup)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(
            message, self.process_select_crypto)
