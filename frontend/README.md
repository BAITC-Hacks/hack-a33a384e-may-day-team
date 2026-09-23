# Career Quest frontend

React/Vite клиент после fallback `014d6c5` и UX `7c22ccd`.

Клиент ходит в backend через `frontend/src/api/client.js`. Dev-server
проксирует `/api` на `http://127.0.0.1:8000`.

С сервера читаются:

- demo-login и текущая сессия;
- профиль сотрудника;
- recommendations;
- completion;
- HR overview;
- import employees JSON и history CSV.

`frontend/src/data/demoDashboard.js` в этом дереве нет. Core-data с fixture не
берутся.

Остатки представления на этом commit:

- gaps и прогноз показывают `skill_id`, не display name;
- блок недавней активности показывает `event_id`;
- пункты «Карьерный путь» и «История» есть в навигации и отключены;
- непустая рекомендация показывается и при `fallback_ranked`, без AI-подписи.

Подробности: [`../docs/FRONTEND.md`](../docs/FRONTEND.md).

## Запуск

Обычный запуск из корня: `python scripts/start.py`.

Отдельный frontend, когда backend уже слушает порт 8000. Нужен Node 20.19+
либо 22.12+. Зависимости launcher не устанавливает.

```powershell
cd frontend
npm install
npm run dev
```

Проверка сборки:

```powershell
npm run build
```

`npm run lint` и `npm run build` на final assembly — PASS.
