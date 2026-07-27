import { useState, useEffect } from 'react'
import { useGoals } from '../../hooks/useGoals'
import { useLogros } from '../../hooks/useLogros'

const BASE = '/api'
const headers = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

/**
 * Tarjeta "Resumen de actividad" (columna lateral de Perfil).
 * Extraída como componente independiente. Hace su propio fetch del
 * perfil del estudiante para "videos vistos"; comparte los hooks de
 * goals y logros con las otras tarjetas que también los necesitan.
 */
export default function ResumenActividadCard() {
  const { goalsCompletados } = useGoals()
  const { desbloqueados } = useLogros()
  const [videosVistos, setVideosVistos] = useState(0)

  useEffect(() => {
    fetch(`${BASE}/auth/profile/student/update/`, { headers: headers() })
      .then(r => r.json())
      .then(data => setVideosVistos(data?.watched_videos_count ?? 0))
      .catch(() => { })
  }, [])

  return (
    <div className="profile-card">
      <h3 className="profile-section-title">Resumen de actividad</h3>
      <div className="activity-row">
        <span>Metas completadas</span>
        <strong>{goalsCompletados}</strong>
      </div>
      <div className="activity-row">
        <span>Videos vistos</span>
        <strong>{videosVistos}</strong>
      </div>
      <div className="activity-row">
        <span>Logros obtenidos</span>
        <strong>{desbloqueados.length}</strong>
      </div>
    </div>
  )
}