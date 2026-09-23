# Current Checkpoint

Updated: 2026-09-23

Current milestone: backend M1.1 — проверка неоднозначных входных данных

## Goal

Минимально закрыть замечания независимой проверки M1: отклонять повторяющиеся
JSON-ключи, повторяющиеся CSV-заголовки и неконечный `duration_hours`, не меняя
расчётный engine, API-контракты или scope MVP.

## Done

- Работа выполнена в отдельном worktree от `cc9deae`, без изменений frontend
  worktree и `main`.
- До исправления 6 новых regression cases воспроизвели молчаливое принятие
  duplicate JSON keys, duplicate CSV headers и неконечных чисел.
- JSON loader отклоняет повторный ключ на любой глубине объекта и сообщает имя
  файла, поле `json` и повторившийся ключ.
- CSV loader проверяет уникальность заголовков до чтения строк; корректная
  обработка пустых optional fields сохранена.
- `duration_hours` принимает только конечное положительное число; `NaN`,
  `Infinity`, `-Infinity` и overflow вида `1e400` отклоняются.
- `engine.py`, правила карьерного развития, зависимости и API не менялись.
- Frontend разрабатывается отдельно; его состояние M1.1 не проверяет и не
  подтверждает.

## Current architecture

```text
JSON/CSV dataset path
  → validated loader
  → pure Python calculation engine
  → diagnostic CLI

FastAPI
  → GET /api/health only
```

Расчётный модуль не зависит от FastAPI, БД и AI. Текущий стек этапа:
Python 3.10+, FastAPI 0.116.1, Uvicorn 0.35.0, pytest 8.4.1 и HTTPX 0.28.1.

## Changed files

- `backend/career_quest/loader.py`
- `tests/test_loader_cli.py`
- `README.md`
- `AGENTS.md`
- `docs/PROJECT.md`
- `docs/CHECKPOINT.md`

## How to verify

Установка:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Синтетические тесты:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Результат M1.1: `23 passed`; есть одно предупреждение о deprecated alias внутри
Starlette TestClient/AnyIO, не в коде проекта.

Официальный dataset:

```powershell
$DATASET = "C:\path\to\career_quest_dataset"
.\.venv\Scripts\python.exe -m backend.career_quest.cli $DATASET E0001 --audit
```

Smoke-check исходного неизменённого набора успешно подтвердил:

- 60 skills, 32 role profiles, 200 employees, 40 events, 2 743 history records;
- окно истории `2024-10-01`–`2026-09-30`;
- статусы: 2 178 completed, 16 in_progress, 160 dropped, 195 no_show,
  104 declined, 90 overdue;
- заново рассчитано 318 completed-записей после review до бизнес-даты;
- положительный прирост получили 111 сотрудников;
- 308 положительных trace-записей, суммарный прирост уровней 308.

Эти значения получены кодом M1, а не скопированы из research.

Health:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.career_quest.api:app --host 127.0.0.1 --port 8000
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

## Git

Branch: `fix/backend-m1-validation`

Base commit: `cc9deae81f52544bac1541f0c81f7a0ff129a1fd`

Milestone commit message: `fix: reject ambiguous dataset inputs`

Pushed: YES, `origin/fix/backend-m1-validation` (точный SHA смотреть в
`git log`)

REPO VERIFY: PENDING — требуется независимая проверка ChatGPT после push.

Интеграция backend-ветки в `main`: PENDING.

## Deploy

URL: отсутствует

Status: не выполнялся. VPS, серверная PostgreSQL и DNS не изменялись.

## Known issues

- Локальная проверка выполнена на Python 3.12.7.
- Python 3.10: NOT TESTED — этот runtime отсутствует на машине.
- Полный однокомандный запуск, требуемый Halyk, ещё не реализован.
- Frontend выполняется в отдельной ветке/worktree; его готовность не проверена.
- JSON/CSV сущности англоязычные; RU/KZ находятся только в README dataset.
- Исходные повторы `EV_001`–`EV_003` после completed сохранены без исправления.
- Числовые веса, подробная схема БД и точный OpenAI model ID не утверждены.
- Health не означает готовность persistence, auth, AI или полного MVP.

## Decisions

- Продукт: карьерный навигатор Employee с отдельной HR-аналитикой и без
  публичного рейтинга.
- Стек: FastAPI + React/Vite + PostgreSQL; production Nginx + systemd без
  Docker.
- Одно адаптивное русскоязычное веб-приложение; без PWA и native apps сейчас.
- Предсозданные Employee/HR accounts и серверная проверка прав; auth следующим
  этапом.
- Основная цель — следующий грейд текущей роли; cross-role `career_goal`
  показывается отдельно; автоматического повышения нет.
- OpenAI позже сравнивает только допустимые факты; model ID конфигурируется и
  проверяется при интеграции; embeddings/vector DB/custom training не нужны.
- Канонический README русский, KZ/EN версии отложены до финала; все затронутые
  технические документы обновляются.

## Next

Независимо проверить backend M1.1. После проверки отдельно решить интеграцию
`fix/backend-m1-validation` в `main`; автоматический merge/cherry-pick не
выполнялся. Frontend продолжает свой отдельный согласованный этап.
