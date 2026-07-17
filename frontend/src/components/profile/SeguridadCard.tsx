import { useState } from 'react'

function EyeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EyeOffIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 11 8 11 8a18.45 18.45 0 0 1-3.06 4.16M6.61 6.61A18.45 18.45 0 0 0 1 13s4 8 11 8a10.43 10.43 0 0 0 5.39-1.49" />
      <line x1="2" y1="2" x2="22" y2="22" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

const BASE = '/api'
const headers = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

function getPasswordChecks(pass: string) {
  return {
    number: /[0-9]/.test(pass),
    upper: /[A-Z]/.test(pass),
    lower: /[a-z]/.test(pass),
    special: /[^A-Za-z0-9]/.test(pass),
    length: pass.length >= 8,
  }
}

/**
 * Tarjeta "Seguridad" / cambio de contraseña (columna principal de Perfil).
 * Totalmente independiente: maneja su propio estado y su propia
 * llamada a la API, sin depender de nada del resto de Profile.tsx.
 */
export default function SeguridadCard() {
  // FE-020: el formulario arranca oculto, y se muestra al tocar el
  // botón "Cambiar contraseña" — antes quedaba siempre visible.
  const [showForm, setShowForm] = useState(false)
  const [current, setCurrent] = useState('')
  const [newPass, setNewPass] = useState('')
  const [confirm, setConfirm] = useState('')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  const checks = getPasswordChecks(newPass)

  const handleChangePass = async () => {
    setMsg('')
    if (!current) { setMsg('❌ Ingresá tu contraseña actual.'); return }
    if (newPass.length < 8) { setMsg('❌ La nueva contraseña debe tener al menos 8 caracteres.'); return }
    if (newPass !== confirm) { setMsg('❌ Las contraseñas no coinciden.'); return }

    setLoading(true)
    try {
      const res = await fetch(`${BASE}/auth/change_password/`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({
          current_password: current,
          new_password: newPass,
          confirm_password: confirm,
        }),
      }).then(r => r.json())

      if (res.message) {
        setMsg('✅ ' + res.message)
        setCurrent(''); setNewPass(''); setConfirm('')
        setTimeout(() => setShowForm(false), 1500)
      } else {
        setMsg('❌ ' + (res.error || 'Ocurrió un error.'))
      }
    } catch {
      setMsg('❌ No se pudo conectar al servidor.')
    }
    setLoading(false)
  }

  const handleCancel = () => {
    setShowForm(false)
    setCurrent(''); setNewPass(''); setConfirm(''); setMsg('')
  }

  return (
    <div className="profile-card">
      <h3 className="profile-section-title">Seguridad</h3>
      <div className="security-row">
        <div className="toggle-row-icon toggle-row-icon--orange">🔒</div>
        <div className="toggle-row-text">
          <strong>Cambiar contraseña</strong>
          <p>Actualiza tu contraseña de acceso.</p>
        </div>
        {!showForm && (
          <button className="btn-outline-sm" onClick={() => setShowForm(true)}>
            Cambiar contraseña
          </button>
        )}
      </div>

      {showForm && (
        <div className="profile-form">
          <label>Contraseña actual</label>
          <div className="input-password-wrap">
            <input
              className="form-input"
              type={showPass ? 'text' : 'password'}
              placeholder="Tu contraseña actual"
              value={current}
              onChange={e => setCurrent(e.target.value)}
              autoComplete="current-password"
            />
            <button className="toggle-pass" onClick={() => setShowPass(!showPass)} tabIndex={-1}>
              {showPass ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>

          <label>Nueva contraseña</label>
          <input
            className="form-input"
            type={showPass ? 'text' : 'password'}
            placeholder="Mínimo 8 caracteres"
            value={newPass}
            onChange={e => setNewPass(e.target.value)}
            autoComplete="new-password"
          />

          {newPass && (
            <ul className="pass-requirements-figma">
              <li className={checks.number ? 'req-ok' : ''}><CheckIcon /> Tiene un número</li>
              <li className={checks.upper ? 'req-ok' : ''}><CheckIcon /> Cuenta con al menos una letra mayúscula</li>
              <li className={checks.lower ? 'req-ok' : ''}><CheckIcon /> Cuenta con al menos una letra minúscula</li>
              <li className={checks.special ? 'req-ok' : ''}><CheckIcon /> Tiene un carácter especial (+,-,*,$,...)</li>
              <li className={checks.length ? 'req-ok' : ''}><CheckIcon /> Tiene 8 o más dígitos</li>
            </ul>
          )}

          <label>Confirmá la nueva contraseña</label>
          <div className="input-password-wrap">
            <input
              className="form-input"
              type={showPass ? 'text' : 'password'}
              placeholder="Repetí la nueva contraseña"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              autoComplete="new-password"
            />
            {confirm && <span className="pass-match">{confirm === newPass ? '✅' : '❌'}</span>}
          </div>

          {msg && (
            <div className={`form-msg ${msg.startsWith('✅') ? 'form-msg--ok' : 'form-msg--error'}`}>
              {msg}
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className="btn-primary"
              onClick={handleChangePass}
              disabled={loading || !current || !newPass || !confirm}
            >
              {loading ? '⏳ Guardando...' : '🔑 Actualizar contraseña'}
            </button>
            <button className="btn-secondary" onClick={handleCancel} disabled={loading}>
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}