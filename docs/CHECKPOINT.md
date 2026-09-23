# Current Checkpoint

Updated: 2026-09-23

Current milestone: M1 — утверждённый MVP и первое рабочее backend-ядро

## Goal

Зафиксировать утверждённые продуктовые решения и реализовать проверяемое
детерминированное ядро: загрузка dataset, актуальные навыки, следующий грейд,
разрывы, допустимые candidate facts, диагностическая CLI и минимальный health.

## Done

- Решения пользователя отделены от требований Halyk, фактов dataset и
  нереализованных частей в `docs/PROJECT.md`.
- Загрузчик читает четыре реальных файла из переданного каталога, проверяет
  структуру, обязательные поля, уникальность ID, ссылки, enum/status, даты и
  диапазоны уровней. Ошибка содержит файл, запись, поле и причину.
- ID и объёмы не ограничены исходными `E0001–E0200`/200 сотрудниками.
- Актуальные навыки пересчитываются от assessment на `last_review_date` по
  `completed` в окне `last_review_date < date <= meta.as_of_date`.
- Прирост стабилен, не понижает навык, не превышает event `max_level`, сохраняет
  trace и не удваивается при повторном вызове.
- Основная траектория — следующий грейд текущей роли. `career_goal` возвращается
  отдельно; Lead не получает выдуманную цель.
- Возвращаются все требования целевого role profile с current/required/missing
  и признаком critical.
- Кандидаты проверяются по mandatory, аудитории, prerequisites, `in_progress`,
  прошлому `completed`, исключению `EV_036`, доступной сессии и полезному
  приросту целевого разрыва.
- `no_show`/`declined`/`dropped` не блокируют рекомендации; возвращаются
  фактические счётчики по событию и связанным навыкам.
- Нет числовых весов и итогового AI-ранжирования: выход честно обозначен как
  candidate facts.
- CLI выводит актуальные навыки, trace, цель, разрывы, кандидатов и причины
  исключения; режим `--audit` пересчитывает агрегаты.
- FastAPI публикует только `GET /api/health`.
- 17 тестов используют только самостоятельно созданные синтетические фикстуры.

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

- `.gitignore`
- `README.md`
- `AGENTS.md`
- `requirements.txt`
- `requirements-dev.txt`
- `backend/__init__.py`
- `backend/career_quest/__init__.py`
- `backend/career_quest/models.py`
- `backend/career_quest/loader.py`
- `backend/career_quest/engine.py`
- `backend/career_quest/cli.py`
- `backend/career_quest/api.py`
- `tests/conftest.py`
- `tests/test_engine.py`
- `tests/test_loader_cli.py`
- `tests/test_api.py`
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

Результат M1: `17 passed`; есть одно предупреждение о deprecated alias внутри
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

Branch: `main`

Parent commit: `a70a3a90a18ca035491de5172f00a547e48fbcbc`

Milestone commit message: `feat: implement verified Career Quest core`

Pushed: YES, `origin/main` (точный SHA намеренно не записан внутрь создаваемого
commit; смотреть `git log`)

REPO VERIFY: PENDING — требуется независимая проверка ChatGPT после push.

## Deploy

URL: отсутствует

Status: не выполнялся. VPS, серверная PostgreSQL и DNS не изменялись.

## Known issues

- Локальная проверка выполнена на Python 3.12.7; код и закреплённые прямые
  зависимости совместимы с Python 3.10+, но Python 3.10 отсутствует на этой
  машине.
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

После независимой проверки M1: persistence/API/auth/AI, затем интерфейс.
HTTP completion, транзакции и защита от двойного нажатия относятся к следующему
этапу.
