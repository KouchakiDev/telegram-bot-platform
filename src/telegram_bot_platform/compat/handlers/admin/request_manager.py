from __future__ import annotations

from .request_manager_context import *
from .request_manager_part_a import RequestManagerPartAMixin
from .request_manager_part_b import RequestManagerPartBMixin
from .request_manager_part_c import RequestManagerPartCMixin
from .request_manager_part_d import RequestManagerPartDMixin


class RequestManager(RequestManagerPartAMixin, RequestManagerPartBMixin, RequestManagerPartCMixin, RequestManagerPartDMixin):
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager, back_to_main, back_to_pervious, bots=None, T_M=ThreadManager() , parent = None):
        """Legacy-compatible behavior preserved for this callable."""
        self.bot = bot
        self.bots: Dict[str, telebot.TeleBot] = bots
        self.db = db
        self.parent = parent
        self.T_M = T_M
        self.back_to_main = back_to_main
        self.back_to_pervious = back_to_pervious
        self.target_request = {}
        self.settings = REQUEST_SETTINGS  # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_table = {}
        self.temp_data = {}
        self.ifuserwantedit = {}
        self.current_ditails = {}
        self.current_publish_selection = {}      # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.current_request = {}
        self.temp_rejection_reason = {}   # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.temp_updated_dict = {}
        self.temp_review_dict = {}
        # self.target_request = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.pending_rejection_fields = {}
        self.temp_rejections = {}         # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.S_media = MediaSender(self.bot)
        self.notification_manager = NotificationManager(
            self.bots, self.db)
        self.staff_profile = StaffProfileHandler(self.bot, self.db)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.staff_bot = self.bots["staff"]
        self.client_bot = self.bots["client"]
        self.publish_scheduler = AdPublishScheduler(
            bots=self.bots,
            db=self.db,
            notification_manager=self.notification_manager,
            ad_sender=self.send_ad_to_channel,
            ad_publish_interval_min=1,
            T_M=self.T_M
        )
        self.register_handlers()  # Internal implementation note: legacy behavior is preserved during modernization.
        log.info("✅ RequestManager initialized successfully.")

