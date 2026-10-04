from __future__ import annotations

from .client_runner_context import *
from .client_runner_lifecycle import ClientRunnerLifecycleMixin
from .client_runner_request_flow import ClientRunnerRequestFlowMixin
from .client_runner_processing import ClientRunnerProcessingMixin
from .client_runner_telegram import ClientRunnerTelegramMixin


class ClientRunner(ClientRunnerLifecycleMixin, ClientRunnerRequestFlowMixin, ClientRunnerProcessingMixin, ClientRunnerTelegramMixin):
    def __init__(self, bot_token: str, flow_config: Dict[str, Dict[str, Any]], db: DatabaseManager) -> None:  # noqa: D401
        self.log = CustomLogger("ClientRunner")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.bot: TeleBot = LocalizedTeleBot(bot_token, parse_mode="HTML")
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.db: DatabaseManager = db
        self.admin_bot = LocalizedTeleBot(BOT_ADMIN_TOKEN)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._contract: Dict[str, Dict[str, Any]] = self._collect_step_handlers()
        self.starter = Starter(self.db, self.bot, welcome_cb=self._pick_random_emoji)
        self._photo_play    = {}   # Internal implementation note: legacy behavior is preserved during modernization.
        self._photo_timers  = {}   # Internal implementation note: legacy behavior is preserved during modernization.
        self.isaskes = {}
        # Internal implementation note: legacy behavior is preserved during modernization.
        self.engine = WorkstationEngine(flow_config=flow_config, target_object=self)
        # Internal implementation note: legacy behavior is preserved during modernization.
        self._register_telegram_handlers()
        self.log.info("ClientRunner initialised – %s steps discovered", len(self._contract))

    """Glue‑code between Telegram *updates* and the WorkstationEngine.*
    Parameters
    ----------
    bot_token : str
        Telegram *bot father* token.
    flow_config : dict
        The *only* place where the workflow is declared.
    db : DatabaseManager
        Data‑layer instance – injected so that handlers can persist data.
    """



# ---------------------------------------------------------------------------
# Example FLOW configuration (can be loaded from JSON/YAML in production)
# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.

CLIENT_RUNNER_FLOW = {
    "choose_dispatch_mode": {
        "label": "نوع خدمات",
        "position": 1,
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": [],
        "dependencies": [],
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "handle_choose_dispatch_mode",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "✨",
            "input_type": "button",
            "description": "دریافت نوع سرویس (ارائه در محل مشتری یا مکان‌دار) از کاربر.",
        },
    },

    "select_staff_code": {
        "label": "کد پرسنل",
        "position": "choose_dispatch_mode",
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": ["choose_dispatch_mode"],
        "dependencies": ["choose_dispatch_mode"],
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "handle_select_staff_code",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "🧚‍♀️",
            "input_type": "button",
            "description": "نمایش فهرست کدهای فعال متناسب با نوع سرویس انتخاب‌شده.",
        },
    },

    "confirm_staff_code": {
        "label": "تأیید کد",
        "position": "select_staff_code",
        "active": True,
        "skippable": False,
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": ["select_staff_code"],
        "dependencies": ["select_staff_code"],
        "on_skip": "fail",
        "on_fail": "restart",
        "handler_fn": "handle_confirm_staff_code",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,   # Internal implementation note: legacy behavior is preserved during modernization.
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "❓",
            "input_type": "button",
            "description": "نمایش بیو کد انتخابی و گرفتن تأیید یا بازگشت به لیست.",
        },
    },

    "enter_address": {
        "label": "آدرس اعزام",
        "position": 4,
        "active": True,
        "skippable": True,          # Internal implementation note: legacy behavior is preserved during modernization.
        "editable": False,
        "timeout": None,
        "retries_allowed": 1,
        "required_fields": ["confirm_staff_code"],
        "dependencies": ["confirm_staff_code"],
        "on_skip": "next",
        "on_fail": "restart",
        "handler_fn": "handle_enter_address",
        "validation_fn": None,
        "display_condition": None,
        "next_step_fn": None,
        "roles_allowed": None,
        "pre_hooks": [],
        "post_hooks": [],
        "meta": {
            "icon": "📍",
            "input_type": "text",
            "description": "دریافت آدرس از کاربر اگر سرویس ارائه در محل مشتری باشد.",
        },
    },
    "select_reserve_time": {
    "label": "ساعت رزرو",
    "position": 5,                       # Internal implementation note: legacy behavior is preserved during modernization.
    "active": True,
    "skippable": False,
    "editable": False,
    "timeout": None,
    "retries_allowed": 1,
    "required_fields": ["confirm_staff_code"],  # Internal implementation note: legacy behavior is preserved during modernization.
    "dependencies": ["confirm_staff_code"],
    "on_skip": "fail",
    "on_fail": "restart",
    "handler_fn": "handle_select_reserve_time",
    "validation_fn": None,
    "display_condition": None,
    "next_step_fn": None,
    "roles_allowed": None,
    "pre_hooks": [],
    "post_hooks": [],
    "meta": {
        "icon": "⏰",
        "input_type": "text",
        "description": "دریافت ساعت دقیق رزرو از کاربر.",
    },
    
},
    # Internal implementation note: legacy behavior is preserved during modernization.
