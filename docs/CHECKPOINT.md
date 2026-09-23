# Current Checkpoint

Updated: 2026-09-23

Current milestone: E2E integration complete / finalization.

Документ фиксирует final assembly поверх:

- backend base: `601d96d9d18fc92ddeb8068b3fa4a4ef25d87137`
- frontend: `30608c2e355917e68847f630dae63368aabd7752`
- integration: `29ab9f659da1bcd02774994746078aedb748bfd6`
- integration fallback: `014d6c5d20dd005af2f5a4987130922ebd343c82`
- UX: `7c22ccd557d894ddeccd4148f4e23a2f4fa55d37`
- docs source: `b90defe25dc6b78a22c3c34681ceabf12a3f7087`

## Работает

- demo Employee/HR login через `POST /api/auth/demo-login`
- обычный username/password login
- профиль сотрудника
- AI recommendation endpoint
- completion и повторное чтение профиля/рекомендации
- HR overview
- import JSON + CSV
- frontend production build
- browser smoke по отчёту integration milestone: Employee, completion, HR,
  import, mobile

## Verification

M2.2 backend при подключённой PostgreSQL test DB: `42 passed`, `0 skipped`.

Final assembly без test DB: `40 passed`, `5 skipped`. Пять PostgreSQL tests
не запускались, потому что `DATABASE_URL` не указывал на `career_quest_test`.
Skipped не входят в passed.

Проверенный runtime этого прогона: Python 3.12.7. Отдельный прогон на
Python 3.10 в checkpoint не зафиксирован.

Frontend этого прогона: `npm run lint` — PASS, `npm run build` — PASS.

`python scripts/start.py`: backend и Vite стартовали. `GET /api/health` — 200.
`GET /api/ready` при настроенной локальной DB — 200. Frontend открылся через
Vite. Ctrl+Break закрыл оба процесса и оба порта.

Live AI smoke, зафиксированный на backend milestone: модель `gpt-5.6-terra`,
`used_ai=true`, latency 7883 ms, три ID из candidate set. Это не утверждение,
что выбор модели всегда лучший.

## Known

- UI показывает `skill_id`: display name навыка в API профиля нет.
- Недавняя активность на главной показывает `event_id`.
- Demo-login — hackathon-specific. Production authentication им не является.
- На этом commit непустой список рекомендаций показывается и для
  `fallback_ranked`. Метка AI остаётся только при `used_ai=true`.
- Deploy не выполнен.
- Локальный запуск: `python scripts/start.py`. Launcher не устанавливает
  зависимости и не заменяет setup.
- Экраны «Карьерный путь» и «История» не реализованы и не входят в обязательный
  сценарий.

## Repo verify

Integration commit `29ab9f6` был независимо проверен ChatGPT. Fallback UI
`014d6c5` и UX `7c22ccd` вошли в эту ветку до final assembly.

Этот commit после push ожидает независимой проверки. REPO VERIFY: PENDING.

## Deploy

Приложение не разворачивалось. Nginx, DNS и systemd для Career Quest не
настраивались и не проверялись.
