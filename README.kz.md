[Русский](README.md) | [Қазақша](README.kz.md) | [English](README.en.md)

# Career Quest

Career Quest қызметкерге ағымдағы рөлдің келесі грейдіне дейін жетуге көмектеседі. Engine дағдыларды, талаптарды және рұқсат етілген белсенділіктерді есептейді. OpenAI сол тізімнен 1–3 қадам таңдап, таңдауды түсіндіреді. Модель қолжетімсіз болса, сол сценарий сервердегі айқын fallback арқылы жалғасады.

## Не шешеді

Employee:

profile → next grade → gaps → recommendation → WHY THIS, NOT THAT → Complete → recalculation.

HR:

gaps → employees without next step → participation → hidden/test profile import.

Негізгі мақсат — ағымдағы рөлдің келесі грейді: `Junior → Middle → Senior → Lead`. Басқа рөлге арналған `career_goal` бөлек көрсетіледі және бұл мақсатты алмастырмайды. Lead үшін келесі грейд ойдан шығарылмайды. Талаптарды орындау қызметкерді автоматты түрде көтермейді. Қызметкерлердің жария рейтингі жоқ.

Complete серверде сақталады және дағдыларды қайта есептейді. Бұл прототип ішіндегі аяқтау моделі. Сыртқы LMS-тегі оқуды растамайды.

## Не істеп тұр

`final/submission` тармағында:

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

`POST /api/auth/demo-login` — hackathon demo кіруі. Username және password бар `POST /api/auth/login` да бар. Demo экраны Employee және HR түймелерін қолданады.

## Неге бұл ChatGPT-wrapper емес

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

- тек рұқсат етілген candidates алады;
- салыстырады;
- 1–3 таңдайды;
- түсіндіреді;
- structured JSON;
- server-side validation.

Модель payload-ына толық аты-жөн, бөлім, басшы және шикі тарих кірмейді. Рөл, грейд, мақсат және рұқсат етілген белсенділік фактілері беріледі. Модель іс-шара, деңгей, талап немесе тарих жасамайды.

Fallback мына жағдайда іске қосылады:

- missing key;
- timeout;
- provider error;
- invalid output.

Сервер `selection_status=fallback_ranked` және `fallback_reason` қайтарады: `missing_api_key`, `timeout`, `provider_error` немесе `invalid_ai_output`. Бұл сандық AI-score емес.

`fallback_ranked` кезінде frontend «Рекомендуемый шаг» деп жазады және жауапты AI деп атамайды. «AI · Рекомендуемый шаг» жазуы тек `used_ai=true` болғанда қалады. Бос тізім «Рекомендация временно недоступна» көрсетеді.

## Архитектура

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

Есептеу engine-і FastAPI, PostgreSQL және OpenAI-ға тәуелді емес. `GET /api/health` backend процесін тексереді. `GET /api/ready` PostgreSQL байланысын тексереді.

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

Dataset синтетикалық.

Расталған өлшемдер:

- 60 skills
- 32 role profiles
- 200 employees
- 40 events
- 2743 history rows

Raw official dataset git-те сақталмайды. `DATASET_PATH` папкаға көрсетеді. Папкада міндетті түрде мына файлдар болуы керек:

```text
career_quest_dataset/
├── skills.json
├── employees.json
├── events.json
└── activity_history.csv
```

Official dataset мазмұны құжаттамада жарияланбайды.

## Бір команда

Тәуелділіктер, PostgreSQL, dataset және `.env` дайын болған соң:

```powershell
python scripts/start.py
```

Launcher backend пен Vite-ті іске қосады. Тәуелділіктерді орнатпайды. Ctrl+C немесе Ctrl+Break екі процесті тоқтатады.

Мекенжайлар: backend `http://127.0.0.1:8000`, frontend `http://127.0.0.1:5173`.

Windows-тағы final smoke: backend started, frontend started, `/api/health` → 200, `/api/ready` → 200, ports closed after stop. Launcher cross-platform жазылған; нақты final smoke Windows-та орындалған.

Таза компьютерден орнату: [docs/SETUP.md](docs/SETUP.md).

## ENV

`.env.example` файлын `.env` етіп көшіріңіз. Нақты құпиялар репозиторийге салынбайды. Толық түсініктеме — [docs/SETUP.md](docs/SETUP.md).

