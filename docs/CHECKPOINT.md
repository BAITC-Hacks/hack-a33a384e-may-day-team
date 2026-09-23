# Current Checkpoint

Updated: 2026-09-23

Current milestone: backend M2.1 — хранение, вход и защищённый API

## Goal

Сохранить расчёты M1 и добавить PostgreSQL, сессии Employee/HR, выполнение
активности и HR import/overview. AI и frontend в этот этап не входят.

## Done

- База ветки: `3ed7fd7357442199d31eabbe20bfc6738df9e44a`.
- Loader и engine не переписывались. Новый слой вызывает их расчёты.
- Добавлены SQLAlchemy/Alembic-схема, seed, сессии, CSRF и маршруты из
  `docs/API.md`.
- Новые завершения отделены от исторического replay и применяются даже если
  `last_review_date` совпадает с бизнес-датой.
- Повторный `Idempotency-Key` и повтор scheduled-сессии `EV_036` покрыты
  policy-тестами.
- Исходный dataset не изменяется и не коммитится.

## Verification

Локальный запуск Cursor на Python 3.12.7:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Результат: `30 passed, 5 skipped`. Пять PostgreSQL-тестов пропущены, потому что
локальный PostgreSQL и `DATABASE_URL` отсутствуют. Их нельзя считать
пройденными.

Python 3.10: NOT TESTED.

Официальный dataset smoke повторно дал 318 применимых completed, 111
сотрудников с приростом, 308 trace и суммарный прирост 308. Это проверка
прежнего расчётного ядра, а не PostgreSQL.

DB ACCESS: BLOCKED. Транзакции, сохранение после перезапуска backend и
параллельные completion на PostgreSQL: NOT RUN.

Независимый code review ChatGPT для M1/M1.1 остаётся прежним. M2.1 его ещё не
проходил. Независимый повтор тестового запуска ChatGPT не заявлялся.

## Current architecture

```text
dataset files → loader/engine
PostgreSQL → accounts, sessions, employees, history, idempotency
HTTP API → auth, employee workflow, HR overview/import
```

AI не подключён. Frontend выполняется отдельно и здесь не проверялся.

## Changed files

- `backend/career_quest/api.py`
- `backend/career_quest/errors.py`
- `backend/career_quest/http_api.py`
- `backend/career_quest/orm.py`
- `backend/career_quest/security.py`
- `backend/career_quest/serve.py`
- `backend/career_quest/settings.py`
- `backend/career_quest/store.py`
- `backend/career_quest/workflow.py`
- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/20260923_0001_initial.py`
- `requirements.txt`
- `.env.example`
- `tests/test_api.py`
- `tests/test_m2_policy.py`
- `tests/test_postgres_workflow.py`
- `README.md`
- `AGENTS.md`
- `docs/API.md`
- `docs/PROJECT.md`
- `docs/CHECKPOINT.md`

## Git

Branch: `feat/backend-m2-api`

Base commit: `3ed7fd7357442199d31eabbe20bfc6738df9e44a`

Commit message: `feat: add persistent employee workflow and protected API`

Pushed: YES, только `origin/feat/backend-m2-api`.

Интеграция в `main`: не выполнена.

REPO VERIFY: PENDING — commit после push ожидает независимой проверки ChatGPT.

## Deploy

Не выполнялся. VPS, серверная БД, DNS и Nginx не изменялись.

## Known issues

- DB ACCESS: BLOCKED; нужен локальный PostgreSQL для `career_quest_dev` или
  `career_quest_test`.
- PostgreSQL durability/concurrency: NOT RUN.
- Python 3.10: NOT TESTED.
- Полный однокомандный запуск сайта не реализован.
- Frontend не проверялся.
- Числовые веса ранжирования и точный AI model ID не утверждены.

## Decisions

Утверждённые решения M1 сохранены: следующий грейд текущей роли, без
автоматического повышения, без рекомендации mandatory и без подмены цели
межролевым `career_goal`.

## Next

Подключить AI к уже допустимым candidate facts, затем соединить проверенный
backend с отдельным frontend и настроить полный запуск.
