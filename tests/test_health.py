from fastapi.testclient import TestClient

from app.core.config import Settings
from app.web.app import create_app


def test_live_health() -> None:
    settings = Settings.for_testing()
    app = create_app(settings)
    client = TestClient(app)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
