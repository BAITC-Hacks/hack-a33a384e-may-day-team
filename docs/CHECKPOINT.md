# Current Checkpoint

Updated: 2026-09-23

Current milestone: backend M2.1B — PostgreSQL проверен, контракт API уточнён

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
- Кандидаты отдают каталожные `type`, `format`, `duration_hours` и
  `upcoming_sessions`.
- Флаг профиля называется `career_goal_differs_from_primary_target` и не меняет
  primary target.

## Verification

M2.1 PostgreSQL: VERIFIED.

Локальной службы PostgreSQL нет. VPS `194.32.141.87` использовался только как
изолированный PostgreSQL host. Созданы `career_quest_dev` и `career_quest_test`,
owner `career_quest_app`. База `hackathon` не изменялась. Порт 5432 слушает
только localhost на VPS; наружу он не открывался. С локальной машины доступ
шёл через SSH-туннель `127.0.0.1:55432`.

PostgreSQL: 14.24. Python: 3.12.7. Python 3.10: NOT TESTED.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Результат при `DATABASE_URL` на `career_quest_test`: `35 passed`, skipped
PostgreSQL-тестов нет. Пять интеграционных тестов заменяют прежние заглушки:
вход и права, сохранение и idempotency, два параллельных completion, одна
scheduled-сессия `EV_036`, атомарный импорт.

Ручной smoke на `career_quest_dev`: `GET /api/ready` вернул 200, completion
сохранился после перезапуска backend, повторный seed того же dataset не сбросил
прогресс, другой dataset вернул `dataset_conflict`.

Официальный dataset до новых app-actions: 318 / 111 / 308 / 308.

Независимый code review ChatGPT для M1/M1.1 остаётся прежним. M2.1B его ещё не
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

Previous commit: `f070d34078189fcbe566879bd7102a238bb0cbfd`

Commit message: `fix: verify persistent workflow on PostgreSQL`

Pushed: YES, только `origin/feat/backend-m2-api`.

Интеграция в `main`: не выполнена.

REPO VERIFY: PENDING — commit после push ожидает независимой проверки ChatGPT.

## Deploy

Приложение не разворачивалось. Nginx, DNS и systemd не изменялись. На VPS
созданы только две базы Career Quest и отдельная role.

## Known issues

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
