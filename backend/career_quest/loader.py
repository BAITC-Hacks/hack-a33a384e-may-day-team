from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

from .models import (
    GRADE_ORDER,
    HISTORY_STATUSES,
    CareerGoal,
    Dataset,
    Employee,
    Event,
    HistoryRecord,
    RoleProfile,
    Skill,
    SkillEffect,
)


EVENT_TYPES = frozenset(
    {
        "compliance",
        "onboarding",
        "course",
        "workshop",
        "mentoring",
        "certification",
        "meetup",
    }
)
EVENT_FORMATS = frozenset({"online", "offline", "self_paced"})
SKILL_TYPES = frozenset({"hard", "soft"})
WORK_FORMATS = frozenset({"office", "hybrid", "remote"})
LANGUAGES = frozenset({"kk", "ru", "en"})
ASSIGNED_BY_VALUES = frozenset({"self", "manager", "hr"})


class DatasetValidationError(ValueError):
    def __init__(self, file_name: str, record: str, field: str, reason: str):
        self.file_name = file_name
        self.record = record
        self.field = field
        self.reason = reason
        super().__init__(
            f"{file_name}: record={record}; field={field}; reason={reason}"
        )


def _error(file_name: str, record: str, field: str, reason: str) -> None:
    raise DatasetValidationError(file_name, record, field, reason)


def _read_json(dataset_path: Path, file_name: str) -> dict[str, Any]:
    path = dataset_path / file_name
    try:
        with path.open(encoding="utf-8-sig") as source:
            value = json.load(source)
    except FileNotFoundError:
        _error(file_name, "$", "file", f"file not found under {dataset_path}")
    except json.JSONDecodeError as exc:
        _error(
            file_name,
            "$",
            "json",
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        )
    except UnicodeDecodeError as exc:
        _error(file_name, "$", "encoding", f"invalid UTF-8: {exc}")
    except OSError as exc:
        _error(file_name, "$", "file", str(exc))

    if not isinstance(value, dict):
        _error(file_name, "$", "$", "top-level value must be an object")
    return value


def _required(
    value: dict[str, Any], key: str, file_name: str, record: str
) -> Any:
    if key not in value:
        _error(file_name, record, key, "required field is missing")
    return value[key]


