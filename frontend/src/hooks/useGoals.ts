import { useState, useEffect } from 'react'

const BASE = '/api'
const headers = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

interface Goal {
  id: number
  goal_text: string
  status: string
  created_at?: string
  total_steps: number
  completed_steps: number
}

function pctFor(g: Goal) {
  return g.total_steps > 0 ? Math.round((g.completed_steps / g.total_steps) * 100) : 0
}

function isCompleta(g: Goal) {
  return g.total_steps > 0 && g.completed_steps >= g.total_steps
}

/**
 * Trae las metas (goals) del usuario y calcula los valores derivados
 * que se usan en más de una tarjeta de Perfil (progreso general,
 * resumen de actividad).
 *
 * Shape real del backend (GoalListView → sp_get_goals_by_user):
 * { goals: [{ id, goal_text, status, created_at, total_steps, completed_steps }] }
 * — no trae "progreso" ni "completado" ya calculados, así que se
 * derivan acá a partir de total_steps/completed_steps (mismo criterio
 * que ya usa GoalCard.tsx para la barra de progreso).
 */
export function useGoals() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}/goals/`, { headers: headers() })
      .then(r => r.json())
      .then(data => setGoals(Array.isArray(data) ? data : data?.goals || data?.results || []))
      .catch(() => { })
      .finally(() => setLoading(false))
  }, [])

  const goalsCompletados = goals.filter(isCompleta).length
  const progresoGeneral = goals.length > 0
    ? Math.round(goals.reduce((acc, g) => acc + pctFor(g), 0) / goals.length)
    : 0
  const moduloActualRaw = goals.find(g => !isCompleta(g))
  // Se le agrega "progreso" calculado para que ProgresoCard no tenga
  // que conocer el shape real del goal.
  const moduloActual = moduloActualRaw ? { ...moduloActualRaw, progreso: pctFor(moduloActualRaw) } : undefined

  return { goals, loading, goalsCompletados, progresoGeneral, moduloActual }
}
