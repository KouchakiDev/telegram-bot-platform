from fastapi.testclient import TestClient

from telegram_bot_platform.core.config import Settings
from telegram_bot_platform.web.app import create_app


def test_live_health() -> None:
    settings = Settings.for_testing()
    app = create_app(settings)
    client = TestClient(app)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
