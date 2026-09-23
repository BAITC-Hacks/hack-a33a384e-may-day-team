from __future__ import annotations

from collections import Counter

from .models import (
    GRADE_ORDER,
    HISTORY_STATUSES,
    NEGATIVE_PARTICIPATION_STATUSES,
    REPEATABLE_EVENT_IDS,
    CandidateAnalysis,
    CandidateFact,
    CareerTarget,
    CurrentSkills,
    Dataset,
    Employee,
    EmployeeDiagnostic,
    ExcludedEvent,
    ExclusionReason,
    ParticipationFacts,
    PotentialSkillChange,
    RequirementCheck,
    SkillChangeTrace,
    SkillGap,
)


class EmployeeNotFoundError(LookupError):
    pass


def _employee(dataset: Dataset, employee_id: str) -> Employee:
    try:
        return dataset.employees[employee_id]
    except KeyError as exc:
        raise EmployeeNotFoundError(
            f"employee_id {employee_id!r} is not present in the dataset"
        ) from exc


def assessed_skill_levels(dataset: Dataset, employee_id: str) -> dict[str, int]:
    employee = _employee(dataset, employee_id)
    levels = {skill_id: 0 for skill_id in dataset.skills}
    levels.update(employee.skills)
    return levels


def calculate_current_skills(
    dataset: Dataset, employee_id: str
) -> CurrentSkills:
    employee = _employee(dataset, employee_id)
    levels = assessed_skill_levels(dataset, employee_id)
    trace: list[SkillChangeTrace] = []

    applicable_records = sorted(
        (
            record
            for record in dataset.history
            if record.employee_id == employee_id
            and record.status == "completed"
            and employee.last_review_date
            < record.activity_date
            <= dataset.as_of_date
        ),
        key=lambda record: (record.activity_date, record.source_row),
    )

    for record in applicable_records:
        event = dataset.events[record.event_id]
        for effect in event.develops_skills:
            current = levels[effect.skill_id]
            delta = max(0, min(effect.gain, effect.max_level - current))
            if delta == 0:
                continue
            new_level = current + delta
            levels[effect.skill_id] = new_level
            trace.append(
                SkillChangeTrace(
                    record_id=record.record_id,
                    event_id=record.event_id,
                    activity_date=record.activity_date,
                    skill_id=effect.skill_id,
                    level_before=current,
                    gain=effect.gain,
                    max_level=effect.max_level,
                    delta=delta,
                    level_after=new_level,
                )
            )

    return CurrentSkills(levels=levels, trace=tuple(trace))


def primary_target(dataset: Dataset, employee_id: str) -> CareerTarget | None:
    employee = _employee(dataset, employee_id)
    grade_index = GRADE_ORDER.index(employee.grade)
    if grade_index == len(GRADE_ORDER) - 1:
        return None
    target = CareerTarget(employee.role, GRADE_ORDER[grade_index + 1])
    if (target.role, target.grade) not in dataset.role_profiles:
        return None
    return target


def target_gaps(
    dataset: Dataset,
    target: CareerTarget,
    current_skills: dict[str, int],
) -> tuple[SkillGap, ...]:
    profile = dataset.role_profiles[(target.role, target.grade)]
    return tuple(
        SkillGap(
            skill_id=skill_id,
            current_level=current_skills.get(skill_id, 0),
            required_level=required_level,
            missing_level=max(
                required_level - current_skills.get(skill_id, 0), 0
            ),
            critical=skill_id in profile.critical_skills,
        )
        for skill_id, required_level in profile.required_skills.items()
    )


def _participation_facts(
    dataset: Dataset,
    employee_id: str,
    event_id: str,
    related_skill_ids: tuple[str, ...],
) -> ParticipationFacts:
    visible_history = (
        record
        for record in dataset.history
        if record.employee_id == employee_id
        and record.activity_date <= dataset.as_of_date
    )
    records = tuple(visible_history)
    event_counts = Counter(
        record.status for record in records if record.event_id == event_id
    )

    related_counts: dict[str, dict[str, int]] = {}
    for skill_id in related_skill_ids:
        counts = Counter(
            record.status
            for record in records
            if skill_id
            in {
                effect.skill_id
                for effect in dataset.events[record.event_id].develops_skills
            }
            and record.status in NEGATIVE_PARTICIPATION_STATUSES
        )
        related_counts[skill_id] = {
            status: counts[status]
            for status in NEGATIVE_PARTICIPATION_STATUSES
        }

    return ParticipationFacts(
        event_status_counts={
            status: event_counts[status] for status in HISTORY_STATUSES
        },
        related_skill_negative_status_counts=related_counts,
    )


