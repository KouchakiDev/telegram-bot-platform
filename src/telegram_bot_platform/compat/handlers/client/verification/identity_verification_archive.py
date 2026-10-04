# identity_verification.py

"""Legacy-compatible behavior preserved for this callable."""

# from datetime import datetime
from telegram_bot_platform.compat.config.settings import *
from telegram_bot_platform.compat.database.database_manager import DatabaseManager
# Internal implementation note: legacy behavior is preserved during modernization.

import json


class AuthStep:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, name, prompt, required=DEFAULT_REQUIRED, step_type='text'):
        self.name = name
        self.prompt = prompt
        self.required = required
        self.enabled = True  # Internal implementation note: legacy behavior is preserved during modernization.
        self.step_type = step_type
        self.response = None

    def run(self):
        """Legacy-compatible behavior preserved for this callable."""
        if not self.enabled:
            print(f"[{self.name}] {AUTH_MESSAGES['skipped']}")
            return None

        # Internal implementation note: legacy behavior is preserved during modernization.
        print(f"[{self.name}] {self.prompt}")
        self.response = input("پاسخ شما: ")
        return self.response

    def validate(self):
        """Legacy-compatible behavior preserved for this callable."""
        if not self.enabled:
            return True
        if self.required and not self.response:
            print(f"*** {AUTH_MESSAGES['required_error']} ***")
            return False
        return True

# Internal implementation note: legacy behavior is preserved during modernization.


class TextAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["text"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="text")


class PhotoAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["photo"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="photo")


class VoiceAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["voice"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="voice")


class VideoAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["video"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="video")


class DocumentAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["document"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="document")


class ContactAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["contact"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="contact")


class LocationAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["location"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="location")


class OTPAuthStep(AuthStep):
    def __init__(self, name, prompt=AUTH_PROMPTS["otp"], required=DEFAULT_REQUIRED):
        super().__init__(name, prompt, required, step_type="otp")

# Internal implementation note: legacy behavior is preserved during modernization.


class AuthenticationManager:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self):
        self.steps = []  # Internal implementation note: legacy behavior is preserved during modernization.

    def on_complete(self, callback):
        """Legacy-compatible behavior preserved for this callable."""
        self._on_complete_callback = callback

    def add_step(self, step: AuthStep):
        """Legacy-compatible behavior preserved for this callable."""
        self.steps.append(step)

    def remove_step(self, name: str):
        """Legacy-compatible behavior preserved for this callable."""
        self.steps = [step for step in self.steps if step.name != name]

    def move_step(self, name: str, new_index: int):
        """Legacy-compatible behavior preserved for this callable."""
        for i, step in enumerate(self.steps):
            if step.name == name:
                step_obj = self.steps.pop(i)
                self.steps.insert(new_index, step_obj)
                break

    def toggle_step(self, name: str, enabled: bool):
        """Legacy-compatible behavior preserved for this callable."""
        for step in self.steps:
            if step.name == name:
                step.enabled = enabled
                break

    def run_authentication(self):
        """Legacy-compatible behavior preserved for this callable."""
        print("========== شروع فرآیند احراز هویت ==========")
        for step in self.steps:
            if step.enabled:
                print(f"\n-- اجرای مرحله: {step.name} ({step.step_type}) --")
                step.run()
                if not step.validate():
                    print(
                        f"*** خطا در مرحله '{step.name}': اطلاعات اجباری وارد نشد. ***")
        print("\n========== پایان فرآیند احراز هویت ==========")
        return {step.name: step.response for step in self.steps if step.enabled}


