# Career Quest frontend

Состояние клиента на integration commit
`29ab9f659da1bcd02774994746078aedb748bfd6`.

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
- Главная и Complete берут первую рекомендацию только если `used_ai === true`.
  При `fallback_ranked` карточка пишет «Рекомендация временно недоступна», и
  Complete не отправляется. Сервер fallback при этом считает. Показ этого
  ответа — предмет параллельного frontend hotfix, не этого commit.
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
frontend/src/App.css            — desktop/mobile
frontend/vite.config.js         — proxy /api → 127.0.0.1:8000
```

## Запуск

Node 20.19+ либо 22.12+. Backend должен слушать порт 8000.

```powershell
cd frontend
npm install
npm run dev
```

Сборка: `npm run build`. На integration milestone сборка прошла.

Browser smoke того же milestone: Employee, completion, HR, import, mobile —
PASS.
