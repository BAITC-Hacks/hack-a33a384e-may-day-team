# Agent rules

Перед изменениями прочитать `README.md`, `docs/PROJECT.md` и
`docs/CHECKPOINT.md`.

`README.md` — canonical source. `README.kz.md` и `README.en.md` разрешены и
входят в финальную сдачу. Они должны соответствовать `README.md`. Команды,
имена переменных, пути и code blocks в переводах не менять.

## Команды

Одна команда локального запуска, после установки зависимостей и `.env`:

```powershell
python scripts/start.py
```

Launcher запускает backend и Vite. Зависимости не устанавливает. Ctrl+C или
Ctrl+Break останавливает оба процесса. Фактический final smoke выполнен на
Windows.

Установка и тесты в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

PostgreSQL-тесты выполняются только когда `DATABASE_URL` указывает на
`career_quest_test`. Без этого они пропускаются и не считаются passed.
Пропуск не записывать как passed. Не складывать разные прогоны в одну цифру.

Диагностика dataset и отдельный backend:

```powershell
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH EMPLOYEE_ID
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH --audit
.\.venv\Scripts\python.exe -m backend.career_quest.serve
```

`serve` и Alembic читают корневой `.env`, если он есть. Уже заданные переменные
процесса важнее файла.

Frontend:

```powershell
cd frontend
npm ci
npm run dev
npm run build
npm run lint
```

Нужен Node 20.19+ либо 22.12+. Контракт API: `docs/API.md`.
`POST /api/auth/demo-login` — hackathon demo, не production authentication.

## Ограничения

- Пользователь утверждает продуктовые и архитектурные решения. Не менять scope,
  стек, data model, API contract, AI-подход или UX без согласования.
- При параллельной работе соблюдать границы backend/frontend и работать в
  назначенном worktree. Не добавлять в staging и не коммитить чужие изменения.
- Общие README и `docs/` согласовывать при объединении параллельных веток.
- Frontend следует утверждённым пользователем макетам. Backend не меняет дизайн
  или API-контракт frontend самостоятельно.
- Не придумывать dataset, события, навыки, требования, результаты тестов,
  метрики, endpoints или готовые интеграции. Не записывать непройденные тесты
  как passed.
- Расчётные факты считает deterministic code. AI не вычисляет skill levels.
  Модель получает только разрешённых candidates.
- Бизнес-дата берётся только из `meta.as_of_date`.
- Официальный dataset передаётся путём и не копируется в repository. Не
  коммитить raw data, DOCX, ZIP, research-отчёты и результаты с профилями.
- Не коммитить `.env`, ключи, токены, пароли и другие секреты.
- Не менять VPS, серверную БД, DNS и deploy без явного разрешения.
- Документация обязана соответствовать фактически работающему коду и
  обновляться после milestone.

После milestone:

1. запустить тесты и релевантный smoke-check;
2. обновить `docs/CHECKPOINT.md` и затронутые README/docs;
3. проверить diff, staged-файлы и отсутствие секретов;
4. сделать осмысленный commit и push, если это разрешено;
5. остановиться для независимой проверки ChatGPT.
