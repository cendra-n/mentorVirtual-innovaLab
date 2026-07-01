// Todas las llamadas van a /api/ — Vite proxy las manda a Django
const BASE = '/api'

const headers = () => ({
  'Content-Type': 'application/json',
  ...(localStorage.getItem('access_token')
    ? { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    : {}),
})

// ── Tipos para respuestas de auth ──────────────────────────────────────────────
export interface ApiResult<T = any> {
  ok: boolean
  status: number
  data: T
}

// Errores de Django vienen como { campo: ["mensaje1", "mensaje2"] } o { detail: "..." }
export type ApiFieldErrors = Record<string, string>

// Convierte la respuesta cruda de error de DRF en un objeto plano { campo: "mensaje" }
// Ignora 'detail' y 'message', que son mensajes generales (no de un campo específico).
export function parseFieldErrors(data: any): ApiFieldErrors {
  const result: ApiFieldErrors = {}
  if (!data || typeof data !== 'object') return result
  for (const key of Object.keys(data)) {
    if (key === 'detail' || key === 'message') continue
    const value = data[key]
    if (Array.isArray(value) && value.length > 0) {
      result[key] = String(value[0])
    } else if (typeof value === 'string') {
      result[key] = value
    }
  }
  return result
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const apiLogin = (email: string, password: string): Promise<ApiResult> =>
  fetch(`${BASE}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  }).then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

export const apiRegister = (
  username: string,
  email: string,
  password: string,
  passwordConfirm: string
): Promise<ApiResult> =>
  fetch(`${BASE}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password, password_confirm: passwordConfirm }),
  }).then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

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

export const apiDeleteGoal = (id: number) =>
  fetch(`${BASE}/goals/${id}/delete/`, {
    method: 'DELETE',
    headers: headers(),
  }).then(r => r.json())

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