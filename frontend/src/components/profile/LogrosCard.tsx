import { useLogros } from '../../hooks/useLogros'

/**
 * Tarjeta "Mis logros" (columna principal de Perfil).
 * Extraída como componente independiente.
 */
export default function LogrosCard() {
  const { desbloqueados, loading } = useLogros()

  return (
    <div className="profile-card">
      <div className="profile-card-header">
        <h3 className="profile-section-title">Mis logros</h3>
        <button className="link-btn">Ver todo →</button>
      </div>
      {loading && <p className="profile-empty-note">Cargando logros...</p>}
      {!loading && desbloqueados.length === 0 && (
        <p className="profile-empty-note">Todavía no desbloqueaste logros. ¡Seguí aprendiendo!</p>
      )}
      {!loading && desbloqueados.length > 0 && (
        <div className="profile-logros-grid">
          {desbloqueados.slice(0, 4).map((l, i) => (
            <div key={l?.id ?? i} className="profile-logro-box">
              <div className="profile-logro-icon">{l?.icon || '🏆'}</div>
              <strong className="profile-logro-nombre">{l?.name || 'Logro'}</strong>
              <span className="profile-logro-fecha">{l?.unlocked_at || ''}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}