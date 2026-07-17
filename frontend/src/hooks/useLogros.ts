import { useState, useEffect } from 'react'

const BASE = '/api'
const headers = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

interface Logro {
  id: number
  goal_id: number
  goal_text: string
  name: string
  description: string
  icon: string
  unlocked: boolean
  unlocked_at: string | null
}

/**
 * Trae los logros del usuario. Se usa tanto en LogrosCard (listado
 * completo) como en ResumenActividadCard (solo el conteo).
 *
 * Shape real del backend (UserLogrosView → sp_get_user_logros):
 * { logros: [{ id, goal_id, goal_text, name, description, icon, unlocked, unlocked_at }] }
 * — OJO: devuelve TODOS los logros, desbloqueados y pendientes (así lo
 * documenta la propia vista). "desbloqueados" filtra solo los que el
 * usuario ya obtuvo, que es lo único que corresponde mostrar/contar.
 */
export function useLogros() {
  const [logros, setLogros] = useState<Logro[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}/progress/logros/`, { headers: headers() })
      .then(r => r.json())
      .then(data => setLogros(Array.isArray(data) ? data : data?.logros || data?.results || []))
      .catch(() => { })
      .finally(() => setLoading(false))
  }, [])

  const desbloqueados = logros.filter(l => l?.unlocked)

  return { logros, desbloqueados, loading }
}
