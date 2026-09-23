from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

from backend.career_quest.engine import (
    analyze_candidates,
    calculate_current_skills,
    employee_diagnostic,
)
from backend.career_quest.loader import load_dataset
from backend.career_quest.models import SkillEffect


def _reason_codes(analysis: object, event_id: str) -> set[str]:
    exclusions = getattr(analysis, "exclusions")
    excluded = next(item for item in exclusions if item.event_id == event_id)
    return {reason.code for reason in excluded.reasons}


def test_current_skills_use_review_window_and_are_idempotent(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)

    first = calculate_current_skills(dataset, "EMP-new-alpha")
    second = calculate_current_skills(dataset, "EMP-new-alpha")

    assert first == second
    assert first.levels["S_ARCH"] == 1
    assert first.levels["S_CODE"] == 2
    assert first.levels["S_PRESENT"] == 0
    assert first.levels["S_EXPERT"] == 5
    assert first.levels["S_CAP"] == 5
    assert [change.record_id for change in first.trace] == [
        "R_AFTER",
        "R_SCALE_CAP",
    ]
    assert all(
        0 <= level <= dataset.max_skill_level
        for level in first.levels.values()
    )


def test_as_of_boundary_is_inclusive_and_same_day_order_uses_source_rows(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    boundary_history = tuple(
        replace(record, activity_date=dataset.as_of_date)
        if record.record_id == "R_FUTURE"
        else record
        for record in dataset.history
    )
    boundary_result = calculate_current_skills(
        replace(dataset, history=boundary_history), "EMP-new-alpha"
    )
    assert boundary_result.levels["S_ARCH"] == 2
    assert "R_FUTURE" in {
        change.record_id for change in boundary_result.trace
    }

    employee = dataset.employees["EMP-new-alpha"]
    reordered_employee = replace(
        employee, skills={**employee.skills, "S_CAP": 2}
    )
    high = replace(
        next(
            record
            for record in dataset.history
            if record.record_id == "R_HIGH_CAP"
        ),
        activity_date=date(2026, 1, 12),
        source_row=10,
    )
    low = replace(
        next(
            record
            for record in dataset.history
            if record.record_id == "R_SCALE_CAP"
        ),
        activity_date=date(2026, 1, 12),
        source_row=11,
    )
    reordered = replace(
        dataset,
        employees={
            **dataset.employees,
            employee.employee_id: reordered_employee,
        },
        events={
            **dataset.events,
            "EV_HIGH_CAP": replace(
                dataset.events["EV_HIGH_CAP"],
                develops_skills=(SkillEffect("S_CAP", 2, 5),),
            ),
            "EV_SCALE_CAP": replace(
                dataset.events["EV_SCALE_CAP"],
                develops_skills=(SkillEffect("S_CAP", 1, 3),),
            ),
        },
        history=(low, high),
    )
    ordered_result = calculate_current_skills(reordered, "EMP-new-alpha")

    assert ordered_result.levels["S_CAP"] == 4
    assert [change.record_id for change in ordered_result.trace] == [
        "R_HIGH_CAP"
    ]


def test_primary_target_ignores_cross_role_goal_and_marks_critical_gaps(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    diagnostic = employee_diagnostic(dataset, "EMP-new-alpha")
    gaps = {gap.skill_id: gap for gap in diagnostic.requirements}

    assert diagnostic.primary_target is not None
    assert diagnostic.primary_target.role == "Engineer"
    assert diagnostic.primary_target.grade == "Middle"
    assert diagnostic.career_goal is not None
    assert diagnostic.career_goal.target_role == "Designer"
    assert diagnostic.career_goal.target_grade == "Senior"
    assert diagnostic.career_goal_changes_primary_target is False
    assert gaps["S_CODE"].missing_level == 1
    assert gaps["S_CODE"].critical is False
    assert gaps["S_ARCH"].current_level == 1
    assert gaps["S_ARCH"].required_level == 2
    assert gaps["S_ARCH"].missing_level == 1
    assert gaps["S_ARCH"].critical is True


def test_lead_has_no_invented_next_grade(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    diagnostic = employee_diagnostic(dataset, "LEAD-custom")

    assert diagnostic.primary_target is None
    assert diagnostic.candidate_status == "no_next_grade"
    assert diagnostic.candidates == ()


def test_candidate_rules_and_participation_facts(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    analysis = analyze_candidates(dataset, "EMP-new-alpha")
    candidates = {candidate.event_id: candidate for candidate in analysis.candidates}

    assert analysis.status == "candidates_available"
    assert "EV_USEFUL" in candidates
    assert "EV_036" in candidates
    assert "EV_DROPPED" in candidates
    assert candidates["EV_USEFUL"].critical_gaps[0].skill_id == "S_ARCH"
    assert (
        candidates["EV_USEFUL"].participation.event_status_counts["no_show"]
        == 1
    )
    assert (
        candidates["EV_USEFUL"].participation.event_status_counts["declined"]
        == 1
    )
    assert (
        candidates["EV_USEFUL"]
        .participation.related_skill_negative_status_counts["S_ARCH"][
            "no_show"
        ]
        == 1
    )
    assert (
        candidates["EV_USEFUL"]
        .participation.related_skill_negative_status_counts["S_ARCH"][
            "declined"
        ]
        == 1
    )
    assert (
        candidates["EV_DROPPED"].participation.event_status_counts["dropped"]
        == 1
    )
    assert (
        candidates["EV_DROPPED"]
        .participation.related_skill_negative_status_counts["S_CODE"][
            "dropped"
        ]
        == 1
    )

    assert "mandatory" in _reason_codes(analysis, "EV_MANDATORY")
    assert "unmet_prerequisites" in _reason_codes(analysis, "EV_PREREQ")
    assert "already_completed" in _reason_codes(analysis, "EV_AFTER")
    assert "already_in_progress" in _reason_codes(analysis, "EV_PROGRESS")
    assert "no_positive_target_gap_effect" in _reason_codes(
        analysis, "EV_CAPPED"
    )
    assert "no_available_session" in _reason_codes(
        analysis, "EV_NO_SESSION"
    )


def test_current_audience_and_available_scheduled_session_are_checked(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    changed_events = {
        **dataset.events,
        "EV_USEFUL": replace(
            dataset.events["EV_USEFUL"], target_roles=("Designer",)
        ),
        "EV_DROPPED": replace(
            dataset.events["EV_DROPPED"], target_grades=("Middle",)
        ),
        "EV_NO_SESSION": replace(
            dataset.events["EV_NO_SESSION"],
            upcoming_sessions=(dataset.as_of_date,),
        ),
    }

    analysis = analyze_candidates(
        replace(dataset, events=changed_events), "EMP-new-alpha"
    )

    assert "role_not_in_target_audience" in _reason_codes(
        analysis, "EV_USEFUL"
    )
    assert "grade_not_in_target_audience" in _reason_codes(
        analysis, "EV_DROPPED"
    )
    assert "EV_NO_SESSION" in {
        candidate.event_id for candidate in analysis.candidates
    }


def test_no_candidates_returns_reason_without_inventing_activity(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    all_mandatory = replace(
        dataset,
        events={
            event_id: replace(event, mandatory=True)
            for event_id, event in dataset.events.items()
        },
    )

    analysis = analyze_candidates(all_mandatory, "EMP-new-alpha")

    assert analysis.status == "no_suitable_available_events"
    assert analysis.candidates == ()
    assert analysis.exclusions
    assert all(
        any(reason.code == "mandatory" for reason in excluded.reasons)
        for excluded in analysis.exclusions
    )


def test_completed_target_requirements_are_reported_separately(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)

    analysis = analyze_candidates(dataset, "MET-777")

    assert analysis.status == "requirements_already_met"
    assert analysis.candidates == ()


def test_empty_target_requirements_are_consistently_met(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)
    key = ("Engineer", "Middle")
    empty_profile = replace(
        dataset.role_profiles[key],
        required_skills={},
        critical_skills=frozenset(),
    )
    changed = replace(
        dataset,
        role_profiles={**dataset.role_profiles, key: empty_profile},
    )

    diagnostic = employee_diagnostic(changed, "EMP-new-alpha")

    assert diagnostic.requirements == ()
    assert diagnostic.requirements_met is True
    assert diagnostic.candidate_status == "requirements_already_met"
