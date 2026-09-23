# Current Checkpoint

Updated: 2026-09-23

Current milestone: E2E integration complete / finalization.

Документ фиксирует integration commit
`29ab9f659da1bcd02774994746078aedb748bfd6`.
Параллельный frontend fallback hotfix в этот commit не входит.

## Commits

- backend base: `601d96d9d18fc92ddeb8068b3fa4a4ef25d87137`
- frontend: `30608c2e355917e68847f630dae63368aabd7752`
- integration: `29ab9f659da1bcd02774994746078aedb748bfd6`

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

Integration-проход этого commit без подключённой test DB:
`40 passed`, `5 skipped`.

Пять PostgreSQL integration tests ранее отдельно прошли на PostgreSQL 14.24.
Суммы «45 tests passed» в документах нет.

Проверенный runtime того PostgreSQL-прогона: Python 3.12.7. Отдельный прогон
на Python 3.10 в checkpoint не зафиксирован.

Frontend: `npm run build` — PASS.

Live AI smoke, зафиксированный на backend milestone: модель `gpt-5.6-terra`,
`used_ai=true`, latency 7883 ms, три ID из candidate set. Это не утверждение,
что выбор модели всегда лучший.

## Known

- UI показывает `skill_id`: display name навыка в API профиля нет.
- Недавняя активность на главной показывает `event_id`.
- Demo-login — hackathon-specific. Production authentication им не является.
- На этом commit карточка рекомендации и Complete доступны только при
  `used_ai=true`. Server-ranked fallback UI не показывает. Final UX hotfix
  выполняется параллельно и в этот docs-commit не входит.
- Deploy не выполнен.
- One-command launcher для всего приложения отсутствует. Backend и frontend
  запускаются отдельно.
- Экраны «Карьерный путь» и «История» не реализованы и не входят в обязательный
  сценарий.

## Repo verify

Integration commit `29ab9f6` был независимо проверен ChatGPT.

Финальный frontend fallback hotfix ожидается отдельно.

Этот docs-commit после push ожидает независимой проверки. REPO VERIFY: PENDING.

## Deploy

Приложение не разворачивалось. Nginx, DNS и systemd для Career Quest не
настраивались и не проверялись.
