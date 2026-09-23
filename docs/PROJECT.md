# Career Quest

Updated: 2026-09-23

## Sources

- Official case brief, read in full on 2026-09-23. The DOCX is not stored in this repository.
- Local synthetic dataset, not stored in this repository: `C:\dev\hackathon-2026\career_quest_dataset\case_1\career_quest_dataset\`.
- Dataset README in English, Russian, and Kazakh. Dataset `meta.version` is `1.0`. Snapshot date in the data is `2026-10-01`.
- Team process rules: `_prestart/WORK_RULES.md` (outside this repository).

The official brief is the source for case requirements. The dataset is the source for data. Where they disagree, see Conflicts. Unapproved product decisions stay in the last section.

## Customer and case

From the official brief:

- Customer: АО Народный Банк Казахстана.
- Hackathon: HackAlem AI.
- Track: Halyk Bank.
- Task title: AI для корпоративных продуктов.
- Task type: product development, AI/LLM engineering, full-stack.
- Tools allowed for the track: any models and services, cloud or local LLM, STT, TTS. No model is selected.
- Two cases are scored separately and are not compared with each other: Career Quest, and Voice Router. This repository is for Career Quest only.
- Official case name: Career Quest — платформа геймификации жизненного цикла сотрудника.

The same brief says the core of Career Quest is recommendation quality and explainability, not the interface shell. Gamification is an overlay and is not part of the mandatory scope.

## Problem

Official Career Quest problem:

An employee receives a stream of disconnected HR events with no visible link to their development. Training is completed formally on the deadline day. Voluntary activities have low attendance, while the people-development budget is fully spent.

The brief's opening also describes a second, separate problem (Voice Router: a dialogue-scenario chooser that fails on live speech). That case is not in scope here.

## Users

Official Career Quest users:

- Primary user: an employee with 1–5 years of tenure. Scenario: sees their profile and trajectory, receives a next-step recommendation with an explanation of what it gives them, completes the activity, and sees progress move.
- Second user: HR. Sees which competencies are lagging and who is dropping out of development.

The track introduction also lists department heads, contact-center clients, operators, and supervisors. Those belong to the shared introduction for both cases. Career Quest section 3 does not add a manager, client, or operator view to the required users.

The dataset records `assigned_by` values `self`, `manager`, and `hr`. That is a history field, not a required manager screen.

Dataset tenure is wider than the primary persona. Hire dates in the file run from `2016-10-03` to `2026-08-27`. The brief does not say the dataset contains only 1–5 year employees.

## Task

Develop a web application with an AI layer. From the profile, history, and next-grade requirements, it selects relevant development steps and returns a justified recommendation plus updatable skill progress. HR receives a view of lagging competencies.

Input stated in the brief: JSON/CSV profiles, events, history, and skills. Stated volume: 200 profiles, 40 events, 60 skills, 24 months of history. The audited files match those counts. The history file spans `2024-10-01`–`2026-09-30`.

Output stated in the brief:

- Profile with trajectory.
- 1–3 recommended steps with a justification. The brief's example wording is: «System Design — 2 при требуемых 4 для Senior; активность закрывает разрыв, предыдущие две пройдены в срок». That sentence is an output example, not a checked row from the dataset.
- Progress update after completion.
- HR screen.

## Official must-have

| Requirement in the brief | How the brief says to check it |
|---|---|
| Profile and career trajectory | Open any employee. Role, grade, skills, completed activities, and available next steps are visible. |
| AI recommendation of the next step | The system offers 1–3 relevant activities. |
| Explanation | The justification relies on at least three factors. The brief names: grade, skill gaps, participation history, next-level requirements. |
| Progress update | Mark an activity completed. Skill progress and the trajectory move. |
| Simple HR view | Which skills lag most often, who has no recommended step, participation by activity. |
| Test profiles | The jury uses three profiles, the same for every team, built so a single-factor rule fails. The solution loads extra profiles and history in the dataset format. At the defense the jury loads them. |

Official wording for the explanation, not shortened: «Обоснование опирается минимум на три фактора — грейд, разрывы по навыкам, история участия, требования следующего уровня». The sentence requires at least three factors and names four. This file does not choose whether all four are mandatory.

Official hidden-profile example, not a dataset row: the employee's lowest skill is Public Speaking, history shows three skips of similar activities, and System Design is critical for the next grade. A recommendation of the form «бери минимальный навык» misses.

Dataset README, still in force for the data:

- Mandatory events are assigned by HR and are not a recommendation target.
- Evaluation uses additional profiles and history in the same format. The solution must load them.
- Skill growth is `gain` up to `max_level`, as stated on each event.

## Optional

Listed in the brief. Not in the mandatory part:

- Internal currency and recognition.
- Rewards catalog and exchanging points.
- Recognition from colleagues.
- Mentor and team mechanics.
- Personal challenges.
- An event builder for HR.
- Attrition-risk forecast.
- An extended HR dashboard.
- Grade-transition modeling.
- Embedding in a messenger or calendar.
- Mobile adaptation.
- A high-quality Kazakh and Russian interface localization.

## Latency

From the brief:

- Interface response: up to 2 seconds.
- AI recommendation: up to 10 seconds.

## Privacy, security, and other constraints

Cannot, from the brief:

- A recommendation from a single profile field presented as AI. The justification must use several factors.
- Public employee rankings by performance. The brief's reason: they motivate a small leader group and demotivate the majority who see an unreachable gap.
- Mechanics around mandatory processes. The brief's example: points for timesheets.
- Real personal data.

Must account for, from the brief:

- Privacy: internal contour. Engagement data are not visible to other employees without consent.
- Security: separate employee and HR permissions.
- Explainability: it is visible why a step was proposed and how advancement was calculated.
- Infrastructure: the project starts with one command.
- Voluntariness: coercion is the main predictor of failure for programs of this kind.

Data rules from the brief:

- The starter kit is issued on hackathon day.
- Data are synthetic and must not be taken outside the hackathon.
- Adding own data is allowed if the schema is kept.
- The brief says the data are in English, with Kazakh and Russian translations. See Conflicts.

Dataset rule that the brief does not repeat as a product ban: mandatory events are not recommendation targets. The brief's ban is mechanics around mandatory processes, with timesheets as the example. Both statements are kept. They are not treated as the same rule.

## AI and explainability

- The required product is a web application with an AI layer.
- The core is recommendation quality and explainability, not the interface shell.
- The explanation must show why the step was proposed.
- Progress must show how advancement was calculated.
- The track allows any cloud or local LLM, and STT/TTS. Career Quest does not name a model, and this file does not choose one.
- STT and TTS are allowed track tools. The Career Quest must-have list does not require voice.

## Launch and reproducibility

The brief requires a repository and a README.

Scoring for README and reproducibility, 25 points: the documentation lets a reader understand the project structure, technologies used, launch order, and main scenario, and the solution can be reproduced and checked from the repository.

Infrastructure constraint: one-command launch.

There is no application in this repository yet, so there is no launch command.

## Evaluation criteria

| Criterion in the brief | Points |
|---|---|
| Соответствие задаче и работоспособность. Fit to the task and whether the main stated scenario works. | 25 |
| Техническая реализация. Approach, architecture, component interaction, use of AI/agentic AI and other technologies, and whether the implementation matches the stated logic. | 25 |
| README и воспроизводимость. Documentation of structure, technologies, launch, and main scenario, plus the ability to reproduce and check the solution from the repository. | 25 |
| Ценность и применимость решения. Whether the solution answers the stated problem, and practical applicability. | 15 |
| Потенциал развития и оригинальность подхода. Further development, broader use, and justified unusual approaches. | 10 |
| Total | 100 |

Artifacts required by the brief: repository, README.

## Conflicts

CONFLICT 1. Language of the data.

- Brief: «Данные на английском, а также переводы на казахский и русский.»
- Dataset records: skill names, event titles, event descriptions, and employee names checked in the JSON/CSV files are English ASCII. No Kazakh or Russian fields were found inside `skills.json`, `employees.json`, `events.json`, or `activity_history.csv`.
- Kazakh and Russian text is present in `README.kz.md` and `README.ru.md`.
- Not resolved here.

No conflict on volume. The brief's 200 profiles, 40 events, 60 skills, and 24 months of history match the audited files and the window `2024-10-01`–`2026-09-30`.

DATASET INTERNAL, not a brief-versus-dataset conflict: the dataset README says an event is not repeated after `completed` except `EV_036`. The history file also has later rows after `completed` for `EV_001`, `EV_002`, and `EV_003`. The brief does not state this rule. It points detail to the starter-kit README. Not resolved here.

AMBIGUITY inside the brief, not a dataset conflict: the explanation must use at least three factors, and the same sentence names four (grade, skill gaps, participation history, next-level requirements). Not resolved here.

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
- Names, skill text, and event text checked as ASCII. `README.md`, `README.ru.md`, and `README.kz.md` are the English, Russian, and Kazakh dataset notes. Interface localization into Kazakh and Russian is optional in the brief, not a must-have. `preferred_language` in the employee file is `kk`, `ru`, or `en`.

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

## Decisions not yet approved

The brief requires a web application, an AI layer, employee/HR permission separation, and one-command launch. It does not choose how those are built.

TBD / REQUIRES USER DECISION:

- Stack.
- Auth mechanism.
- Database schema.
- Recommendation architecture.
- AI provider and model.
- PWA. Mobile adaptation is optional in the brief, not selected.
- Admin.
- Final UX.

Do not treat any of those as chosen.

## Documentation decisions

This is a user organizational decision. It is not a Halyk requirement.

Documentation language policy:

- canonical README: Russian;
- Kazakh and English README translations: final stage;
- technical project documents: single version only;
- translations must remain semantically equivalent to canonical README.
