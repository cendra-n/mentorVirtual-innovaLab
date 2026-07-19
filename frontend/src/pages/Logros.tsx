import { useLogros } from '../hooks/useLogros'
import MentorBot from '../components/MentorBot'

/**
 * Página dedicada de Logros (destino real del ítem "Logros" del Sidebar).
 * Reusa el mismo hook useLogros() que ya alimenta LogrosCard en Perfil,
 * pero acá se muestra el listado completo: desbloqueados + pendientes.
 */
export default function Logros() {
  const { logros, desbloqueados, loading } = useLogros()
  const pendientes = logros.filter(l => !l?.unlocked)

  return (
    <div className="dash-header-wrap">
      <header className="dash-header">
        <div>
          <h1 className="dash-greeting">Tus logros 🏆</h1>
          <p className="dash-sub">Cada meta completada te va desbloqueando algo nuevo.</p>
        </div>
      </header>

      {loading && <p className="profile-empty-note">Cargando logros...</p>}

      {!loading && (
        <>
          <section className="dash-section">
            <div className="section-head">
              <h3>Desbloqueados ({desbloqueados.length})</h3>
            </div>
            {desbloqueados.length === 0 ? (
              <div className="empty-state">
                <MentorBot mood="ayudando" size={80} />
                <h3>Todavía no desbloqueaste ninguno</h3>
                <p>Completá pasos de tus metas para ir ganando logros.</p>
              </div>
            ) : (
              <div className="profile-logros-grid">
                {desbloqueados.map(l => (
                  <div key={l.id} className="profile-logro-box">
                    <div className="profile-logro-icon">{l.icon || '🏆'}</div>
                    <strong className="profile-logro-nombre">{l.name}</strong>
                    <span className="profile-logro-fecha">{l.unlocked_at || ''}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          {pendientes.length > 0 && (
            <section className="dash-section">
              <div className="section-head">
                <h3>Por desbloquear ({pendientes.length})</h3>
              </div>
              <div className="profile-logros-grid">
                {pendientes.map(l => (
                  <div key={l.id} className="profile-logro-box profile-logro-box--bloqueado">
                    <div className="profile-logro-icon">🔒</div>
                    <strong className="profile-logro-nombre">{l.name}</strong>
                    <span className="profile-logro-fecha">{l.description}</span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}
