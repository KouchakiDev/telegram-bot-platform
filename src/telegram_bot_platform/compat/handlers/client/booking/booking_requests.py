from __future__ import annotations

from .booking_requests_context import *
from .booking_requests_core import BookingHandlerCoreMixin
from .booking_requests_flows import BookingHandlerFlowsMixin
from .booking_requests_data import BookingHandlerDataMixin
from .booking_requests_integrations import BookingHandlerIntegrationsMixin


class BookingHandler(BookingHandlerCoreMixin, BookingHandlerFlowsMixin, BookingHandlerDataMixin, BookingHandlerIntegrationsMixin):
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, bot : TeleBot, db: DatabaseManager, back_main, back_previous, start):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.db = db
        self.back_main = back_main
        self.back_previous = back_previous
        self.start = start
        self.premiumr = PREMIUMRegistration(bot, db, back_main, back_previous)
        self.profile = PREMIUMProfile(bot, db, back_main, back_previous, start)
        self.settings = REQUEST_SETTINGS
        self.admin_bot = TeleBot(BOT_ADMIN_TOKEN)
        self.staff_bot = TeleBot(BOT_STAFF_TOKEN)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_data = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.identity_verification_manager = None
        self.identity_verification_user = None


