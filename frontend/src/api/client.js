const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

let csrfToken = ''

export class ApiError extends Error {
  constructor(message, status, code, details = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers)
  let body = options.body

  if (body && !(body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
    body = JSON.stringify(body)
  }

  if (options.method === 'POST' && csrfToken) {
    headers.set('X-CSRF-Token', csrfToken)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    body,
    credentials: 'include',
    headers,
  })
  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const error = typeof payload === 'object' && payload !== null ? payload : {}
    throw new ApiError(
      error.message || `Request failed with status ${response.status}.`,
      response.status,
      error.code || 'request_failed',
      error.details,
    )
  }

  if (payload?.csrf_token) csrfToken = payload.csrf_token
  return payload
}

export const careerQuestApi = {
  demoLogin(role) {
    return request('/api/auth/demo-login', {
      method: 'POST',
      body: { role },
    })
  },

  me() {
    return request('/api/auth/me')
  },

  employeeProfile(employeeId) {
    return request(`/api/employees/${encodeURIComponent(employeeId)}`)
  },

  recommendations(employeeId) {
    return request(
      `/api/employees/${encodeURIComponent(employeeId)}/recommendations`,
    )
  },

  candidates(employeeId) {
    return request(`/api/employees/${encodeURIComponent(employeeId)}/candidates`)
  },

  completeActivity(employeeId, eventId, sessionDate) {
    return request(
      `/api/employees/${encodeURIComponent(employeeId)}/activities/${encodeURIComponent(eventId)}/complete`,
      {
        method: 'POST',
        headers: { 'Idempotency-Key': crypto.randomUUID() },
        body: sessionDate ? { session_date: sessionDate } : {},
      },
    )
  },

  hrOverview() {
    return request('/api/hr/overview')
  },

  importHr(employeesFile, historyFile) {
    const form = new FormData()
    form.append('employees_file', employeesFile)
    form.append('history_file', historyFile)
    return request('/api/hr/import', { method: 'POST', body: form })
  },
}
