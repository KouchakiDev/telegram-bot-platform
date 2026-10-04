from __future__ import annotations

from .requests_handler_context import *
from .requests_handler_core import RequestsHandlerCoreMixin
from .requests_handler_flows import RequestsHandlerFlowsMixin
from .requests_handler_data import RequestsHandlerDataMixin
from .requests_handler_integrations import RequestsHandlerIntegrationsMixin


class RequestsHandler(RequestsHandlerCoreMixin, RequestsHandlerFlowsMixin, RequestsHandlerDataMixin, RequestsHandlerIntegrationsMixin):
    def __init__(self, bot, data, parent):
        self.bot = bot
        self.data = data
        self.parent = parent
        self.db = parent.db
        self.bots = parent.bots


