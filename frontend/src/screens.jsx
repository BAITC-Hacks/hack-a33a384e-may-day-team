import {
  BackIcon,
  BarsIcon,
  CheckIcon,
  DocumentIcon,
  LogoMark,
  UserIcon,
  UsersIcon,
} from './components/Icons.jsx'
import { demoDashboard } from './data/demoDashboard.js'

function Brand() {
  return (
    <div className="brand" aria-label="Career Quest">
      <LogoMark className="brand__mark" />
      <span>Career Quest</span>
    </div>
  )
}

export function LoginScreen({ onEmployee, onHr, onImport }) {
  const { employee } = demoDashboard

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
          <span className="login-pill">
            {employee.currentGrade} → {employee.targetGrade}
          </span>
        </div>
        <p className="login-footnote">Career Quest · Визуальная концепция</p>
      </section>
      <section className="login-panel">
        <article className="card login-card">
          <h2>Войти в демо</h2>
          <p>Выберите роль для знакомства с продуктом</p>
          <div className="login-role">
            <span className="login-role__icon" aria-hidden="true">
              <UserIcon />
            </span>
            <div>
              <strong>Сотрудник</strong>
              <span>
                {employee.fullName} · {employee.role}
              </span>
            </div>
          </div>
          <button className="button button--primary login-card__action" onClick={onEmployee} type="button">
            Войти как сотрудник
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
          <button className="button button--secondary login-card__action" onClick={onHr} type="button">
            Войти как HR
          </button>
          <p className="login-card__note">Демонстрационные аккаунты. Это не проверка прав.</p>
        </article>
        <button className="text-button login-import" onClick={onImport} type="button">
          Проверка жюри
        </button>
      </section>
    </main>
  )
}

