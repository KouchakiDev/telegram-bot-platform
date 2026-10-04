from __future__ import annotations

from .accounting_handler_context import *
from .accounting_handler_core import AccountingHandlerCoreMixin
from .accounting_handler_flows import AccountingHandlerFlowsMixin
from .accounting_handler_data import AccountingHandlerDataMixin
from .accounting_handler_integrations import AccountingHandlerIntegrationsMixin


class AccountingHandler(AccountingHandlerCoreMixin, AccountingHandlerFlowsMixin, AccountingHandlerDataMixin, AccountingHandlerIntegrationsMixin):
    def __init__(self, bot:TeleBot, db: DatabaseManager, send_welcome, back_to_settings):
        self.bot = bot
        self.db = db
        self.send_welcome = send_welcome
        self.back_to_settings = back_to_settings
        self.temp_data = {}
        self.active_sessions = set()
        self.back_targets = {
            BUTTONS["back_to_accounting"]: "accounting",
            BUTTONS["back_to_bank_accounts"]: "bank_accounts",
            BUTTONS["back_to_crypto_wallets"]: "crypto_wallets",
        }
        self.parent_menu = {
            # Internal implementation note: legacy behavior is preserved during modernization.
            "accounting": "accounting",
            "bank_accounts": "bank_accounts",   # Internal implementation note: legacy behavior is preserved during modernization.
            # Internal implementation note: legacy behavior is preserved during modernization.
            "crypto_wallets": "crypto_wallets"
        }
        self.setup_handlers()


##################
##################
##################
