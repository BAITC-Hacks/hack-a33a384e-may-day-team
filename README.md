# Career Quest

AI career navigator для Halyk HackAlem AI.

Документ описывает final assembly: launcher и проверка поверх UX
`7c22ccd557d894ddeccd4148f4e23a2f4fa55d37`. Fallback UI вошёл в
`014d6c5d20dd005af2f5a4987130922ebd343c82`. Docs source:
`b90defe25dc6b78a22c3c34681ceabf12a3f7087`.

## Что решает

Профиль сотрудника
→ требования следующего грейда
→ допустимые активности
→ AI выбирает 1–3
→ объясняет почему
→ сотрудник завершает
→ прогресс пересчитывается
→ HR видит агрегаты.

Основная цель — следующий грейд текущей роли:
`Junior → Middle → Senior → Lead`. Межролевой `career_goal` показывается
отдельно и не подменяет эту цель. Для Lead следующий грейд не выдумывается.
Выполнение требований не повышает сотрудника автоматически.

Employee видит только своё развитие. HR видит частые разрывы навыков,
сотрудников без следующего шага и участие по активностям. Публичного рейтинга
сотрудников нет.

Отметка выполнения сохраняется на сервере и пересчитывает навыки. Это модель
завершения в прототипе, а не подтверждение обучения во внешней LMS.

## Главный сценарий demo

Employee:

1. demo login;
2. профиль;
3. target grade / gaps;
4. AI recommendation;
5. WHY THIS, NOT THAT;
6. Complete;
7. skill/progress update;
8. новая recommendation.

HR:

1. demo login HR;
2. frequent gaps;
3. employees without next step;
4. participation;
5. import hidden/test profile JSON + CSV.

`POST /api/auth/demo-login` — вход для hackathon demo, не production
authentication. Обычный `POST /api/auth/login` с username и password остаётся.

## Почему это не ChatGPT-wrapper

Детерминированный backend считает:

- replay skills;
- next grade;
- gaps;
- prerequisites;
- eligibility;
- event effects;
- history facts.

AI:

- получает только допустимых candidates;
- выбирает 1–3;
- объясняет;
- structured output;
- server validates IDs/factors/ranks;
- deterministic fallback.

Модель не создаёт мероприятия, уровни, требования или историю. Невалидный
ответ, чужой ID, таймаут, ошибка провайдера и отсутствие ключа не становятся
рекомендацией модели: сервер возвращает явный `fallback_ranked`. Это не
утверждение, что выбор AI всегда лучший.

## Технологии

Backend:

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

AI:

- OpenAI Responses API
- Structured Outputs / strict JSON schema
- `OPENAI_MODEL` configurable
- Live smoke использовал `gpt-5.6-terra`
- OpenAI SDK `2.8.1`

Frontend:

- React 19
- Vite 8
- CSS
- Inter

Auth:

- server sessions
- HttpOnly cookie
- CSRF
- Employee/HR server authorization
- hackathon server-side demo-login

## Архитектура

```text
React/Vite
   ↓
FastAPI
   ├ deterministic Career Engine
   ├ AI recommendation layer
   ├ auth / completion / HR / import
   ↓
PostgreSQL

dataset → validated loader → engine
```

Расчётный engine не зависит от FastAPI, PostgreSQL и OpenAI. Контракт HTTP —
`docs/API.md`.

## Dataset

Подтверждённые объёмы синтетического dataset:

- 60 skills
- 32 role profiles
- 200 employees
- 40 events
- 2743 history rows

Raw official dataset в git не хранится. Загрузчик принимает каталог той же
схемы: `skills.json`, `employees.json`, `events.json`,
`activity_history.csv`.

## AI

- Модель задаётся `OPENAI_MODEL`.
- Live smoke на синтетическом профиле: `gpt-5.6-terra`, latency 7883 ms.
- SLA кейса на AI-рекомендацию: меньше 10 секунд. Этот smoke уложился в лимит.
- Fallback при отсутствии ключа, timeout, ошибке провайдера и невалидном output.
- В payload модели не входят полное имя, отдел, руководитель и сырая история.
  Передаются роль, грейд, цель и факты допустимых активностей.

На этом commit непустой `recommendations` показывается всегда.
`used_ai=true` подписан «AI · Рекомендуемый шаг». `fallback_ranked` подписан
«Рекомендуемый шаг» и не называется AI. Пустой список показывает
«Рекомендация временно недоступна». Detail, сравнение и Complete работают
для fallback-активности.

## Проверки

M2.2 backend, когда PostgreSQL test DB была подключена:
`42 passed`, `0 skipped`.

Final assembly без подключённой test DB: `40 passed`, `5 skipped`.
Пять PostgreSQL tests не запускались: `DATABASE_URL` не указывал на
`career_quest_test`. Skipped не считаются passed.

