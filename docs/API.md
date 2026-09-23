# Career Quest API — M2.2

Технический контракт backend. Frontend в этом этапе не изменялся.
Отметка выполнения моделирует завершение в прототипе и не подтверждает обучение
во внешней системе. AI выбирает только из серверных candidate facts.

Базовый URL локального backend: `http://127.0.0.1:8000`.

## Ошибки

```json
{"code": "not_found", "message": "Employee was not found.", "details": {}}
```

| Код | HTTP | Когда |
|---|---|---|
| `invalid_credentials` | 401 | Неверный логин или пароль |
| `not_authenticated` | 401 | Нет действующей сессии |
| `csrf_failed` | 403 | Неверный CSRF или запрещённый Origin |
| `forbidden` | 403 | Employee обращается к HR-операции |
| `not_found` | 404 | Нет объекта либо Employee запрашивает чужой профиль |
| `validation_error` | 400 | Неверное тело, заголовок или пакет импорта |
| `already_completed` | 409 | Повтор одноразовой активности |
| `session_already_completed` | 409 | Повтор той же scheduled-сессии |
| `idempotency_key_reused` | 409 | Тот же ключ с другим содержимым |
| `activity_not_eligible` | 409 | Активность не проходит правила M1 |
| `session_not_available` | 409 | Даты нет в каталоге или она раньше бизнес-даты |
| `import_conflict` | 409 | Тот же ID с другим содержимым |
| `payload_too_large` | 413 | Файл импорта больше 1 МиБ |
| `database_unavailable` | 503 | Хранилище не настроено или недоступно |
| `configuration_error` | 500 | Demo-вход не настроен или роль аккаунта не совпадает |
| `dataset_conflict` | 409 | Seed получил другой dataset |

Ответы не содержат пароли, хеши, session token или URL базы.

## Сессия и CSRF

`POST /api/auth/login` принимает JSON `{"username": "...", "password": "..."}`.
Лишнее поле, включая `role`, отклоняется. Роль берётся только из серверной
учётной записи.

Для hackathon demo `POST /api/auth/demo-login` принимает только
`{"role":"employee"}` или `{"role":"hr"}` без дополнительных полей. Сервер
выбирает настроенный `employee_one` или HR-аккаунт и использует тот же механизм
сессии; логин и пароль в запросе и ответе отсутствуют. Без demo-конфигурации
возвращается безопасный `configuration_error`. Обычный `/api/auth/login`
остаётся доступен.

Успешный вход ставит:

- `cq_session`: случайный token, `HttpOnly`, `SameSite=Lax`, срок
  `SESSION_TTL_HOURS`;
- `cq_csrf`: читаемый frontend cookie с тем же сроком.

`Secure` включается при `COOKIE_SECURE=true`. Тело ответа содержит `username`,
`role`, `employee_id`, `csrf_token`, но не session token.

Для `POST` после входа нужны одновременно:

- cookie `cq_session`;
- cookie `cq_csrf`;
- заголовок `X-CSRF-Token` с тем же значением.

Если браузер прислал `Origin`, он должен входить в `ALLOWED_ORIGINS`.
`CORS` не использует `*` вместе с credentials.

`POST /api/auth/logout` с валидным CSRF удаляет серверную сессию и cookies.
`GET /api/auth/me` возвращает текущего пользователя.

## Сотрудник

`GET /api/employees/{employee_id}`

Employee получает только свой ID. HR получает любой существующий ID.

```json
{
  "employee_id": "EMP-EXAMPLE",
  "role": "Engineer",
  "grade": "Junior",
  "career_goal": {"target_role": "Designer", "target_grade": "Senior"},
  "primary_target": {"role": "Engineer", "grade": "Middle"},
  "career_goal_differs_from_primary_target": true,
  "as_of_date": "2026-01-20",
  "skills": [{"skill_id": "S_ARCH", "current_level": 1}],
  "requirements": [{
    "skill_id": "S_ARCH",
    "current_level": 1,
    "required_level": 2,
    "missing_level": 1,
    "critical": true
  }],
  "requirements_met_count": 0,
  "requirements_total": 2,
  "candidate_status": "candidates_available",
  "history": [{
    "record_id": "R1",
    "event_id": "EV_EXAMPLE",
    "date": "2026-01-11",
    "status": "completed",
    "completion_pct": 100,
    "assigned_by": "self",
    "origin": "dataset"
  }]
}
```

`career_goal_differs_from_primary_target` равен `true`, когда сохранённая
`career_goal` отличается от следующего грейда текущей роли. Это информационный
флаг: primary target не меняется.

`GET /api/employees/{employee_id}/candidates` возвращает факты M1 без ранжирования.
У каждого кандидата есть каталожные `type`, `format`, `duration_hours` и
`upcoming_sessions` — даты ISO из dataset, без выдуманных сессий:

```json
{
  "used_ai": false,
  "selection_status": "not_ranked",
  "candidate_status": "candidates_available",
  "candidates": [{
    "event_id": "EV_EXAMPLE",
    "title": "Synthetic activity",
    "type": "course",
    "format": "offline",
    "duration_hours": 2,
    "upcoming_sessions": ["2026-01-20"]
  }],
  "exclusions": []
}
```

