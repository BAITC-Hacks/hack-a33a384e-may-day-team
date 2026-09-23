from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest


META = {
    "dataset": "Synthetic Career Fixture",
    "version": "test-1",
    "as_of_date": "2026-01-20",
}


def _event(
    event_id: str,
    skill_id: str,
    *,
    gain: int = 1,
    max_level: int = 5,
    mandatory: bool = False,
    prerequisites: dict[str, int] | None = None,
    event_format: str = "self_paced",
    sessions: list[str] | None = None,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "title": f"Synthetic activity {event_id}",
        "description": "Fictional test-only activity.",
        "type": "course",
        "format": event_format,
        "duration_hours": 2,
        "mandatory": mandatory,
        "target_roles": ["Engineer", "Designer"],
        "target_grades": ["Junior", "Middle", "Senior", "Lead"],
        "develops_skills": [
            {"skill_id": skill_id, "gain": gain, "max_level": max_level}
        ],
        "prerequisites": prerequisites or {},
        "upcoming_sessions": sessions or [],
    }


def _history(
    record_id: str,
    employee_id: str,
    event_id: str,
    activity_date: str,
    status: str,
    completion_pct: int,
) -> dict[str, object]:
    return {
        "record_id": record_id,
        "employee_id": employee_id,
        "event_id": event_id,
        "date": activity_date,
        "due_date": "",
        "status": status,
        "completion_pct": completion_pct,
        "score": "",
        "feedback_rating": "",
        "assigned_by": "self",
    }