def _mapping(
    value: Any, file_name: str, record: str, field: str
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _error(file_name, record, field, "must be an object")
    return value


def _list(value: Any, file_name: str, record: str, field: str) -> list[Any]:
    if not isinstance(value, list):
        _error(file_name, record, field, "must be an array")
    return value


def _string(
    value: Any,
    file_name: str,
    record: str,
    field: str,
    *,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        _error(file_name, record, field, "must be a string")
    if not allow_empty and not value.strip():
        _error(file_name, record, field, "must not be empty")
    return value


def _integer(
    value: Any, file_name: str, record: str, field: str
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _error(file_name, record, field, "must be an integer")
    return value


def _number(
    value: Any, file_name: str, record: str, field: str
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _error(file_name, record, field, "must be a number")
    return float(value)


def _boolean(
    value: Any, file_name: str, record: str, field: str
) -> bool:
    if not isinstance(value, bool):
        _error(file_name, record, field, "must be a boolean")
    return value


def _date(
    value: Any, file_name: str, record: str, field: str
) -> date:
    text = _string(value, file_name, record, field)
    if (
        len(text) != 10
        or text[4] != "-"
        or text[7] != "-"
        or not (text[:4] + text[5:7] + text[8:]).isdigit()
    ):
        _error(file_name, record, field, "must be an ISO date (YYYY-MM-DD)")
    try:
        return date.fromisoformat(text)
    except ValueError:
        _error(file_name, record, field, "must be an ISO date (YYYY-MM-DD)")


def _choice(
    value: Any,
    choices: frozenset[str] | tuple[str, ...],
    file_name: str,
    record: str,
    field: str,
) -> str:
    text = _string(value, file_name, record, field)
    if text not in choices:
        _error(
            file_name,
            record,
            field,
            f"unsupported value {text!r}; allowed: {', '.join(sorted(choices))}",
        )
    return text


def _string_list(
    value: Any,
    file_name: str,
    record: str,
    field: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    raw_items = _list(value, file_name, record, field)
    if not allow_empty and not raw_items:
        _error(file_name, record, field, "must not be empty")
    items = tuple(
        _string(item, file_name, record, f"{field}[{index}]")
        for index, item in enumerate(raw_items)
    )
    if len(items) != len(set(items)):
        _error(file_name, record, field, "must not contain duplicates")
    return items


def _meta(
    root: dict[str, Any], file_name: str
) -> tuple[str, str, date]:
    record = "meta"
    raw = _mapping(_required(root, "meta", file_name, "$"), file_name, "$", "meta")
    name = _string(_required(raw, "dataset", file_name, record), file_name, record, "dataset")
    version = _string(
        _required(raw, "version", file_name, record), file_name, record, "version"
    )
    as_of_date = _date(
        _required(raw, "as_of_date", file_name, record),
        file_name,
        record,
        "as_of_date",
    )
    return name, version, as_of_date


def _load_skills(
    dataset_path: Path,
) -> tuple[
    tuple[str, str, date],
    dict[int, str],
    dict[str, Skill],
    dict[tuple[str, str], RoleProfile],
]:
    file_name = "skills.json"
    root = _read_json(dataset_path, file_name)
    meta = _meta(root, file_name)

    raw_scale = _mapping(
        _required(root, "proficiency_scale", file_name, "$"),
        file_name,
        "$",
        "proficiency_scale",
    )
    scale: dict[int, str] = {}
    for raw_level, raw_description in raw_scale.items():
        try:
            level = int(raw_level)
        except (TypeError, ValueError):
            _error(
                file_name,
                "proficiency_scale",
                str(raw_level),
                "level key must be an integer",
            )
        if str(level) != str(raw_level):
            _error(
                file_name,
                "proficiency_scale",
                str(raw_level),
                "level key must use canonical integer form",
            )
        if level in scale:
            _error(
                file_name,
                "proficiency_scale",
                str(raw_level),
                "duplicate numeric level",
            )
        scale[level] = _string(
            raw_description,
            file_name,
            "proficiency_scale",
            str(raw_level),
        )
    if not scale or 0 not in scale:
        _error(
            file_name,
            "proficiency_scale",
            "proficiency_scale",
            "must contain level 0",
        )
    expected_levels = list(range(0, max(scale) + 1))
    if sorted(scale) != expected_levels:
        _error(
            file_name,
            "proficiency_scale",
            "proficiency_scale",
            "levels must be contiguous from 0",
        )

    raw_skills = _list(
        _required(root, "skills", file_name, "$"), file_name, "$", "skills"
    )
    skills: dict[str, Skill] = {}
    for index, raw_value in enumerate(raw_skills):
        record = f"skills[{index}]"
        raw = _mapping(raw_value, file_name, record, record)
        skill_id = _string(
            _required(raw, "skill_id", file_name, record),
            file_name,
            record,
            "skill_id",
        )
        record = f"skill {skill_id}"
        if skill_id in skills:
            _error(file_name, record, "skill_id", "duplicate ID")
        skills[skill_id] = Skill(
            skill_id=skill_id,
            name=_string(
                _required(raw, "name", file_name, record),
                file_name,
                record,
                "name",
            ),
            skill_type=_choice(
                _required(raw, "type", file_name, record),
                SKILL_TYPES,
                file_name,
                record,
                "type",
            ),
            category=_string(
                _required(raw, "category", file_name, record),
                file_name,
                record,
                "category",
            ),
            description=_string(
                _required(raw, "description", file_name, record),
                file_name,
                record,
                "description",
                allow_empty=True,
            ),
        )
    if not skills:
        _error(file_name, "$", "skills", "must contain at least one skill")

    raw_profiles = _list(
        _required(root, "role_profiles", file_name, "$"),
        file_name,
        "$",
        "role_profiles",
    )
    profiles: dict[tuple[str, str], RoleProfile] = {}
    for index, raw_value in enumerate(raw_profiles):
        initial_record = f"role_profiles[{index}]"
        raw = _mapping(raw_value, file_name, initial_record, initial_record)
        role = _string(
            _required(raw, "role", file_name, initial_record),
            file_name,
            initial_record,
            "role",
        )
        grade = _choice(
            _required(raw, "grade", file_name, initial_record),
            GRADE_ORDER,
            file_name,
            initial_record,
            "grade",
        )
        record = f"role_profile {role}/{grade}"
        key = (role, grade)
        if key in profiles:
            _error(file_name, record, "role+grade", "duplicate role profile")

        raw_requirements = _mapping(
            _required(raw, "required_skills", file_name, record),
            file_name,
            record,
            "required_skills",
        )
        requirements: dict[str, int] = {}
        for skill_id, raw_level in raw_requirements.items():
            if skill_id not in skills:
                _error(
                    file_name,
                    record,
                    f"required_skills.{skill_id}",
                    "unknown skill reference",
                )
            level = _integer(
                raw_level,
                file_name,
                record,
                f"required_skills.{skill_id}",
            )
            if level not in scale:
                _error(
                    file_name,
                    record,
                    f"required_skills.{skill_id}",
                    f"level {level} is outside the proficiency scale",
                )
            requirements[skill_id] = level

        critical = frozenset(
            _string_list(
                _required(raw, "critical_skills", file_name, record),
                file_name,
                record,
                "critical_skills",
                allow_empty=True,
            )
        )
        for skill_id in critical:
            if skill_id not in requirements:
                _error(
                    file_name,
                    record,
                    "critical_skills",
                    f"{skill_id} must also be present in required_skills",
                )
        profiles[key] = RoleProfile(
            role=role,
            grade=grade,
            required_skills=requirements,
            critical_skills=critical,
        )
    if not profiles:
        _error(file_name, "$", "role_profiles", "must contain at least one profile")

    return meta, scale, skills, profiles


def _load_employees(
    dataset_path: Path,
    scale: dict[int, str],
    skills: dict[str, Skill],
    profiles: dict[tuple[str, str], RoleProfile],
) -> tuple[tuple[str, str, date], dict[str, Employee]]:
    file_name = "employees.json"
    root = _read_json(dataset_path, file_name)
    meta = _meta(root, file_name)
    as_of_date = meta[2]
    raw_employees = _list(
        _required(root, "employees", file_name, "$"),
        file_name,
        "$",
        "employees",
    )
    employees: dict[str, Employee] = {}

    for index, raw_value in enumerate(raw_employees):
        initial_record = f"employees[{index}]"
        raw = _mapping(raw_value, file_name, initial_record, initial_record)
        employee_id = _string(
            _required(raw, "employee_id", file_name, initial_record),
            file_name,
            initial_record,
            "employee_id",
        )
        record = f"employee {employee_id}"
        if employee_id in employees:
            _error(file_name, record, "employee_id", "duplicate ID")

        role = _string(
            _required(raw, "role", file_name, record), file_name, record, "role"
        )
        grade = _choice(
            _required(raw, "grade", file_name, record),
            GRADE_ORDER,
            file_name,
            record,
            "grade",
        )
        if (role, grade) not in profiles:
            _error(
                file_name,
                record,
                "role+grade",
                "no matching role profile",
            )

        manager_raw = _required(raw, "manager_id", file_name, record)
        manager_id = (
            None
            if manager_raw is None
            else _string(manager_raw, file_name, record, "manager_id")
        )

        goal_raw = _required(raw, "career_goal", file_name, record)
        career_goal: CareerGoal | None = None
        if goal_raw is not None:
            goal_mapping = _mapping(
                goal_raw, file_name, record, "career_goal"
            )
            target_role = _string(
                _required(goal_mapping, "target_role", file_name, record),
                file_name,
                record,
                "career_goal.target_role",
            )
            target_grade = _choice(
                _required(goal_mapping, "target_grade", file_name, record),
                GRADE_ORDER,
                file_name,
                record,
                "career_goal.target_grade",
            )
            if (target_role, target_grade) not in profiles:
                _error(
                    file_name,
                    record,
                    "career_goal",
                    "no matching target role profile",
                )
            career_goal = CareerGoal(target_role, target_grade)

        raw_levels = _mapping(
            _required(raw, "skills", file_name, record),
            file_name,
            record,
            "skills",
        )
        levels: dict[str, int] = {}
        for skill_id, raw_level in raw_levels.items():
            if skill_id not in skills:
                _error(
                    file_name,
                    record,
                    f"skills.{skill_id}",
                    "unknown skill reference",
                )
            level = _integer(
                raw_level, file_name, record, f"skills.{skill_id}"
            )
            if level not in scale:
                _error(
                    file_name,
                    record,
                    f"skills.{skill_id}",
                    f"level {level} is outside the proficiency scale",
                )
            levels[skill_id] = level

        hire_date = _date(
            _required(raw, "hire_date", file_name, record),
            file_name,
            record,
            "hire_date",
        )
        review_date = _date(
            _required(raw, "last_review_date", file_name, record),
            file_name,
            record,
            "last_review_date",
        )
        if hire_date > as_of_date:
            _error(
                file_name,
                record,
                "hire_date",
                "must not be after meta.as_of_date",
            )
        if review_date > as_of_date:
            _error(
                file_name,
                record,
                "last_review_date",
                "must not be after meta.as_of_date",
            )
        if review_date < hire_date:
            _error(
                file_name,
                record,
                "last_review_date",
                "must not be before hire_date",
            )

        tenure = _integer(
            _required(raw, "tenure_months", file_name, record),
            file_name,
            record,
            "tenure_months",
        )
        if tenure < 0:
            _error(
                file_name, record, "tenure_months", "must be non-negative"
            )

        employees[employee_id] = Employee(
            employee_id=employee_id,
            full_name=_string(
                _required(raw, "full_name", file_name, record),
                file_name,
                record,
                "full_name",
            ),
            department=_string(
                _required(raw, "department", file_name, record),
                file_name,
                record,
                "department",
            ),
            role=role,
            grade=grade,
            manager_id=manager_id,
            hire_date=hire_date,
            tenure_months=tenure,
            work_format=_choice(
                _required(raw, "work_format", file_name, record),
                WORK_FORMATS,
                file_name,
                record,
                "work_format",
            ),
            preferred_language=_choice(
                _required(raw, "preferred_language", file_name, record),
                LANGUAGES,
                file_name,
                record,
                "preferred_language",
            ),
            career_goal=career_goal,
            skills=levels,
            last_review_date=review_date,
        )

    for employee in employees.values():
        if employee.manager_id is not None:
            if employee.manager_id == employee.employee_id:
                _error(
                    file_name,
                    f"employee {employee.employee_id}",
                    "manager_id",
                    "employee cannot manage themselves",
                )
            if employee.manager_id not in employees:
                _error(
                    file_name,
                    f"employee {employee.employee_id}",
                    "manager_id",
                    f"unknown employee reference {employee.manager_id}",
                )
    return meta, employees


def _load_events(
    dataset_path: Path,
    scale: dict[int, str],
    skills: dict[str, Skill],
    profiles: dict[tuple[str, str], RoleProfile],
) -> tuple[tuple[str, str, date], dict[str, Event]]:
    file_name = "events.json"
    root = _read_json(dataset_path, file_name)
    meta = _meta(root, file_name)
    raw_events = _list(
        _required(root, "events", file_name, "$"), file_name, "$", "events"
    )
    known_roles = {role for role, _ in profiles}
    events: dict[str, Event] = {}

    for index, raw_value in enumerate(raw_events):
        initial_record = f"events[{index}]"
        raw = _mapping(raw_value, file_name, initial_record, initial_record)
        event_id = _string(
            _required(raw, "event_id", file_name, initial_record),
            file_name,
            initial_record,
            "event_id",
        )
        record = f"event {event_id}"
        if event_id in events:
            _error(file_name, record, "event_id", "duplicate ID")

        target_roles = _string_list(
            _required(raw, "target_roles", file_name, record),
            file_name,
            record,
            "target_roles",
        )
        for role in target_roles:
            if role not in known_roles:
                _error(
                    file_name,
                    record,
                    "target_roles",
                    f"unknown role {role!r}",
                )
        target_grades = _string_list(
            _required(raw, "target_grades", file_name, record),
            file_name,
            record,
            "target_grades",
        )
        for grade in target_grades:
            if grade not in GRADE_ORDER:
                _error(
                    file_name,
                    record,
                    "target_grades",
                    f"unsupported grade {grade!r}",
                )

        raw_effects = _list(
            _required(raw, "develops_skills", file_name, record),
            file_name,
            record,
            "develops_skills",
        )
        effects: list[SkillEffect] = []
        effect_ids: set[str] = set()
        for effect_index, raw_effect in enumerate(raw_effects):
            field = f"develops_skills[{effect_index}]"
            effect = _mapping(raw_effect, file_name, record, field)
            skill_id = _string(
                _required(effect, "skill_id", file_name, record),
                file_name,
                record,
                f"{field}.skill_id",
            )
            if skill_id not in skills:
                _error(
                    file_name,
                    record,
                    f"{field}.skill_id",
                    "unknown skill reference",
                )
            if skill_id in effect_ids:
                _error(
                    file_name,
                    record,
                    "develops_skills",
                    f"duplicate skill effect {skill_id}",
                )
            effect_ids.add(skill_id)
            gain = _integer(
                _required(effect, "gain", file_name, record),
                file_name,
                record,
                f"{field}.gain",
            )
            if gain <= 0:
                _error(
                    file_name, record, f"{field}.gain", "must be positive"
                )
            max_level = _integer(
                _required(effect, "max_level", file_name, record),
                file_name,
                record,
                f"{field}.max_level",
            )
            if max_level not in scale:
                _error(
                    file_name,
                    record,
                    f"{field}.max_level",
                    f"level {max_level} is outside the proficiency scale",
                )
            effects.append(SkillEffect(skill_id, gain, max_level))

        raw_prerequisites = _mapping(
            _required(raw, "prerequisites", file_name, record),
            file_name,
            record,
            "prerequisites",
        )
        prerequisites: dict[str, int] = {}
        for skill_id, raw_level in raw_prerequisites.items():
            if skill_id not in skills:
                _error(
                    file_name,
                    record,
                    f"prerequisites.{skill_id}",
                    "unknown skill reference",
                )
            level = _integer(
                raw_level,
                file_name,
                record,
                f"prerequisites.{skill_id}",
            )
            if level not in scale:
                _error(
                    file_name,
                    record,
                    f"prerequisites.{skill_id}",
                    f"level {level} is outside the proficiency scale",
                )
            prerequisites[skill_id] = level

        raw_sessions = _list(
            _required(raw, "upcoming_sessions", file_name, record),
            file_name,
            record,
            "upcoming_sessions",
        )
        sessions = tuple(
            _date(
                raw_session,
                file_name,
                record,
                f"upcoming_sessions[{session_index}]",
            )
            for session_index, raw_session in enumerate(raw_sessions)
        )
        duration = _number(
            _required(raw, "duration_hours", file_name, record),
            file_name,
            record,
            "duration_hours",
        )
        if duration <= 0:
            _error(
                file_name, record, "duration_hours", "must be positive"
            )

        events[event_id] = Event(
            event_id=event_id,
            title=_string(
                _required(raw, "title", file_name, record),
                file_name,
                record,
                "title",
            ),
            description=_string(
                _required(raw, "description", file_name, record),
                file_name,
                record,
                "description",
                allow_empty=True,
            ),
            event_type=_choice(
                _required(raw, "type", file_name, record),
                EVENT_TYPES,
                file_name,
                record,
                "type",
            ),
            event_format=_choice(
                _required(raw, "format", file_name, record),
                EVENT_FORMATS,
                file_name,
                record,
                "format",
            ),
            duration_hours=duration,
            mandatory=_boolean(
                _required(raw, "mandatory", file_name, record),
                file_name,
                record,
                "mandatory",
            ),
            target_roles=target_roles,
            target_grades=target_grades,
            develops_skills=tuple(effects),
            prerequisites=prerequisites,
            upcoming_sessions=sessions,
        )
    return meta, events


def _csv_required(
    row: dict[str | None, str | list[str]],
    field: str,
    file_name: str,
    record: str,
) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        _error(file_name, record, field, "required value is missing")
    return value


def _csv_optional(
    row: dict[str | None, str | list[str]], field: str
) -> str | None:
    value = row.get(field)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return None
    return value


def _csv_int(
    value: str,
    file_name: str,
    record: str,
    field: str,
) -> int:
    try:
        return int(value)
    except ValueError:
        _error(file_name, record, field, "must be an integer")


def _csv_date(
    value: str, file_name: str, record: str, field: str
) -> date:
    if (
        len(value) != 10
        or value[4] != "-"
        or value[7] != "-"
        or not (value[:4] + value[5:7] + value[8:]).isdigit()
    ):
        _error(file_name, record, field, "must be an ISO date (YYYY-MM-DD)")
    try:
        return date.fromisoformat(value)
    except ValueError:
        _error(file_name, record, field, "must be an ISO date (YYYY-MM-DD)")


def _load_history(
    dataset_path: Path,
    employees: dict[str, Employee],
    events: dict[str, Event],
) -> tuple[HistoryRecord, ...]:
    file_name = "activity_history.csv"
    path = dataset_path / file_name
    required_columns = (
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
    )
    try:
        source = path.open(encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        _error(file_name, "$", "file", f"file not found under {dataset_path}")
    except OSError as exc:
        _error(file_name, "$", "file", str(exc))

    records: list[HistoryRecord] = []
    seen_ids: set[str] = set()
    with source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            _error(file_name, "header", "columns", "CSV header is missing")
        missing = [column for column in required_columns if column not in reader.fieldnames]
        if missing:
            _error(
                file_name,
                "header",
                "columns",
                f"required columns are missing: {', '.join(missing)}",
            )

        for row_number, row in enumerate(reader, start=2):
            record_id = _csv_required(
                row, "record_id", file_name, f"row {row_number}"
            )
            record = f"row {row_number} ({record_id})"
            if None in row:
                _error(
                    file_name,
                    record,
                    "columns",
                    "row has more values than the header",
                )
            if record_id in seen_ids:
                _error(file_name, record, "record_id", "duplicate ID")
            seen_ids.add(record_id)

            employee_id = _csv_required(
                row, "employee_id", file_name, record
            )
            event_id = _csv_required(row, "event_id", file_name, record)
            if employee_id not in employees:
                _error(
                    file_name,
                    record,
                    "employee_id",
                    f"unknown employee reference {employee_id}",
                )
            if event_id not in events:
                _error(
                    file_name,
                    record,
                    "event_id",
                    f"unknown event reference {event_id}",
                )

            activity_date = _csv_date(
                _csv_required(row, "date", file_name, record),
                file_name,
                record,
                "date",
            )
            due_raw = _csv_optional(row, "due_date")
            due_date = (
                None
                if due_raw is None
                else _csv_date(due_raw, file_name, record, "due_date")
            )
            if due_date is not None and due_date < activity_date:
                _error(
                    file_name,
                    record,
                    "due_date",
                    "must not be before date",
                )

            status = _csv_required(row, "status", file_name, record)
            if status not in HISTORY_STATUSES:
                _error(
                    file_name,
                    record,
                    "status",
                    f"unsupported value {status!r}; allowed: "
                    + ", ".join(HISTORY_STATUSES),
                )
            completion_pct = _csv_int(
                _csv_required(row, "completion_pct", file_name, record),
                file_name,
                record,
                "completion_pct",
            )
            if not 0 <= completion_pct <= 100:
                _error(
                    file_name,
                    record,
                    "completion_pct",
                    "must be between 0 and 100",
                )
            if status == "completed" and completion_pct != 100:
                _error(
                    file_name,
                    record,
                    "completion_pct",
                    "completed status requires 100",
                )
            if status in {"no_show", "declined"} and completion_pct != 0:
                _error(
                    file_name,
                    record,
                    "completion_pct",
                    f"{status} status requires 0",
                )
            if status == "dropped" and not 5 <= completion_pct <= 95:
                _error(
                    file_name,
                    record,
                    "completion_pct",
                    "dropped status requires a value from 5 to 95",
                )
            if status in {"in_progress", "overdue"} and completion_pct > 95:
                _error(
                    file_name,
                    record,
                    "completion_pct",
                    f"{status} status requires a value from 0 to 95",
                )

            score_raw = _csv_optional(row, "score")
            score = (
                None
                if score_raw is None
                else _csv_int(score_raw, file_name, record, "score")
            )
            if score is not None and not 0 <= score <= 100:
                _error(
                    file_name, record, "score", "must be between 0 and 100"
                )

            rating_raw = _csv_optional(row, "feedback_rating")
            feedback_rating = (
                None
                if rating_raw is None
                else _csv_int(
                    rating_raw, file_name, record, "feedback_rating"
                )
            )
            if feedback_rating is not None and not 1 <= feedback_rating <= 5:
                _error(
                    file_name,
                    record,
                    "feedback_rating",
                    "must be between 1 and 5",
                )

            assigned_by = _csv_required(
                row, "assigned_by", file_name, record
            )
            if assigned_by not in ASSIGNED_BY_VALUES:
                _error(
                    file_name,
                    record,
                    "assigned_by",
                    f"unsupported value {assigned_by!r}; allowed: "
                    + ", ".join(sorted(ASSIGNED_BY_VALUES)),
                )

            records.append(
                HistoryRecord(
                    record_id=record_id,
                    employee_id=employee_id,
                    event_id=event_id,
                    activity_date=activity_date,
                    due_date=due_date,
                    status=status,
                    completion_pct=completion_pct,
                    score=score,
                    feedback_rating=feedback_rating,
                    assigned_by=assigned_by,
                    source_row=row_number,
                )
            )
    return tuple(records)


def load_dataset(dataset_path: str | Path) -> Dataset:
    path = Path(dataset_path).expanduser()
    if not path.is_dir():
        _error(
            str(path),
            "$",
            "dataset_path",
            "path does not exist or is not a directory",
        )

    skills_meta, scale, skills, profiles = _load_skills(path)
    employees_meta, employees = _load_employees(path, scale, skills, profiles)
    events_meta, events = _load_events(path, scale, skills, profiles)

    for file_name, meta in (
        ("employees.json", employees_meta),
        ("events.json", events_meta),
    ):
        if meta != skills_meta:
            _error(
                file_name,
                "meta",
                "meta",
                "dataset, version, and as_of_date must match skills.json",
            )

    try:
        history = _load_history(path, employees, events)
    except UnicodeDecodeError as exc:
        _error(
            "activity_history.csv",
            "$",
            "encoding",
            f"invalid UTF-8: {exc}",
        )
    except csv.Error as exc:
        _error("activity_history.csv", "$", "csv", str(exc))
    name, version, as_of_date = skills_meta
    return Dataset(
        name=name,
        version=version,
        as_of_date=as_of_date,
        proficiency_scale=scale,
        skills=skills,
        role_profiles=profiles,
        employees=employees,
        events=events,
        history=history,
    )
