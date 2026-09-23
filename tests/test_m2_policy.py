from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from backend.career_quest.api import app
from backend.career_quest.errors import WorkflowError
from backend.career_quest.http_api import get_store
from backend.career_quest.loader import load_dataset
from backend.career_quest.models import HistoryRecord
from backend.career_quest.security import (
    hash_password,
    hash_token,
    new_token,
    verify_password,
)
from backend.career_quest.store import Actor, completion_payload
from backend.career_quest.workflow import (
    EmployeeState,
    Participation,
    build_candidates,
    build_profile,
    current_levels,
    employee_to_payload,
    history_to_payload,
    orchestrate_completion,
    prepare_import,
)


class PolicyStore:
    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self.dataset = load_dataset(dataset_path)
        self.password_hash = hash_password("correct-password")
        self.accounts = {
            "employee.a": ("employee", "EMP-new-alpha"),
            "employee.b": ("employee", "LEAD-custom"),
            "hr.user": ("hr", None),
        }
        self.sessions: dict[str, tuple[str, str]] = {}
        self.states: dict[str, EmployeeState] = {}
        self.import_called = False

    def ping(self) -> None:
        return None

    def login(self, username: str, password: str) -> tuple[Actor, str]:
        account = self.accounts.get(username)
        if account is None or not verify_password(password, self.password_hash):
            raise WorkflowError(
                401, "invalid_credentials", "Invalid username or password."
            )
        token = new_token()
        csrf = new_token()
        self.sessions[hash_token(token)] = (username, csrf)
        return Actor(username, account[0], account[1], csrf), token

    def actor_from_token(self, token: str) -> Actor | None:
        found = self.sessions.get(hash_token(token))
        if found is None:
            return None
        username, csrf = found
        role, employee_id = self.accounts[username]
        return Actor(username, role, employee_id, csrf)

    def logout(self, token: str) -> None:
        self.sessions.pop(hash_token(token), None)

    def profile(self, employee_id: str) -> dict[str, object]:
        return build_profile(self._state(employee_id))

    def candidates(self, employee_id: str) -> dict[str, object]:
        return build_candidates(self._state(employee_id))

    def recommendations(self, employee_id: str) -> dict[str, object]:
        from backend.career_quest.ai_select import select_recommendations

        return select_recommendations(
            self.candidates(employee_id),
            api_key=None,
            model="gpt-5.6-terra",
            timeout_seconds=7,
        )

    def employees(self) -> list[dict[str, object]]:
        return [
            {
                "employee_id": employee_id,
                "candidate_status": build_profile(self._state(employee_id))[
                    "candidate_status"
                ],
            }
            for employee_id in self.dataset.employees
        ]

    def overview(self) -> dict[str, object]:
        from backend.career_quest.workflow import build_overview

        return build_overview(
            tuple(self._state(employee_id) for employee_id in self.dataset.employees)
        )

    def complete(
        self,
        employee_id: str,
        event_id: str,
        idempotency_key: str,
        session_date,
    ) -> dict[str, object]:
        state = self._state(employee_id)
        outcome = orchestrate_completion(
            state, event_id, idempotency_key, session_date, "APP-POLICY"
        )
        if not outcome.replay:
            self.states[employee_id] = outcome.state
        return completion_payload(outcome)

    def import_package(self, employees_payload: bytes, history_payload: bytes):
        self.import_called = True
        stored_employees = {
            employee_id: employee_to_payload(employee)
            for employee_id, employee in self.dataset.employees.items()
        }
        stored_history = {
            record.record_id: history_to_payload(record)
            for record in self.dataset.history
        }
        plan = prepare_import(
            self.dataset_path,
            stored_employees,
            stored_history,
            employees_payload,
            history_payload,
        )
        return {
            "employees_added": len(plan.new_employees),
            "employees_unchanged": plan.unchanged_employees,
            "history_added": len(plan.new_history),
            "history_unchanged": plan.unchanged_history,
        }

    def _state(self, employee_id: str) -> EmployeeState:
        if employee_id not in self.states:
            if employee_id not in self.dataset.employees:
                raise WorkflowError(404, "not_found", "Employee was not found.")
            employee = self.dataset.employees[employee_id]
            self.states[employee_id] = EmployeeState(
                self.dataset,
                employee,
                tuple(
                    Participation(record, True, "dataset")
                    for record in self.dataset.history
                    if record.employee_id == employee_id
                ),
                {},
            )
        return self.states[employee_id]


def _client(store: PolicyStore) -> TestClient:
    app.dependency_overrides[get_store] = lambda: store
    return TestClient(app)


def _login(client: TestClient, username: str, password: str = "correct-password"):
    return client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )


def test_login_logout_and_hidden_session_token(synthetic_dataset_path: Path) -> None:
    store = PolicyStore(synthetic_dataset_path)
    client = _client(store)
    rejected = _login(client, "employee.a", "wrong-password")
    assert rejected.status_code == 401
    assert rejected.json()["code"] == "invalid_credentials"

    response = _login(client, "employee.a")
    assert response.status_code == 200
    body = response.json()
    session_cookie = response.headers.get_list("set-cookie")
    session_header = next(item for item in session_cookie if item.startswith("cq_session="))
    csrf_header = next(item for item in session_cookie if item.startswith("cq_csrf="))
    assert "HttpOnly" in session_header
    assert "HttpOnly" not in csrf_header
    assert client.cookies["cq_session"] not in response.text
    assert body["role"] == "employee"
    assert body["employee_id"] == "EMP-new-alpha"

    logged_out = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": body["csrf_token"]},
    )
    assert logged_out.status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    app.dependency_overrides.clear()


def test_employee_boundaries_csrf_and_role_spoofing(
    synthetic_dataset_path: Path,
) -> None:
    store = PolicyStore(synthetic_dataset_path)
    client = _client(store)
    spoofed = client.post(
        "/api/auth/login",
        json={
            "username": "employee.a",
            "password": "correct-password",
            "role": "hr",
        },
    )
    assert spoofed.status_code == 400
    assert "correct-password" not in spoofed.text

    login = _login(client, "employee.a")
    csrf = login.json()["csrf_token"]
    assert client.get("/api/employees/LEAD-custom").status_code == 404
    assert client.get("/api/employees/LEAD-custom/recommendations").status_code == 404
    assert (
        client.post(
            "/api/employees/LEAD-custom/activities/EV_USEFUL/complete",
            headers={"X-CSRF-Token": csrf, "Idempotency-Key": "cross"},
            json={},
        ).status_code
        == 404
    )
    assert client.get("/api/hr/overview").status_code == 403
    denied_import = client.post(
        "/api/hr/import",
        headers={"X-CSRF-Token": csrf},
        files={
            "employees_file": ("employees.json", b"{}", "application/json"),
            "history_file": ("history.csv", b"record_id\n", "text/csv"),
        },
    )
    assert denied_import.status_code == 403
    assert store.import_called is False
    assert (
        client.post(
            "/api/employees/EMP-new-alpha/activities/EV_USEFUL/complete",
            headers={"X-CSRF-Token": "different-token", "Idempotency-Key": "k"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/employees/EMP-new-alpha/activities/EV_USEFUL/complete",
            headers={
                "X-CSRF-Token": csrf,
                "Idempotency-Key": "origin",
                "Origin": "https://evil.example",
            },
        ).status_code
        == 403
    )
    app.dependency_overrides.clear()


def test_completion_retry_is_not_a_second_gain(synthetic_dataset_path: Path) -> None:
    store = PolicyStore(synthetic_dataset_path)
    client = _client(store)
    login = _login(client, "employee.a")
    csrf = login.json()["csrf_token"]
    before = client.get("/api/employees/EMP-new-alpha").json()
    assert before["career_goal_differs_from_primary_target"] is True
    assert "career_goal_changes_primary_target" not in before
    useful = next(
        item
        for item in client.get("/api/employees/EMP-new-alpha/candidates").json()[
            "candidates"
        ]
        if item["event_id"] == "EV_USEFUL"
    )
    assert useful["type"] == "course"
    assert useful["format"] == "self_paced"
    assert useful["duration_hours"] == 2
    assert useful["upcoming_sessions"] == []
    before_level = next(
        item["current_level"]
        for item in before["skills"]
        if item["skill_id"] == "S_ARCH"
    )
    headers = {"X-CSRF-Token": csrf, "Idempotency-Key": "visit-1"}
    first = client.post(
        "/api/employees/EMP-new-alpha/activities/EV_USEFUL/complete",
        headers=headers,
        json={},
    )
    assert first.status_code == 200
    assert first.json()["idempotent_replay"] is False
    assert first.json()["skill_changes"][0]["delta"] == 1
    replay = client.post(
        "/api/employees/EMP-new-alpha/activities/EV_USEFUL/complete",
        headers=headers,
        json={},
    )
    assert replay.status_code == 200
    assert replay.json()["idempotent_replay"] is True
    assert replay.json()["skill_changes"] == []
    conflict = client.post(
        "/api/employees/EMP-new-alpha/activities/EV_USEFUL/complete",
        headers={"X-CSRF-Token": csrf, "Idempotency-Key": "visit-2"},
        json={},
    )
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "already_completed"
    after = client.get("/api/employees/EMP-new-alpha").json()
    after_level = next(
        item["current_level"]
        for item in after["skills"]
        if item["skill_id"] == "S_ARCH"
    )
    assert after_level == before_level + 1
    assert (
        client.get("/api/employees/EMP-new-alpha/candidates").json()["used_ai"]
        is False
    )
    app.dependency_overrides.clear()


def test_app_completion_counts_when_review_is_business_date(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    employee = replace(
        dataset.employees["EMP-new-alpha"],
        last_review_date=dataset.as_of_date,
        skills={"S_ARCH": 0},
    )
    record = HistoryRecord(
        "APP-BOUNDARY",
        employee.employee_id,
        "EV_USEFUL",
        dataset.as_of_date,
        None,
        "completed",
        100,
        None,
        None,
        "self",
        50,
    )
    applied = EmployeeState(
        dataset,
        employee,
        (Participation(record, False, "app"),),
        {},
    )
    replayed = EmployeeState(
        dataset,
        employee,
        (Participation(record, True, "dataset"),),
        {},
    )

    assert current_levels(applied)["S_ARCH"] == 1
    assert current_levels(replayed)["S_ARCH"] == 0
    assert current_levels(applied) == current_levels(applied)


def test_open_attempt_and_repeatable_sessions(synthetic_dataset_path: Path) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    employee = dataset.employees["EMP-new-alpha"]
    state = EmployeeState(
        dataset,
        employee,
        tuple(
            Participation(record, True, "dataset")
            for record in dataset.history
            if record.employee_id == employee.employee_id
        ),
        {},
    )
    before = current_levels(state)["S_ARCH"]
    progressed = orchestrate_completion(
        state, "EV_PROGRESS", "finish-open", None, "APP-OPEN"
    )
    assert progressed.state.participations[-1].record.record_id != "APP-OPEN"
    assert current_levels(progressed.state)["S_ARCH"] == before + 1

    scheduled = replace(
        dataset.events["EV_036"],
        event_format="offline",
        upcoming_sessions=(dataset.as_of_date,),
    )
    catalog = replace(dataset, events={**dataset.events, "EV_036": scheduled})
    fresh = EmployeeState(
        catalog,
        replace(employee, skills={"S_ARCH": 0}),
        (),
        {},
    )
    first = orchestrate_completion(
        fresh, "EV_036", "session-a", dataset.as_of_date, "APP-A"
    )
    second = orchestrate_completion(
        first.state, "EV_036", "session-a", dataset.as_of_date, "APP-B"
    )
    assert second.replay is True
    assert current_levels(second.state)["S_ARCH"] == 1
    try:
        orchestrate_completion(
            first.state, "EV_036", "session-b", dataset.as_of_date, "APP-C"
        )
    except WorkflowError as exc:
        assert exc.code == "session_already_completed"
    else:
        raise AssertionError("same session was completed twice")


def test_import_rejects_conflicts_without_partial_plan(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    stored_employees = {
        employee_id: employee_to_payload(employee)
        for employee_id, employee in dataset.employees.items()
    }
    stored_history = {
        record.record_id: history_to_payload(record) for record in dataset.history
    }
    before = {
        path.name: path.read_bytes()
        for path in synthetic_dataset_path.iterdir()
    }
    employees = json.loads(
        (synthetic_dataset_path / "employees.json").read_text(encoding="utf-8")
    )
    employees["employees"][0]["full_name"] = "Changed Synthetic Name"
    employees["employees"].append(
        {
            **employees["employees"][1],
            "employee_id": "EMP-IMPORTED",
            "full_name": "Imported Synthetic Person",
            "manager_id": "LEAD-custom",
        }
    )
    history = (synthetic_dataset_path / "activity_history.csv").read_bytes()

    try:
        prepare_import(
            synthetic_dataset_path,
            stored_employees,
            stored_history,
            json.dumps(employees).encode(),
            history,
        )
    except WorkflowError as exc:
        assert exc.code == "import_conflict"
    else:
        raise AssertionError("conflicting import was accepted")
    assert {
        path.name: path.read_bytes() for path in synthetic_dataset_path.iterdir()
    } == before

    person = dict(employees["employees"][1])
    person["employee_id"] = "EMP-IMPORTED"
    person["manager_id"] = "LEAD-custom"
    valid = dict(employees)
    valid["employees"] = [person]
    plan = prepare_import(
        synthetic_dataset_path,
        stored_employees,
        stored_history,
        json.dumps(valid).encode(),
        b"record_id,employee_id,event_id,date,due_date,status,completion_pct,score,feedback_rating,assigned_by\n",
    )
    assert [employee.employee_id for employee in plan.new_employees] == [
        "EMP-IMPORTED"
    ]
    assert plan.new_history == ()
