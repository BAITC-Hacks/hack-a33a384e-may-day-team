# Career Quest frontend

Текущий клиент ходит в реальный backend. Файла `frontend/src/data/demoDashboard.js` нет. Профиль, рекомендация, completion, HR и import не читаются из fixture.

## Integration

`frontend/src/api/client.js` вызывает backend с cookie-сессией и CSRF.

- `POST /api/auth/demo-login` — кнопки Employee и HR. Это hackathon demo entry.
- `GET /api/auth/me` — восстановление сессии.
- `GET /api/employees/{id}` — профиль, грейд, gaps, история.
- `GET /api/employees/{id}/recommendations` — рекомендация.
- `POST .../complete` — серверное завершение и следующий пересчёт.
- `GET /api/hr/overview` — частые gaps, сотрудники без следующего шага, участие.
- `POST /api/hr/import` — multipart JSON профилей и CSV истории.

## Fallback UI

Непустой список рекомендаций показывается и для `fallback_ranked`. `used_ai=true` подписан «AI · Рекомендуемый шаг». `fallback_ranked` подписан «Рекомендуемый шаг» и не называется AI. Пустой список показывает «Рекомендация временно недоступна». Detail, сравнение и Complete работают для показанной активности, включая fallback.

## Layout

Один адаптивный клиент:

- mobile `<768`
- tablet `768–1199`
- desktop `>=1200`

Исправлена desktop-раскладка на ширине 1280. Смена экрана сбрасывает scroll, кроме возврата к карточке рекомендации. Выбранная альтернатива открывается в detail. С экрана HR import есть возврат на HR overview.

## Что осталось представлением

- Навыки и разрывы рисуются как `skill_id`. Display name в ответе профиля нет.
- Недавняя активность на главной показывает `event_id` и статус.
- «Карьерный путь» и «История» стоят в навигации с `aria-disabled`. Отдельных экранов нет.
- Экран входа не содержит форму username/password. Такой login на сервере есть; клиент demo использует только demo-login.

## Стек и файлы

- React 19
- Vite 8
- CSS
- Inter через `@fontsource-variable/inter`
- локальные SVG-иконки

```text
frontend/src/App.jsx               — сессия, главная, навигация, scroll
frontend/src/screens.jsx           — login, объяснение, completion, HR, import
frontend/src/api/client.js         — HTTP-клиент
frontend/src/recommendationView.js — выбор первой рекомендации и подпись
frontend/src/App.css               — desktop, tablet и mobile
frontend/vite.config.js            — proxy /api → 127.0.0.1:8000
```

## Запуск и проверки

Обычный запуск из корня: `python scripts/start.py`. Зависимости ставятся заранее через `npm ci`.

```powershell
cd frontend
npm ci
npm run dev
npm run build
npm run lint
```

Final assembly: `npm run build` PASS, `npm run lint` PASS.

Earlier integration browser smoke: Employee, completion, HR, import, mobile — PASS.

Final UX smoke: HR PASS. Employee completion повторно не выполнялся, потому что persisted demo profile вернул `not_applicable` / empty recommendations. Это не зафиксировано как функциональный regression.
