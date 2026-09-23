from fastapi.testclient import TestClient

from backend.career_quest.api import app


def test_health_only_confirms_backend_process() -> None:
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "career-quest-backend",
    }
    assert "/api/health" in {route.path for route in app.routes}


def test_ready_does_not_claim_database_without_configuration(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATASET_PATH", raising=False)
    response = TestClient(app).get("/api/ready")

    assert response.status_code == 503
    assert response.json()["code"] == "database_unavailable"
    assert "://" not in response.text