export function DetailScreen({ completed, onBack, onComplete }) {
  const { comparison, employee } = demoDashboard
  const recommendation = completed
    ? demoDashboard.after.recommendation
    : demoDashboard.before.recommendation

  return (
    <article className="detail-screen">
      <button className="text-button detail-back" onClick={onBack} type="button">
        <BackIcon /> К рекомендациям
      </button>
      <p className="dashboard-intro__eyebrow">РЕКОМЕНДУЕМЫЙ ШАГ</p>
      <h1>{recommendation.title}</h1>
      <p className="detail-lead">Ближайший шаг к {employee.targetGrade}</p>
      <div className="detail-levels">
        <div>
          <span>Сейчас</span>
          <strong>{recommendation.currentLevel}</strong>
          <small>{recommendation.skill}</small>
        </div>
        <span aria-hidden="true">→</span>
        <div>
          <span>После выполнения</span>
          <strong>{recommendation.projectedLevel}</strong>
          <small>+1 к навыку</small>
        </div>
        <span aria-hidden="true">→</span>
        <div>
          <span>Требуется для {employee.targetGrade}</span>
          <strong>{recommendation.targetLevel}</strong>
          <small>{recommendation.skill}</small>
        </div>
      </div>
      <p className="detail-note">
        {recommendation.targetLevel - recommendation.projectedLevel > 0
          ? `После активности до цели останется ${recommendation.targetLevel - recommendation.projectedLevel} уровень.`
          : 'После активности требование этого навыка будет закрыто.'}
      </p>

      {completed ? (
        <section className="card detail-next">
          <h2>Следующая демонстрационная рекомендация</h2>
          <p>
            Повторное выполнение не повышает навык ещё раз. System Design остаётся 3 из 4,
            требования — 6 из 10.
          </p>
        </section>
      ) : (
        <section className="card compare-card">
          <p className="compare-kicker">WHY THIS, NOT THAT?</p>
          <h2>Почему это, а не другая активность?</h2>
          <div className="compare-grid">
            <div className="compare-option compare-option--chosen">
              <span>Приоритет сейчас</span>
              <h3>{comparison.chosen.title}</h3>
            </div>
            <div className="compare-option">
              <span>Альтернатива</span>
              <h3>{comparison.alternative.title}</h3>
            </div>
            <span>Навык сейчас / цель</span>
            <strong>{comparison.chosen.now}</strong>
            <strong>{comparison.alternative.now}</strong>
            <span>Для перехода в {employee.targetGrade}</span>
            <strong>{comparison.chosen.importance}</strong>
            <strong>{comparison.alternative.importance}</strong>
            <span>После выполнения</span>
            <strong>{comparison.chosen.after}</strong>
            <strong>{comparison.alternative.after}</strong>
          </div>
          <p>
            Public Speaking развит слабее, но System Design — критический навык для{' '}
            {employee.targetGrade}. Сейчас важнее сократить именно этот разрыв.
          </p>
          <ul>
            {comparison.reasons.map((reason) => (
              <li key={reason}>
                <CheckIcon />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="detail-actions">
        <button
          className="button button--primary"
          disabled={completed}
          onClick={onComplete}
          type="button"
        >
          {completed ? 'Уже выполнено' : 'Отметить выполненным'}
        </button>
        <button className="text-button" onClick={onBack} type="button">
          Назад
        </button>
      </div>
    </article>
  )
}

export function CompletionScreen({ onHome }) {
  const { completedActivity, employee, progress } = demoDashboard
  const next = demoDashboard.after.recommendation

  return (
    <article className="completion-screen">
      <header className="completion-heading">
        <span aria-hidden="true">
          <CheckIcon />
        </span>
        <div>
          <h1>Активность выполнена</h1>
          <p>{completedActivity.title}</p>
        </div>
      </header>
      <section className="card completion-result">
        <p className="dashboard-intro__eyebrow">ВАШ РЕЗУЛЬТАТ</p>
        <div>
          <h2>{completedActivity.skill}</h2>
          <p className="completion-change">
            <strong>{completedActivity.from}</strong>
            <span>→</span>
            <strong>{completedActivity.to}</strong>
          </p>
        </div>
        <div>
          <span>До требования {employee.targetGrade}</span>
          <strong>1 уровень</strong>
          <small>Целевой уровень — {completedActivity.target}</small>
        </div>
        <p>Навык вырос. Требование будет выполнено на уровне {completedActivity.target}.</p>
      </section>
      <div className="completion-stats">
        <section className="card">
          <span>Требования {employee.targetGrade}</span>
          <strong>
            {progress.completed} из {progress.total}
          </strong>
          <small>Без изменения</small>
        </section>
        <section className="card">
          <span>Критические требования</span>
          <strong>
            {progress.criticalCompleted} из {progress.criticalTotal}
          </strong>
          <small>Без изменения</small>
        </section>
      </div>
      <section className="card completion-next">
        <p className="recommendation-badge">Обновлённая рекомендация</p>
        <h2>{next.title}</h2>
        <p>
          {next.skill} {next.currentLevel} → {next.projectedLevel}
        </p>
        <small>Поможет выполнить ещё одно критическое требование {employee.targetGrade}.</small>
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

export function HrScreen({ onImport }) {
  const { hr } = demoDashboard
  const maxGap = Math.max(...hr.gaps.map((gap) => gap.employees))

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
          <ul>
            {hr.gaps.map((gap) => (
              <li key={gap.skill}>
                <span>{gap.skill}</span>
                <span className="hr-bar">
                  <span style={{ width: `${(gap.employees / maxGap) * 100}%` }} />
                </span>
                <strong>{gap.label}</strong>
              </li>
            ))}
          </ul>
        </section>
        <section className="card hr-empty">
          <span className="hr-empty__icon" aria-hidden="true">
            <BarsIcon />
          </span>
          <h2>Без следующего шага</h2>
          <strong>{hr.withoutNextStep}</strong>
          <p>сотрудников</p>
          <small>Для этих сотрудников нет подходящей рекомендации.</small>
        </section>
      </div>
      <section className="card hr-table-card">
        <h2>Участие в активностях</h2>
        <div className="hr-totals">
          <span>Выполнено <strong>{hr.totals.completed}</strong></span>
          <span>Не пришли <strong>{hr.totals.missed}</strong></span>
          <span>Прервали <strong>{hr.totals.dropped}</strong></span>
          <span>Отказались <strong>{hr.totals.declined}</strong></span>
        </div>
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
              {hr.participation.map((row) => (
                <tr key={row.activity}>
                  <th scope="row">{row.activity}</th>
                  <td>{row.completed}</td>
                  <td>{row.missed}</td>
                  <td>{row.dropped}</td>
                  <td>{row.declined}</td>
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

export function ImportScreen({ onGenerate, onBack }) {
  const { importCheck } = demoDashboard

  return (
    <main className="import-screen">
      <header className="import-top">
        <Brand />
        <button className="text-button" onClick={onBack} type="button">
          Проверка жюри
        </button>
      </header>
      <article>
        <p className="dashboard-intro__eyebrow">СЛУЖЕБНЫЙ ЭКРАН</p>
        <h1>Проверка тестового профиля</h1>
        <p>Импортируйте профиль сотрудника и историю участия</p>
        <div className="import-files">
          {importCheck.files.map((file) => (
            <section className="import-drop" key={file.name}>
              <DocumentIcon />
              <h2>{file.title}</h2>
              <span>{file.format}</span>
              <p>
                <strong>{file.name}</strong>
                <span>Загружено</span>
              </p>
              <button
                className="button button--secondary"
                title="Показан заранее подготовленный демо-файл"
                type="button"
              >
                Выбрать файл
              </button>
            </section>
          ))}
        </div>
        <section className="import-checks">
          <h2>Проверка данных</h2>
          <ul>
            {importCheck.checks.map((check) => (
              <li key={check}>
                <CheckIcon />
                <span>{check}</span>
              </li>
            ))}
          </ul>
        </section>
        <footer>
          <span>Готово к проверке</span>
          <button className="button button--primary" onClick={onGenerate} type="button">
            Сформировать рекомендацию
          </button>
        </footer>
        <small>Демонстрационный пример. Файл не отправляется и не проверяется сервером.</small>
      </article>
    </main>
  )
}
