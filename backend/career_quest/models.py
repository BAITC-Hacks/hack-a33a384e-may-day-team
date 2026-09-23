from __future__ import annotations

from dataclasses import dataclass
from datetime import date


GRADE_ORDER = ("Junior", "Middle", "Senior", "Lead")
HISTORY_STATUSES = (
    "completed",
    "in_progress",
    "dropped",
    "no_show",
    "declined",
    "overdue",
)
NEGATIVE_PARTICIPATION_STATUSES = ("no_show", "declined", "dropped")
REPEATABLE_EVENT_IDS = frozenset({"EV_036"})


@dataclass(frozen=True)
class Skill:
    skill_id: str
    name: str
    skill_type: str
    category: str
    description: str


@dataclass(frozen=True)
class RoleProfile:
    role: str
    grade: str
    required_skills: dict[str, int]
    critical_skills: frozenset[str]


@dataclass(frozen=True)
class CareerGoal:
    target_role: str
    target_grade: str


@dataclass(frozen=True)
class Employee:
    employee_id: str
    full_name: str
    department: str
    role: str
    grade: str
    manager_id: str | None
    hire_date: date
    tenure_months: int
    work_format: str
    preferred_language: str
    career_goal: CareerGoal | None
    skills: dict[str, int]
    last_review_date: date


@dataclass(frozen=True)
class SkillEffect:
    skill_id: str
    gain: int
    max_level: int


@dataclass(frozen=True)
class Event:
    event_id: str
    title: str
    description: str
    event_type: str
    event_format: str
    duration_hours: float
    mandatory: bool
    target_roles: tuple[str, ...]
    target_grades: tuple[str, ...]
    develops_skills: tuple[SkillEffect, ...]
    prerequisites: dict[str, int]
    upcoming_sessions: tuple[date, ...]


@dataclass(frozen=True)
class HistoryRecord:
    record_id: str
    employee_id: str
    event_id: str
    activity_date: date
    due_date: date | None
    status: str
    completion_pct: int
    score: int | None
    feedback_rating: int | None
    assigned_by: str
    source_row: int


@dataclass(frozen=True)
class Dataset:
    name: str
    version: str
    as_of_date: date
    proficiency_scale: dict[int, str]
    skills: dict[str, Skill]
    role_profiles: dict[tuple[str, str], RoleProfile]
    employees: dict[str, Employee]
    events: dict[str, Event]
    history: tuple[HistoryRecord, ...]

    @property
    def min_skill_level(self) -> int:
        return min(self.proficiency_scale)

    @property
    def max_skill_level(self) -> int:
        return max(self.proficiency_scale)


@dataclass(frozen=True)
class SkillChangeTrace:
    record_id: str
    event_id: str
    activity_date: date
    skill_id: str
    level_before: int
    gain: int
    max_level: int
    delta: int
    level_after: int


@dataclass(frozen=True)
class CurrentSkills:
    levels: dict[str, int]
    trace: tuple[SkillChangeTrace, ...]


@dataclass(frozen=True)
class CareerTarget:
    role: str
    grade: str


@dataclass(frozen=True)
class SkillGap:
    skill_id: str
    current_level: int
    required_level: int
    missing_level: int
    critical: bool


@dataclass(frozen=True)
class RequirementCheck:
    skill_id: str
    current_level: int
    required_level: int
    met: bool


@dataclass(frozen=True)
class PotentialSkillChange:
    skill_id: str
    current_level: int
    gain: int
    max_level: int
    delta: int
    new_level: int
    target_required_level: int | None
    target_gap_before: int
    target_gap_after: int


@dataclass(frozen=True)
class ParticipationFacts:
    event_status_counts: dict[str, int]
    related_skill_negative_status_counts: dict[str, dict[str, int]]


@dataclass(frozen=True)
class CandidateFact:
    event_id: str
    title: str
    target: CareerTarget
    gaps: tuple[SkillGap, ...]
    critical_gaps: tuple[SkillGap, ...]
    prerequisites: tuple[RequirementCheck, ...]
    potential_skill_changes: tuple[PotentialSkillChange, ...]
    participation: ParticipationFacts


@dataclass(frozen=True)
class ExclusionReason:
    code: str
    details: object | None = None


@dataclass(frozen=True)
class ExcludedEvent:
    event_id: str
    title: str
    reasons: tuple[ExclusionReason, ...]


@dataclass(frozen=True)
class CandidateAnalysis:
    status: str
    candidates: tuple[CandidateFact, ...]
    exclusions: tuple[ExcludedEvent, ...]


@dataclass(frozen=True)
class EmployeeDiagnostic:
    employee_id: str
    as_of_date: date
    assessed_at: date
    assessed_skills: dict[str, int]
    current_skills: dict[str, int]
    skill_change_trace: tuple[SkillChangeTrace, ...]
    primary_target: CareerTarget | None
    career_goal: CareerGoal | None
    career_goal_changes_primary_target: bool
    requirements: tuple[SkillGap, ...]
    requirements_met: bool
    candidate_status: str
    candidates: tuple[CandidateFact, ...]
    exclusions: tuple[ExcludedEvent, ...]
