// F1 presentation fixture only. This shape is not an API contract and contains
// no real employee data; production values will come from the approved backend.
export const demoDashboard = {
  employee: {
    firstName: 'Марат',
    fullName: 'Марат Есенов',
    initials: 'МЕ',
    role: 'Backend Engineer',
    currentGrade: 'Middle',
    targetGrade: 'Senior',
  },
  progress: {
    completed: 6,
    total: 10,
  },
  recommendation: {
    title: 'System Design Fundamentals',
    desktopBadge: 'AI · Рекомендуемый шаг',
    mobileBadge: 'Лучший следующий шаг',
    description: 'Критический навык для Senior',
    skill: 'System Design',
    currentLevel: 2,
    projectedLevel: 3,
    targetLevel: 4,
    desktopReasons: [
      'Критический навык для Senior',
      'Предварительные требования выполнены',
      'История участия учтена',
    ],
    mobileReasons: ['Активность доступна', 'История учтена'],
  },
  criticalGaps: [
    { skill: 'System Design', current: 2, required: 4 },
    { skill: 'API Design', current: 3, required: 4 },
    { skill: 'Architecture', current: 2, required: 3 },
  ],
  alternateStep: {
    title: 'API Design Workshop',
    skill: 'API Design',
    currentLevel: 3,
    projectedLevel: 4,
  },
  recentActivity: [
    {
      title: 'Code Review Practice',
      status: 'Завершено',
      date: '20 сентября',
      tone: 'success',
    },
    {
      title: 'Architecture Workshop',
      status: 'Не посетил',
      date: '18 сентября',
      tone: 'neutral',
    },
  ],
}
