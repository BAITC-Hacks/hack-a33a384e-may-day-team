import { useState } from 'react'
import {
  BackIcon,
  BarsIcon,
  CheckIcon,
  DocumentIcon,
  LogoMark,
  UserIcon,
  UsersIcon,
} from './components/Icons.jsx'

function Brand() {
  return (
    <div className="brand" aria-label="Career Quest">
      <LogoMark className="brand__mark" />
      <span>Career Quest</span>
    </div>
  )
}

function impactFor(recommendation) {
  if (!recommendation) return null
  const skillId =
    recommendation.critical_gaps?.[0] ||
    recommendation.potential_skill_changes?.[0]?.skill_id ||
    recommendation.gaps?.[0]?.skill_id
  const change = recommendation.potential_skill_changes?.find(
    (item) => item.skill_id === skillId,
  )
  const gap = recommendation.gaps?.find((item) => item.skill_id === skillId)
  return {
    skillId: skillId || '—',
    currentLevel: change?.current_level ?? gap?.current_level ?? '—',
    newLevel: change?.new_level ?? '—',
    requiredLevel: gap?.required_level ?? change?.max_level ?? '—',
  }
}

export function LoginScreen({
  error,
  loading,
  onEmployee,
  onHr,
  onImport,
}) {
  return (
    <main className="login-screen">
      <section className="login-hero">
        <Brand />
        <div className="login-hero__copy">
          <h1>
            Ваш следующий
            <br />
            шаг в <span>карьере.</span>
          </h1>
          <p>Корпоративное развитие сотрудников</p>
          <small>Понятная цель. Подходящая активность. Видимый результат.</small>
          <span className="login-pill">Профиль → следующий шаг</span>
        </div>
        <p className="login-footnote">Career Quest · Hackathon demo</p>
      </section>
      <section className="login-panel">
        <article className="card login-card">
          <h2>Войти в демо</h2>
          <p>Выберите серверный demo account</p>
          <div className="login-role">
            <span className="login-role__icon" aria-hidden="true">
              <UserIcon />
            </span>
            <div>
              <strong>Сотрудник</strong>
              <span>Профиль и рекомендации из API</span>
            </div>
          </div>
          <button
            className="button button--primary login-card__action"
            disabled={loading}
            onClick={onEmployee}
            type="button"
          >
            {loading ? 'Входим…' : 'Войти как сотрудник'}
          </button>
          <div className="login-role">
            <span className="login-role__icon" aria-hidden="true">
              <UsersIcon />
            </span>
            <div>
              <strong>HR</strong>
              <span>Навыки и участие сотрудников</span>
            </div>
          </div>
          <button
            className="button button--secondary login-card__action"
            disabled={loading}
            onClick={onHr}
            type="button"
          >
            {loading ? 'Входим…' : 'Войти как HR'}
          </button>
          {error ? (
            <p className="api-status api-status--error">{error}</p>
          ) : (
            <p className="login-card__note">
              Сессия создаётся сервером, пароль не передаётся во frontend.
            </p>
          )}
        </article>
        <button
          className="text-button login-import"
          disabled={loading}
          onClick={onImport}
          type="button"
        >
          Проверка жюри
        </button>
      </section>
    </main>
  )
}

