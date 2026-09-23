import { useState } from 'react'
import './App.css'
import {
  ArrowRightIcon,
  BarsIcon,
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
import {
  CompletionScreen,
  DetailScreen,
  HrScreen,
  ImportScreen,
  LoginScreen,
} from './screens.jsx'

const employeeNavigation = [
  { id: 'home', label: 'Главная', shortLabel: 'Главная', Icon: HomeIcon },
  { id: 'path', label: 'Карьерный путь', shortLabel: 'Путь', Icon: PathIcon },
  { id: 'history', label: 'История', shortLabel: 'История', Icon: HistoryIcon },
]

const hrNavigation = [
  { id: 'hr', label: 'Обзор HR', shortLabel: 'HR', Icon: BarsIcon },
]

function Brand() {
  return (
    <div className="brand" aria-label="Career Quest">
      <LogoMark className="brand__mark" />
      <span>Career Quest</span>
    </div>
  )
}

function UserIdentity({ person, showName = false }) {
  return (
    <div className="user-identity">
      <span className="avatar" aria-hidden="true">
        {person.initials}
      </span>
      {showName && (
        <>
          <span className="user-identity__name">
            {person.fullName || person.name}
            {person.role === 'HR' ? ' · HR' : ''}
          </span>
          <ChevronDownIcon className="user-identity__chevron" />
        </>
      )}
    </div>
  )
}

function Navigation({ activeId, items, mobile = false, onSelect }) {
  return (
    <nav
      className={mobile ? 'bottom-navigation' : 'sidebar-navigation'}
      aria-label="Основная навигация"
    >
      {items.map(({ Icon, id, label, shortLabel }) => {
        const active = id === activeId
        const className = mobile
          ? 'bottom-navigation__item'
          : 'sidebar-navigation__item'
        if (!active && id !== 'home' && id !== 'hr') {
          return (
            <span
              aria-disabled="true"
              className={className}
              key={id}
              title="Для этого раздела нет утверждённого экрана"
            >
              <Icon className="navigation-icon" />
              <span>{mobile ? shortLabel : label}</span>
            </span>
          )
        }

        return (
          <button
            aria-current={active ? 'page' : undefined}
            className={active ? `${className} is-active` : className}
            key={id}
            onClick={() => onSelect(id)}
            type="button"
          >
            <Icon className="navigation-icon" />
            <span>{mobile ? shortLabel : label}</span>
          </button>
        )
      })}
    </nav>
  )
}

function ProgressCard({ progress }) {
  const { completed, total } = progress
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

function RecommendationCard({ completed, onComplete, onOpen, recommendation }) {
  const { employee } = demoDashboard

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
        <button className="button button--primary" onClick={onOpen} type="button">
          <span className="desktop-only">Подробнее</span>
          <span className="mobile-only">Почему именно это?</span>
        </button>
        <button
          className="button button--secondary"
          disabled={completed}
          onClick={onComplete}
          type="button"
        >
          <span className="desktop-only">
            {completed ? 'Уже выполнено' : 'Отметить выполненным'}
          </span>
          <span className="mobile-only">{completed ? 'Уже выполнено' : 'Выполнено'}</span>
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

function CriticalGaps({ gaps }) {
  return (
    <section className="card gaps-card" aria-labelledby="gaps-heading">
      <h2 id="gaps-heading">Критические пробелы</h2>
      <ul>
        {gaps.map(({ current, required, skill }) => (
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

function AlternateStep({ alternateStep, onOpen }) {
  if (!alternateStep) return null

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
        <button className="alternate-step__link" onClick={onOpen} type="button">
          Подробнее
          <ArrowRightIcon />
        </button>
      </article>
    </section>
  )
}

function RecentActivity({ completed }) {
  const activity = completed
    ? [
        {
          title: demoDashboard.completedActivity.title,
          status: 'Завершено',
          date: 'сегодня',
          tone: 'success',
        },
        ...demoDashboard.recentActivity,
      ]
    : demoDashboard.recentActivity

  return (
    <section className="card activity-card" aria-labelledby="activity-heading">
      <h2 id="activity-heading">Последняя активность</h2>
      <ul>
        {activity.map((item) => (
          <li key={item.title}>
            <span
              className={`activity-card__icon activity-card__icon--${item.tone}`}
              aria-hidden="true"
            >
              <DocumentIcon />
            </span>
            <div>
              <h3>{item.title}</h3>
              <p>
                {item.status} · {item.date}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

function EmployeeHome({ completed, onComplete, onOpen }) {
  const { employee, progress } = demoDashboard
  const scenario = completed ? demoDashboard.after : demoDashboard.before

  return (
    <>
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
      <ProgressCard progress={progress} />
      <div className="dashboard-grid">
        <div className="dashboard-grid__primary">
          <RecommendationCard
            completed={completed}
            onComplete={onComplete}
            onOpen={onOpen}
            recommendation={scenario.recommendation}
          />
          <AlternateStep alternateStep={scenario.alternateStep} onOpen={onOpen} />
        </div>
        <div className="dashboard-grid__secondary">
          <CriticalGaps gaps={scenario.criticalGaps} />
          <RecentActivity completed={completed} />
        </div>
      </div>
      <p className="content-demo-label">Демо-данные</p>
    </>
  )
}

function App() {
  const [screen, setScreen] = useState('login')
  const [completed, setCompleted] = useState(false)
  const employeeZone = screen === 'home' || screen === 'detail' || screen === 'completion'
  const hrZone = screen === 'hr'

  function completeActivity() {
    setCompleted(true)
    setScreen('completion')
  }

  if (screen === 'login') {
    return (
      <LoginScreen
        onEmployee={() => setScreen('home')}
        onHr={() => setScreen('hr')}
        onImport={() => setScreen('import')}
      />
    )
  }

  if (screen === 'import') {
    return (
      <ImportScreen
        onBack={() => setScreen('login')}
        onGenerate={() => setScreen('home')}
      />
    )
  }

  const person = hrZone ? demoDashboard.hr : demoDashboard.employee
  const navigation = hrZone ? hrNavigation : employeeNavigation

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand />
        <p className="sidebar-zone">{hrZone ? 'HR-ЗОНА' : 'СОТРУДНИК'}</p>
        <Navigation
          activeId={employeeZone ? 'home' : screen}
          items={navigation}
          onSelect={setScreen}
        />
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
          <UserIdentity person={person} showName />
        </header>
        <main className="dashboard" id="main-content">
          {screen === 'home' && (
            <EmployeeHome
              completed={completed}
              onComplete={completeActivity}
              onOpen={() => setScreen('detail')}
            />
          )}
          {screen === 'detail' && (
            <DetailScreen
              completed={completed}
              onBack={() => setScreen('home')}
              onComplete={completeActivity}
            />
          )}
          {screen === 'completion' && (
            <CompletionScreen onHome={() => setScreen('home')} />
          )}
          {screen === 'hr' && <HrScreen onImport={() => setScreen('import')} />}
        </main>
      </div>
      <Navigation
        activeId={employeeZone ? 'home' : screen}
        items={navigation}
        mobile
        onSelect={setScreen}
      />
    </div>
  )
}

export default App
