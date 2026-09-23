from __future__ import annotations

import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine.url import make_url

from backend.career_quest.api import app
from backend.career_quest.errors import WorkflowError
from backend.career_quest.loader import load_dataset
from backend.career_quest.settings import assert_safe_database, load_settings
from backend.career_quest.store import PostgresStore, _catalog
from backend.career_quest.workflow import employee_to_payload

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="PostgreSQL integration NOT RUN: DATABASE_URL is not configured",
)


@pytest.fixture(scope="session", autouse=True)
def _migrate_test_database() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or make_url(database_url).database != "career_quest_test":
        return
    from alembic import command
    from alembic.config import Config

    command.upgrade(Config("alembic.ini"), "head")

DEMO_ENV = {
    "DEMO_EMPLOYEE_ONE_USERNAME": "employee.one",
    "DEMO_EMPLOYEE_ONE_PASSWORD": "employee-one-test",
    "DEMO_EMPLOYEE_ONE_ID": "EMP-new-alpha",
    "DEMO_EMPLOYEE_TWO_USERNAME": "employee.two",
    "DEMO_EMPLOYEE_TWO_PASSWORD": "employee-two-test",
    "DEMO_EMPLOYEE_TWO_ID": "LEAD-custom",
    "DEMO_HR_USERNAME": "hr.user",
    "DEMO_HR_PASSWORD": "hr-user-test",
}


def _require_test_database() -> str:
    database_url = os.environ.get("DATABASE_URL", "")
    name = make_url(database_url).database if database_url else None
    if name != "career_quest_test":
        pytest.fail(
            "Refusing PostgreSQL cleanup unless DATABASE_URL names career_quest_test."
        )
    assert_safe_database(database_url)
    return database_url


def _reset(store: PostgresStore) -> None:
    _require_test_database()
    engine = store.session_factory.kw["bind"]
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE sessions, idempotency_keys, activity_history, "
                "accounts, employees, dataset_state RESTART IDENTITY CASCADE"
            )
        )
    engine.dispose()
    _catalog.cache_clear()


@pytest.fixture
def ready_store(synthetic_dataset_path: Path, monkeypatch: pytest.MonkeyPatch):
    _require_test_database()
    monkeypatch.setenv("DATASET_PATH", str(synthetic_dataset_path))
    for name, value in DEMO_ENV.items():
        monkeypatch.setenv(name, value)
    _catalog.cache_clear()
    store = PostgresStore(load_settings())
    _reset(store)
    store = PostgresStore(load_settings())
    store.seed()
    yield store
    _reset(store)


def _skill(store: PostgresStore, skill_id: str) -> int:
    profile = store.profile("EMP-new-alpha")
    return next(
        item["current_level"]
        for item in profile["skills"]
        if item["skill_id"] == skill_id
    )


def test_postgres_login_logout_and_authorization(ready_store: PostgresStore) -> None:
    employee_client = TestClient(app)
    hr_client = TestClient(app)
    employee = employee_client.post(
        "/api/auth/login",
        json={"username": "employee.one", "password": "employee-one-test"},
    )
    hr = hr_client.post(
        "/api/auth/login",
        json={"username": "hr.user", "password": "hr-user-test"},
    )
    assert employee.status_code == 200
    assert hr.status_code == 200
    assert employee.json()["role"] == "employee"
    assert hr.json()["role"] == "hr"
    csrf = employee.json()["csrf_token"]
    assert employee_client.get("/api/employees/LEAD-custom").status_code == 404
    assert employee_client.get("/api/hr/overview").status_code == 403
    logout = employee_client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf},
    )
    assert logout.status_code == 200
    assert employee_client.get("/api/auth/me").status_code == 401
    assert "password" not in employee.text


def test_postgres_completion_is_durable_and_idempotent(
    ready_store: PostgresStore,
) -> None:
    before = _skill(ready_store, "S_ARCH")
    first = ready_store.complete("EMP-new-alpha", "EV_USEFUL", "once", None)
    assert first["skill_changes"][0]["delta"] == 1
    reloaded = PostgresStore(load_settings())
    assert _skill(reloaded, "S_ARCH") == before + 1
    replay = reloaded.complete("EMP-new-alpha", "EV_USEFUL", "once", None)
    assert replay["idempotent_replay"] is True
    assert replay["skill_changes"] == []
    with pytest.raises(WorkflowError) as caught:
        reloaded.complete("EMP-new-alpha", "EV_USEFUL", "another", None)
    assert caught.value.status_code == 409
    assert _skill(PostgresStore(load_settings()), "S_ARCH") == before + 1


