// Todas las llamadas van a /api/ — Vite proxy las manda a Django
const BASE = '/api'

const headers = () => ({
  'Content-Type': 'application/json',
  ...(localStorage.getItem('access_token')
    ? { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    : {}),
})

// ── Auth ──────────────────────────────────────────────────────────────────────
export const apiLogin = (username: string, password: string) =>
  fetch(`${BASE}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  }).then(r => r.json())

export const apiRegister = (username: string, email: string, password: string, passwordConfirm: string) =>
  fetch(`${BASE}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password, password_confirm: passwordConfirm }),
  }).then(r => r.json())

export const apiMe = () =>
  fetch(`${BASE}/auth/me/`, { headers: headers() }).then(r => r.json())

// ── Goals ─────────────────────────────────────────────────────────────────────
export const apiGetGoals = () =>
  fetch(`${BASE}/goals/`, { headers: headers() }).then(r => r.json())

export const apiCreateGoal = (goal_text: string) =>
  fetch(`${BASE}/goals/create/`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ goal_text }),
  }).then(r => r.json())

export const apiGetGoal = (id: number) =>
  fetch(`${BASE}/goals/${id}/`, { headers: headers() }).then(r => r.json())

// ── Progress ──────────────────────────────────────────────────────────────────
export const apiCompleteStep = (stepId: number, goalId: number) =>
  fetch(`${BASE}/progress/steps/${stepId}/complete/`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ goal_id: goalId }),
  }).then(r => r.json())

export const apiVideoView = (videoId: number, stepId: number) =>
  fetch(`${BASE}/progress/videos/${videoId}/view/`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ step_id: stepId }),
  }).then(r => r.json())

export const apiStreak = () =>
  fetch(`${BASE}/progress/streak/`, { headers: headers() }).then(r => r.json())

export const apiLogros = () =>
  fetch(`${BASE}/progress/logros/`, { headers: headers() }).then(r => r.json())
