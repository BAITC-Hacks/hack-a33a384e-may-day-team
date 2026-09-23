# Career Quest frontend

Состояние клиента после fallback `014d6c5d20dd005af2f5a4987130922ebd343c82`
и UX `7c22ccd557d894ddeccd4148f4e23a2f4fa55d37`.

## Что подключено к API

`frontend/src/api/client.js` вызывает backend с cookie-сессией и CSRF.

- `POST /api/auth/demo-login` — кнопки Employee и HR. Это hackathon demo entry.
- `GET /api/auth/me` — восстановление сессии.
- `GET /api/employees/{id}` — профиль, грейд, gaps, история.
- `GET /api/employees/{id}/recommendations` — рекомендация.
- `POST .../complete` — серверное завершение и следующий пересчёт.
- `GET /api/hr/overview` — частые gaps, сотрудники без следующего шага, участие.
- `POST /api/hr/import` — JSON профилей и CSV истории.

Профиль, рекомендация, completion, HR и import не читаются из demo fixture.
Файла `demoDashboard.js` в `frontend/src` нет.

## Что осталось представлением

- Навыки и разрывы рисуются как `skill_id`. Display name в ответе профиля нет.
- Недавняя активность на главной показывает `event_id` и статус, не название
  события.
- «Карьерный путь» и «История» стоят в навигации с `aria-disabled`. Отдельных
  экранов нет. Это не обязательный сценарий кейса.
- Главная берёт первую рекомендацию, если массив не пуст. `used_ai=true`
  подписан как AI. `fallback_ranked` подписан «Рекомендуемый шаг» и не
  называется AI. Complete отправляется для показанной активности. Пустой
  список показывает «Рекомендация временно недоступна».
- Экран входа не содержит форму username/password. Такой login на сервере есть;
  клиент demo использует только demo-login.

## Стек

- React 19
- Vite 8
- обычный CSS
- Inter через `@fontsource-variable/inter`
- локальные SVG-иконки

Основные файлы:

```text
frontend/src/App.jsx            — сессия, главная, навигация
frontend/src/screens.jsx        — login, объяснение, completion, HR, import
frontend/src/api/client.js      — HTTP-клиент
frontend/src/recommendationView.js — выбор первой рекомендации и подпись
frontend/src/App.css            — desktop, tablet и mobile
frontend/vite.config.js         — proxy /api → 127.0.0.1:8000
```

## Запуск

Обычный запуск из корня репозитория: `python scripts/start.py`. Он поднимает
backend и этот dev server. Зависимости нужно установить заранее.

Отдельный frontend:

```powershell
cd frontend
npm install
npm run dev
```

Сборка и lint этого прогона: `npm run build` — PASS, `npm run lint` — PASS.

Browser smoke того же milestone: Employee, completion, HR, import, mobile —
PASS.
