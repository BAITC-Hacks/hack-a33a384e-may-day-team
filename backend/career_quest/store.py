from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from .errors import WorkflowError
from .loader import load_dataset
from .models import CareerGoal, Employee, HistoryRecord
from .orm import (
    AccountRow,
    DatasetStateRow,
    EmployeeRow,
    HistoryRow,
    IdempotencyRow,
    SessionRow,
)
from .security import hash_password, hash_token, new_token, verify_password
from .settings import DEMO_VARIABLES, Settings, assert_safe_database
from .ai_select import select_recommendations
from .workflow import (
    CompletionOutcome,
    EmployeeState,
    IdempotencyRecord,
    ImportPlan,
    Participation,
    build_candidates,
    build_overview,
    build_profile,
    employee_to_payload,
    history_to_payload,
    orchestrate_completion,
    prepare_import,
)


class Actor:
    def __init__(
        self,
        username: str,
        role: str,
        employee_id: str | None,
        csrf_token: str,
    ):
        self.username = username
        self.role = role
        self.employee_id = employee_id
        self.csrf_token = csrf_token


def completion_payload(outcome: CompletionOutcome) -> dict[str, object]:
    return {
        "idempotent_replay": outcome.replay,
        "modeled_completion": True,
        "record_id": outcome.record_id,
        "activity_date": outcome.activity_date.isoformat(),
        "skill_changes": list(outcome.skill_changes),
        "requirements": list(outcome.requirements),
        "candidate_status": outcome.candidate_status,
    }