Frontend этого прогона: `npm run lint` — PASS, `npm run build` — PASS.

`python scripts/start.py` поднял backend и Vite. `GET /api/health` вернул 200.
При настроенной локальной DB `GET /api/ready` вернул 200. Frontend открылся
на `http://127.0.0.1:5173`. Ctrl+Break завершил оба процесса, порты 8000 и
5173 закрылись.

## Запуск

Из корня репозитория, после setup:

```powershell
python scripts/start.py
```

Команда запускает текущий backend entrypoint и `npm run dev`. Зависимости
сама не устанавливает. Ctrl+C или Ctrl+Break останавливает оба процесса.
Backend: `http://127.0.0.1:8000`. Frontend: `http://127.0.0.1:5173`.

### Prerequisites

- Python 3.10+
- PostgreSQL
- Node, совместимый с Vite 8: Node 20.19+ либо 22.12+
- dataset той же схемы
- установленные Python- и frontend-зависимости

### Setup

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Для тестов вместо `requirements.txt` установите `requirements-dev.txt`.

Frontend:

```powershell
cd frontend
npm install
```

Linux/macOS: `python3 -m venv .venv`, затем `pip` из `.venv/bin`.

### Env

Скопируйте `.env.example` в локальный `.env`. Реальные пароли, URL с паролем и
ключ OpenAI в репозиторий не кладутся.

| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | PostgreSQL для `career_quest_dev` или `career_quest_test` |
| `DATASET_PATH` | Каталог четырёх файлов dataset |
| `ALLOWED_ORIGINS` | Разрешённые Origin для cookie-запросов |
| `COOKIE_SECURE` | Флаг `Secure` у session cookie |
| `SESSION_TTL_HOURS` | Срок серверной сессии |
| `DEMO_EMPLOYEE_ONE_USERNAME` | Логин первого demo employee |
| `DEMO_EMPLOYEE_ONE_PASSWORD` | Пароль первого demo employee |
| `DEMO_EMPLOYEE_ONE_ID` | `employee_id` первого demo employee |
| `DEMO_EMPLOYEE_TWO_USERNAME` | Логин второго demo employee |
| `DEMO_EMPLOYEE_TWO_PASSWORD` | Пароль второго demo employee |
| `DEMO_EMPLOYEE_TWO_ID` | `employee_id` второго demo employee |
| `DEMO_HR_USERNAME` | Логин demo HR |
| `DEMO_HR_PASSWORD` | Пароль demo HR |
| `OPENAI_API_KEY` | Ключ OpenAI, только на сервере |
| `OPENAI_MODEL` | ID модели |
| `OPENAI_TIMEOUT_SECONDS` | Таймаут вызова модели |

`serve` и Alembic читают корневой `.env`, если он есть. Переменные процесса
важнее файла. Миграции разрешены только для баз `career_quest_dev` и
`career_quest_test`. `scripts/start.py` вызывает тот же `serve` и отдельный
`.env` не читает.

Отдельный backend по-прежнему запускается так:

```powershell
.\.venv\Scripts\python.exe -m backend.career_quest.serve
```

Команда применяет миграции к настроенной локальной БД Career Quest, загружает
dataset и стартует API.

### Frontend

Во втором терминале, если backend уже запущен отдельно:

```powershell
cd frontend
npm run dev
```

Dev-server Vite проксирует `/api` на `http://127.0.0.1:8000`.

Диагностика dataset без сайта:

```powershell
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH EMPLOYEE_ID
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH --audit
```

## Безопасность и приватность

- `.env` в git ignore.
- Ключ OpenAI только на сервере.
- Пароль БД в репозиторий не входит.
- Официальный raw dataset в репозиторий не входит.
- Session cookie `HttpOnly`.
- CSRF на изменяющих запросах.
- Employee не открывает чужой профиль.
- HR-маршруты защищены сервером.
- AI payload не содержит полное имя, отдел, руководителя и сырую историю.

## Known limitations

- Demo-login — hackathon entry, не production authentication.
- Навыки в UI показываются как `skill_id`: API профиля не отдаёт display name.
- Недавняя активность на главной показывает `event_id`.
- Отдельные экраны «Карьерный путь» и «История» не сделаны и не являются
  обязательным сценарием; пункты навигации отключены.
- Deploy не выполнен: Nginx, DNS, systemd и live demo не проверялись.

## Структура

```text
backend/career_quest/   — loader, engine, API, auth, AI, completion, HR
frontend/               — React/Vite клиент
scripts/start.py        — локальный запуск backend и frontend
alembic/                — миграции PostgreSQL
tests/                  — синтетические фикстуры и тесты
docs/PROJECT.md         — требования и утверждённые решения
docs/CHECKPOINT.md      — текущий milestone
docs/API.md             — HTTP-контракт
docs/FRONTEND.md        — состояние клиента
```
