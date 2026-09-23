# Career Quest

Updated: 2026-09-23

## Sources

Confirmed from files that were read:

- Local synthetic dataset, already unpacked, not stored in this repository: `C:\dev\hackathon-2026\career_quest_dataset\case_1\career_quest_dataset\`.
- Dataset README in English, Russian, and Kazakh. Dataset `meta.version` is `1.0`. Snapshot date in the data is `2026-10-01`.
- Team process rules: `_prestart/WORK_RULES.md` (outside this repository).

A separate official case brief file (PDF or page) was not in the workspace. Requirements below that are not in the dataset are taken from the milestone task for this case and are marked as such. Nothing beyond those sources is treated as approved.

## Customer and case

- Customer named in the milestone task: Halyk Bank.
- Event named in the milestone task: HackAlem AI.
- Case selected for the official repository: Career Quest.

## Problem

The case dataset describes employees, skill requirements by role and grade, development activities, and participation history. The milestone task requires a solution that helps an employee see a profile and career trajectory and receive the next development activities.

A longer narrative problem statement was not present in the dataset files.

## Users

Named in the milestone task:

- Employee
- HR

The dataset also records `assigned_by` values `self`, `manager`, and `hr`. A separate manager product view is not listed in the milestone must-have list.

## Official must-have

From the milestone task:

- Employee profile and career trajectory.
- AI recommendation of 1–3 next activities.
- An explanation based on multiple factors.
- Progress update after an activity is completed.
- HR view.
- Ability to load additional test profiles and history in the same format.

From the dataset README:

- Mandatory events are assigned by HR and are not a recommendation target.
- Evaluation uses additional employee profiles and history records in the same format. The solution must be able to load them.
- The milestone task adds: the jury will load unknown test profiles on which single-factor recommendation logic is specifically expected to fail.

## Dataset overview

Synthetic data. The dataset README states that there are no real people or companies. The dataset was not modified. It is not committed in this repository.

Counts verified by reading the files:

| File | Format | Records |
|---|---|---|
| `skills.json` | JSON | 60 skills, 32 role profiles (8 roles × 4 grades) |
| `employees.json` | JSON | 200 employees |
| `events.json` | JSON | 40 events |
| `activity_history.csv` | CSV | 2,743 participation rows |

History window in the data: `2024-10-01` – `2026-09-30`. Rows are sorted by `date`, `employee_id`, `event_id`. Record IDs run from `R000001` to `R002743`. Employee IDs run from `E0001` to `E0200`. Event IDs run from `EV_001` to `EV_040`.

All checked references are valid. Skill, employee, event, and history IDs are unique. Every employee and every event appears in the history.

### skills.json

Proficiency scale is 0–5:

| Level | Meaning in the file |
|---|---|
| 0 | No knowledge |
| 1 | Basic awareness |
| 2 | Working knowledge |
| 3 | Proficient |
| 4 | Advanced |
| 5 | Expert |

Skill fields: `skill_id`, `name`, `type` (`hard` or `soft`), `category`, `description`.

Verified split: 46 hard, 14 soft. Categories: engineering 10, product 7, frontend 6, data 6, hr 6, sales 5, quality 4, communication 4, leadership 4, support 2, collaboration 2, thinking 2, personal_effectiveness 2.

Role profile fields: `role`, `grade` (`Junior`, `Middle`, `Senior`, `Lead`), `required_skills` (`skill_id` → minimum level), `critical_skills`.

Roles: Backend Engineer, Frontend Engineer, Data Analyst, QA Engineer, Product Manager, HR Business Partner, Sales Manager, Customer Support Specialist.

Required-skill counts per profile: 7–16. Critical-skill counts: 1 (9 profiles), 2 (22 profiles), 3 (1 profile). Every critical skill is also in `required_skills` for that profile. Checked requirement levels do not decrease from Junior to Lead within a role.

### employees.json

Fields: `employee_id`, `full_name`, `department`, `role`, `grade`, `manager_id`, `hire_date`, `tenure_months`, `work_format`, `preferred_language`, `career_goal`, `skills`, `last_review_date`.

Verified distributions:

- One department per role: Backend Development, Frontend Development, Data & Analytics, Quality Assurance, Product Management, Human Resources, Sales, Customer Support.
- Headcount: Backend Engineer 40, Sales Manager 30, Frontend Engineer 28, Customer Support Specialist 26, Data Analyst 24, QA Engineer 20, Product Manager 18, HR Business Partner 14.
- Grades: Middle 78, Junior 59, Senior 47, Lead 16.
- `preferred_language`: `ru` 100, `kk` 89, `en` 11.
- `work_format`: `office` 90, `hybrid` 75, `remote` 35.
- `career_goal` is null for 66 employees. Same-role goals: 106. Cross-role goals: 28. Every non-null goal points at a role and grade that exists in `role_profiles`.
- `manager_id` is null for 8 employees. Each is a Lead and the only head of that department. Every other manager is a Lead in the same department.
- Each employee stores 18–25 skill levels. Observed levels are 0–5. A skill omitted from the object means level 0, per the dataset README. Explicit zeros are present (333).
- `tenure_months` matches full months from `hire_date` to `2026-10-01` for all 200 employees.
- Hire dates: `2016-10-03` – `2026-08-27`. Last review dates: `2026-01-05` – `2026-09-29`.
- 114 employees are below the required level of at least one critical skill for their current grade.
- Names, skill text, and event text checked as ASCII. The dataset READMEs exist in English, Russian, and Kazakh. UI copy in three languages is not specified beyond the `preferred_language` field.

### events.json

Fields: `event_id`, `title`, `description`, `type`, `format`, `duration_hours`, `mandatory`, `target_roles`, `target_grades`, `develops_skills`, `prerequisites`, `upcoming_sessions`.

Types: workshop 17, course 15, compliance 3, mentoring 2, onboarding 1, certification 1, meetup 1.

Formats: online 21, offline 10, self_paced 9.

`duration_hours` values present: 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 30, 40.

Mandatory events, which the dataset README says are not recommendation targets:

| ID | Type | Title | Format | `develops_skills` |
|---|---|---|---|---|
| `EV_001` | compliance | Information Security Awareness | self_paced | empty |
| `EV_002` | compliance | Personal Data Protection | self_paced | empty |
| `EV_003` | compliance | Code of Conduct & Workplace Safety | self_paced | empty |
| `EV_004` | onboarding | New Employee Onboarding | offline | `SK_PRODUCT_KNOWLEDGE` and `SK_TEAMWORK`, each `gain` 1, `max_level` 2 |

`develops_skills` entries are `{skill_id, gain, max_level}`. Every non-mandatory event has at least one entry. Observed `gain` is always 1. Observed `max_level` is 2, 3, 4, or 5. Completion raises the skill by `gain` but not above `max_level`. Compliance training has an empty array.

`prerequisites` is `skill_id` → minimum level. 28 events have an empty object.

`upcoming_sessions`: empty for all 9 `self_paced` events. Every online or offline event has at least one session. 79 session dates were counted, from `2026-10-05` to `2026-12-25`, all on or after the snapshot date.

`EV_036` is the recurring meetup "Public Speaking Club" (`offline`, not mandatory). It develops `SK_PUBLIC_SPEAKING` with `gain` 1 and `max_level` 4.

Most voluntary events target a subset of roles and grades. `EV_001`–`EV_004`, `EV_036`, and some others target all 8 roles.

### activity_history.csv

Columns: `record_id`, `employee_id`, `event_id`, `date`, `due_date`, `status`, `completion_pct`, `score`, `feedback_rating`, `assigned_by`.

Statuses and observed `completion_pct`:

| Status | Rows | Observed `completion_pct` | README allowed range |
|---|---|---|---|
| `completed` | 2,178 | 100 | 100 |
| `no_show` | 195 | 0 | 0 |
| `dropped` | 160 | 10–90 | 5–95 |
| `declined` | 104 | 0 | 0 |
| `overdue` | 90 | 0–60 | 0–95 |
| `in_progress` | 16 | 15–90 | 0–95 |

`assigned_by`: `hr` 1,381, `self` 865, `manager` 497.

`due_date` is present only on mandatory events, and every mandatory history row has one. `overdue` occurs only on mandatory events. `no_show` does not occur on `self_paced` events. `declined` is only `manager` (83) or `hr` (21).

`score` is an integer 60–100 when present, otherwise empty. Non-empty scores occur only on compliance, course, and certification. Some of those rows still have an empty score: compliance 90, course 138, certification 20. Workshop, mentoring, meetup, and onboarding rows have no score.

`feedback_rating` is optional, 1–5 when present. 1,847 rows are empty.

### Relations

```
employees.skills ─────────────┐
role_profiles.required_skills ├──> skills.skill_id
events.develops_skills ───────┤
events.prerequisites ─────────┘
employees.(role, grade) ──────> role_profiles.(role, grade)
employees.manager_id ─────────> employees.employee_id
activity_history.employee_id ─> employees.employee_id
activity_history.event_id ────> events.event_id
```

### Dataset rules and observed edge cases

Stated in the dataset README and checked against the files:

- An event is not repeated after `completed`, with the stated exception `EV_036`. In the file, later rows after a `completed` participation also exist for the annual compliance events `EV_001`, `EV_002`, and `EV_003`. No other event has a row after a completed participation of the same employee and event.
- Voluntary history rows match the employee's current role. 84 voluntary rows do not match the employee's current grade: the current grade is above the event's `target_grades`. The README says voluntary history matches the current or a previous grade. Previous grades are not stored, so that part was not reconstructed.
- Using current skill levels, no voluntary history row fails the event's current prerequisites. The README says history matched prerequisites at the time of participation. Skill levels are the last assessment, not a historical snapshot.
- 318 `completed` rows have a date after that employee's `last_review_date`. The README says those completions are not yet included in skill levels.
- The README says new employees complete `EV_004` in their first month. The file contains 80 `completed` rows for `EV_004` and no other status for that event. First-month timing was not fully reconstructed in this audit.

## Constraints recorded from available sources

- Data are synthetic.
- Treat `2026-10-01` as "today".
- Mandatory activities are not recommendation targets.
- Additional test profiles and history must load in the same format.
- Single-factor recommendation logic is expected to fail on unknown jury profiles (milestone task).
- Skill level after completion is capped by `max_level`.
- A missing skill level means 0.

Not found in the dataset files or READMEs, so not recorded as requirements:

- A numeric latency limit.
- A privacy or data-handling policy.
- An access-control specification for Employee and HR separation. The milestone task requires an HR view and names both users. How access is separated is not specified.
- A list of forbidden product mechanics beyond "mandatory events are not a recommendation target".
- A numeric scoring rubric.

Team reproducibility rule, from `WORK_RULES.md`, not from the case file: the project must be possible to run from this repository, and secrets stay out of git. There is no application to run yet.

## Decisions not yet approved

TBD / REQUIRES USER DECISION:

- Stack.
- Auth.
- Database schema.
- Recommendation architecture.
- AI provider and model.
- PWA.
- Admin.
- Final UX.

Do not treat any of those as chosen.