def test_postgres_parallel_completion_applies_once(ready_store: PostgresStore) -> None:
    before = _skill(ready_store, "S_ARCH")
    settings = load_settings()

    def attempt(key: str):
        try:
            return PostgresStore(settings).complete(
                "EMP-new-alpha", "EV_USEFUL", key, None
            )
        except WorkflowError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ("left", "right")))
    successes = [item for item in results if isinstance(item, dict)]
    failures = [item for item in results if isinstance(item, WorkflowError)]
    assert len(successes) == 1
    assert successes[0]["skill_changes"][0]["delta"] == 1
    assert len(failures) == 1
    assert failures[0].status_code == 409
    assert _skill(PostgresStore(load_settings()), "S_ARCH") == before + 1


def test_postgres_repeatable_session_is_distinct_from_retry(
    synthetic_dataset_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scheduled = tmp_path / "scheduled"
    shutil.copytree(synthetic_dataset_path, scheduled)
    events_path = scheduled / "events.json"
    document = json.loads(events_path.read_text(encoding="utf-8"))
    for event in document["events"]:
        if event["event_id"] == "EV_036":
            event["format"] = "offline"
            event["upcoming_sessions"] = ["2026-01-20"]
    events_path.write_text(json.dumps(document), encoding="utf-8")
    _require_test_database()
    monkeypatch.setenv("DATASET_PATH", str(scheduled))
    for name, value in DEMO_ENV.items():
        monkeypatch.setenv(name, value)
    _catalog.cache_clear()
    store = PostgresStore(load_settings())
    _reset(store)
    store = PostgresStore(load_settings())
    store.seed()
    session_date = __import__("datetime").date(2026, 1, 20)
    try:
        before = _skill(store, "S_ARCH")
        first = store.complete("EMP-new-alpha", "EV_036", "session-key", session_date)
        assert first["idempotent_replay"] is False
        replay = PostgresStore(load_settings()).complete(
            "EMP-new-alpha", "EV_036", "session-key", session_date
        )
        assert replay["idempotent_replay"] is True
        with pytest.raises(WorkflowError) as caught:
            PostgresStore(load_settings()).complete(
                "EMP-new-alpha", "EV_036", "other-key", session_date
            )
        assert caught.value.code == "session_already_completed"
        assert _skill(PostgresStore(load_settings()), "S_ARCH") == before + 1
    finally:
        _reset(PostgresStore(load_settings()))


def test_postgres_import_is_atomic(ready_store: PostgresStore) -> None:
    stored = ready_store.profile("EMP-new-alpha")
    existing = employee_to_payload(
        load_dataset(Path(os.environ["DATASET_PATH"])).employees["EMP-new-alpha"]
    )
    existing["full_name"] = "Changed Synthetic Person"
    changed = json.dumps(
        {
            "employees": [
                existing,
                {
                    "employee_id": "EMP-PG-NEW",
                    "full_name": "Imported Synthetic Person",
                    "department": "Test Engineering",
                    "role": "Engineer",
                    "grade": "Junior",
                    "manager_id": "LEAD-custom",
                    "hire_date": "2025-02-01",
                    "tenure_months": 11,
                    "work_format": "hybrid",
                    "preferred_language": "ru",
                    "career_goal": None,
                    "skills": {"S_CODE": 1},
                    "last_review_date": "2026-01-10",
                },
            ]
        }
    ).encode()
    history = (
        "record_id,employee_id,event_id,date,due_date,status,"
        "completion_pct,score,feedback_rating,assigned_by\n"
    ).encode()
    with pytest.raises(WorkflowError) as caught:
        ready_store.import_package(changed, history)
    assert caught.value.code == "import_conflict"
    fresh = PostgresStore(load_settings())
    assert fresh.profile("EMP-new-alpha")["full_name"] == stored["full_name"]
    with pytest.raises(WorkflowError) as missing:
        fresh.profile("EMP-PG-NEW")
    assert missing.value.status_code == 404
    valid = json.dumps(
        {
            "employees": [
                {
                    "employee_id": "EMP-PG-NEW",
                    "full_name": "Imported Synthetic Person",
                    "department": "Test Engineering",
                    "role": "Engineer",
                    "grade": "Junior",
                    "manager_id": "LEAD-custom",
                    "hire_date": "2025-02-01",
                    "tenure_months": 11,
                    "work_format": "hybrid",
                    "preferred_language": "ru",
                    "career_goal": None,
                    "skills": {"S_CODE": 1},
                    "last_review_date": "2026-01-10",
                }
            ]
        }
    ).encode()
    added = fresh.import_package(valid, history)
    assert added["employees_added"] == 1
    visible = {
        item["employee_id"] for item in PostgresStore(load_settings()).employees()
    }
    assert "EMP-PG-NEW" in visible
