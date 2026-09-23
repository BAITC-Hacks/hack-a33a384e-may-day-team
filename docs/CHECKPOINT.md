# Current Checkpoint

Updated: 2026-09-23

Current branch: `final/submission`

Assembly before this documentation pass: `23abab7f76b71e36683cb41a858835073c18d55b`

This documentation commit is the HEAD of `final/submission` after `docs: finalize submission documentation`. Its parent is the assembly SHA above.

## Milestone SHA

- backend: `601d96d9d18fc92ddeb8068b3fa4a4ef25d87137`
- frontend: `30608c2e355917e68847f630dae63368aabd7752`
- integration: `29ab9f659da1bcd02774994746078aedb748bfd6`
- fallback: `014d6c5d20dd005af2f5a4987130922ebd343c82`
- UX: `7c22ccd557d894ddeccd4148f4e23a2f4fa55d37`
- docs source: `b90defe25dc6b78a22c3c34681ceabf12a3f7087`
- assembly: `23abab7f76b71e36683cb41a858835073c18d55b`

## Works on final/submission

- Employee/HR demo login
- profile, trajectory, next-grade requirements
- deterministic candidate engine
- OpenAI recommendation 1–3, explanation, fallback
- completion, progress recalculation, refreshed recommendations
- HR overview and multipart import
- responsive frontend
- `python scripts/start.py`

## Verification

Final assembly without `DATABASE_URL` on `career_quest_test`: `40 passed`, `5 skipped`. Пять PostgreSQL tests не запускались. Skipped не входят в passed.

Earlier PostgreSQL milestone with `DATABASE_URL` on `career_quest_test`: `42 passed`, `0 skipped`. Пять PostgreSQL integration tests проходили на PostgreSQL 14.24. Прогоны не суммируются.

Проверенный runtime Python для этих записей: 3.12.7. Отдельный прогон на Python 3.10 не зафиксирован.

Frontend final assembly: `npm run lint` PASS, `npm run build` PASS.

`python scripts/start.py` на Windows: backend started, frontend started, `GET /api/health` 200, `GET /api/ready` 200, ports closed after stop. Linux launcher smoke не выполнялся. Код launcher cross-platform.

Live AI smoke backend milestone: модель `gpt-5.6-terra`, `used_ai=true`, latency 7883 ms, три ID из candidate set.

Earlier integration browser smoke: Employee, completion, HR, import, mobile — PASS.

Final UX smoke: HR PASS. Employee completion повторно не выполнялся, потому что persisted demo profile вернул `not_applicable` / empty recommendations. Функциональным regression это не объявлено.

## Known

- Demo-login — hackathon entry, не production authentication.
- UI показывает `skill_id`, где API профиля не отдаёт display name.
- Недавняя активность показывает `event_id`.
- Экраны Path и History не реализованы.
- Публичный live deploy не проверен.

## Repo verify

`23abab7` independently inspected by ChatGPT: CODE/STRUCTURE PASS. Runtime claims remain based on Cursor final smoke.

Этот documentation commit после push ожидает независимой проверки. REPO VERIFY: PENDING.

## Deploy

Infrastructure prepared: Ubuntu 22.04, Nginx, HTTPS / Let's Encrypt, PostgreSQL, domain `hack.qazentra.com`. systemd для backend запланирован. Docker для MVP не требуется.

Career Quest final build is not claimed as publicly deployed. Live smoke публичного сайта не выполнялся. См. `docs/DEPLOYMENT.md`.