def analyze_candidates(
    dataset: Dataset,
    employee_id: str,
    current_skills: dict[str, int] | None = None,
) -> CandidateAnalysis:
    employee = _employee(dataset, employee_id)
    levels = (
        calculate_current_skills(dataset, employee_id).levels
        if current_skills is None
        else dict(current_skills)
    )
    target = primary_target(dataset, employee_id)

    if target is None:
        exclusions = tuple(
            ExcludedEvent(
                event_id=event.event_id,
                title=event.title,
                reasons=(ExclusionReason("no_next_grade_in_catalog"),),
            )
            for event in dataset.events.values()
        )
        return CandidateAnalysis("no_next_grade", (), exclusions)

    gaps = target_gaps(dataset, target, levels)
    if all(gap.missing_level == 0 for gap in gaps):
        exclusions = tuple(
            ExcludedEvent(
                event_id=event.event_id,
                title=event.title,
                reasons=(ExclusionReason("target_requirements_already_met"),),
            )
            for event in dataset.events.values()
        )
        return CandidateAnalysis(
            "requirements_already_met", (), exclusions
        )

    target_profile = dataset.role_profiles[(target.role, target.grade)]
    gap_by_skill = {gap.skill_id: gap for gap in gaps}
    employee_history = tuple(
        record
        for record in dataset.history
        if record.employee_id == employee_id
        and record.activity_date <= dataset.as_of_date
    )
    candidates: list[CandidateFact] = []
    exclusions: list[ExcludedEvent] = []

    for event in dataset.events.values():
        reasons: list[ExclusionReason] = []
        if event.mandatory:
            reasons.append(ExclusionReason("mandatory"))
        if employee.role not in event.target_roles:
            reasons.append(
                ExclusionReason(
                    "role_not_in_target_audience",
                    {"current_role": employee.role},
                )
            )
        if employee.grade not in event.target_grades:
            reasons.append(
                ExclusionReason(
                    "grade_not_in_target_audience",
                    {"current_grade": employee.grade},
                )
            )

        prerequisite_checks = tuple(
            RequirementCheck(
                skill_id=skill_id,
                current_level=levels.get(skill_id, 0),
                required_level=required_level,
                met=levels.get(skill_id, 0) >= required_level,
            )
            for skill_id, required_level in event.prerequisites.items()
        )
        unmet = tuple(
            check for check in prerequisite_checks if not check.met
        )
        if unmet:
            reasons.append(
                ExclusionReason(
                    "unmet_prerequisites",
                    [
                        {
                            "skill_id": check.skill_id,
                            "current_level": check.current_level,
                            "required_level": check.required_level,
                        }
                        for check in unmet
                    ],
                )
            )

        event_history = tuple(
            record
            for record in employee_history
            if record.event_id == event.event_id
        )
        if any(record.status == "in_progress" for record in event_history):
            reasons.append(ExclusionReason("already_in_progress"))
        if (
            event.event_id not in REPEATABLE_EVENT_IDS
            and any(record.status == "completed" for record in event_history)
        ):
            reasons.append(ExclusionReason("already_completed"))

        has_available_session = event.event_format == "self_paced" or any(
            session >= dataset.as_of_date
            for session in event.upcoming_sessions
        )
        if not has_available_session:
            reasons.append(ExclusionReason("no_available_session"))

        potential_changes: list[PotentialSkillChange] = []
        useful_gap_ids: set[str] = set()
        for effect in event.develops_skills:
            current = levels.get(effect.skill_id, 0)
            delta = max(0, min(effect.gain, effect.max_level - current))
            new_level = current + delta
            required = target_profile.required_skills.get(effect.skill_id)
            gap_before = (
                max(required - current, 0) if required is not None else 0
            )
            gap_after = (
                max(required - new_level, 0) if required is not None else 0
            )
            if gap_after < gap_before:
                useful_gap_ids.add(effect.skill_id)
            potential_changes.append(
                PotentialSkillChange(
                    skill_id=effect.skill_id,
                    current_level=current,
                    gain=effect.gain,
                    max_level=effect.max_level,
                    delta=delta,
                    new_level=new_level,
                    target_required_level=required,
                    target_gap_before=gap_before,
                    target_gap_after=gap_after,
                )
            )
        if not useful_gap_ids:
            reasons.append(ExclusionReason("no_positive_target_gap_effect"))

        if reasons:
            exclusions.append(
                ExcludedEvent(
                    event_id=event.event_id,
                    title=event.title,
                    reasons=tuple(reasons),
                )
            )
            continue

        useful_gaps = tuple(
            gap
            for gap in gaps
            if gap.skill_id in useful_gap_ids and gap.missing_level > 0
        )
        candidates.append(
            CandidateFact(
                event_id=event.event_id,
                title=event.title,
                target=target,
                gaps=useful_gaps,
                critical_gaps=tuple(
                    gap for gap in useful_gaps if gap.critical
                ),
                prerequisites=prerequisite_checks,
                potential_skill_changes=tuple(potential_changes),
                participation=_participation_facts(
                    dataset,
                    employee_id,
                    event.event_id,
                    tuple(
                        effect.skill_id
                        for effect in event.develops_skills
                    ),
                ),
            )
        )

    status = (
        "candidates_available"
        if candidates
        else "no_suitable_available_events"
    )
    return CandidateAnalysis(status, tuple(candidates), tuple(exclusions))