"verification_photo_1": {
    "label": "سلفی اول",
    "position": 6,                       # Internal implementation note: legacy behavior is preserved during modernization.
    "active": True,
    "skippable": False,
    "editable": False,
    "timeout": 180,                     # Internal implementation note: legacy behavior is preserved during modernization.
    "retries_allowed": 1,
    "required_fields": ["confirm_staff_code"],   # Internal implementation note: legacy behavior is preserved during modernization.
    "dependencies": ["confirm_staff_code"],
    "on_skip": "fail",
    "on_fail": "restart",
    "handler_fn": "handle_verification_photo_1",           # Internal implementation note: legacy behavior is preserved during modernization.
    "validation_fn": None,
    "display_condition": None,
    "next_step_fn": None,
    "roles_allowed": None,
    "pre_hooks": [],
    "post_hooks": [],
    "meta": {
        "icon": "📸",
        "input_type": "photo",
        "description": "دریافت سلفی اول با ایموجی تصادفی برای احراز.",
    },
},

# Internal implementation note: legacy behavior is preserved during modernization.
"verification_photo_2": {
    "label": "سلفی دوم",
    "position": "verification_photo_1",                       # Internal implementation note: legacy behavior is preserved during modernization.
    "active": False,
    "skippable": False,
    "editable": False,
    "timeout": 180,
    "retries_allowed": 1,
    "required_fields": ["verification_photo_1"],
    "dependencies": ["verification_photo_1"],
    "on_skip": "fail",
    "on_fail": "restart",
    "handler_fn": "handle_verification_photo_2",           # Internal implementation note: legacy behavior is preserved during modernization.
    "validation_fn": None,
    "display_condition": None,
    "next_step_fn": None,
    "roles_allowed": None,
    "pre_hooks": [],
    "post_hooks": [],
    "meta": {
        "icon": "📸",
        "input_type": "photo",
        "description": "دریافت سلفی دوم با ایموجی متفاوت جهت تأیید هویت.",
    },
},

# Internal implementation note: legacy behavior is preserved during modernization.
"video_note": {
    "label": "ویدیو احراز",
    "position": "verification_photo_1",        # Internal implementation note: legacy behavior is preserved during modernization.
    "active": True,
    "skippable": False,
    "editable": False,
    "timeout": 180,
    "retries_allowed": 1,
    "required_fields": ["verification_photo_1"],
    "dependencies": ["verification_photo_1"],
    "on_skip": "fail",
    "on_fail": "restart",
    "handler_fn": "handle_video_note",   # Internal implementation note: legacy behavior is preserved during modernization.
    "meta": {
        "icon": "📹",
        "input_type": "video_note",
        "description": "ویدیو کوتاه که کاربر جملهٔ رندوم را می‌خواند.",
    },
},

