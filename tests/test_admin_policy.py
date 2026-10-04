import pytest

from telegram_bot_platform.application.services.admin_service import AdminService
from telegram_bot_platform.core.exceptions import AuthorizationError


class FakeResult:
    def scalar_one_or_none(self):
        return None


class FakeSession:
    async def execute(self, *args, **kwargs):
        return FakeResult()


@pytest.mark.asyncio
async def test_configured_admin_is_accepted_without_database_lookup() -> None:
    await AdminService(FakeSession(), (123,)).ensure_admin(123)


@pytest.mark.asyncio
async def test_unknown_admin_is_rejected() -> None:
    with pytest.raises(AuthorizationError, match="Administrator access required"):
        await AdminService(FakeSession(), (123,)).ensure_admin(999)
