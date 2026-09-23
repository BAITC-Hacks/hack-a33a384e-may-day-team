from fastapi.testclient import TestClient

from backend.career_quest.api import app


def test_health_only_confirms_backend_process() -> None:
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "career-quest-backend",
    }
    assert {route.path for route in app.routes} == {"/api/health"}
