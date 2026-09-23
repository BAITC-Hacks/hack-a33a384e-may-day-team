// Presentation fixture only. This shape is not an API contract.
const demoEmployee = {
  firstName: 'Марат',
  fullName: 'Марат Есенов',
  initials: 'МЕ',
  role: 'Backend Engineer',
  currentGrade: 'Middle',
  targetGrade: 'Senior',
}

const gaps = [
  { skill: 'System Design', current: 2, required: 4 },
  { skill: 'API Design', current: 3, required: 4 },
  { skill: 'Architecture', current: 2, required: 3 },
]

export const demoDashboard = {
  employee: demoEmployee,
  progress: { completed: 6, total: 10, criticalCompleted: 1, criticalTotal: 4 },
  before: {
    recommendation: {
      title: 'System Design Fundamentals',
      desktopBadge: 'AI · Рекомендуемый шаг',
      mobileBadge: 'Лучший следующий шаг',
      description: `Критический навык для ${demoEmployee.targetGrade}`,
      skill: 'System Design',
      currentLevel: 2,
      projectedLevel: 3,
      targetLevel: 4,
      desktopReasons: [
        `Критический навык для ${demoEmployee.targetGrade}`,
        'Предварительные требования выполнены',
        'История участия учтена',
      ],
      mobileReasons: ['Активность доступна', 'История учтена'],
    },
    criticalGaps: gaps,
    alternateStep: {
      title: 'API Design Workshop',
      skill: 'API Design',
      currentLevel: 3,
      projectedLevel: 4,
    },
  },
  after: {
    recommendation: {
      title: 'API Design Workshop',
      desktopBadge: 'Следующий шаг',
      mobileBadge: 'Следующий шаг',
      description: 'Ещё одно критическое требование Senior',
      skill: 'API Design',
      currentLevel: 3,
      projectedLevel: 4,
      targetLevel: 4,
      desktopReasons: [
        'Критический навык для Senior',
        'System Design уже вырос до 3',
        'Требование Senior ещё не закрыто',
      ],
      mobileReasons: ['Критический навык', 'До цели 1 уровень'],
    },
    criticalGaps: [
      { skill: 'System Design', current: 3, required: 4 },
      gaps[1],
      gaps[2],
    ],
    alternateStep: null,
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
  completedActivity: {
    title: 'System Design Fundamentals',
    skill: 'System Design',
    from: 2,
    to: 3,
    target: 4,
  },
  comparison: {
    chosen: {
      title: 'System Design Fundamentals',
      now: '2 / 4',
      importance: 'Критический',
      after: '3 / 4',
    },
    alternative: {
      title: 'Public Speaking Club',
      now: '0 / 1',
      importance: 'Некритический',
      after: '1 / 1',
    },
    reasons: [
      'Грейд: ближайший шаг — переход Middle → Senior',
      'Разрыв: System Design критичен и ещё не закрыт',
      'История: предварительные требования выполнены, активность не пройдена',
      'Требования следующего уровня: после шага останется 3 / 4',
    ],
  },
  hr: {
    name: 'Анна Садыкова',
    initials: 'АС',
    role: 'HR',
    withoutNextStep: 12,
    gaps: [
      { skill: 'System Design', employees: 34, label: '34 сотрудника' },
      { skill: 'Leadership', employees: 28, label: '28 сотрудников' },
      { skill: 'Data Analysis', employees: 21, label: '21 сотрудник' },
    ],
    participation: [
      { activity: 'System Design Fundamentals', completed: 18, missed: 3, dropped: 2, declined: 4 },
      { activity: 'API Design Workshop', completed: 14, missed: 1, dropped: 3, declined: 2 },
      { activity: 'Public Speaking Club', completed: 23, missed: 2, dropped: 1, declined: 5 },
    ],
    totals: { completed: 55, missed: 6, dropped: 6, declined: 11 },
  },
  importCheck: {
    files: [
      { title: 'Профиль сотрудника', format: 'JSON', name: 'employee.json' },
      { title: 'История участия', format: 'CSV', name: 'history.csv' },
    ],
    checks: ['Схема корректна', '14 записей истории', 'Навыки распознаны'],
  },
}