| Айнымалы | Міндетті | Мақсаты |
|---|---|---|
| `DATABASE_URL` | иә, жұмыс істейтін іске қосу үшін | PostgreSQL. Тек `career_quest_dev` және `career_quest_test` рұқсат |
| `DATASET_PATH` | иә, жұмыс істейтін іске қосу үшін | Төрт dataset файлы бар папка |
| `ALLOWED_ORIGINS` | жоқ | Cookie сұрауларына арналған Origin. Default: `http://127.0.0.1:5173,http://localhost:5173` |
| `COOKIE_SECURE` | жоқ | Session cookie үшін `Secure`. Default: `false` |
| `SESSION_TTL_HOURS` | жоқ | Сервер сессиясының мерзімі. Default: `12` |
| `DEMO_EMPLOYEE_ONE_USERNAME` | қалған `DEMO_*` бірге | Бірінші demo employee логині |
| `DEMO_EMPLOYEE_ONE_PASSWORD` | қалған `DEMO_*` бірге | Бірінші demo employee құпиясөзі |
| `DEMO_EMPLOYEE_ONE_ID` | қалған `DEMO_*` бірге | Жүктелген dataset ішіндегі `employee_id` |
| `DEMO_EMPLOYEE_TWO_USERNAME` | қалған `DEMO_*` бірге | Екінші demo employee логині |
| `DEMO_EMPLOYEE_TWO_PASSWORD` | қалған `DEMO_*` бірге | Екінші demo employee құпиясөзі |
| `DEMO_EMPLOYEE_TWO_ID` | қалған `DEMO_*` бірге | Жүктелген dataset ішіндегі `employee_id` |
| `DEMO_HR_USERNAME` | қалған `DEMO_*` бірге | Demo HR логині |
| `DEMO_HR_PASSWORD` | қалған `DEMO_*` бірге | Demo HR құпиясөзі |
| `OPENAI_API_KEY` | жоқ | OpenAI кілті, тек серверде. Бос болса, `fallback_ranked` қалады |
| `OPENAI_MODEL` | жоқ | Модель ID. Default: `gpt-5.6-terra` |
| `OPENAI_TIMEOUT_SECONDS` | жоқ | Шақыру timeout. Default: `7` |

Нақты құпиясыз URL мысалы:

```text
postgresql+psycopg://career_quest:CHANGE_ME@127.0.0.1:5432/career_quest_dev
```

Demo config қолданылса, барлық `DEMO_*` толтырылуы керек. Frontend құпияларын қажет етпейді: `VITE_OPENAI_KEY` және `VITE_DATABASE_URL` талап етілмейді және болмауы керек.

## Build және тесттер

Frontend-ті қайталанатын түрде орнату:

```powershell
cd frontend
npm ci
npm run build
npm run lint
```

Final assembly: `npm run lint` және `npm run build` — PASS.

Backend:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest -q
```

Final assembly: `40 passed`, `5 skipped`. Бес PostgreSQL тесті skipped: `DATABASE_URL` `career_quest_test` базасына бағытталмаған. Skipped passed болып саналмайды.

Бұрынғы PostgreSQL milestone, `DATABASE_URL` `career_quest_test` болғанда: `42 passed`, `0 skipped`. Бес PostgreSQL integration tests PostgreSQL 14.24 үстінде өткен. Бұл нәтижелер қосылмайды.

## Сценарийді тексеру

1. `http://127.0.0.1:5173` ашыңыз.
2. Employee: profile, next grade, gaps, ұсыныс, түсіндірме, Complete — сервер ұсыныс қайтарса.
3. HR: gaps, келесі қадамы жоқ қызметкерлер, participation, JSON + CSV import.
4. `http://127.0.0.1:8000/api/health` — backend процесі.
5. `http://127.0.0.1:8000/api/ready` — PostgreSQL байланысы.

Сақталған demo profile үшін рұқсат етілген келесі қадам болмаса, ұсыныстар бос және `selection_status` `not_applicable` болуы мүмкін. Бұл engine күйі, AI өшірілгені емес.

## Қауіпсіздік

- `.env` git ignore ішінде.
- Құпиялар commit-ке кірмейді.
- OpenAI кілті тек backend-те.
- Дерекқор құпиясөзі серверде немесе жергілікті машинада қалады.
- Raw official dataset репозиторийге кірмейді.
- Session cookie — `HttpOnly`.
- Өзгертетін сұрауларда CSRF.
- Рөл серверде тексеріледі.
- Employee басқа қызметкерді аша алмайды.
- HR endpoints серверде қорғалған.
- AI payload толық аты-жөнді, бөлімді, басшыны және шикі тарихты қамтымайды.

## Known limitations

- Hackathon demo login — production auth емес.
- API display name бермеген жерде UI `skill_id` көрсетеді.
- Соңғы белсенділік `event_id` көрсетеді.
- Path және History экрандары әдейі жасалмаған.
- Жария live deploy әлі тексерілмеген.

## Infrastructure

Ubuntu 22.04, Nginx, HTTPS / Let's Encrypt, PostgreSQL және `hack.qazentra.com` домені дайындалған. Ұсынылатын сұлба: Nginx → static React build → `/api` proxy → Uvicorn/FastAPI → PostgreSQL. Backend үшін systemd жоспарланған. MVP үшін Docker керек емес.

Career Quest final build жария түрде орналастырылды деп айтылмайды, live smoke орындалғанша. Толығырақ: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Негізгі файлдар

```text
backend/career_quest/loader.py    — validated loader
backend/career_quest/engine.py    — deterministic career engine
backend/career_quest/ai_select.py — OpenAI layer және fallback
backend/career_quest/api.py       — HTTP API
backend/career_quest/serve.py     — миграция, seed, Uvicorn
scripts/start.py                  — backend + Vite
frontend/src/App.jsx              — сессия және экрандар
frontend/src/screens.jsx          — login, detail, HR, import
frontend/src/api/client.js        — API шақырулары
alembic/                          — PostgreSQL миграциялары
docs/SETUP.md                     — нөлден орнату
docs/API.md                       — HTTP келісімшарты
docs/PROJECT.md                   — өнім және техникалық шешімдер
docs/CHECKPOINT.md                — нақты мәртебе
```
