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
.\.venv\Scripts\python.exe -m uvicorn backend.career_quest.api:app --host 127.0.0.1 --port 8000
```

## Ограничения

- Пользователь утверждает продуктовые и архитектурные решения. Не менять scope,
  стек, data model, API contract, AI-подход или UX без согласования.
- Не придумывать dataset, события, навыки, требования, результаты тестов,
  метрики, endpoints или готовые интеграции.
- Расчётные функции сохранять независимыми от FastAPI, PostgreSQL и OpenAI.
- Бизнес-дата берётся только из `meta.as_of_date`.
- Официальный dataset передаётся путём и не копируется в repository. Не
  коммитить raw data, DOCX, ZIP, research-отчёты и результаты с профилями.
- Не коммитить `.env`, ключи, токены, пароли и другие секреты.
- Не менять VPS, серверную БД, DNS и deploy без отдельного задания.
- Документация обязана соответствовать фактически работающему коду.

`README.md` — канонический русский README. До финального этапа не создавать и не
обновлять `README.kz.md`/`README.en.md`. Это языковое правило не отменяет
обновление всех затронутых технических документов: `AGENTS.md`,
`docs/PROJECT.md` и `docs/CHECKPOINT.md`.

После milestone:

1. запустить тесты и релевантный smoke-check;
2. обновить `docs/CHECKPOINT.md`;
3. проверить diff, staged-файлы и отсутствие секретов;
4. сделать осмысленный commit и push, если это разрешено;
5. остановиться для независимой проверки ChatGPT.