class PostgresStore:
    def __init__(self, settings: Settings):
        if not settings.database_url or not settings.dataset_path:
            raise WorkflowError(
                503,
                "database_unavailable",
                "Backend storage is not configured.",
            )
        assert_safe_database(settings.database_url)
        self.settings = settings
        self.session_factory = sessionmaker(
            create_engine(settings.database_url, pool_pre_ping=True),
            expire_on_commit=False,
        )

    def ping(self) -> None:
        try:
            with self.session_factory() as session:
                session.execute(text("SELECT 1"))
        except Exception as exc:
            raise WorkflowError(
                503,
                "database_unavailable",
                "PostgreSQL is not available.",
            ) from exc

    def login(self, username: str, password: str) -> tuple[Actor, str]:
        with self.session_factory() as session:
            account = session.get(AccountRow, username)
            if account is None or not verify_password(password, account.password_hash):
                raise WorkflowError(
                    401,
                    "invalid_credentials",
                    "Invalid username or password.",
                )
            token = new_token()
            csrf = new_token()
            session.add(
                SessionRow(
                    token_hash=hash_token(token),
                    username=account.username,
                    csrf_token=csrf,
                    expires_at=datetime.now(timezone.utc)
                    + timedelta(hours=self.settings.session_ttl_hours),
                )
            )
            session.commit()
            return (
                Actor(account.username, account.role, account.employee_id, csrf),
                token,
            )

    def actor_from_token(self, token: str) -> Actor | None:
        with self.session_factory() as session:
            row = session.get(SessionRow, hash_token(token))
            if row is None:
                return None
            expires_at = row.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= datetime.now(timezone.utc):
                session.delete(row)
                session.commit()
                return None
            account = session.get(AccountRow, row.username)
            if account is None:
                return None
            return Actor(
                account.username, account.role, account.employee_id, row.csrf_token
            )

    def logout(self, token: str) -> None:
        with self.session_factory() as session:
            row = session.get(SessionRow, hash_token(token))
            if row is not None:
                session.delete(row)
                session.commit()

    def profile(self, employee_id: str) -> dict[str, object]:
        with self.session_factory() as session:
            return build_profile(self._state(session, employee_id))

    def candidates(self, employee_id: str) -> dict[str, object]:
        with self.session_factory() as session:
            return build_candidates(self._state(session, employee_id))

    def recommendations(self, employee_id: str) -> dict[str, object]:
        facts = self.candidates(employee_id)
        return select_recommendations(
            facts,
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
            timeout_seconds=self.settings.openai_timeout_seconds,
        )

    def employees(self) -> list[dict[str, object]]:
        with self.session_factory() as session:
            return [
                {
                    "employee_id": state.employee.employee_id,
                    "full_name": state.employee.full_name,
                    "role": state.employee.role,
                    "grade": state.employee.grade,
                    "candidate_status": build_profile(state)["candidate_status"],
                }
                for state in self._all_states(session)
            ]

    def overview(self) -> dict[str, object]:
        with self.session_factory() as session:
            return build_overview(self._all_states(session))

    def complete(
        self,
        employee_id: str,
        event_id: str,
        idempotency_key: str,
        session_date: date | None,
    ) -> dict[str, object]:
        try:
            with self.session_factory() as session, session.begin():
                row = session.execute(
                    select(EmployeeRow)
                    .where(EmployeeRow.employee_id == employee_id)
                    .with_for_update()
                ).scalar_one_or_none()
                if row is None:
                    raise WorkflowError(404, "not_found", "Employee was not found.")
                state = self._state(session, employee_id)
                outcome = orchestrate_completion(
                    state,
                    event_id,
                    idempotency_key,
                    session_date,
                    f"APP-{uuid.uuid4().hex}",
                )
                if not outcome.replay:
                    self._persist_outcome(session, state, outcome)
                return completion_payload(outcome)
        except IntegrityError as exc:
            raise WorkflowError(
                409,
                "conflict",
                "The completion conflicted with another request.",
            ) from exc

    def import_package(
        self, employees_payload: bytes, history_payload: bytes
    ) -> dict[str, int]:
        with self.session_factory() as session:
            stored_employees = {
                row.employee_id: row.payload
                for row in session.scalars(select(EmployeeRow))
            }
            stored_history = {
                row.record_id: history_to_payload(self._record(row))
                for row in session.scalars(select(HistoryRow))
            }
        plan = prepare_import(
            Path(self.settings.dataset_path or ""),
            stored_employees,
            stored_history,
            employees_payload,
            history_payload,
        )
        self.apply_import(plan)
        return {
            "employees_added": len(plan.new_employees),
            "employees_unchanged": plan.unchanged_employees,
            "history_added": len(plan.new_history),
            "history_unchanged": plan.unchanged_history,
        }

    def apply_import(self, plan: ImportPlan) -> None:
        with self.session_factory() as session, session.begin():
            next_row = session.scalar(select(func.max(HistoryRow.source_row))) or 0
            for employee in plan.new_employees:
                if session.get(EmployeeRow, employee.employee_id) is not None:
                    raise WorkflowError(
                        409,
                        "import_conflict",
                        "Import matches existing IDs with different content.",
                    )
                session.add(
                    EmployeeRow(
                        employee_id=employee.employee_id,
                        source="import",
                        payload=employee_to_payload(employee),
                    )
                )
            session.flush()
            for offset, record in enumerate(plan.new_history, start=1):
                if session.get(HistoryRow, record.record_id) is not None:
                    raise WorkflowError(
                        409,
                        "import_conflict",
                        "Import matches existing IDs with different content.",
                    )
                session.add(self._history_row(
                    record, "import", True, next_row + offset
                ))

    def seed(self) -> None:
        if self.settings.demo_accounts is None:
            raise WorkflowError(
                500,
                "configuration_error",
                "Demo accounts are not configured.",
                {"missing": list(DEMO_VARIABLES)},
            )
        dataset_path = Path(self.settings.dataset_path or "")
        catalog = load_dataset(dataset_path)
        digest = _fingerprint(dataset_path)
        with self.session_factory() as session, session.begin():
            state = session.get(DatasetStateRow, 1)
            if state is None:
                for employee in catalog.employees.values():
                    session.add(
                        EmployeeRow(
                            employee_id=employee.employee_id,
                            source="dataset",
                            payload=employee_to_payload(employee),
                        )
                    )
                session.flush()
                for record in catalog.history:
                    session.add(
                        self._history_row(record, "dataset", True, record.source_row)
                    )
                session.add(
                    DatasetStateRow(
                        id=1,
                        fingerprint=digest,
                        dataset_name=catalog.name,
                        version=catalog.version,
                        as_of_date=catalog.as_of_date,
                    )
                )
            elif state.fingerprint != digest:
                raise WorkflowError(
                    409,
                    "dataset_conflict",
                    "The dataset differs from the one already stored.",
                )
            self._ensure_accounts(session)

    def _ensure_accounts(self, session: Session) -> None:
        demo = self.settings.demo_accounts
        assert demo is not None
        specs = (
            (
                demo.employee_one_username,
                demo.employee_one_password,
                "employee",
                demo.employee_one_id,
            ),
            (
                demo.employee_two_username,
                demo.employee_two_password,
                "employee",
                demo.employee_two_id,
            ),
            (demo.hr_username, demo.hr_password, "hr", None),
        )
        for username, password, role, employee_id in specs:
            if employee_id is not None and session.get(EmployeeRow, employee_id) is None:
                raise WorkflowError(
                    500,
                    "configuration_error",
                    "A demo employee ID is not present in the stored dataset.",
                )
            if session.get(AccountRow, username) is None:
                session.add(
                    AccountRow(
                        username=username,
                        password_hash=hash_password(password),
                        role=role,
                        employee_id=employee_id,
                    )
                )

    def _state(self, session: Session, employee_id: str) -> EmployeeState:
        row = session.get(EmployeeRow, employee_id)
        if row is None:
            raise WorkflowError(404, "not_found", "Employee was not found.")
        history = session.scalars(
            select(HistoryRow)
            .where(HistoryRow.employee_id == employee_id)
            .order_by(HistoryRow.source_row)
        ).all()
        idempotency = {
            item.idempotency_key: IdempotencyRecord(
                item.idempotency_key, item.request_hash, item.record_id
            )
            for item in session.scalars(
                select(IdempotencyRow).where(
                    IdempotencyRow.employee_id == employee_id
                )
            )
        }
        return EmployeeState(
            catalog=_catalog(self.settings.dataset_path or ""),
            employee=_employee(row.payload),
            participations=tuple(
                Participation(self._record(item), item.counts_in_replay, item.origin)
                for item in history
            ),
            idempotency=idempotency,
        )

    def _all_states(self, session: Session) -> tuple[EmployeeState, ...]:
        return tuple(
            self._state(session, row.employee_id)
            for row in session.scalars(select(EmployeeRow).order_by(EmployeeRow.employee_id))
        )

    def _persist_outcome(
        self,
        session: Session,
        previous: EmployeeState,
        outcome: CompletionOutcome,
    ) -> None:
        previous_ids = {
            item.record.record_id for item in previous.participations
        }
        for item in outcome.state.participations:
            if item.record.record_id not in previous_ids:
                session.add(
                    self._history_row(
                        item.record, item.origin, item.counts_in_replay, item.record.source_row
                    )
                )
                continue
            row = session.get(HistoryRow, item.record.record_id)
            if row is None:
                continue
            row.status = item.record.status
            row.completion_pct = item.record.completion_pct
            row.origin = item.origin
            row.counts_in_replay = item.counts_in_replay
        session.flush()
        for key, record in outcome.state.idempotency.items():
            if key in previous.idempotency:
                continue
            session.add(
                IdempotencyRow(
                    employee_id=outcome.state.employee.employee_id,
                    idempotency_key=key,
                    request_hash=record.request_hash,
                    record_id=record.record_id,
                )
            )

    @staticmethod
    def _history_row(
        record: HistoryRecord,
        origin: str,
        counts_in_replay: bool,
        source_row: int,
    ) -> HistoryRow:
        return HistoryRow(
            record_id=record.record_id,
            employee_id=record.employee_id,
            event_id=record.event_id,
            activity_date=record.activity_date,
            due_date=record.due_date,
            status=record.status,
            completion_pct=record.completion_pct,
            score=record.score,
            feedback_rating=record.feedback_rating,
            assigned_by=record.assigned_by,
            source_row=source_row,
            origin=origin,
            counts_in_replay=counts_in_replay,
        )

    @staticmethod
    def _record(row: HistoryRow) -> HistoryRecord:
        return HistoryRecord(
            record_id=row.record_id,
            employee_id=row.employee_id,
            event_id=row.event_id,
            activity_date=row.activity_date,
            due_date=row.due_date,
            status=row.status,
            completion_pct=row.completion_pct,
            score=row.score,
            feedback_rating=row.feedback_rating,
            assigned_by=row.assigned_by,
            source_row=row.source_row,
        )


def _employee(payload: dict) -> Employee:
    goal = payload["career_goal"]
    return Employee(
        employee_id=payload["employee_id"],
        full_name=payload["full_name"],
        department=payload["department"],
        role=payload["role"],
        grade=payload["grade"],
        manager_id=payload["manager_id"],
        hire_date=date.fromisoformat(payload["hire_date"]),
        tenure_months=payload["tenure_months"],
        work_format=payload["work_format"],
        preferred_language=payload["preferred_language"],
        career_goal=(
            None
            if goal is None
            else CareerGoal(goal["target_role"], goal["target_grade"])
        ),
        skills=dict(payload["skills"]),
        last_review_date=date.fromisoformat(payload["last_review_date"]),
    )


@lru_cache(maxsize=4)
def _catalog(dataset_path: str):
    return load_dataset(dataset_path)


def _fingerprint(dataset_path: Path) -> str:
    digest = hashlib.sha256()
    for name in (
        "skills.json",
        "employees.json",
        "events.json",
        "activity_history.csv",
    ):
        digest.update(name.encode("utf-8"))
        digest.update((dataset_path / name).read_bytes())
    return digest.hexdigest()
