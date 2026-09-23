# Career Quest frontend

React/Vite клиент integration commit
`29ab9f659da1bcd02774994746078aedb748bfd6`.

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
- карточка рекомендации и Complete рисуются только при `used_ai=true`;
  ответ `fallback_ranked` показывается как «Рекомендация временно недоступна».

Подробности: [`../docs/FRONTEND.md`](../docs/FRONTEND.md).

## Запуск

Нужен уже запущенный backend и Node 20.19+ либо 22.12+.

```powershell
cd frontend
npm install
npm run dev
```

Проверка сборки:

```powershell
npm run build
```

`npm run build` на integration milestone — PASS.
