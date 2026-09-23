# Career Quest frontend

React 19 / Vite 8 клиент. Данные берутся из backend через `frontend/src/api/client.js`. Dev-server проксирует `/api` на `http://127.0.0.1:8000`.

`frontend/src/data/demoDashboard.js` в этом дереве нет.

Обычный запуск из корня репозитория:

```powershell
python scripts/start.py
```

Launcher зависимости не устанавливает. Нужен Node 20.19+ либо 22.12+.

Воспроизводимая установка, сборка и lint:

```powershell
cd frontend
npm ci
npm run build
npm run lint
```

Отдельный dev-server, когда backend уже слушает порт 8000:

```powershell
npm run dev
```

`npm run lint` и `npm run build` на final assembly — PASS.

Подробности экранов, fallback UI и browser smoke: [`../docs/FRONTEND.md`](../docs/FRONTEND.md).
