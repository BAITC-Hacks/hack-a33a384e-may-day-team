# Career Quest setup

Установка с чистого ПК. Команды рассчитаны на репозиторий Career Quest. Raw official dataset в git не хранится и в эту инструкцию не копируется.

Dataset синтетический. Подтверждённые размеры: 60 skills, 32 role profiles, 200 employees, 40 events, 2743 history rows.

`DATASET_PATH` указывает на папку. В ней обязательно четыре файла:

```text
career_quest_dataset/
├── skills.json
├── employees.json
├── events.json
└── activity_history.csv
```

# Windows quick start

## Prerequisites

- Git
- Python 3.10+
- PostgreSQL
- Node 20.19+ или >=22.12
- npm
- dataset

## 1. Clone

```powershell
git clone <repository-url>
cd <repository-directory>
```

## 2. Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Для тестов дополнительно: `pip install -r requirements-dev.txt`.

## 3. Frontend

```powershell
cd frontend
npm ci
cd ..
```

`npm ci` ставит зависимости по lockfile. Launcher сам их не устанавливает.

## 4. PostgreSQL

Текущий safety guard разрешает только базы `career_quest_dev` и `career_quest_test`. Другие имена backend отклоняет.

Пример через `psql`:

```sql
CREATE USER career_quest WITH PASSWORD 'CHANGE_ME';
CREATE DATABASE career_quest_dev OWNER career_quest;
```

Для integration-тестов нужна отдельная база `career_quest_test` с тем же владельцем. Не подставляйте в `DATABASE_URL` другое имя базы.

## 5. Dataset

Положите четыре файла в одну папку и укажите эту папку в `DATASET_PATH`.

## 6. ENV

```powershell
Copy-Item .env.example .env
```

Заполните `.env`. Файл в git ignore. Реальные пароли и ключ OpenAI не коммитить.

`serve` и Alembic читают корневой `.env`, если он есть. Переменные процесса важнее файла.

### Переменные

`DATABASE_URL` — обязательна для рабочего запуска. Назначение: подключение SQLAlchemy/psycopg к локальной базе Career Quest.

```text
postgresql+psycopg://career_quest:CHANGE_ME@127.0.0.1:5432/career_quest_dev
```

`DATASET_PATH` — обязательна для рабочего запуска. Назначение: путь к папке четырёх файлов, не к одному JSON.

```text
C:/path/to/career_quest_dataset
```

`ALLOWED_ORIGINS` — optional. Назначение: разрешённые Origin для запросов с cookie. Default: `http://127.0.0.1:5173,http://localhost:5173`. Локальный пример совпадает с default.

`COOKIE_SECURE` — optional. Назначение: флаг `Secure` у session cookie. Локально `false`. Для HTTPS production — `true`. Default: `false`.

`SESSION_TTL_HOURS` — optional. Назначение: срок серверной сессии в часах. Default: `12`.

Demo accounts. Если хотя бы одна `DEMO_*` задана, должны быть заполнены все:

- `DEMO_EMPLOYEE_ONE_USERNAME`
- `DEMO_EMPLOYEE_ONE_PASSWORD`
- `DEMO_EMPLOYEE_ONE_ID`
- `DEMO_EMPLOYEE_TWO_USERNAME`
- `DEMO_EMPLOYEE_TWO_PASSWORD`
- `DEMO_EMPLOYEE_TWO_ID`
- `DEMO_HR_USERNAME`
- `DEMO_HR_PASSWORD`

`DEMO_EMPLOYEE_ONE_ID` и `DEMO_EMPLOYEE_TWO_ID` должны существовать в загруженном dataset. Пароли — локальные demo-значения, не из репозитория. Без полного demo config кнопка demo-login получает `configuration_error`. Обычный `POST /api/auth/login` от demo-конфига не зависит.

`OPENAI_API_KEY` — optional, server-only. Назначение: ключ OpenAI Responses API. Если ключ отсутствует, приложение продолжает работать через `fallback_ranked`. Пример: оставить пустым или подставить ключ только в локальный `.env`.

`OPENAI_MODEL` — optional. Назначение: ID модели. Default: `gpt-5.6-terra`. Live smoke использовал это значение.

`OPENAI_TIMEOUT_SECONDS` — optional. Назначение: таймаут вызова модели в секундах. Default: `7`.

Frontend secrets не нужны. `VITE_OPENAI_KEY` и `VITE_DATABASE_URL` не требуются и быть не должны.

## 7. Одна команда

Из корня репозитория, с активированным `.venv` или тем `python`, где установлены зависимости:

```powershell
python scripts/start.py
```

Команда запускает backend (`python -m backend.career_quest.serve`) и Vite на `127.0.0.1:5173`. `serve` применяет миграции Alembic к настроенной базе и загружает dataset. Зависимости команда не устанавливает.

Откройте `http://127.0.0.1:5173`.

Проверка:

- `http://127.0.0.1:8000/api/health` — процесс backend. Ожидаемый ответ при живом процессе: HTTP 200.
- `http://127.0.0.1:8000/api/ready` — соединение с PostgreSQL. Ожидаемый ответ при доступной базе: HTTP 200. Если база недоступна, backend отвечает 503 `database_unavailable`.

Остановка: Ctrl+C или Ctrl+Break. Final smoke на Windows: backend started, frontend started, оба URL вернули 200, после остановки порты 8000 и 5173 закрылись.

Launcher реализован cross-platform. Фактический final smoke выполнен на Windows. Отдельный Linux launcher smoke в этом checkpoint не зафиксирован.

Отдельный backend, если frontend уже запущен иначе:

```powershell
.\.venv\Scripts\python.exe -m backend.career_quest.serve
```

Отдельный frontend, когда backend слушает порт 8000:

```powershell
cd frontend
npm run dev
```

Dev-server проксирует `/api` на `http://127.0.0.1:8000`.

## 8. Сценарий Employee / HR

1. Открыть `http://127.0.0.1:5173`.
2. Employee: demo login, профиль, next grade, gaps, рекомендация, WHY THIS, NOT THAT, Complete и пересчёт, если сервер вернул рекомендацию.
3. HR: gaps, employees without next step, participation, import JSON профилей и CSV истории.

`fallback_ranked` в интерфейсе не подписан как AI. Пустой список и `not_applicable` означают, что для этого профиля допустимого следующего шага нет.

Диагностика dataset без сайта:

```powershell
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH EMPLOYEE_ID
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH --audit
```

## 9. Build и тесты

Frontend:

```powershell
cd frontend
npm ci
npm run build
npm run lint
```

Final assembly: `npm run lint` PASS, `npm run build` PASS.

Backend:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest -q
```

Final assembly: `40 passed`, `5 skipped`. Причина skip: `DATABASE_URL` не указывал на `career_quest_test`.

Ранее PostgreSQL milestone: `42 passed`, `0 skipped`. Пять PostgreSQL integration tests проходили на PostgreSQL 14.24. Результаты прогонов не суммируются.

## Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend
npm ci
cd ..

python scripts/start.py
```

PostgreSQL, dataset и `.env` готовятся так же, как на Windows. `psql` и путь в `DATASET_PATH` зависят от машины. Launcher реализован cross-platform; фактический final smoke выполнен на Windows.

## Безопасность

- `.env` ignored.
- Secrets never committed.
- OpenAI key backend-only.
- DB password остаётся в локальном `.env` или на сервере.
- Raw official dataset excluded.
- HttpOnly session, CSRF, role authorization.
- Employee cannot access another employee.
- HR endpoints защищены на сервере.
- AI payload не содержит полное имя, отдел, руководителя и сырую историю.