# Internal implementation note: legacy behavior is preserved during modernization.
if __name__ == "__main__":
    # Internal implementation note: legacy behavior is preserved during modernization.
    auth_manager = AuthenticationManager()

    # Internal implementation note: legacy behavior is preserved during modernization.
    auth_manager.add_step(TextAuthStep(
        "step1", prompt="لطفاً نام کاربری خود را وارد کنید:", required=True))
    auth_manager.add_step(PhotoAuthStep(
        "step2", prompt="لطفاً تصویر مدرک شناسایی را ارسال کنید:", required=True))
    auth_manager.add_step(VoiceAuthStep(
        "step3", prompt="لطفاً یک پیام صوتی ارسال کنید:", required=False))
    auth_manager.add_step(VideoAuthStep(
        "step4", prompt="لطفاً یک ویدئو از خودتان ارسال کنید:", required=False))
    auth_manager.add_step(DocumentAuthStep(
        "step5", prompt="لطفاً یک فایل اسکن شده از مدارک خود ارسال کنید:", required=True))
    auth_manager.add_step(ContactAuthStep(
        "step6", prompt="لطفاً شماره تماس خود را ارسال کنید:", required=True))
    auth_manager.add_step(LocationAuthStep(
        "step7", prompt="لطفاً موقعیت مکانی خود را ارسال کنید:", required=False))
    auth_manager.add_step(OTPAuthStep(
        "step8", prompt="لطفاً کد تایید دریافتی را وارد کنید:", required=True))

    # Internal implementation note: legacy behavior is preserved during modernization.
    # Internal implementation note: legacy behavior is preserved during modernization.
    auth_manager.move_step("step8", 0)

    # Internal implementation note: legacy behavior is preserved during modernization.
    auth_manager.toggle_step("step4", False)

    # Internal implementation note: legacy behavior is preserved during modernization.
    results = auth_manager.run_authentication()

    # Internal implementation note: legacy behavior is preserved during modernization.
    print("\nنتایج احراز هویت:")
    for step_name, response in results.items():
        print(f"{step_name}: {response}")


class IDENTITY_VERIFICATIONService:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_status(self, telegram_id: int) -> tuple[str, list[str]]:
        """Legacy-compatible behavior preserved for this callable."""
        premium_rows = self.db.select_dict(
            "premium_clients",
            "telegram_id = ? AND C_status = 'approved'",
            (telegram_id,)
        )
        if not premium_rows:
            return 'not_premium', []

        if not self.db.table_exists("identity_verification_requests"):
            return 'premium_no_identity_verification', []

        identity_verification_rows = self.db.select_dict(
            "identity_verification_requests",
            "telegram_id = ?",
            (telegram_id,)
        )
        if not identity_verification_rows:
            return 'premium_no_identity_verification', []

        docs = json.loads(identity_verification_rows[0].get("identity_verification_docs", "{}") or "{}")
        completed = []

        for f, info in docs.items():
            # Internal implementation note: legacy behavior is preserved during modernization.
            if isinstance(info, dict):
                if info.get("approved"):
                    completed.append(f)
            elif isinstance(info, bool):
                if info:
                    completed.append(f)

        required = identity_verification_fields
        missing = [f for f in required if f not in completed]

        if missing:
            return 'identity_verification_incomplete', completed

        return 'identity_verification_complete', completed

    def get_missing_fields(self, telegram_id: int) -> list:
        """Legacy-compatible behavior preserved for this callable."""
        status, completed = self.get_status(telegram_id)
        required = ['photo_id', 'video_message']
        return [f for f in required if f not in completed]

    def get_identity_verification_data(self, telegram_id: int) -> dict:
        """Legacy-compatible behavior preserved for this callable."""
        if not self.db.table_exists("identity_verification_requests"):
            return {}
        rows = self.db.select_dict(
            "identity_verification_requests",
            "telegram_id = ?",
            (telegram_id,)
        )
        if not rows:
            return {}
        return json.loads(rows[0].get("identity_verification_docs", "{}") or "{}")

    def save_identity_verification_data(self, telegram_id: int, identity_verification_docs: dict):
        """Legacy-compatible behavior preserved for this callable."""
        data_json = json.dumps(identity_verification_docs)
        if self.db.select_dict("identity_verification_requests", "telegram_id = ?", (telegram_id,)):
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.update(
                "identity_verification_requests",
                {"identity_verification_docs": data_json},
                "telegram_id = ?",
                (telegram_id,)
            )
        else:
            # Internal implementation note: legacy behavior is preserved during modernization.
            self.db.insert(
                "identity_verification_requests",
                {"telegram_id": telegram_id, "identity_verification_docs": data_json}
            )
