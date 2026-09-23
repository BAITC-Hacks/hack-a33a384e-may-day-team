import './App.css'
import {
  ArrowRightIcon,
  CheckIcon,
  ChevronDownIcon,
  CodeIcon,
  DocumentIcon,
  HistoryIcon,
  HomeIcon,
  LogoMark,
  PathIcon,
} from './components/Icons.jsx'
import { demoDashboard } from './data/demoDashboard.js'

const navigation = [
  { label: 'Главная', shortLabel: 'Главная', Icon: HomeIcon, active: true },
  {
    label: 'Карьерный путь',
    shortLabel: 'Путь',
    Icon: PathIcon,
    active: false,
  },
  { label: 'История', shortLabel: 'История', Icon: HistoryIcon, active: false },
]

function Brand() {
  return (
    <div className="brand" aria-label="Career Quest">
      <LogoMark className="brand__mark" />
      <span>Career Quest</span>
    </div>
  )
}

function UserIdentity({ showName = false }) {
  const { employee } = demoDashboard

  return (
    <div className="user-identity">
      <span className="avatar" aria-hidden="true">
        {employee.initials}
      </span>
      {showName && (
        <>
          <span className="user-identity__name">{employee.fullName}</span>
          <ChevronDownIcon className="user-identity__chevron" />
        </>
      )}
    </div>
  )
}

function Navigation({ mobile = false }) {
  return (
    <nav
      className={mobile ? 'bottom-navigation' : 'sidebar-navigation'}
      aria-label="Основная навигация"
    >
      {navigation.map(({ active, Icon, label, shortLabel }) =>
        active ? (
          <a
            className={mobile ? 'bottom-navigation__item is-active' : 'sidebar-navigation__item is-active'}
            href="#main-content"
            key={label}
            aria-current="page"
          >
            <Icon className="navigation-icon" />
            <span>{mobile ? shortLabel : label}</span>
          </a>
        ) : (
          <span
            aria-disabled="true"
            className={mobile ? 'bottom-navigation__item' : 'sidebar-navigation__item'}
            key={label}
            title="Раздел будет подключён на следующем этапе"
          >
            <Icon className="navigation-icon" />
            <span>{mobile ? shortLabel : label}</span>
          </span>
        ),
      )}
    </nav>
  )
}

function ProgressCard() {
  const { completed, total } = demoDashboard.progress
  const percentage = (completed / total) * 100

  return (
    <section className="card progress-card" aria-labelledby="progress-heading">
      <div className="progress-card__copy">
        <h2 id="progress-heading">
          Прогресс к {demoDashboard.employee.targetGrade}
        </h2>
        <p>
          <strong>
            {completed} из {total}
          </strong>
          <span>требований выполнено</span>
        </p>
      </div>
      <div
        aria-label={`${completed} из ${total} требований выполнено`}
        aria-valuemax={total}
        aria-valuemin="0"
        aria-valuenow={completed}
        className="progress-track"
        role="progressbar"
        style={{ '--progress': `${percentage}%` }}
      >
        <span />
      </div>
    </section>
  )
}

function RecommendationCard() {
  const { employee, recommendation } = demoDashboard

  return (
    <article className="card recommendation-card">
      <p className="recommendation-badge">
        <span className="desktop-only">{recommendation.desktopBadge}</span>
        <span className="mobile-only">{recommendation.mobileBadge}</span>
      </p>
      <h2>{recommendation.title}</h2>
      <p className="recommendation-card__description">
        <span className="desktop-only">
          Усильте критический навык для перехода в {employee.targetGrade}
        </span>
        <span className="mobile-only">{recommendation.description}</span>
      </p>

      <div className="recommendation-forecast">
        <span className="forecast-skill desktop-only">{recommendation.skill}</span>
        <div className="forecast-change">
          <span>
            <small className="mobile-only">Сейчас</small>{' '}
            {recommendation.currentLevel}
          </span>
          <span className="forecast-arrow">→</span>
          <span>
            <small className="mobile-only">После</small>{' '}
            {recommendation.projectedLevel}
          </span>
        </div>
        <span className="forecast-divider desktop-only" aria-hidden="true">
          /
        </span>
        <span className="forecast-target">
          <span className="desktop-only">цель </span>
          <span className="mobile-only">Цель — </span>
          {recommendation.targetLevel}
        </span>
      </div>

      <ul className="recommendation-reasons desktop-only">
        {recommendation.desktopReasons.map((reason) => (
          <li key={reason}>
            <CheckIcon />
            <span>{reason}</span>
          </li>
        ))}
      </ul>
      <ul className="recommendation-reasons mobile-only">
        {recommendation.mobileReasons.map((reason) => (
          <li key={reason}>
            <CheckIcon />
            <span>{reason}</span>
          </li>
        ))}
      </ul>

      <div className="recommendation-actions">
        <button
          className="button button--primary"
          disabled
          title="Переход будет подключён на этапе F2"
          type="button"
        >
          <span className="desktop-only">Подробнее</span>
          <span className="mobile-only">Почему именно это?</span>
        </button>
        <button
          className="button button--secondary"
          disabled
          title="Выполнение будет подключено на этапе F2"
          type="button"
        >
          <span className="desktop-only">Отметить выполненным</span>
          <span className="mobile-only">Выполнено</span>
        </button>
      </div>

      <p className="recommendation-card__note desktop-only">
        Рекомендация основана на профиле и истории
      </p>
    </article>
  )
}

