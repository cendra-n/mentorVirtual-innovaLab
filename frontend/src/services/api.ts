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
    if (key === 'detail' || key === 'message' || key === 'error') continue
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

export const apiLogout = (refreshToken: string): Promise<ApiResult> =>
  fetch(`${BASE}/auth/logout/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
    body: JSON.stringify({ refresh: refreshToken }),
  }).then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

export const apiRegister = (
  username: string,
  email: string,
  password: string,
  passwordConfirm: string,
  geo?: { country?: number | null; province?: number | null; locality?: number | null }
): Promise<ApiResult> =>
  fetch(`${BASE}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username, email, password, password_confirm: passwordConfirm,
      ...(geo?.country  ? { country: geo.country }   : {}),
      ...(geo?.province ? { province: geo.province } : {}),
      ...(geo?.locality ? { locality: geo.locality } : {}),
    }),
  }).then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

// PATCH /me/ — email, teléfono, avatar y país/provincia/localidad de residencia
export const apiUpdateProfile = (data: Record<string, any>): Promise<ApiResult> =>
  fetch(`${BASE}/auth/me/`, {
    method: 'PATCH',
    headers: headers(),
    body: JSON.stringify(data),
  }).then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

// ── Geo (países / provincias) ──────────────────────────────────────────────────
export const apiGeoCountries = (): Promise<ApiResult> =>
  fetch(`${BASE}/auth/geo/countries/`, { headers: headers() })
    .then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

export const apiGeoProvinces = (countryId: number | string): Promise<ApiResult> =>
  fetch(`${BASE}/auth/geo/provinces/list?country=${countryId}`, { headers: headers() })
    .then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

// Ojo: 'province' es obligatorio en el backend — pedirlo sin filtro devuelve 400
// (antes bloqueaba Swagger devolviendo las ~3.800 localidades de golpe, sin paginar).
// 'search' filtra por texto server-side — es lo que arma el autocompletado
// (con page_size chico ahora, no tiene sentido traer todo de una).
export const apiGeoLocalities = (provinceId: number | string, search?: string): Promise<ApiResult> =>
  fetch(`${BASE}/auth/geo/localities/?province=${provinceId}${search ? `&search=${encodeURIComponent(search)}` : ''}`, { headers: headers() })
    .then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

export const apiUpdateStudentProfile = (
  accessToken: string,
  // Acepta cualquier campo de StudentProfile en inglés (birth_date,
  // education_level, employment_status, user_gender, primary_objective,
  // time_availability, user_interests, etc.) — migración ES→EN completa.
  data: Record<string, any>
): Promise<ApiResult> =>
  fetch(`${BASE}/auth/profile/student/update/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(data),
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

// ── authFetch: intercepta 401, refresca el token una vez y reintenta ──────────
// Si el refresh también falla, fuerza logout (limpia tokens y recarga para
// que App.tsx vuelva a la pantalla de login).
let refreshing: Promise<boolean> | null = null

async function doRefresh(): Promise<boolean> {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return false
  try {
    const r = await fetch(`${BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
    if (!r.ok) return false
    const data = await r.json()
    if (!data.access) return false
    localStorage.setItem('access_token', data.access)
    // ROTATE_REFRESH_TOKENS=True en el backend: si vuelve un refresh nuevo, lo guardamos.
    if (data.refresh) localStorage.setItem('refresh_token', data.refresh)
    return true
  } catch {
    return false
  }
}

function forceLogout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('chat_recientes')
  window.location.reload()
}

export async function authFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const doFetch = () =>
    fetch(input, {
      ...init,
      headers: { ...headers(), ...(init.headers || {}) },
    })

  let res = await doFetch()

  if (res.status === 401) {
    if (!refreshing) refreshing = doRefresh().finally(() => { refreshing = null })
    const ok = await refreshing
    if (!ok) {
      forceLogout()
      return res
    }
    res = await doFetch()
    if (res.status === 401) {
      forceLogout()
    }
  }

  return res
}

// ── Tutor / Chat con Pulso ─────────────────────────────────────────────────
export const apiChatPulso = (question: string): Promise<ApiResult> =>
  authFetch(`${BASE}/tutor/chat/`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  }).then(async r => ({ ok: r.ok, status: r.status, data: await r.json() }))

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