# Agent rules

Перед изменениями прочитать `README.md`, `docs/PROJECT.md` и
`docs/CHECKPOINT.md`.

## Команды

Установка и тесты в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Диагностика dataset и локальный backend:

```powershell
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH EMPLOYEE_ID
.\.venv\Scripts\python.exe -m backend.career_quest.cli DATASET_PATH --audit
.\.venv\Scripts\python.exe -m backend.career_quest.serve
```

`serve` и Alembic читают корневой `.env`, если он есть. Уже заданные переменные
процесса важнее файла. Нужны `DATABASE_URL`, `DATASET_PATH` и демо-учётные
записи. PostgreSQL-тесты выполняются только когда `DATABASE_URL` указывает на
`career_quest_test`; без URL они пропускаются и не считаются пройденными.
Пропуск не записывать как passed.

Frontend, когда backend уже слушает порт 8000:

```powershell
cd frontend
npm install
npm run dev
npm run build
```

Одной команды на backend и frontend нет. Контракт API: `docs/API.md`.
`POST /api/auth/demo-login` — hackathon demo, не production authentication.

## Ограничения

- Пользователь утверждает продуктовые и архитектурные решения. Не менять scope,
  стек, data model, API contract, AI-подход или UX без согласования.
- При параллельной работе соблюдать границы backend/frontend и работать в
  назначенном worktree. Не добавлять в staging и не коммитить чужие изменения.
- Общие `README.md`, `docs/PROJECT.md` и `docs/CHECKPOINT.md` согласовывать при
  объединении параллельных веток.
- Frontend следует утверждённым пользователем макетам. Backend не меняет дизайн
  или API-контракт frontend самостоятельно.
- Не придумывать dataset, события, навыки, требования, результаты тестов,
  метрики, endpoints или готовые интеграции.
- Расчётные функции сохранять независимыми от FastAPI, PostgreSQL и OpenAI.
- Бизнес-дата берётся только из `meta.as_of_date`.
- Официальный dataset передаётся путём и не копируется в repository. Не
  коммитить raw data, DOCX, ZIP, research-отчёты и результаты с профилями.
- Не коммитить `.env`, ключи, токены, пароли и другие секреты.
- Не менять VPS, серверную БД, DNS и deploy без отдельного задания.
- Документация обязана соответствовать фактически работающему коду.

`README.md` — канонический русский README. `README.kz.md` и `README.en.md` не
создавать. Это языковое правило не отменяет обновление затронутых технических
документов: `AGENTS.md`, `docs/PROJECT.md`, `docs/CHECKPOINT.md`,
`docs/FRONTEND.md` и `frontend/README.md`.

После milestone:

1. запустить тесты и релевантный smoke-check;
2. обновить `docs/CHECKPOINT.md`;
3. проверить diff, staged-файлы и отсутствие секретов;
4. сделать осмысленный commit и push, если это разрешено;
5. остановиться для независимой проверки ChatGPT.
