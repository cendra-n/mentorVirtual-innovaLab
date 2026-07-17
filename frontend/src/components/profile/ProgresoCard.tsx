import { useGoals } from '../../hooks/useGoals'

/**
 * Tarjeta "Tu progreso general" (columna lateral de Perfil).
 * Extraída como componente independiente para poder editarla sin
 * tocar el resto de Profile.tsx.
 */
export default function ProgresoCard() {
  const { progresoGeneral, moduloActual } = useGoals()

  return (
    <div className="profile-card profile-progress-card">
      <h3 className="profile-section-title">Tu progreso general</h3>
      <div className="progress-ring-wrap">
        <div
          className="progress-ring"
          style={{ background: `conic-gradient(var(--azul) ${progresoGeneral * 3.6}deg, var(--gris-borde) 0deg)` }}
        >
          <div className="progress-ring-inner">{progresoGeneral}%</div>
        </div>
      </div>
      {/* TODO: reemplazar por datos reales de "módulo actual" cuando exista el campo en backend */}
      <div className="progress-mini-row">
        <span>Meta actual</span>
        <span>{moduloActual?.progreso ?? 0}%</span>
      </div>
      <div className="progress-mini-bar">
        <div className="progress-mini-fill" style={{ width: `${moduloActual?.progreso ?? 0}%` }} />
      </div>
    </div>
  )
}