def employee_diagnostic(
    dataset: Dataset, employee_id: str
) -> EmployeeDiagnostic:
    employee = _employee(dataset, employee_id)
    assessed = assessed_skill_levels(dataset, employee_id)
    current = calculate_current_skills(dataset, employee_id)
    target = primary_target(dataset, employee_id)
    gaps = (
        ()
        if target is None
        else target_gaps(dataset, target, current.levels)
    )
    candidates = analyze_candidates(dataset, employee_id, current.levels)
    return EmployeeDiagnostic(
        employee_id=employee.employee_id,
        as_of_date=dataset.as_of_date,
        assessed_at=employee.last_review_date,
        assessed_skills=assessed,
        current_skills=current.levels,
        skill_change_trace=current.trace,
        primary_target=target,
        career_goal=employee.career_goal,
        career_goal_changes_primary_target=False,
        requirements=gaps,
        requirements_met=target is not None
        and all(gap.missing_level == 0 for gap in gaps),
        candidate_status=candidates.status,
        candidates=candidates.candidates,
        exclusions=candidates.exclusions,
    )


def audit_dataset(dataset: Dataset) -> dict[str, object]:
    status_counts = Counter(record.status for record in dataset.history)
    dates = [record.activity_date for record in dataset.history]
    eligible_completed_records = sum(
        1
        for record in dataset.history
        if record.status == "completed"
        and dataset.employees[record.employee_id].last_review_date
        < record.activity_date
        <= dataset.as_of_date
    )

    total_gain = 0
    trace_entries = 0
    employees_with_growth = 0
    for employee_id in dataset.employees:
        current = calculate_current_skills(dataset, employee_id)
        if current.trace:
            employees_with_growth += 1
        trace_entries += len(current.trace)
        total_gain += sum(change.delta for change in current.trace)

    return {
        "as_of_date": dataset.as_of_date,
        "counts": {
            "skills": len(dataset.skills),
            "role_profiles": len(dataset.role_profiles),
            "employees": len(dataset.employees),
            "events": len(dataset.events),
            "history_records": len(dataset.history),
        },
        "history_window": {
            "from": min(dates) if dates else None,
            "through": max(dates) if dates else None,
        },
        "history_status_counts": {
            status: status_counts[status] for status in HISTORY_STATUSES
        },
        "recalculated_growth": {
            "completed_records_after_review_through_as_of": (
                eligible_completed_records
            ),
            "employees_with_positive_growth": employees_with_growth,
            "positive_skill_change_trace_entries": trace_entries,
            "total_skill_level_gain": total_gain,
        },
    }
