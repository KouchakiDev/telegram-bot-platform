from __future__ import annotations

from .accounting_handler_context import *


class AccountingHandlerIntegrationsMixin:
    def select_network_for_delete_wallet(self, message):
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
            user_id, MESSAGES["select_network_wallet_delete"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_network_for_delete_wallet)
    def process_select_network_for_delete_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        network = message.text.split(" - ")[0]
        self.temp_data[user_id]['network'] = network
        self.select_wallet_address_for_delete_wallet(message)
    def select_wallet_address_for_delete_wallet(self, message):
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
            user_id, MESSAGES["select_wallet_delete"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_wallet_address_for_delete_wallet)
    def process_select_wallet_address_for_delete_wallet(self, message):
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
            self.select_wallet_address_for_delete_wallet(message)
            return
        try:
            self.db.delete('wallets', 'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["wallet_deleted"])
        except Exception as e:
            log.error(f"خطا در حذف کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_deleting_wallet"])
        self.cleanup_temp_data(user_id)
        self.handle_crypto_wallets_menu(message)
    def handle_delete_wallet(self, message):
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
            user_id, MESSAGES["select_wallet_to_delete"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_delete_wallet)
    def process_delete_wallet(self, message):
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
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_delete_wallet)
            return
        try:
            self.db.delete('wallets', 'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["wallet_deleted"])
        except Exception as e:
            log.error(f"خطا در حذف کیف‌پول: {e}")
            self.bot.send_message(user_id, MESSAGES["error_deleting_wallet"])
        self.handle_crypto_wallets_menu(message)
    def handle_select_default_wallet(self, message):
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for wallet in wallets:
            label = f"{wallet['crypto']} ({wallet['network']}) - {wallet['address'][-6:]}" + (
                "☑" if int(wallet['is_default']) else "")
            markup.add(types.KeyboardButton(label))
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            user_id, MESSAGES["select_default_wallet"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_default_wallet)
    def process_select_default_wallet(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        wallets = self.db.select_dict('wallets', 'user_id = ?', (user_id,))
        selected_wallet = next(
            (w for w in wallets if message.text.startswith(f"{w['crypto']} ({w['network']}) - {w['address'][-6:]}")), None)
        if not selected_wallet:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            self.handle_select_default_wallet(message)
            return
        try:
            self.db.update('wallets', {'is_default': 0},
                           'user_id = ?', (user_id,))
            self.db.update('wallets', {'is_default': 1},
                           'id = ?', (selected_wallet['id'],))
            self.bot.send_message(user_id, MESSAGES["default_wallet_selected"])
        except Exception as e:
            log.error(f"خطا در انتخاب کیف‌پول پیش‌فرض: {e}")
            self.bot.send_message(user_id, MESSAGES["error_selecting_default"])
        self.handle_crypto_wallets_menu(message)
    def select_currency(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        results = self.db.select_dict(
            table='wallets', condition='user_id = ?', params=(user_id,))
        row_wi = 1
        buttons = []
        if results:
            currencies = list({row['crypto'] for row in results})
            for row in currencies:
                # 'COUNT(*) as count',
                currency = row
                if 6 < len(currencies) < 3:
                    row_wi = 3
                elif len(currencies) < 6:
                    row_wi = 4
                count = self.db.count_rows(
                    "wallets", "user_id = ? AND crypto = ?", (user_id, currency,))
                label = f"{currency} - ({count} wallets)"
                buttons.append(types.KeyboardButton(label))
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=row_wi)
        markup.add(*buttons)
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            message.chat.id, MESSAGES["select_curnecy"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_currency)
    def process_select_currency(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        text = message.text.split(" - ")
        print(text)
        currency = text[0]
        print(currency)
        if currency not in CRYPTO_CURRENCY:
            self.bot.send_message(user_id, MESSAGES["invalid_crypto"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.process_select_currency)
            return
        self.temp_data[user_id] = {'currency': currency}
        self.select_network(message)
    def select_network(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        # Internal implementation note: legacy behavior is preserved during modernization.
        selected_currency = self.temp_data[user_id]['currency']
        # Internal implementation note: legacy behavior is preserved during modernization.
        results = self.db.select_dict(
            'wallets',  'user_id = ? AND crypto = ?', (user_id, selected_currency))
        networks = list({row['network'] for row in results})
        buttons = []
        row_wi = 1
        if networks:
            for network in networks:
                if 6 < len(networks) < 3:
                    row_wi = 3
                elif len(networks) < 6:
                    row_wi = 4
                count = self.db.count_rows(
                    "wallets", "user_id = ? AND crypto = ? AND network = ?", (user_id, selected_currency, network,))
                label = f"{network} - ({count} wallets)"
                buttons.append(types.KeyboardButton(label))
        if not buttons:
            self.bot.send_message(
                user_id, f"{MESSAGES["not_found_network"].format(coin={selected_currency})} .")
            self.handle_crypto_wallets_menu(message)
            return
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=row_wi)
        markup.add(*buttons)
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            message.chat.id, f"{MESSAGES["P_select_network"]}:", reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_network_C)
    def process_select_network_C(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        network = message.text.split(" - ")[0]
        currency = self.temp_data[user_id]['currency']
        if network not in CRYPTO_CURRENCY[currency]:
            self.bot.send_message(user_id, MESSAGES["invalid_network"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.select_network)
            return
        self.temp_data[user_id]['network'] = network
        self.select_wallet_address(message)
    def select_wallet_address(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        selected_currency = self.temp_data[user_id]['currency']
        selected_network = self.temp_data[user_id]['network']
        wallets = self.db.select_dict(
            'wallets', 'user_id = ? AND crypto = ? AND network = ?', (user_id, selected_currency, selected_network))
        if not wallets:
            self.bot.send_message(
                user_id, f"{MESSAGES["not_found_address"].format(coin=selected_currency, net=selected_network)} ")
            self.handle_crypto_wallets_menu(message)
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for wallet in wallets:
            # Internal implementation note: legacy behavior is preserved during modernization.
            label = wallet['address']
            address = f"{label[:6]}...{label[-6:]}" + \
                ("☑" if int(wallet['is_default']) else "")
            markup.add(types.KeyboardButton(address))
        markup.add(*self.get_bottom_row("crypto_wallets",
                   BUTTONS["back_to_crypto_wallets"]))
        self.bot.send_message(
            message.chat.id, MESSAGES["P_select_Address"], reply_markup=markup)
        self.bot.register_next_step_handler(
            message, self.process_select_wallet_address)
    def process_select_wallet_address(self, message):
        result = self.handle_back_buttons(message, "crypto_wallets")
        if result is True or result == "HELP":
            return
        user_id = message.chat.id
        selected_label = message.text.strip()
        selected_currency = self.temp_data[user_id]['currency']
        selected_network = self.temp_data[user_id]['network']
        wallets = self.db.select_dict(
            "wallets", "user_id = ? AND crypto = ? AND network = ?", (user_id, selected_currency, selected_network,))
        label = label = selected_label.replace("☑", "").strip()
        print(label)
        selected_wallet = next(
            (wallet for wallet in wallets if label ==
             f"{wallet['address'][:6]}...{wallet['address'][-6:]}"),
            None
        )
        if not selected_wallet:
            self.bot.send_message(user_id, MESSAGES["invalid_selection"])
            self.bot.register_next_step_handler_by_chat_id(
                user_id, self.select_wallet_address)
            return
        self.db.update(
            'wallets',
            {"is_default": 0},
            'user_id = ? AND crypto = ? AND network = ?',
            (user_id, selected_currency, selected_network)
        )
        self.db.update('wallets', {'is_default': 1},
                       'id = ?', (selected_wallet['id'],))
        self.bot.send_message(
            user_id,  MESSAGES["You_selected_this_w"].format(coin=selected_currency, net=selected_network, address=selected_wallet["address"]))
        self.handle_crypto_wallets_menu(message)
    def route_accounting(self, message):
        text = message.text.strip()
        if text == BUTTONS["bank_accounts"]:
            self.handle_bank_accounts_menu(message)
        elif text == BUTTONS["crypto_wallets"]:
            self.handle_crypto_wallets_menu(message)
        elif text == BUTTONS["add_card"]:
            self.handle_add_card(message)
        elif text == BUTTONS["edit_card"]:
            self.handle_edit_card(message)
        elif text == BUTTONS["delete_card"]:
            self.handle_delete_card(message)
        elif text == BUTTONS["select_default_card"]:
            self.handle_select_default_card(message)
        elif text == BUTTONS["add_wallet"]:
            self.handle_add_wallet(message)
        elif text == BUTTONS["edit_wallet"]:
            self.select_currency_for_edit_wallet(message)
        elif text == BUTTONS["delete_wallet"]:
            self.select_currency_for_delete_wallet(message)
        elif text == BUTTONS["select_default_wallet"]:
            self.handle_select_default_wallet(message)
        elif text == BUTTONS["select_wallet"]:
            self.select_currency(message)
        elif text in [
            BUTTONS["back_to_accounting"],
            BUTTONS["back_to_bank_accounts"],
            BUTTONS["back_to_crypto_wallets"],
            BUTTONS["back_to_previous"],
            BUTTONS["back_to_main"],
        ]:
            self.handle_back_buttons(message, "accounting")
        else:
            text = message.text.strip()
            if text in BUTTONS.values():
                key = next((k for k, v in BUTTONS.items()
                            if k.startswith("help_") and v == text), None)
            if key:  # Internal implementation note: legacy behavior is preserved during modernization.
                contaxt = key.replace("help_", "", 1)
                res = self.handle_back_buttons(message, contaxt)
            if res == "HELP":
                self.bot.register_next_step_handler(
                    message, self.route_accounting)
            else:
                self.bot.send_message(
                    message.chat.id, MESSAGES["invalid_choice"])
                self.back_to_settings(message)
    def setup_handlers(self):
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["bank_accounts"])
        def handle_bank_accounts(message):
            self.handle_bank_accounts_menu(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["crypto_wallets"])
        def handle_crypto_wallets(message):
            self.handle_crypto_wallets_menu(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["back_to_accounting"])
        def back_to_accounting(message):
            self.cleanup_temp_data(message.chat.id)
            self.handle_accounting_menu(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["back_to_main"])
        def back_main(message):
            self.cleanup_temp_data(message.chat.id)
            self.active_sessions.discard(message.chat.id)
            self.send_welcome(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["back_to_previous"])
        def back_settings(message):
            self.cleanup_temp_data(message.chat.id)
            self.active_sessions.discard(message.chat.id)
            self.back_to_settings(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["help_accounting"])
        def help_accounting(message):
            self.bot.send_message(message.chat.id, MESSAGES["help_accounting"])
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["help_bank_accounts"])
        def help_bank_accounts(message):
            self.bot.send_message(
                message.chat.id, MESSAGES["help_bank_accounts"])
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["help_crypto_wallets"])
        def help_crypto_wallets(message):
            self.bot.send_message(
                message.chat.id, MESSAGES["help_crypto_wallets"])
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["add_card"])
        def add_card(message):
            self.handle_add_card(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["edit_card"])
        def edit_card(message):
            self.handle_edit_card(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["delete_card"])
        def delete_card(message):
            self.handle_delete_card(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["select_default_card"])
        def select_default_card(message):
            self.handle_select_default_card(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["add_wallet"])
        def add_wallet(message):
            self.handle_add_wallet(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["edit_wallet"])
        def edit_wallet(message):
            self.select_currency_for_edit_wallet(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["delete_wallet"])
        def delete_wallet(message):
            self.select_currency_for_delete_wallet(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["select_default_wallet"])
        def select_default_wallet(message):
            self.handle_select_default_wallet(message)
        @self.bot.message_handler(func=lambda m: m.chat.id in self.active_sessions and m.text == BUTTONS["select_wallet"])
        def select_wallet(message):
            self.select_currency(message)
