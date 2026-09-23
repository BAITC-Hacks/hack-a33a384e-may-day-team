# Career Quest deployment

Infrastructure prepared. Career Quest final build is not claimed as publicly deployed until a live smoke is actually performed.

Этот документ не описывает выполненный production deploy.

## Prepared infrastructure

- VPS: Ubuntu 22.04
- Nginx установлен
- HTTPS / Let's Encrypt подготовлен
- PostgreSQL установлен
- Domain prepared: `hack.qazentra.com`

## Preferred architecture

```text
Nginx
  → static React build
  → /api proxy → Uvicorn/FastAPI
  → PostgreSQL
```

systemd planned for the backend. Docker deliberately not required for MVP.

Локальный safety guard по-прежнему разрешает приложению только базы `career_quest_dev` и `career_quest_test`. Production URL, пароль и `OPENAI_API_KEY` остаются на сервере, не в git.

`COOKIE_SECURE=true` предназначен для HTTPS. `ALLOWED_ORIGINS` на публичном сайте должен совпадать с реальным origin фронтенда.

Сборка статики:

```powershell
cd frontend
npm ci
npm run build
```

Каталог сборки Vite — `frontend/dist`. Этот репозиторий не содержит настроенный unit-файл systemd и не фиксирует, что `frontend/dist` уже выложен на VPS.

## Dataset

Raw official dataset must not be published to a public VPS without organizer confirmation. `DATASET_PATH` на сервере должен указывать на приватную папку с `skills.json`, `employees.json`, `events.json` и `activity_history.csv`.

## Status

Infrastructure prepared.

Career Quest final build is NOT claimed as publicly deployed until live smoke is actually performed. Проверка Nginx, сертификата, systemd и публичного домена для этого приложения в final assembly не выполнялась.
