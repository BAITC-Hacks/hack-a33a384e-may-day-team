import { useEffect, useState } from 'react'
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
import { careerQuestApi } from './api/client.js'
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

function initials(value = '') {
  return value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase() || 'CQ'
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
            {person.name}
            {person.role === 'hr' ? ' · HR' : ''}
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

function ProgressCard({ profile }) {
  const completed = profile.requirements_met_count
  const total = profile.requirements_total
  const percentage = total > 0 ? (completed / total) * 100 : 0
  const targetGrade = profile.primary_target?.grade || 'следующей цели'

  return (
    <section className="card progress-card" aria-labelledby="progress-heading">
      <div className="progress-card__copy">
        <h2 id="progress-heading">Прогресс к {targetGrade}</h2>
        <p>
          <strong>{completed} из {total}</strong>
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

function primaryImpact(recommendation) {
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

function RecommendationCard({
  loading,
  onComplete,
  onOpen,
  recommendation,
  usedAi,
}) {
  if (!recommendation || !usedAi) {
    return (
      <article className="card recommendation-card">
        <p className="recommendation-badge">Статус рекомендации</p>
        <h2>Рекомендация временно недоступна</h2>
        <p className="recommendation-card__description">
          Профиль загружен, но AI-рекомендация сейчас не получена.
        </p>
      </article>
    )
  }

  const impact = primaryImpact(recommendation)
  const reasons = [
    recommendation.reasoning_summary,
    recommendation.tradeoff,
  ].filter(Boolean)

  return (
    <article className="card recommendation-card">
      <p className="recommendation-badge">
        <span className="desktop-only">AI · Рекомендуемый шаг</span>
        <span className="mobile-only">AI · Следующий шаг</span>
      </p>
      <h2>{recommendation.title}</h2>
      <p className="recommendation-card__description">
        {recommendation.type} · {recommendation.format}
      </p>

      <div className="recommendation-forecast">
        <span className="forecast-skill desktop-only">{impact.skillId}</span>
        <div className="forecast-change">
          <span>
            <small className="mobile-only">Сейчас</small>{' '}
            {impact.currentLevel}
          </span>
          <span className="forecast-arrow">→</span>
          <span>
            <small className="mobile-only">После</small> {impact.newLevel}
          </span>
        </div>
        <span className="forecast-divider desktop-only" aria-hidden="true">/</span>
        <span className="forecast-target">
          <span className="desktop-only">цель </span>
          <span className="mobile-only">Цель — </span>
          {impact.requiredLevel}
        </span>
      </div>

      <ul className="recommendation-reasons">
        {reasons.map((reason) => (
          <li key={reason}>
            <CheckIcon />
            <span>{reason}</span>
          </li>
        ))}
      </ul>

      <div className="recommendation-actions">
        <button
          className="button button--primary"
          disabled={loading}
          onClick={onOpen}
          type="button"
        >
          <span className="desktop-only">Подробнее</span>
          <span className="mobile-only">Почему именно это?</span>
        </button>
        <button
          className="button button--secondary"
          disabled={loading}
          onClick={onComplete}
          type="button"
        >
          {loading ? 'Обновляем…' : 'Отметить выполненным'}
        </button>
      </div>

      <p className="recommendation-card__note desktop-only">
        Рекомендация получена из защищённого API
      </p>
    </article>
  )
}

function LevelSegments({ current, required }) {
  const safeRequired = Number.isInteger(required) ? required : 0
  return (
    <span className="level-segments" aria-hidden="true">
      {Array.from({ length: safeRequired }, (_, index) => (
        <span className={index < current ? 'is-filled' : ''} key={index} />
      ))}
    </span>
  )
}

function CriticalGaps({ requirements, skills }) {
  const gaps = requirements.filter(
    (item) => item.critical && item.missing_level > 0,
  )

  return (
    <section className="card gaps-card" aria-labelledby="gaps-heading">
      <h2 id="gaps-heading">Критические пробелы</h2>
      {gaps.length === 0 ? (
        <p>Критические требования закрыты.</p>
      ) : (
        <ul>
          {gaps.map((gap) => (
            <li key={gap.skill_id}>
              <span className="gap-name">{gap.skill_id}</span>
              <span className="gap-value">
                {skills.find((skill) => skill.skill_id === gap.skill_id)
                  ?.current_level ?? gap.current_level}{' '}
                / {gap.required_level}
              </span>
              <LevelSegments
                current={
                  skills.find((skill) => skill.skill_id === gap.skill_id)
                    ?.current_level ?? gap.current_level
                }
                required={gap.required_level}
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function AlternateStep({ alternateStep, onOpen }) {
  if (!alternateStep) return null
  const impact = primaryImpact(alternateStep)

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
            {impact.skillId} &nbsp;{impact.currentLevel} → {impact.newLevel}
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

function RecentActivity({ history }) {
  const recent = history.slice(-2).reverse()

  return (
    <section className="card activity-card" aria-labelledby="activity-heading">
      <h2 id="activity-heading">Последняя активность</h2>
      {recent.length === 0 ? (
        <p>История пока пуста.</p>
      ) : (
        <ul>
          {recent.map((item) => (
            <li key={item.record_id}>
              <span
                className={`activity-card__icon ${
                  item.status === 'completed'
                    ? 'activity-card__icon--success'
                    : 'activity-card__icon--neutral'
                }`}
                aria-hidden="true"
              >
                <DocumentIcon />
              </span>
              <div>
                <h3>{item.event_id}</h3>
                <p>{item.status} · {item.date}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function EmployeeHome({
  loading,
  onComplete,
  onOpen,
  profile,
  recommendations,
}) {
  const recommendation =
    recommendations?.used_ai === true
      ? recommendations.recommendations?.[0] || null
      : null
  const alternative = recommendations?.comparison?.alternative_event || null
  const target = profile.primary_target

  return (
    <>
      <header className="dashboard-intro">
        <div className="dashboard-intro__desktop">
          <p className="dashboard-intro__eyebrow">ВАШ КАРЬЕРНЫЙ ПУТЬ</p>
          <h1>{profile.full_name}, ваш следующий шаг</h1>
          <p className="dashboard-intro__subtitle">
            {profile.role} · {profile.grade}
            {target ? ` → ${target.grade}` : ''}
          </p>
        </div>
        <div className="dashboard-intro__mobile">
          <p>{profile.full_name}</p>
          <h1>{profile.role}</h1>
          <p>{profile.grade}{target ? ` → ${target.grade}` : ''}</p>
        </div>
      </header>
      <ProgressCard profile={profile} />
      <div className="dashboard-grid">
        <div className="dashboard-grid__primary">
          <RecommendationCard
            loading={loading}
            onComplete={onComplete}
            onOpen={onOpen}
            recommendation={recommendation}
            usedAi={recommendations?.used_ai === true}
          />
          <AlternateStep alternateStep={alternative} onOpen={onOpen} />
        </div>
        <div className="dashboard-grid__secondary">
          <CriticalGaps
            requirements={profile.requirements}
            skills={profile.skills}
          />
          <RecentActivity history={profile.history} />
        </div>
      </div>
      <p className="content-demo-label">
        Данные backend API · {profile.candidate_status}
      </p>
    </>
  )
}

function App() {
  const [screen, setScreen] = useState('login')
  const [session, setSession] = useState(null)
  const [profile, setProfile] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [completion, setCompletion] = useState(null)
  const [hrOverview, setHrOverview] = useState(null)
  const [importResult, setImportResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    async function restoreSession() {
      try {
        const current = await careerQuestApi.me()
        if (!active) return
        setSession(current)
        if (current.role === 'employee' && current.employee_id) {
          const [nextProfile, nextRecommendations] = await Promise.all([
            careerQuestApi.employeeProfile(current.employee_id),
            careerQuestApi.recommendations(current.employee_id),
          ])
          if (!active) return
          setProfile(nextProfile)
          setRecommendations(nextRecommendations)
          setScreen('home')
        } else if (current.role === 'hr') {
          const overview = await careerQuestApi.hrOverview()
          if (!active) return
          setHrOverview(overview)
          setScreen('hr')
        }
      } catch (caught) {
        if (active && caught.status !== 401) setError(caught.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    restoreSession()
    return () => {
      active = false
    }
  }, [])

  async function login(role, destination) {
    setLoading(true)
    setError('')
    setImportResult(null)
    try {
      await careerQuestApi.demoLogin(role)
      const current = await careerQuestApi.me()
      if (current.role !== role) {
        throw new Error('Сервер вернул аккаунт с другой ролью.')
      }
      setSession(current)
      if (role === 'employee') {
        if (!current.employee_id) throw new Error('В сессии нет employee_id.')
        const [nextProfile, nextRecommendations] = await Promise.all([
          careerQuestApi.employeeProfile(current.employee_id),
          careerQuestApi.recommendations(current.employee_id),
        ])
        setProfile(nextProfile)
        setRecommendations(nextRecommendations)
        setScreen('home')
      } else {
        const overview = await careerQuestApi.hrOverview()
        setHrOverview(overview)
        setScreen(destination || 'hr')
      }
    } catch (caught) {
      setError(caught.message)
    } finally {
      setLoading(false)
    }
  }

  async function completeActivity() {
    const recommendation =
      recommendations?.used_ai === true
        ? recommendations.recommendations?.[0]
        : null
    if (!session?.employee_id || !recommendation) return

    const sessionDate =
      recommendation.format === 'self_paced'
        ? undefined
        : recommendation.upcoming_sessions?.[0]
    if (recommendation.format !== 'self_paced' && !sessionDate) {
      setError('Для этой активности сервер не вернул доступную сессию.')
      return
    }

    setLoading(true)
    setError('')
    try {
      const result = await careerQuestApi.completeActivity(
        session.employee_id,
        recommendation.event_id,
        sessionDate,
      )
      const [nextProfile, nextRecommendations] = await Promise.all([
        careerQuestApi.employeeProfile(session.employee_id),
        careerQuestApi.recommendations(session.employee_id),
      ])
      setCompletion(result)
      setProfile(nextProfile)
      setRecommendations(nextRecommendations)
      setScreen('completion')
    } catch (caught) {
      setError(caught.message)
    } finally {
      setLoading(false)
    }
  }

  async function importFiles(employeesFile, historyFile) {
    setLoading(true)
    setError('')
    setImportResult(null)
    try {
      const result = await careerQuestApi.importHr(employeesFile, historyFile)
      setImportResult(result)
      setHrOverview(await careerQuestApi.hrOverview())
    } catch (caught) {
      setError(caught.message)
    } finally {
      setLoading(false)
    }
  }

  if (screen === 'login' || (!session && screen !== 'login')) {
    return (
      <LoginScreen
        error={error}
        loading={loading}
        onEmployee={() => login('employee')}
        onHr={() => login('hr')}
        onImport={() => login('hr', 'import')}
      />
    )
  }

  if (screen === 'import') {
    return (
      <ImportScreen
        error={error}
        loading={loading}
        onBack={() => setScreen('hr')}
        onImport={importFiles}
        result={importResult}
      />
    )
  }

  const employeeZone =
    screen === 'home' || screen === 'detail' || screen === 'completion'
  const hrZone = screen === 'hr'
  const personName =
    session.role === 'employee' ? profile?.full_name : session.username
  const person = {
    initials: initials(personName),
    name: personName || session.username,
    role: session.role,
  }
  const navigation = hrZone ? hrNavigation : employeeNavigation
  const activeRecommendation =
    recommendations?.used_ai === true
      ? recommendations.recommendations?.[0] || null
      : null

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
          Данные API
          <span>Защищённая сессия</span>
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
          {error && <p className="api-status api-status--error">{error}</p>}
          {screen === 'home' && profile && (
            <EmployeeHome
              loading={loading}
              onComplete={completeActivity}
              onOpen={() => setScreen('detail')}
              profile={profile}
              recommendations={recommendations}
            />
          )}
          {screen === 'detail' && profile && (
            <DetailScreen
              loading={loading}
              onBack={() => setScreen('home')}
              onComplete={completeActivity}
              profile={profile}
              recommendation={activeRecommendation}
              recommendationEnvelope={recommendations}
            />
          )}
          {screen === 'completion' && profile && completion && (
            <CompletionScreen
              completion={completion}
              nextRecommendation={activeRecommendation}
              onHome={() => setScreen('home')}
              profile={profile}
            />
          )}
          {screen === 'hr' && hrOverview && (
            <HrScreen
              onImport={() => {
                setError('')
                setImportResult(null)
                setScreen('import')
              }}
              overview={hrOverview}
            />
          )}
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
