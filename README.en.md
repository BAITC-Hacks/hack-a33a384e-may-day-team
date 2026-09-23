[Русский](README.md) | [Қазақша](README.kz.md) | [English](README.en.md)

# Career Quest

Career Quest helps an employee reach the next grade of the current role. The engine calculates skills, requirements, and eligible activities. OpenAI selects 1–3 steps from that list and explains the choice. If the model is unavailable, the same flow continues through an explicit server fallback.

## What it solves

Employee:

profile → next grade → gaps → recommendation → WHY THIS, NOT THAT → Complete → recalculation.

HR:

gaps → employees without next step → participation → hidden/test profile import.

The primary target is the next grade of the current role: `Junior → Middle → Senior → Lead`. A cross-role `career_goal` is shown separately and does not replace that target. Lead does not get an invented next grade. Meeting requirements does not promote the employee automatically. There is no public employee ranking.

Completion is stored on the server and recalculates skills. It models completion inside the prototype. It does not confirm training in an external LMS.

## What already works

On branch `final/submission`:

- Employee/HR demo login;
- profile;
- trajectory / next-grade requirements;
- deterministic candidate engine;
- OpenAI recommendation 1–3;
- explanation;
- fallback;
- completion;
- progress recalculation;
- refreshed recommendations;
- HR overview;
- multipart import;
- responsive frontend;
- one-command launcher.

`POST /api/auth/demo-login` is the hackathon demo entry. `POST /api/auth/login` with username and password also exists. The demo screen uses Employee and HR buttons.

## Why this is not a ChatGPT wrapper

DETERMINISTIC CODE:

- replay skills;
- current levels;
- next grade;
- requirements;
- gaps;
- prerequisites;
- eligibility;
- event effects;
- participation facts.

AI:

- receives only allowed candidates;
- compares them;
- selects 1–3;
- explains the choice;
- structured JSON;
- server-side validation.

The model payload does not include full name, department, manager, or raw history. It receives role, grade, target, and facts about eligible activities. The model does not create events, levels, requirements, or history.

Fallback runs on:

- missing key;
- timeout;
- provider error;
- invalid output.

The server returns `selection_status=fallback_ranked` and `fallback_reason`: `missing_api_key`, `timeout`, `provider_error`, or `invalid_ai_output`. This is not a numeric AI score.

For `fallback_ranked`, the frontend says “Рекомендуемый шаг” and does not call the answer AI. The label “AI · Рекомендуемый шаг” stays only when `used_ai=true`. An empty list shows “Рекомендация временно недоступна”.

## Architecture

```text
Dataset
  ↓
Validated Loader
  ↓
Deterministic Career Engine
  ↓
FastAPI
  ├ Auth / Sessions / CSRF
  ├ Employee API
  ├ Completion
  ├ HR / Import
  └ OpenAI Recommendation Layer
  ↓
PostgreSQL

React/Vite → FastAPI
```

The calculation engine does not depend on FastAPI, PostgreSQL, or OpenAI. `GET /api/health` checks that the backend process is up. `GET /api/ready` checks PostgreSQL connectivity.

## Stack

Backend:

- Python 3.10+
- FastAPI 0.116.1
- SQLAlchemy 2.0.43
- Alembic 1.16.5
- PostgreSQL
- psycopg 3.2.9

AI:

- OpenAI Responses API
- OpenAI SDK 2.8.1
- strict JSON Schema
- `OPENAI_MODEL` configurable
- live smoke: `gpt-5.6-terra`

Frontend:

- React 19
- Vite 8
- Inter
- CSS
- local SVG icons

Auth:

- server-side sessions
- HttpOnly cookie
- CSRF
- Employee/HR authorization

## Dataset

The dataset is synthetic.

Confirmed sizes:

- 60 skills
- 32 role profiles
- 200 employees
- 40 events
- 2743 history rows

The raw official dataset is not stored in git. `DATASET_PATH` points to a directory. That directory must contain:

```text
career_quest_dataset/
├── skills.json
├── employees.json
├── events.json
└── activity_history.csv
```

The contents of the official dataset are not published in the docs.

## One command

After dependencies, PostgreSQL, the dataset, and `.env` are in place:

```powershell
python scripts/start.py
```

The launcher starts the backend and Vite. It does not install dependencies. Ctrl+C or Ctrl+Break stops both processes.

Addresses: backend `http://127.0.0.1:8000`, frontend `http://127.0.0.1:5173`.

Final smoke on Windows: backend started, frontend started, `/api/health` → 200, `/api/ready` → 200, ports closed after stop. The launcher is implemented cross-platform; the actual final smoke ran on Windows.

Clean-machine setup: [docs/SETUP.md](docs/SETUP.md).

## ENV

