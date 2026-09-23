# Current Checkpoint

Updated: 2026-09-23

Current milestone: M1 backend + F1 frontend в отдельной ветке

## Goal

Зафиксировать утверждённые продуктовые решения и реализовать проверяемое
детерминированное ядро: загрузка dataset, актуальные навыки, следующий грейд,
разрывы, допустимые candidate facts, диагностическая CLI и минимальный health.
Параллельно, без изменения backend, перенести утверждённую главную сотрудника в
React/Vite для desktop и mobile.

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
- В отдельной frontend-ветке создан React/Vite-интерфейс F1: оболочка, главная
  сотрудника, desktop-сетка и мобильная компоновка с нижней навигацией.
- Один явно маркированный fixture питает desktop/mobile. API, AI, БД и
  серверные расчёты frontend не вызывает и не дублирует.
- В той же frontend-ветке добавлены demo-экраны входа, объяснения, результата
  выполнения, HR-обзора и служебного импорта. Переход выполнения один раз
  переключает заранее подготовленное состояние и не обращается к backend.

## Current architecture

```text
JSON/CSV dataset path
  → validated loader
  → pure Python calculation engine
  → diagnostic CLI

FastAPI
  → GET /api/health only

Synthetic F1 fixture
  → React/Vite employee home
    ├─ desktop shell
    └─ mobile layout
```

Расчётный модуль не зависит от FastAPI, БД и AI. Текущий стек этапа:
Python 3.10+, FastAPI 0.116.1, Uvicorn 0.35.0, pytest 8.4.1 и HTTPX 0.28.1.
Frontend F1 использует React 19, Vite 8 и локальный Inter; связи с API пока нет.

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
- `docs/FRONTEND.md`
- `frontend/`

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

Frontend:

```powershell
cd frontend
npm install
npm run lint
npm run build
npm run dev -- --host 127.0.0.1
```

Визуально проверены viewport 1586×992 и 390×853. На ширинах 360, 768 и
1440 px подтверждено отсутствие горизонтального переполнения.

## Git

Branch: `main`

Parent commit: `a70a3a90a18ca035491de5172f00a547e48fbcbc`

Milestone commit message: `feat: implement verified Career Quest core`

Pushed: YES, `origin/main` (точный SHA намеренно не записан внутрь создаваемого
commit; смотреть `git log`)

REPO VERIFY: PENDING — требуется независимая проверка ChatGPT после push.

Frontend branch: `feat/career-quest-ui`

Frontend base: `cc9deae81f52544bac1541f0c81f7a0ff129a1fd`

Frontend milestone commit: смотреть `git log` (SHA не записывается внутрь
создающего его commit).

Frontend push target: `origin/feat/career-quest-ui`. Фактический результат push
проверяется по remote и финальному отчёту: commit не может достоверно записать
операцию, которая выполняется только после его создания.

FRONTEND VERIFY: PENDING — после F1 требуется независимая проверка commit,
diff и screenshots.

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
- Frontend использует только синтетические данные представления. Auth, API,
  загрузка файлов и серверное выполнение не подключены. Разделы «Путь» и
  «История» остаются без экранов.

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

Визуальный frontend F1–F3 остановлен для проверки ветки. Merge с main не
выполняется. Backend-направление после проверки M1: persistence/API/auth/AI.
