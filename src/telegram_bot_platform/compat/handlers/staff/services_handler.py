from __future__ import annotations

from .services_handler_context import *
from .services_handler_core import ServicesHandlerCoreMixin
from .services_handler_flows import ServicesHandlerFlowsMixin
from .services_handler_data import ServicesHandlerDataMixin
from .services_handler_integrations import ServicesHandlerIntegrationsMixin


class ServicesHandler(ServicesHandlerCoreMixin, ServicesHandlerFlowsMixin, ServicesHandlerDataMixin, ServicesHandlerIntegrationsMixin):
    def __init__(self, bot: telebot.TeleBot, data, parent, db: DatabaseManager = DatabaseManager(**DB_PARAMS)):
        self.bot = bot
        self.data = data
        self.parent = parent
        self.db = db
        self.ucode = "p0000"
        self.service_key_map = {
            "گزینه خدمات ۱": "back",
            "گروه خدمات": "group_option_b",
            "گزینه خدمات A": "group_option_a",
            "گزینه خدمات ۲": "service_option_2",
            "گزینه خدمات ۳": "service_option_3",
            "گزینه خدمات ۴": "service_option_4",
            "محصول سفارشی": "custom_outfit",
            "خدمات تعاملی": "social_service",
            "خدمت ویژه": "massage",
            "گزینهٔ سفارشی ویژه": "special_service"
        }
        self.dev_mode_premium_access = False 


