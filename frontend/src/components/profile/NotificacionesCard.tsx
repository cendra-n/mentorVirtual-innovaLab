import { useState, useEffect } from 'react'

type Notificaciones = { correo: boolean; push: boolean }

function loadNotificaciones(): Notificaciones {
  try {
    const raw = localStorage.getItem('notificaciones_prefs')
    if (raw) return JSON.parse(raw)
  } catch { }
  return { correo: true, push: false }
}

/**
 * Tarjeta "Notificaciones" (columna principal de Perfil).
 * Totalmente independiente: guarda su estado en localStorage,
 * a la espera de que backend tenga un endpoint propio.
 */
export default function NotificacionesCard() {
  // Lazy initialization: React solo ejecuta loadNotificaciones al montar,
  // no en cada render (aporte de FE-017 / PR #47).
  const [notificaciones, setNotificaciones] = useState<Notificaciones>(loadNotificaciones)

  useEffect(() => {
    localStorage.setItem('notificaciones_prefs', JSON.stringify(notificaciones))
  }, [notificaciones])

  return (
    <div className="profile-card">
      <h3 className="profile-section-title">Notificaciones</h3>
      <div className="toggle-row">
        <div className="toggle-row-icon toggle-row-icon--blue">📧</div>
        <div className="toggle-row-text">
          <strong>Notificaciones por correo</strong>
          <p>Recibe actualizaciones, recordatorios y novedades en tu correo electrónico.</p>
        </div>
        <button type="button"
          className={`switch ${notificaciones.correo ? 'switch--on' : ''}`}
          onClick={() => setNotificaciones(p => ({ ...p, correo: !p.correo }))}
          aria-pressed={notificaciones.correo}
        >
          <span className="switch-knob" />
        </button>
      </div>
      <div className="toggle-row">
        <div className="toggle-row-icon toggle-row-icon--purple">📱</div>
        <div className="toggle-row-text">
          <strong>Notificaciones push</strong>
          <p>Activa las alertas del dispositivo para no perderte ningún evento.</p>
        </div>
        <button type="button"
          className={`switch ${notificaciones.push ? 'switch--on' : ''}`}
          onClick={() => setNotificaciones(p => ({ ...p, push: !p.push }))}
          aria-pressed={notificaciones.push}
        >
          <span className="switch-knob" />
        </button>
      </div>
    </div>
  )
}