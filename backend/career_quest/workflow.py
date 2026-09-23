from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import tempfile
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from .engine import analyze_candidates, calculate_current_skills, primary_target, target_gaps
from .errors import WorkflowError
from .loader import DatasetValidationError, load_dataset
from .models import REPEATABLE_EVENT_IDS, Dataset, Employee, Event, HistoryRecord

MAX_IMPORT_BYTES = 1_048_576


@dataclass(frozen=True)
class Participation:
    record: HistoryRecord
    counts_in_replay: bool
    origin: str


@dataclass(frozen=True)
class IdempotencyRecord:
    key: str
    request_hash: str
    record_id: str


@dataclass(frozen=True)
class EmployeeState:
    catalog: Dataset
    employee: Employee
    participations: tuple[Participation, ...]
    idempotency: dict[str, IdempotencyRecord]


@dataclass(frozen=True)
class CompletionOutcome:
    replay: bool
    state: EmployeeState
    record_id: str
    activity_date: date
    skill_changes: tuple[dict[str, object], ...]
    requirements: tuple[dict[str, object], ...]
    candidate_status: str


@dataclass(frozen=True)
class ImportPlan:
    new_employees: tuple[Employee, ...]
    new_history: tuple[HistoryRecord, ...]
    unchanged_employees: int
    unchanged_history: int