@pytest.fixture
def synthetic_dataset_path(tmp_path: Path) -> Path:
    dataset_path = tmp_path / "synthetic_dataset"
    dataset_path.mkdir()

    skills = [
        {
            "skill_id": skill_id,
            "name": name,
            "type": skill_type,
            "category": category,
            "description": "Synthetic test skill.",
        }
        for skill_id, name, skill_type, category in (
            ("S_CODE", "Coding", "hard", "engineering"),
            ("S_ARCH", "Architecture", "hard", "engineering"),
            ("S_PRESENT", "Presenting", "soft", "communication"),
            ("S_EXPERT", "Expert practice", "hard", "engineering"),
            ("S_CAP", "Capped practice", "hard", "engineering"),
        )
    ]
    profiles: list[dict[str, object]] = []
    engineer_requirements = {
        "Junior": ({"S_CODE": 1}, ["S_CODE"]),
        "Middle": ({"S_CODE": 3, "S_ARCH": 2}, ["S_ARCH"]),
        "Senior": (
            {"S_CODE": 4, "S_ARCH": 3, "S_PRESENT": 2},
            ["S_ARCH"],
        ),
        "Lead": (
            {"S_CODE": 5, "S_ARCH": 4, "S_PRESENT": 3},
            ["S_ARCH"],
        ),
    }
    designer_requirements = {
        "Junior": ({"S_PRESENT": 1}, ["S_PRESENT"]),
        "Middle": ({"S_PRESENT": 2}, ["S_PRESENT"]),
        "Senior": ({"S_PRESENT": 3}, ["S_PRESENT"]),
        "Lead": ({"S_PRESENT": 4}, ["S_PRESENT"]),
    }
    for role, requirements in (
        ("Engineer", engineer_requirements),
        ("Designer", designer_requirements),
    ):
        for grade, (required_skills, critical_skills) in requirements.items():
            profiles.append(
                {
                    "role": role,
                    "grade": grade,
                    "required_skills": required_skills,
                    "critical_skills": critical_skills,
                }
            )

    skills_payload = {
        "meta": META,
        "proficiency_scale": {
            str(level): f"Synthetic level {level}" for level in range(6)
        },
        "skills": skills,
        "role_profiles": profiles,
    }
    employees_payload = {
        "meta": META,
        "employees": [
            {
                "employee_id": "EMP-new-alpha",
                "full_name": "Synthetic Person Alpha",
                "department": "Test Engineering",
                "role": "Engineer",
                "grade": "Junior",
                "manager_id": None,
                "hire_date": "2025-01-01",
                "tenure_months": 12,
                "work_format": "hybrid",
                "preferred_language": "ru",
                "career_goal": {
                    "target_role": "Designer",
                    "target_grade": "Senior",
                },
                "skills": {
                    "S_CODE": 2,
                    "S_EXPERT": 5,
                    "S_CAP": 4,
                },
                "last_review_date": "2026-01-10",
            },
            {
                "employee_id": "LEAD-custom",
                "full_name": "Synthetic Lead",
                "department": "Test Engineering",
                "role": "Engineer",
                "grade": "Lead",
                "manager_id": None,
                "hire_date": "2020-01-01",
                "tenure_months": 72,
                "work_format": "office",
                "preferred_language": "kk",
                "career_goal": None,
                "skills": {"S_CODE": 5, "S_ARCH": 4, "S_PRESENT": 3},
                "last_review_date": "2026-01-10",
            },
            {
                "employee_id": "MET-777",
                "full_name": "Synthetic Ready Person",
                "department": "Test Engineering",
                "role": "Engineer",
                "grade": "Junior",
                "manager_id": None,
                "hire_date": "2024-01-01",
                "tenure_months": 24,
                "work_format": "remote",
                "preferred_language": "en",
                "career_goal": None,
                "skills": {"S_CODE": 3, "S_ARCH": 2},
                "last_review_date": "2026-01-10",
            },
        ],
    }

    events = [
        _event("EV_BEFORE", "S_CODE"),
        _event("EV_ON_REVIEW", "S_ARCH"),
        _event("EV_AFTER", "S_ARCH"),
        _event("EV_FUTURE", "S_ARCH"),
        _event("EV_DROPPED", "S_CODE"),
        _event("EV_HIGH_CAP", "S_EXPERT", max_level=4),
        _event("EV_SCALE_CAP", "S_CAP", gain=3, max_level=5),
        _event("EV_USEFUL", "S_ARCH"),
        _event("EV_MANDATORY", "S_ARCH", mandatory=True),
        _event("EV_PREREQ", "S_ARCH", prerequisites={"S_PRESENT": 2}),
        _event("EV_036", "S_ARCH", max_level=4),
        _event("EV_PROGRESS", "S_ARCH"),
        _event("EV_CAPPED", "S_ARCH", max_level=1),
        _event(
            "EV_NO_SESSION",
            "S_ARCH",
            event_format="online",
            sessions=["2026-01-19"],
        ),
    ]
    events_payload = {"meta": META, "events": events}

    history = [
        _history(
            "R_BEFORE",
            "EMP-new-alpha",
            "EV_BEFORE",
            "2026-01-09",
            "completed",
            100,
        ),
        _history(
            "R_ON_REVIEW",
            "EMP-new-alpha",
            "EV_ON_REVIEW",
            "2026-01-10",
            "completed",
            100,
        ),
        _history(
            "R_AFTER",
            "EMP-new-alpha",
            "EV_AFTER",
            "2026-01-11",
            "completed",
            100,
        ),
        _history(
            "R_FUTURE",
            "EMP-new-alpha",
            "EV_FUTURE",
            "2026-01-21",
            "completed",
            100,
        ),
        _history(
            "R_DROPPED",
            "EMP-new-alpha",
            "EV_DROPPED",
            "2026-01-12",
            "dropped",
            40,
        ),
        _history(
            "R_HIGH_CAP",
            "EMP-new-alpha",
            "EV_HIGH_CAP",
            "2026-01-13",
            "completed",
            100,
        ),
        _history(
            "R_SCALE_CAP",
            "EMP-new-alpha",
            "EV_SCALE_CAP",
            "2026-01-14",
            "completed",
            100,
        ),
        _history(
            "R_REPEATABLE",
            "EMP-new-alpha",
            "EV_036",
            "2026-01-08",
            "completed",
            100,
        ),
        _history(
            "R_PROGRESS",
            "EMP-new-alpha",
            "EV_PROGRESS",
            "2026-01-15",
            "in_progress",
            50,
        ),
        _history(
            "R_NO_SHOW",
            "EMP-new-alpha",
            "EV_USEFUL",
            "2026-01-16",
            "no_show",
            0,
        ),
        _history(
            "R_DECLINED",
            "EMP-new-alpha",
            "EV_USEFUL",
            "2026-01-17",
            "declined",
            0,
        ),
    ]

    for file_name, payload in (
        ("skills.json", skills_payload),
        ("employees.json", employees_payload),
        ("events.json", events_payload),
    ):
        (dataset_path / file_name).write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    with (dataset_path / "activity_history.csv").open(
        "w", encoding="utf-8", newline=""
    ) as target:
        writer = csv.DictWriter(target, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)

    return dataset_path
