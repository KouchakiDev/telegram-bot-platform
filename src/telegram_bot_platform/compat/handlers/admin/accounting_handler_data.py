from __future__ import annotations

from .accounting_handler_context import *


class AccountingHandlerDataMixin:
    def process_select_crypto(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        crypto = message.text
        if crypto not in CRYPTO_CURRENCY:
            self.bot.send_message(user_id, MESSAGES["invalid_crypto"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_select_crypto)
            return
        self.temp_data[user_id] = {'crypto': crypto}
        networks = CRYPTO_CURRENCY[crypto]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*[types.KeyboardButton(network) for network in networks])
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_network"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_network)
    def process_select_network(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        network = message.text
        print(network)
        crypto = self.temp_data[user_id]['crypto']
        print(crypto)
        print(CRYPTO_CURRENCY[crypto])
        if network not in CRYPTO_CURRENCY[crypto]:
            self.bot.send_message(user_id, MESSAGES["invalid_network"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_select_network)  # injest
            return
        self.temp_data[user_id]['network'] = network
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["enter_wallet_address"], reply_markup=markup)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot.register_next_step_handler(
            message, self.process_wallet_address_input)
    def process_wallet_address_input(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        address = message.text.strip()
        crypto = self.temp_data[user_id]['crypto']
        network = self.temp_data[user_id]['network']
        # Internal implementation note: legacy behavior is preserved during modernization.
        if not re.match(r'^(0x)?[A-Za-z0-9]{20,100}$', address):
            self.bot.send_message(user_id, MESSAGES["invalid_wallet_address"])
            self.bot.register_next_step_handler(
                message, self.process_wallet_address_input)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        if self.db.select_dict('wallets', 'user_id = ? AND crypto = ? AND network = ? AND address = ?',
                               (user_id, crypto, network, address)):
            self.bot.send_message(user_id, MESSAGES["wallet_exists"])
            self.handle_crypto_wallets_menu(message)
            return
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_data[user_id]['address'] = address
        # Internal implementation note: legacy behavior is preserved during modernization.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(BUTTONS["yes"], BUTTONS["no"])
        self.bot.send_message(
            user_id, MESSAGES["do_you_want_set_default"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_wallet_default_choice)
    def process_wallet_default_choice(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data or 'address' not in self.temp_data[user_id]:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        address = self.temp_data[user_id]['address']
        crypto = self.temp_data[user_id]['crypto']
        network = self.temp_data[user_id]['network']
        # Internal implementation note: legacy behavior is preserved during modernization.
        choice = message.text.strip().lower()
        if choice == BUTTONS["yes"].lower() or choice == "yes":
            is_default = 1
            try:
                # Internal implementation note: legacy behavior is preserved during modernization.
                self.db.update(
                    'wallets',
                    {"is_default": 0},
                    f"user_id = ? AND crypto = ? AND network = ? AND address != ?",
                    params=(user_id, crypto, network, address,)
                )
            except Exception as e:
                log.error(f"Error upsocial_service wallets to non-default: {e}")
        else:
            is_default = 0
        try:
            self.db.insert('wallets', {
                'user_id': user_id,
                'crypto': crypto,
                'network': network,
                'address': address,
                'is_default': is_default
            })
            self.bot.send_message(
                user_id, MESSAGES["wallet_added_successfully"])
        except Exception as e:
            log.error(f"خطا در افزودن کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_adding_wallet"])
        self.cleanup_temp_data(user_id)
        self.handle_crypto_wallets_menu(message)
    def handle_edit_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        wallets = self.db.select_dict('wallets', 'user_id = ?', (user_id,))
        if not wallets:
            self.bot.send_message(user_id, MESSAGES["no_wallets_found"])
            self.handle_crypto_wallets_menu(message)
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for wallet in wallets:
            label = f"{wallet['crypto']} ({wallet['network']}) - {wallet['address'][-6:]}"
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_wallet_to_edit"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_wallet_to_edit)
    def process_select_wallet_to_edit(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        wallets = self.db.select_dict('wallets', 'user_id = ?', (user_id,))
        selected_wallet = next(
            (w for w in wallets if f"{w['crypto']} ({w['network']}) - {w['address'][-6:]}" == message.text), None)
        if not selected_wallet:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            self.handle_edit_wallet(message)
            return
        self.temp_data[user_id] = {'selected_wallet': selected_wallet}
        buttons = [BUTTONS["edit_crypto_wallet"], BUTTONS["edit_network_only"],
                   BUTTONS["edit_wallet_address"]]  # injest2
        markup = self.get_menu_keyboard(
            buttons, "crypto_wallets", BUTTONS["back_to_crypto_wallets"])
        self.bot.send_message(
            user_id, MESSAGES["select_field_to_edit_wallet"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_edit_wallet_field)
    def process_edit_wallet_field(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        selected_wallet = self.temp_data[user_id]['selected_wallet']
        if message.text == BUTTONS["edit_crypto_wallet"]:
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=2)
            markup.add(*[types.KeyboardButton(crypto)
                       for crypto in CRYPTO_CURRENCY.keys()])
            markup.add(*self.get_bottom_row("crypto_wallets",
                       BUTTONS["back_to_crypto_wallets"]))
            self.bot.send_message(
                user_id, MESSAGES["enter_new_crypto_wallet"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_currency, selected_wallet)
        elif message.text == BUTTONS["edit_network_only"]:
            crypto = selected_wallet['crypto']
            networks = CRYPTO_CURRENCY[crypto]
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=2)
            markup.add(*[types.KeyboardButton(network)
                       for network in networks])
            markup.add(*self.get_bottom_row("crypto_wallets",
                       BUTTONS["back_to_crypto_wallets"]))
            self.bot.send_message(
                user_id, MESSAGES["enter_new_network_wallet"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_network, selected_wallet)
        elif message.text == BUTTONS["edit_wallet_address"]:
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=3)
            markup.add(*self.get_bottom_row("crypto_wallets",
                       BUTTONS["back_to_crypto_wallets"]))
            self.bot.send_message(
                user_id, MESSAGES["enter_new_wallet_address"], reply_markup=markup)
            self.bot.register_next_step_handler(
                message, self.process_new_address, selected_wallet)
        else:
            self.bot.send_message(user_id, MESSAGES["invalid_choice"])
            self.handle_crypto_wallets_menu(message)
    def process_new_currency(self, message, selected_wallet):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        new_crypto = message.text
        if new_crypto not in CRYPTO_CURRENCY:
            self.bot.send_message(user_id, MESSAGES["invalid_crypto"])
            self.bot.register_next_step_handler(
                message, self.process_new_currency, selected_wallet)
            return
        self.temp_data[user_id]['new_crypto'] = new_crypto
        networks = CRYPTO_CURRENCY[new_crypto]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*[types.KeyboardButton(network) for network in networks])
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["enter_new_network_wallet"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_new_network_for_currency, selected_wallet)
    def process_new_network_for_currency(self, message, selected_wallet):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data or 'new_crypto' not in self.temp_data[user_id]:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        new_network = message.text
        new_crypto = self.temp_data[user_id]['new_crypto']
        if new_network not in CRYPTO_CURRENCY[new_crypto]:
            self.bot.send_message(user_id, MESSAGES["invalid_network"])
            self.bot.register_next_step_handler(
                message, self.process_new_network_for_currency, selected_wallet)
            return
        self.temp_data[user_id]['new_network'] = new_network
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["enter_new_wallet_address"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_new_address_for_currency, selected_wallet)
    def process_new_address_for_currency(self, message, selected_wallet):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data or 'new_crypto' not in self.temp_data[user_id] or 'new_network' not in self.temp_data[user_id]:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        new_address = message.text.strip()
        new_crypto = self.temp_data[user_id]['new_crypto']
        new_network = self.temp_data[user_id]['new_network']
        if not re.match(r'^(0x)?[A-Za-z0-9]{20,100}$', new_address):
            self.bot.send_message(user_id, MESSAGES["invalid_wallet_address"])
            self.bot.register_next_step_handler(
                message, self.process_new_address_for_currency, selected_wallet)
            return
        if self.db.select_dict('wallets', 'user_id = ? AND crypto = ? AND network = ? AND address = ?', (user_id, new_crypto, new_network, new_address)):
            self.bot.send_message(user_id, MESSAGES["wallet_exists"])
            self.handle_crypto_wallets_menu(message)
            return
        try:
            self.db.update('wallets', {
                'crypto': new_crypto,
                'network': new_network,
                'address': new_address
            }, 'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["wallet_address_updated"])
        except Exception as e:
            log.error(f"خطا در به‌روزرسانی کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_upsocial_service_wallet"])
        self.cleanup_temp_data(user_id)
        self.handle_crypto_wallets_menu(message)
    def process_new_network(self, message, selected_wallet):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        new_network = message.text
        crypto = selected_wallet['crypto']
        if new_network not in CRYPTO_CURRENCY[crypto]:
            self.bot.send_message(user_id, MESSAGES["invalid_network"])
            self.bot.register_next_step_handler(
                message, self.process_new_network, selected_wallet)
            return
        self.temp_data[user_id]['new_network'] = new_network
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["enter_new_wallet_address"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_new_address_for_network, selected_wallet)
    def process_new_address_for_network(self, message, selected_wallet):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        if user_id not in self.temp_data or 'new_network' not in self.temp_data[user_id]:
            self.bot.send_message(user_id, MESSAGES["session_expired"])
            self.handle_crypto_wallets_menu(message)
            return
        new_address = message.text.strip()
        new_network = self.temp_data[user_id]['new_network']
        crypto = selected_wallet['crypto']
        if not re.match(r'^(0x)?[A-Za-z0-9]{20,100}$', new_address):
            self.bot.send_message(user_id, MESSAGES["invalid_wallet_address"])
            self.bot.register_next_step_handler(
                message, self.process_new_address_for_network, selected_wallet)
            return
        if self.db.select_dict('wallets', 'user_id = ? AND crypto = ? AND network = ? AND address = ?', (user_id, crypto, new_network, new_address)):
            self.bot.send_message(user_id, MESSAGES["wallet_exists"])
            self.handle_crypto_wallets_menu(message)
            return
        try:
            self.db.update('wallets', {
                'network': new_network,
                'address': new_address
            }, 'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["wallet_address_updated"])
        except Exception as e:
            log.error(f"خطا در به‌روزرسانی کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_upsocial_service_wallet"])
        self.cleanup_temp_data(user_id)
        self.handle_crypto_wallets_menu(message)
    def process_new_address(self, message, selected_wallet):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True:
            return
        elif result == "HELP":
            return
        user_id = message.chat.id
        new_address = message.text.strip()
        if not re.match(r'^(0x)?[A-Za-z0-9]{20,100}$', new_address):
            self.bot.send_message(user_id, MESSAGES["invalid_wallet_address"])
            self.bot.register_next_step_handler(
                message, self.process_new_address, selected_wallet)
            return
        crypto = selected_wallet['crypto']
        network = selected_wallet['network']
        if self.db.select_dict('wallets', 'user_id = ? AND crypto = ? AND network = ? AND address = ?', (user_id, crypto, network, new_address)):
            self.bot.send_message(user_id, MESSAGES["wallet_exists"])
            self.handle_crypto_wallets_menu(message)
            return
        try:
            self.db.update(
                'wallets', {'address': new_address}, 'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["wallet_address_updated"])
        except Exception as e:
            log.error(f"خطا در به‌روزرسانی آدرس کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_upsocial_service_wallet"])
        self.cleanup_temp_data(user_id)
        self.handle_crypto_wallets_menu(message)
    def select_currency_for_delete_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        """انتخاب ارز کیف‌پول جهت حذف"""
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
            user_id, MESSAGES["select_crypto_wallet_delete"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_currency_for_delete_wallet)
    def process_select_currency_for_delete_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        currency = message.text.split(" - ")[0]
        self.temp_data[user_id] = {'currency': currency}
        self.select_network_for_delete_wallet(message)