function LevelSegments({ current, required }) {
  return (
    <span className="level-segments" aria-hidden="true">
      {Array.from({ length: required }, (_, index) => (
        <span className={index < current ? 'is-filled' : ''} key={index} />
      ))}
    </span>
  )
}

function CriticalGaps() {
  return (
    <section className="card gaps-card" aria-labelledby="gaps-heading">
      <h2 id="gaps-heading">Критические пробелы</h2>
      <ul>
        {demoDashboard.criticalGaps.map(({ current, required, skill }) => (
          <li key={skill}>
            <span className="gap-name">{skill}</span>
            <span className="gap-value">
              {current} / {required}
            </span>
            <LevelSegments current={current} required={required} />
          </li>
        ))}
      </ul>
    </section>
  )
}

function AlternateStep() {
  const { alternateStep } = demoDashboard

  return (
    <section className="alternate-step" aria-labelledby="alternate-heading">
      <h2 id="alternate-heading">Ещё один подходящий шаг</h2>
      <article className="card alternate-step__card">
        <span className="alternate-step__icon" aria-hidden="true">
          <CodeIcon />
        </span>
        <div>
          <h3>{alternateStep.title}</h3>
          <p>
            {alternateStep.skill} &nbsp;{alternateStep.currentLevel} →{' '}
            {alternateStep.projectedLevel}
          </p>
        </div>
        <span className="alternate-step__link" aria-disabled="true">
          Подробнее
          <ArrowRightIcon />
        </span>
      </article>
    </section>
  )
}

function RecentActivity() {
  return (
    <section className="card activity-card" aria-labelledby="activity-heading">
      <h2 id="activity-heading">Последняя активность</h2>
      <ul>
        {demoDashboard.recentActivity.map((activity) => (
          <li key={activity.title}>
            <span
              className={`activity-card__icon activity-card__icon--${activity.tone}`}
              aria-hidden="true"
            >
              <DocumentIcon />
            </span>
            <div>
              <h3>{activity.title}</h3>
              <p>
                {activity.status} · {activity.date}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

function App() {
  const { employee } = demoDashboard

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand />
        <Navigation />
        <p className="sidebar__demo-label">
          Демо-данные
          <span>Концепция</span>
        </p>
      </aside>

      <div className="page-shell">
        <header className="topbar">
          <div className="topbar__mobile-brand">
            <Brand />
          </div>
          <UserIdentity showName />
        </header>

        <main className="dashboard" id="main-content">
          <header className="dashboard-intro">
            <div className="dashboard-intro__desktop">
              <p className="dashboard-intro__eyebrow">ВАШ КАРЬЕРНЫЙ ПУТЬ</p>
              <h1>{employee.firstName}, ваш следующий шаг</h1>
              <p className="dashboard-intro__subtitle">
                {employee.role} · {employee.currentGrade} → {employee.targetGrade}
              </p>
            </div>
            <div className="dashboard-intro__mobile">
              <p>{employee.fullName}</p>
              <h1>{employee.role}</h1>
              <p>
                {employee.currentGrade} → {employee.targetGrade}
              </p>
            </div>
          </header>

          <ProgressCard />

          <div className="dashboard-grid">
            <div className="dashboard-grid__primary">
              <RecommendationCard />
              <AlternateStep />
            </div>
            <div className="dashboard-grid__secondary">
              <CriticalGaps />
              <RecentActivity />
            </div>
          </div>
          <p className="content-demo-label">Демо-данные</p>
        </main>
      </div>

      <Navigation mobile />
    </div>
  )
}

export default App