export function DetailScreen({
  loading,
  onBack,
  onComplete,
  profile,
  recommendation,
  recommendationEnvelope,
}) {
  if (!recommendation) {
    return (
      <article className="detail-screen">
        <button className="text-button detail-back" onClick={onBack} type="button">
          <BackIcon /> К рекомендациям
        </button>
        <p className="dashboard-intro__eyebrow">РЕКОМЕНДУЕМЫЙ ШАГ</p>
        <h1>Рекомендация временно недоступна</h1>
        <p className="detail-lead">
          Backend не вернул AI-рекомендацию для текущего профиля.
        </p>
      </article>
    )
  }

  const comparison = recommendationEnvelope?.comparison
  const alternative = comparison?.alternative_event
  const chosenImpact = impactFor(recommendation)
  const alternativeImpact = impactFor(alternative)
  const targetGrade = profile.primary_target?.grade || 'следующей цели'
  const factors = recommendation.factor_types || []

  return (
    <article className="detail-screen">
      <button className="text-button detail-back" onClick={onBack} type="button">
        <BackIcon /> К рекомендациям
      </button>
      <p className="dashboard-intro__eyebrow">РЕКОМЕНДУЕМЫЙ ШАГ</p>
      <h1>{recommendation.title}</h1>
      <p className="detail-lead">Ближайший шаг к {targetGrade}</p>
      <div className="detail-levels">
        <div>
          <span>Сейчас</span>
          <strong>{chosenImpact.currentLevel}</strong>
          <small>{chosenImpact.skillId}</small>
        </div>
        <span aria-hidden="true">→</span>
        <div>
          <span>После выполнения</span>
          <strong>{chosenImpact.newLevel}</strong>
          <small>прогноз backend</small>
        </div>
        <span aria-hidden="true">→</span>
        <div>
          <span>Требуется для {targetGrade}</span>
          <strong>{chosenImpact.requiredLevel}</strong>
          <small>{chosenImpact.skillId}</small>
        </div>
      </div>
      <p className="detail-note">{recommendation.reasoning_summary}</p>

      <section className="card compare-card">
        <p className="compare-kicker">WHY THIS, NOT THAT?</p>
        <h2>Почему это, а не другая активность?</h2>
        {alternative ? (
          <div className="compare-grid">
            <div className="compare-option compare-option--chosen">
              <span>Приоритет сейчас</span>
              <h3>{recommendation.title}</h3>
            </div>
            <div className="compare-option">
              <span>Альтернатива</span>
              <h3>{alternative.title}</h3>
            </div>
            <span>Навык сейчас / цель</span>
            <strong>
              {chosenImpact.currentLevel} / {chosenImpact.requiredLevel}
            </strong>
            <strong>
              {alternativeImpact.currentLevel} / {alternativeImpact.requiredLevel}
            </strong>
            <span>Критические пробелы</span>
            <strong>{recommendation.critical_gaps?.join(', ') || 'нет'}</strong>
            <strong>{alternative.critical_gaps?.join(', ') || 'нет'}</strong>
            <span>После выполнения</span>
            <strong>{chosenImpact.newLevel}</strong>
            <strong>{alternativeImpact.newLevel}</strong>
          </div>
        ) : (
          <p>
            Backend не вернул допустимую альтернативу для этого набора кандидатов.
          </p>
        )}
        {comparison?.summary && <p>{comparison.summary}</p>}
        <ul>
          {[recommendation.tradeoff, ...factors].filter(Boolean).map((reason) => (
            <li key={reason}>
              <CheckIcon />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </section>

      <div className="detail-actions">
        <button
          className="button button--primary"
          disabled={loading}
          onClick={onComplete}
          type="button"
        >
          {loading ? 'Обновляем…' : 'Отметить выполненным'}
        </button>
        <button className="text-button" onClick={onBack} type="button">
          Назад
        </button>
      </div>
    </article>
  )
}

export function CompletionScreen({
  completion,
  nextRecommendation,
  onHome,
  profile,
}) {
  const firstChange = completion.skill_changes?.[0]
  const nextImpact = impactFor(nextRecommendation)
  const targetGrade = profile.primary_target?.grade || 'следующей цели'

  return (
    <article className="completion-screen">
      <header className="completion-heading">
        <span aria-hidden="true">
          <CheckIcon />
        </span>
        <div>
          <h1>Активность выполнена</h1>
          <p>{completion.record_id}</p>
        </div>
      </header>
      <section className="card completion-result">
        <p className="dashboard-intro__eyebrow">ВАШ РЕЗУЛЬТАТ</p>
        {firstChange ? (
          <>
            <div>
              <h2>{firstChange.skill_id}</h2>
              <p className="completion-change">
                <strong>{firstChange.level_before}</strong>
                <span>→</span>
                <strong>{firstChange.level_after}</strong>
              </p>
            </div>
            <div>
              <span>Изменение уровня</span>
              <strong>+{firstChange.delta}</strong>
              <small>Рассчитано backend</small>
            </div>
            <p>
              Сервер подтвердил моделируемое выполнение от {completion.activity_date}.
            </p>
          </>
        ) : (
          <p>Сервер подтвердил выполнение без изменения уровня навыка.</p>
        )}
      </section>
      <div className="completion-stats">
        <section className="card">
          <span>Требования {targetGrade}</span>
          <strong>
            {profile.requirements_met_count} из {profile.requirements_total}
          </strong>
          <small>Обновлено из профиля</small>
        </section>
        <section className="card">
          <span>Статус кандидатов</span>
          <strong>{profile.candidate_status}</strong>
          <small>Ответ backend</small>
        </section>
      </div>
      <section className="card completion-next">
        <p className="recommendation-badge">Обновлённая рекомендация</p>
        {nextRecommendation ? (
          <>
            <h2>{nextRecommendation.title}</h2>
            <p>
              {nextImpact.skillId} {nextImpact.currentLevel} → {nextImpact.newLevel}
            </p>
            <small>{nextRecommendation.reasoning_summary}</small>
          </>
        ) : (
          <>
            <h2>Рекомендация временно недоступна</h2>
            <p>Профиль обновлён, но новый AI-ответ не получен.</p>
          </>
        )}
        <button className="button button--primary" onClick={onHome} type="button">
          Посмотреть следующий шаг
        </button>
        <button className="text-button" onClick={onHome} type="button">
          На главную
        </button>
      </section>
    </article>
  )
}

export function HrScreen({ onImport, overview }) {
  const gaps = overview.frequent_skill_gaps || []
  const withoutStep = overview.employees_without_next_step || []
  const participation = overview.participation_by_activity || []
  const maxGap = Math.max(1, ...gaps.map((gap) => gap.employees_missing))

  return (
    <article className="hr-screen">
      <header>
        <h1>Развитие сотрудников</h1>
        <p>Навыки, следующие шаги и участие</p>
      </header>
      <div className="hr-top">
        <section className="card">
          <h2>Основные дефициты навыков</h2>
          <p>Сотрудники с незакрытым требованием</p>
          {gaps.length === 0 ? (
            <p>Дефициты не найдены.</p>
          ) : (
            <ul>
              {gaps.map((gap) => (
                <li key={gap.skill_id}>
                  <span>{gap.skill_id}</span>
                  <span className="hr-bar">
                    <span
                      style={{
                        width: `${(gap.employees_missing / maxGap) * 100}%`,
                      }}
                    />
                  </span>
                  <strong>{gap.employees_missing}</strong>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="card hr-empty">
          <span className="hr-empty__icon" aria-hidden="true">
            <BarsIcon />
          </span>
          <h2>Без следующего шага</h2>
          <strong>{withoutStep.length}</strong>
          <p>сотрудников</p>
          <small>
            {withoutStep.length > 0
              ? withoutStep
                  .map((item) => `${item.employee_id}: ${item.reason}`)
                  .join(', ')
              : 'У всех сотрудников есть подходящий следующий шаг.'}
          </small>
        </section>
      </div>
      <section className="card hr-table-card">
        <h2>Участие в активностях</h2>
        <p className="hr-totals">Источник: {overview.basis}</p>
        <div className="hr-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Активность</th>
                <th>Выполнено</th>
                <th>Не пришли</th>
                <th>Прервали</th>
                <th>Отказались</th>
              </tr>
            </thead>
            <tbody>
              {participation.map((row) => (
                <tr key={row.event_id}>
                  <th scope="row">{row.event_id}</th>
                  <td>{row.status_counts?.completed || 0}</td>
                  <td>{row.status_counts?.no_show || 0}</td>
                  <td>{row.status_counts?.dropped || 0}</td>
                  <td>{row.status_counts?.declined || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <button className="text-button" onClick={onImport} type="button">
        Проверка жюри
      </button>
    </article>
  )
}

export function ImportScreen({ error, loading, onBack, onImport, result }) {
  const [employeesFile, setEmployeesFile] = useState(null)
  const [historyFile, setHistoryFile] = useState(null)

  function submit(event) {
    event.preventDefault()
    if (employeesFile && historyFile) onImport(employeesFile, historyFile)
  }

  return (
    <main className="import-screen">
      <header className="import-top">
        <Brand />
        <button className="text-button" onClick={onBack} type="button">
          К обзору HR
        </button>
      </header>
      <article>
        <p className="dashboard-intro__eyebrow">СЛУЖЕБНЫЙ ЭКРАН</p>
        <h1>Импорт тестового профиля</h1>
        <p>Импортируйте профиль сотрудника и историю участия</p>
        <form onSubmit={submit}>
          <div className="import-files">
            <section className="import-drop">
              <DocumentIcon />
              <h2>Профили сотрудников</h2>
              <span>JSON</span>
              <p>
                <strong>{employeesFile?.name || 'Файл не выбран'}</strong>
                <span>{employeesFile ? 'Готов к отправке' : 'Выберите файл'}</span>
              </p>
              <input
                accept=".json,application/json"
                aria-label="Файл профилей сотрудников"
                onChange={(event) => setEmployeesFile(event.target.files?.[0] || null)}
                type="file"
              />
            </section>
            <section className="import-drop">
              <DocumentIcon />
              <h2>История участия</h2>
              <span>CSV</span>
              <p>
                <strong>{historyFile?.name || 'Файл не выбран'}</strong>
                <span>{historyFile ? 'Готов к отправке' : 'Выберите файл'}</span>
              </p>
              <input
                accept=".csv,text/csv"
                aria-label="Файл истории участия"
                onChange={(event) => setHistoryFile(event.target.files?.[0] || null)}
                type="file"
              />
            </section>
          </div>
          <section className="import-checks">
            <h2>Ответ backend</h2>
            {result ? (
              <ul>
                {Object.entries(result).map(([key, value]) => (
                  <li key={key}>
                    <CheckIcon />
                    <span>{key}: {value}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Результат появится после серверной проверки файлов.</p>
            )}
            {error && <p className="api-status api-status--error">{error}</p>}
          </section>
          <footer>
            <span>{result ? 'Импорт завершён' : 'Ожидаются два файла'}</span>
            <button
              className="button button--primary"
              disabled={loading || !employeesFile || !historyFile}
              type="submit"
            >
              {loading ? 'Импортируем…' : 'Импортировать данные'}
            </button>
          </footer>
        </form>
        <small>Файлы отправляются в защищённый HR endpoint.</small>
      </article>
    </main>
  )
}
