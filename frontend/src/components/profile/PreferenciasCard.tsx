import { useState, useEffect } from 'react'

type Preferencias = { idioma: string; modoOscuro: boolean }

function loadPreferencias(): Preferencias {
  try {
    const raw = localStorage.getItem('ui_preferencias')
    if (raw) return JSON.parse(raw)
  } catch { }
  return { idioma: 'es', modoOscuro: false }
}

/**
 * Tarjeta "Preferencias" (columna principal de Perfil).
 * Totalmente independiente: guarda su estado en localStorage,
 * a la espera de que backend tenga un endpoint propio.
 */
export default function PreferenciasCard() {
  const [preferencias, setPreferencias] = useState<Preferencias>(loadPreferencias())

  useEffect(() => {
    localStorage.setItem('ui_preferencias', JSON.stringify(preferencias))
    // Acá es donde se aplica de verdad el modo oscuro a toda la app.
    // Si UX/UI pide otra forma de aplicarlo (ej. atributo en vez de
    // clase), es este el único lugar que hay que tocar.
    document.body.classList.toggle('dark-mode', preferencias.modoOscuro)
  }, [preferencias])

  return (
    <div className="profile-card">
      <h3 className="profile-section-title">Preferencias</h3>
      <div className="toggle-row">
        <div className="toggle-row-icon toggle-row-icon--green">🌐</div>
        <div className="toggle-row-text">
          <strong>Idioma de la plataforma</strong>
          <p>Elige el idioma de tu preferencia.</p>
        </div>
        <select
          className="form-select"
          value={preferencias.idioma}
          onChange={e => setPreferencias(p => ({ ...p, idioma: e.target.value }))}
        >
          <option value="es">Español</option>
          <option value="en">English</option>
        </select>
      </div>
      <div className="toggle-row">
        <div className="toggle-row-icon toggle-row-icon--dark">{preferencias.modoOscuro ? '☀️' : '🌙'}</div>
        <div className="toggle-row-text">
          <strong>{preferencias.modoOscuro ? 'Modo claro' : 'Modo oscuro'}</strong>
          <p>
            {preferencias.modoOscuro
              ? 'Volvé al tema claro.'
              : 'Activa el tema oscuro para mayor comodidad visual.'}
          </p>
        </div>
        <button
          className={`switch ${preferencias.modoOscuro ? 'switch--on' : ''}`}
          onClick={() => setPreferencias(p => ({ ...p, modoOscuro: !p.modoOscuro }))}
          aria-pressed={preferencias.modoOscuro}
        >
          <span className="switch-knob" />
        </button>
      </div>
    </div>
  )
}