Copy `.env.example` to `.env`. Real secrets are not committed. The full explanation is in [docs/SETUP.md](docs/SETUP.md).

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | yes, for a working run | PostgreSQL. Only `career_quest_dev` and `career_quest_test` are allowed |
| `DATASET_PATH` | yes, for a working run | Directory with the four dataset files |
| `ALLOWED_ORIGINS` | no | Origins for cookie requests. Default: `http://127.0.0.1:5173,http://localhost:5173` |
| `COOKIE_SECURE` | no | `Secure` flag on the session cookie. Default: `false` |
| `SESSION_TTL_HOURS` | no | Server session lifetime. Default: `12` |
| `DEMO_EMPLOYEE_ONE_USERNAME` | with the other `DEMO_*` | First demo employee username |
| `DEMO_EMPLOYEE_ONE_PASSWORD` | with the other `DEMO_*` | First demo employee password |
| `DEMO_EMPLOYEE_ONE_ID` | with the other `DEMO_*` | `employee_id` in the loaded dataset |
| `DEMO_EMPLOYEE_TWO_USERNAME` | with the other `DEMO_*` | Second demo employee username |
| `DEMO_EMPLOYEE_TWO_PASSWORD` | with the other `DEMO_*` | Second demo employee password |
| `DEMO_EMPLOYEE_TWO_ID` | with the other `DEMO_*` | `employee_id` in the loaded dataset |
| `DEMO_HR_USERNAME` | with the other `DEMO_*` | Demo HR username |
| `DEMO_HR_PASSWORD` | with the other `DEMO_*` | Demo HR password |
| `OPENAI_API_KEY` | no | OpenAI key, server only. Empty keeps `fallback_ranked` |
| `OPENAI_MODEL` | no | Model ID. Default: `gpt-5.6-terra` |
| `OPENAI_TIMEOUT_SECONDS` | no | Call timeout. Default: `7` |

Example URL without a real secret:

```text
postgresql+psycopg://career_quest:CHANGE_ME@127.0.0.1:5432/career_quest_dev
```

If demo config is used, every `DEMO_*` variable must be set. The frontend needs no secrets: `VITE_OPENAI_KEY` and `VITE_DATABASE_URL` are not required and must not be added.

## Build and tests

Reproducible frontend install:

```powershell
cd frontend
npm ci
npm run build
npm run lint
```

On final assembly, `npm run lint` and `npm run build` are PASS.

Backend:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest -q
```

Final assembly: `40 passed`, `5 skipped`. Five PostgreSQL tests were skipped because `DATABASE_URL` did not point at `career_quest_test`. Skipped tests are not counted as passed.

Earlier PostgreSQL milestone, with `DATABASE_URL` on `career_quest_test`: `42 passed`, `0 skipped`. Five PostgreSQL integration tests ran on PostgreSQL 14.24. These runs are not added together.

## How to check the flow

1. Open `http://127.0.0.1:5173`.
2. Employee: profile, next grade, gaps, recommendation, explanation, Complete, when the server returned a recommendation.
3. HR: gaps, employees without a next step, participation, import JSON + CSV.
4. `http://127.0.0.1:8000/api/health` — backend process.
5. `http://127.0.0.1:8000/api/ready` — PostgreSQL connectivity.

If the saved demo profile has no eligible next step, recommendations are empty and `selection_status` can be `not_applicable`. That is an engine state, not AI switched off.

## Security

- `.env` is gitignored.
- Secrets are never committed.
- The OpenAI key stays on the backend.
- The database password stays on the server or the local machine.
- The raw official dataset is not in the repository.
- The session cookie is `HttpOnly`.
- Changing requests use CSRF.
- The role is checked on the server.
- An employee cannot open another employee.
- HR endpoints are protected on the server.
- The AI payload excludes full name, department, manager, and raw history.

## Known limitations

- Hackathon demo login is not production auth.
- The UI shows `skill_id` where the API does not expose a skill display name.
- Recent activity shows `event_id`.
- Path and History screens are intentionally not implemented.
- Public live deploy has not been verified yet.

## Infrastructure

Ubuntu 22.04, Nginx, HTTPS / Let's Encrypt, PostgreSQL, and the domain `hack.qazentra.com` are prepared. Preferred shape: Nginx → static React build → `/api` proxy → Uvicorn/FastAPI → PostgreSQL. systemd is planned for the backend. Docker is not required for the MVP.

The Career Quest final build is not claimed as publicly deployed until a live smoke is performed. Details: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Key files

```text
backend/career_quest/loader.py    — validated loader
backend/career_quest/engine.py    — deterministic career engine
backend/career_quest/ai_select.py — OpenAI layer and fallback
backend/career_quest/api.py       — HTTP API
backend/career_quest/serve.py     — migrations, seed, Uvicorn
scripts/start.py                  — backend + Vite
frontend/src/App.jsx              — session and screens
frontend/src/screens.jsx          — login, detail, HR, import
frontend/src/api/client.js        — API calls
alembic/                          — PostgreSQL migrations
docs/SETUP.md                     — clean-machine setup
docs/API.md                       — HTTP contract
docs/PROJECT.md                   — product and technical decisions
docs/CHECKPOINT.md                — actual status
```
