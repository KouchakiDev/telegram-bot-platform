from __future__ import annotations

from .login_handler_context import *
from .login_handler_core import LoginHandlerCoreMixin
from .login_handler_flows import LoginHandlerFlowsMixin
from .login_handler_data import LoginHandlerDataMixin
from .login_handler_integrations import LoginHandlerIntegrationsMixin


class LoginHandler(LoginHandlerCoreMixin, LoginHandlerFlowsMixin, LoginHandlerDataMixin, LoginHandlerIntegrationsMixin):
    def __init__(self, bot: telebot.TeleBot, data, handlers, parent):
        self.bot = bot
        self.data = data
        self.handlers = handlers
        self.parent = parent  # Reference to StaffBot
        self.db:DatabaseManager = parent.db   # Use the database manager from parent
        self.callBack_handler()
        # List of Persian months, used in multiple places
        self.persian_months = [
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "عضواد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]