def request_hash(
    employee_id: str, event_id: str, session_date: date | None
) -> str:
    raw = "|".join(
        (
            employee_id,
            event_id,
            session_date.isoformat() if session_date else "",
        )
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _replay_dataset(state: EmployeeState) -> Dataset:
    records = tuple(
        item.record for item in state.participations if item.counts_in_replay
    )
    return replace(
        state.catalog,
        employees={state.employee.employee_id: state.employee},
        history=records,
    )


def _full_dataset(state: EmployeeState) -> Dataset:
    return replace(
        state.catalog,
        employees={state.employee.employee_id: state.employee},
        history=tuple(item.record for item in state.participations),
    )


def current_levels(state: EmployeeState) -> dict[str, int]:
    levels = dict(
        calculate_current_skills(
            _replay_dataset(state), state.employee.employee_id
        ).levels
    )
    app_records = sorted(
        (
            item.record
            for item in state.participations
            if not item.counts_in_replay and item.record.status == "completed"
        ),
        key=lambda record: (record.activity_date, record.source_row),
    )
    for record in app_records:
        event = state.catalog.events[record.event_id]
        for effect in event.develops_skills:
            current = levels.get(effect.skill_id, 0)
            delta = max(0, min(effect.gain, effect.max_level - current))
            if delta:
                levels[effect.skill_id] = current + delta
    return levels


def _requirement_payload(state: EmployeeState) -> tuple[dict[str, object], ...]:
    target = primary_target(
        _full_dataset(state), state.employee.employee_id
    )
    if target is None:
        return ()
    return tuple(
        {
            "skill_id": gap.skill_id,
            "current_level": gap.current_level,
            "required_level": gap.required_level,
            "missing_level": gap.missing_level,
            "critical": gap.critical,
        }
        for gap in target_gaps(state.catalog, target, current_levels(state))
    )


def _analysis(state: EmployeeState):
    return analyze_candidates(
        _full_dataset(state),
        state.employee.employee_id,
        current_levels(state),
    )


def build_profile(state: EmployeeState) -> dict[str, object]:
    employee = state.employee
    target = primary_target(_full_dataset(state), employee.employee_id)
    requirements = _requirement_payload(state)
    goal = employee.career_goal
    return {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "role": employee.role,
        "grade": employee.grade,
        "career_goal": (
            None
            if goal is None
            else {
                "target_role": goal.target_role,
                "target_grade": goal.target_grade,
            }
        ),
        "primary_target": (
            None if target is None else {"role": target.role, "grade": target.grade}
        ),
        "career_goal_changes_primary_target": bool(
            goal is not None
            and target is not None
            and (goal.target_role, goal.target_grade)
            != (target.role, target.grade)
        ),
        "as_of_date": state.catalog.as_of_date.isoformat(),
        "skills": [
            {"skill_id": skill_id, "current_level": level}
            for skill_id, level in sorted(current_levels(state).items())
        ],
        "requirements": list(requirements),
        "requirements_met_count": sum(
            1 for item in requirements if item["missing_level"] == 0
        ),
        "requirements_total": len(requirements),
        "candidate_status": _analysis(state).status,
        "history": [
            {
                "record_id": item.record.record_id,
                "event_id": item.record.event_id,
                "date": item.record.activity_date.isoformat(),
                "status": item.record.status,
                "completion_pct": item.record.completion_pct,
                "assigned_by": item.record.assigned_by,
                "origin": item.origin,
            }
            for item in sorted(
                state.participations,
                key=lambda item: (
                    item.record.activity_date,
                    item.record.source_row,
                ),
            )
        ],
    }


def build_candidates(state: EmployeeState) -> dict[str, object]:
    analysis = _analysis(state)
    return {
        "used_ai": False,
        "selection_status": "not_ranked",
        "candidate_status": analysis.status,
        "candidates": [
            {
                "event_id": item.event_id,
                "title": item.title,
                "target": {
                    "role": item.target.role,
                    "grade": item.target.grade,
                },
                "gaps": [
                    {
                        "skill_id": gap.skill_id,
                        "current_level": gap.current_level,
                        "required_level": gap.required_level,
                        "missing_level": gap.missing_level,
                        "critical": gap.critical,
                    }
                    for gap in item.gaps
                ],
                "critical_gaps": [gap.skill_id for gap in item.critical_gaps],
                "prerequisites": [
                    {
                        "skill_id": check.skill_id,
                        "current_level": check.current_level,
                        "required_level": check.required_level,
                        "met": check.met,
                    }
                    for check in item.prerequisites
                ],
                "potential_skill_changes": [
                    {
                        "skill_id": change.skill_id,
                        "current_level": change.current_level,
                        "gain": change.gain,
                        "max_level": change.max_level,
                        "delta": change.delta,
                        "new_level": change.new_level,
                    }
                    for change in item.potential_skill_changes
                ],
                "participation": {
                    "event_status_counts": item.participation.event_status_counts,
                    "related_skill_negative_status_counts": (
                        item.participation.related_skill_negative_status_counts
                    ),
                },
            }
            for item in analysis.candidates
        ],
        "exclusions": [
            {
                "event_id": item.event_id,
                "reasons": [
                    {"code": reason.code, "details": reason.details}
                    for reason in item.reasons
                ],
            }
            for item in analysis.exclusions
        ],
    }


def build_overview(states: tuple[EmployeeState, ...]) -> dict[str, object]:
    gap_counts: dict[str, int] = {}
    critical_counts: dict[str, int] = {}
    without_step = []
    participation: dict[str, dict[str, int]] = {}
    for state in states:
        analysis = _analysis(state)
        if analysis.status != "candidates_available":
            without_step.append(
                {
                    "employee_id": state.employee.employee_id,
                    "reason": analysis.status,
                }
            )
        target = primary_target(
            _full_dataset(state), state.employee.employee_id
        )
        if target is not None:
            for gap in target_gaps(
                state.catalog, target, current_levels(state)
            ):
                if gap.missing_level <= 0:
                    continue
                gap_counts[gap.skill_id] = gap_counts.get(gap.skill_id, 0) + 1
                if gap.critical:
                    critical_counts[gap.skill_id] = (
                        critical_counts.get(gap.skill_id, 0) + 1
                    )
        for item in state.participations:
            counts = participation.setdefault(item.record.event_id, {})
            counts[item.record.status] = counts.get(item.record.status, 0) + 1
    return {
        "basis": "eligible_candidates_before_ai",
        "frequent_skill_gaps": [
            {
                "skill_id": skill_id,
                "employees_missing": gap_counts[skill_id],
                "critical_employees_missing": critical_counts.get(skill_id, 0),
            }
            for skill_id in sorted(
                gap_counts, key=lambda item: (-gap_counts[item], item)
            )
        ],
        "employees_without_next_step": without_step,
        "participation_by_activity": [
            {"event_id": event_id, "status_counts": participation[event_id]}
            for event_id in sorted(participation)
        ],
    }


def _event(state: EmployeeState, event_id: str) -> Event:
    try:
        return state.catalog.events[event_id]
    except KeyError as exc:
        raise WorkflowError(
            404, "not_found", "Activity was not found."
        ) from exc


def orchestrate_completion(
    state: EmployeeState,
    event_id: str,
    idempotency_key: str,
    session_date: date | None,
    new_record_id: str,
) -> CompletionOutcome:
    event = _event(state, event_id)
    digest = request_hash(state.employee.employee_id, event_id, session_date)
    stored = state.idempotency.get(idempotency_key)
    if stored is not None:
        if stored.request_hash != digest:
            raise WorkflowError(
                409,
                "idempotency_key_reused",
                "Idempotency-Key was already used with different content.",
            )
        return _outcome(state, stored.record_id, replay=True)

    employee_records = [
        item for item in state.participations
        if item.record.event_id == event_id
    ]
    open_attempt = next(
        (
            item
            for item in reversed(employee_records)
            if item.record.status == "in_progress"
        ),
        None,
    )
    if event.event_format == "self_paced":
        if session_date is not None:
            raise WorkflowError(
                400,
                "validation_error",
                "session_date is not used for a self-paced activity.",
            )
        activity_date = state.catalog.as_of_date
    else:
        if session_date is None:
            raise WorkflowError(
                400,
                "validation_error",
                "session_date is required for a scheduled activity.",
            )
        if open_attempt is not None:
            if session_date != open_attempt.record.activity_date:
                raise WorkflowError(
                    409,
                    "session_not_available",
                    "session_date does not match the started attempt.",
                )
        elif (
            session_date not in event.upcoming_sessions
            or session_date < state.catalog.as_of_date
        ):
            raise WorkflowError(
                409,
                "session_not_available",
                "The session is not available on the business date.",
            )
        activity_date = session_date

    completed = [
        item for item in employee_records if item.record.status == "completed"
    ]
    repeatable = event.event_id in REPEATABLE_EVENT_IDS
    if not repeatable and completed and open_attempt is None:
        raise WorkflowError(
            409,
            "already_completed",
            "This activity is already completed.",
        )
    if (
        repeatable
        and event.event_format != "self_paced"
        and any(item.record.activity_date == activity_date for item in completed)
    ):
        raise WorkflowError(
            409,
            "session_already_completed",
            "This session is already completed.",
        )

    eligible = {
        item.event_id for item in _analysis(state).candidates
    }
    if open_attempt is None and event_id not in eligible:
        raise WorkflowError(
            409,
            "activity_not_eligible",
            "The activity is not currently eligible.",
            {
                "reasons": [
                    reason.code
                    for excluded in _analysis(state).exclusions
                    if excluded.event_id == event_id
                    for reason in excluded.reasons
                ]
            },
        )

    before = current_levels(state)
    if open_attempt is not None:
        in_window = (
            state.employee.last_review_date
            < open_attempt.record.activity_date
            <= state.catalog.as_of_date
        )
        updated = replace(
            open_attempt.record,
            status="completed",
            completion_pct=100,
        )
        participations = tuple(
            Participation(updated, in_window, "app")
            if item.record.record_id == updated.record_id
            else item
            for item in state.participations
        )
        record_id = updated.record_id
        activity_date = updated.activity_date
    else:
        source_row = 1 + max(
            (item.record.source_row for item in state.participations),
            default=0,
        )
        created = HistoryRecord(
            record_id=new_record_id,
            employee_id=state.employee.employee_id,
            event_id=event_id,
            activity_date=activity_date,
            due_date=None,
            status="completed",
            completion_pct=100,
            score=None,
            feedback_rating=None,
            assigned_by="self",
            source_row=source_row,
        )
        participations = state.participations + (
            Participation(created, False, "app"),
        )
        record_id = created.record_id

    new_state = replace(
        state,
        participations=participations,
        idempotency={
            **state.idempotency,
            idempotency_key: IdempotencyRecord(
                idempotency_key, digest, record_id
            ),
        },
    )
    after = current_levels(new_state)
    changes = tuple(
        {
            "skill_id": skill_id,
            "level_before": before.get(skill_id, 0),
            "level_after": after[skill_id],
            "delta": after[skill_id] - before.get(skill_id, 0),
        }
        for skill_id in sorted(after)
        if after[skill_id] != before.get(skill_id, 0)
    )
    return CompletionOutcome(
        replay=False,
        state=new_state,
        record_id=record_id,
        activity_date=activity_date,
        skill_changes=changes,
        requirements=_requirement_payload(new_state),
        candidate_status=_analysis(new_state).status,
    )


def _outcome(
    state: EmployeeState, record_id: str, replay: bool
) -> CompletionOutcome:
    record = next(
        item.record
        for item in state.participations
        if item.record.record_id == record_id
    )
    return CompletionOutcome(
        replay=replay,
        state=state,
        record_id=record_id,
        activity_date=record.activity_date,
        skill_changes=(),
        requirements=_requirement_payload(state),
        candidate_status=_analysis(state).status,
    )


def employee_to_payload(employee: Employee) -> dict[str, object]:
    goal = employee.career_goal
    return {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "department": employee.department,
        "role": employee.role,
        "grade": employee.grade,
        "manager_id": employee.manager_id,
        "hire_date": employee.hire_date.isoformat(),
        "tenure_months": employee.tenure_months,
        "work_format": employee.work_format,
        "preferred_language": employee.preferred_language,
        "career_goal": (
            None
            if goal is None
            else {
                "target_role": goal.target_role,
                "target_grade": goal.target_grade,
            }
        ),
        "skills": dict(sorted(employee.skills.items())),
        "last_review_date": employee.last_review_date.isoformat(),
    }


def history_to_payload(record: HistoryRecord) -> dict[str, object]:
    return {
        "record_id": record.record_id,
        "employee_id": record.employee_id,
        "event_id": record.event_id,
        "date": record.activity_date.isoformat(),
        "due_date": "" if record.due_date is None else record.due_date.isoformat(),
        "status": record.status,
        "completion_pct": record.completion_pct,
        "score": "" if record.score is None else record.score,
        "feedback_rating": (
            "" if record.feedback_rating is None else record.feedback_rating
        ),
        "assigned_by": record.assigned_by,
    }


def _read_object(payload: bytes, label: str) -> dict:
    try:
        value = json.loads(
            payload.decode("utf-8-sig"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except UnicodeDecodeError as exc:
        raise WorkflowError(
            400, "validation_error", f"{label} is not valid UTF-8."
        ) from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            400, "validation_error", f"{label} is not valid JSON."
        ) from exc
    except ValueError as exc:
        raise WorkflowError(400, "validation_error", str(exc)) from exc
    if not isinstance(value, dict):
        raise WorkflowError(
            400, "validation_error", f"{label} must contain a JSON object."
        )
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    value: dict = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON object key {key!r}")
        value[key] = item
    return value


def _read_history(payload: bytes) -> list[dict[str, str]]:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise WorkflowError(
            400, "validation_error", "history file is not valid UTF-8."
        ) from exc
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        raise WorkflowError(
            400, "validation_error", "history file is empty."
        )
    header = rows[0]
    duplicates = sorted({name for name in header if header.count(name) > 1})
    if duplicates:
        raise WorkflowError(
            400,
            "validation_error",
            "history file has duplicate column names: " + ", ".join(duplicates),
        )
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def prepare_import(
    dataset_path: Path,
    stored_employees: dict[str, dict[str, object]],
    stored_history: dict[str, dict[str, object]],
    employees_payload: bytes,
    history_payload: bytes,
) -> ImportPlan:
    if len(employees_payload) > MAX_IMPORT_BYTES or len(history_payload) > MAX_IMPORT_BYTES:
        raise WorkflowError(
            413,
            "payload_too_large",
            "An import file exceeds 1 MiB.",
        )
    document = _read_object(employees_payload, "employees file")
    incoming_employees = document.get("employees")
    if not isinstance(incoming_employees, list):
        raise WorkflowError(
            400,
            "validation_error",
            "employees file must contain an employees array.",
        )
    incoming_history = _read_history(history_payload)
    merged_employees = dict(stored_employees)
    incoming_employee_ids: list[str] = []
    for index, raw in enumerate(incoming_employees):
        if not isinstance(raw, dict) or not isinstance(raw.get("employee_id"), str):
            raise WorkflowError(
                400,
                "validation_error",
                f"employees[{index}] has no employee_id.",
            )
        employee_id = raw["employee_id"]
        if employee_id in incoming_employee_ids:
            raise WorkflowError(
                400,
                "validation_error",
                f"Duplicate employee_id {employee_id} in import.",
            )
        incoming_employee_ids.append(employee_id)
        merged_employees[employee_id] = raw

    merged_history = dict(stored_history)
    incoming_record_ids: list[str] = []
    for index, raw in enumerate(incoming_history, start=2):
        record_id = raw.get("record_id", "")
        if not record_id:
            raise WorkflowError(
                400,
                "validation_error",
                f"history row {index} has no record_id.",
            )
        if record_id in incoming_record_ids:
            raise WorkflowError(
                400,
                "validation_error",
                f"Duplicate record_id {record_id} in import.",
            )
        incoming_record_ids.append(record_id)
        merged_history[record_id] = raw

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name in ("skills.json", "events.json"):
            shutil.copyfile(dataset_path / name, root / name)
        skills_meta = json.loads((dataset_path / "skills.json").read_text(encoding="utf-8"))
        (root / "employees.json").write_text(
            json.dumps(
                {"meta": skills_meta["meta"], "employees": list(merged_employees.values())},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        fieldnames = [
            "record_id",
            "employee_id",
            "event_id",
            "date",
            "due_date",
            "status",
            "completion_pct",
            "score",
            "feedback_rating",
            "assigned_by",
        ]
        with (root / "activity_history.csv").open(
            "w", encoding="utf-8", newline=""
        ) as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames)
            writer.writeheader()
            for record_id in sorted(merged_history):
                writer.writerow(
                    {field: merged_history[record_id].get(field, "") for field in fieldnames}
                )
        try:
            loaded = load_dataset(root)
        except DatasetValidationError as exc:
            raise WorkflowError(
                400, "validation_error", str(exc)
            ) from exc

    conflicts = []
    unchanged_employees = 0
    new_employee_ids = []
    for employee_id in incoming_employee_ids:
        payload = employee_to_payload(loaded.employees[employee_id])
        if employee_id in stored_employees:
            if payload != stored_employees[employee_id]:
                conflicts.append({"employee_id": employee_id})
            else:
                unchanged_employees += 1
        else:
            new_employee_ids.append(employee_id)
    unchanged_history = 0
    new_record_ids = []
    for record_id in incoming_record_ids:
        loaded_record = next(
            record for record in loaded.history if record.record_id == record_id
        )
        payload = history_to_payload(loaded_record)
        if record_id in stored_history:
            if payload != stored_history[record_id]:
                conflicts.append({"record_id": record_id})
            else:
                unchanged_history += 1
        else:
            new_record_ids.append(record_id)
    if conflicts:
        raise WorkflowError(
            409,
            "import_conflict",
            "Import matches existing IDs with different content.",
            {"conflicts": conflicts},
        )
    return ImportPlan(
        new_employees=tuple(loaded.employees[employee_id] for employee_id in new_employee_ids),
        new_history=tuple(
            record
            for record in loaded.history
            if record.record_id in set(new_record_ids)
        ),
        unchanged_employees=unchanged_employees,
        unchanged_history=unchanged_history,
    )