Порядок массива не является AI-рекомендацией и не выбирает первые три элемента.

`GET /api/employees/{employee_id}/recommendations` — выбор 1–3 из того же списка.
Цифры и каталог копируются с серверного кандидата. Текст модели — только
`reasoning_summary`, `factor_types`, `tradeoff` и `comparison.summary`.

```json
{
  "used_ai": true,
  "selection_status": "ai_ranked",
  "model": "gpt-5.6-terra",
  "latency_ms": 1200,
  "fallback_reason": null,
  "recommendations": [{
    "event_id": "EV_EXAMPLE",
    "title": "Synthetic activity",
    "type": "course",
    "format": "offline",
    "duration_hours": 2,
    "upcoming_sessions": ["2026-01-20"],
    "target": {"role": "Engineer", "grade": "Middle"},
    "gaps": [],
    "critical_gaps": ["S_ARCH"],
    "potential_skill_changes": [],
    "participation": {"event_status_counts": {}},
    "reasoning_summary": "Закрывает критический разрыв следующего грейда.",
    "factor_types": ["grade", "skill_gap", "participation_history", "next_level_requirements"],
    "tradeoff": "Сильнее второй активности по критическому разрыву."
  }],
  "comparison": {
    "chosen_event": {"event_id": "EV_EXAMPLE"},
    "alternative_event": {"event_id": "EV_OTHER"},
    "summary": "Первая сильнее закрывает критический разрыв."
  }
}
```

`comparison` равен `null`, если допустим только один кандидат. При двух и более
`chosen_event` — рекомендация с rank 1, `alternative_event` — другой кандидат
из того же списка.

Сбой модели не отдаёт 500. Ответ тот же формы, но `used_ai=false`,
`selection_status=fallback_ranked`, а `fallback_reason` — один из
`missing_api_key`, `timeout`, `provider_error`, `invalid_ai_output`.
Порядок fallback прозрачный и не является AI-оценкой: больше критических
разрывов, больше суммарный прирост по целевым навыкам, больше затронутых
целевых разрывов, меньше `no_show` + `declined` + `dropped`, затем `event_id`.
Пустой список кандидатов не вызывает модель: `selection_status=not_applicable`,
`recommendations=[]`.

## Выполнение

`POST /api/employees/{employee_id}/activities/{event_id}/complete`

Обязателен заголовок `Idempotency-Key`. Тело — JSON-объект. Для scheduled
активности обязательно `session_date` из каталога; для `self_paced` поле не
передаётся. Клиент не передаёт уровни навыков, `gain` или `max_level`.

```json
{"session_date": "2026-01-20"}
```

```json
{
  "idempotent_replay": false,
  "modeled_completion": true,
  "record_id": "APP-EXAMPLE",
  "activity_date": "2026-01-20",
  "skill_changes": [{
    "skill_id": "S_ARCH",
    "level_before": 1,
    "level_after": 2,
    "delta": 1
  }],
  "requirements": [],
  "candidate_status": "candidates_available"
}
```

Тот же ключ и то же содержимое возвращают `idempotent_replay=true` и не создают
второе завершение. Тот же ключ с другой датой — конфликт. Новый ключ не
завершает одноразовую активность повторно.

`EV_036`: для scheduled-формата одна дата каталога — одно посещение; повторный
запрос той же пары ключ/дата не является новым посещением. Начатую
`in_progress` попытку можно завершить, после чего у этой попытки больше нет
статуса `in_progress`.

## HR

`GET /api/hr/employees` — список сотрудников и `candidate_status`.

`GET /api/hr/overview` считает данные без LLM:

```json
{
  "basis": "eligible_candidates_before_ai",
  "frequent_skill_gaps": [{
    "skill_id": "S_ARCH",
    "employees_missing": 1,
    "critical_employees_missing": 1
  }],
  "employees_without_next_step": [{
    "employee_id": "LEAD-EXAMPLE",
    "reason": "no_next_grade"
  }],
  "participation_by_activity": [{
    "event_id": "EV_EXAMPLE",
    "status_counts": {"completed": 1}
  }]
}
```

`reason` бывает `no_next_grade`, `requirements_already_met` или
`no_suitable_available_events`. Отсутствие AI-запуска само по себе не помещает
сотрудника в этот список.

`POST /api/hr/import` принимает `multipart/form-data`: `employees_file` и
`history_file`. Серверный путь к файлу не принимается. Лимит каждого файла —
1 МиБ. Пакет проверяется целиком; конфликт или ошибка не создают частичную
запись. Повтор идентичного пакета не дублирует строки. Импорт не создаёт
HR-аккаунт и не меняет права.

## Служебные маршруты

`GET /api/health` возвращает только
`{"status":"ok","service":"career-quest-backend"}`.

`GET /api/ready` проверяет соединение с PostgreSQL и при недоступности возвращает
503 `database_unavailable`.