"get_contact": {
    "label": "شماره تماس",
    "position": 8,                       # Internal implementation note: legacy behavior is preserved during modernization.
    "active": True,
    "skippable": False,
    "editable": False,
    "timeout": None,                     # Internal implementation note: legacy behavior is preserved during modernization.
    "retries_allowed": 1,
    "required_fields": ["video_note"],     # Internal implementation note: legacy behavior is preserved during modernization.
    "dependencies":  ["video_note"],
    "on_skip": "fail",
    "on_fail": "restart",
    "handler_fn": "request_contact_generic",   # Internal implementation note: legacy behavior is preserved during modernization.
    "validation_fn": None,
    "display_condition": None,
    "next_step_fn": None,                # Internal implementation note: legacy behavior is preserved during modernization.
    "roles_allowed": None,
    "pre_hooks": [],
    "post_hooks": [],
    "meta": {
        "icon": "📞",
        "input_type": "contact",
        "description": "دریافت شمارهٔ تماس (user’s contact) با دکمهٔ ارسال شماره.",
    },
},
# Internal implementation note: legacy behavior is preserved during modernization.
"collect_note": {
    "label": "توضیح اضافی",
    "position": 9,                         # Internal implementation note: legacy behavior is preserved during modernization.
    "active": True,
    "skippable": True,                     # Internal implementation note: legacy behavior is preserved during modernization.
    "editable": False,
    "timeout": None,
    "retries_allowed": 1,
    "required_fields": ["get_contact"],    # Internal implementation note: legacy behavior is preserved during modernization.
    "dependencies": ["get_contact"],
    "on_skip": "next",                     # Internal implementation note: legacy behavior is preserved during modernization.
    "on_fail": "restart",
    "handler_fn": "handle_collect_note",   # Internal implementation note: legacy behavior is preserved during modernization.
    "validation_fn": None,                 # Internal implementation note: legacy behavior is preserved during modernization.
    "display_condition": None,
    "next_step_fn": None,                  # Internal implementation note: legacy behavior is preserved during modernization.
    "roles_allowed": None,
    "pre_hooks": [],
    "post_hooks": [],
    "meta": {
        "icon": "📝",
        "input_type": "text",
        "description": "گرفتن توضیح یا نکتهٔ اختیاری از کاربر (سؤال ۸).",
    },
},
# Internal implementation note: legacy behavior is preserved during modernization.
"finish_booking": {
    "label": "ثبت نهایی",
    "position": "end",                    # Internal implementation note: legacy behavior is preserved during modernization.
    "active": True,
    "skippable": False,
    "editable": False,
    "timeout": None,
    "retries_allowed": 0,
    "required_fields": ["get_contact"],   # Internal implementation note: legacy behavior is preserved during modernization.
    "dependencies": ["get_contact"],
    "on_skip": "fail",
    "on_fail": "restart",
    "handler_fn": "handle_finish_booking",
    "validation_fn": None,
    "display_condition": None,
    "next_step_fn": None,                # Internal implementation note: legacy behavior is preserved during modernization.
    "roles_allowed": None,
    "pre_hooks": [],
    "post_hooks": [],
    "meta": {
        "icon": "💾",
        "input_type": "system",
        "description": "ثبت همهٔ اطلاعات در DB و پیام پایان + گزینهٔ کنسل.",
    },
},


}


# ---------------------------------------------------------------------------
# Internal implementation note: legacy behavior is preserved during modernization.
# ---------------------------------------------------------------------------

def start_client_bot(bot_token: str, db: DatabaseManager, flow: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
    flow = flow or CLIENT_RUNNER_FLOW
    runner = ClientRunner(bot_token=bot_token, flow_config=flow, db=db)
    runner.run()


if __name__ == "__main__":  # pragma: no cover
    # Internal implementation note: legacy behavior is preserved during modernization.
    from telegram_bot_platform.compat.config.settings import BOT_CLIENT_TOKEN, DB_PARAMS

    db_instance = DatabaseManager(**DB_PARAMS)
    start_client_bot(BOT_CLIENT_TOKEN, db_instance)
