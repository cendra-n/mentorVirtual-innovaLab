import { useState } from 'react'
import MentorBot from '../components/MentorBot'

interface Props {
  user: any
}

const BASE = '/api'
const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

export default function Profile({ user }: Props) {
  const [current,  setCurrent]  = useState('')
  const [newPass,  setNewPass]  = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [msg,      setMsg]      = useState('')
  const [loading,  setLoading]  = useState(false)
  const [showPass, setShowPass] = useState(false)

  const displayName = user?.first_name || user?.username || '...'

  const handleChangePass = async () => {
    setMsg('')
    if (!current)           { setMsg('❌ Ingresá tu contraseña actual.'); return }
    if (newPass.length < 8) { setMsg('❌ La nueva contraseña debe tener al menos 8 caracteres.'); return }
    if (newPass !== confirm) { setMsg('❌ Las contraseñas no coinciden.'); return }

    setLoading(true)
    try {
      const res = await fetch(`${BASE}/auth/change_password/`, {
        method: 'POST',
        headers: h(),
        body: JSON.stringify({
          current_password:  current,
          new_password:      newPass,
          confirm_password:  confirm,
        }),
      }).then(r => r.json())

      if (res.message) {
        setMsg('✅ ' + res.message)
        setCurrent('')
        setNewPass('')
        setConfirm('')
      } else {
        setMsg('❌ ' + (res.error || 'Ocurrió un error.'))
      }
    } catch {
      setMsg('❌ No se pudo conectar al servidor.')
    }
    setLoading(false)
  }

  const strength = (p: string) => {
    let s = 0
    if (p.length >= 8) s++
    if (/[A-Z]/.test(p)) s++
    if (/[0-9]/.test(p)) s++
    if (/[^A-Za-z0-9]/.test(p)) s++
    return s
  }
  const strengthLabel = ['', 'Débil', 'Regular', 'Buena', 'Fuerte']

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1 className="detail-title">Mi perfil</h1>
        <p className="detail-sub">Tus datos y configuración de cuenta</p>
      </div>

      <div className="profile-body">
        {/* Datos del usuario */}
        <div className="profile-card">
          <div className="profile-avatar-row">
            <div className="profile-avatar">
              {displayName.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="profile-name">{displayName}</h2>
              <p className="profile-username">@{user?.username}</p>
              {user?.is_staff && <span className="profile-badge">⚙️ Administrador</span>}
            </div>
            <MentorBot mood="guiñando" size={56} className="profile-bot" />
          </div>

          <div className="profile-info-grid">
            <div className="profile-info-item">
              <span className="profile-info-label">Usuario</span>
              <span className="profile-info-value">{user?.username}</span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Email</span>
              <span className="profile-info-value">{user?.email || '—'}</span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Miembro desde</span>
              <span className="profile-info-value">
                {user?.date_joined
                  ? new Date(user.date_joined).toLocaleDateString('es-AR', { year: 'numeric', month: 'long' })
                  : '—'}
              </span>
            </div>
          </div>
        </div>

        {/* Cambiar contraseña */}
        <div className="profile-card">
          <h3 className="profile-section-title">🔑 Cambiar contraseña</h3>

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
                {showPass ? '🙈' : '👁️'}
              </button>
            </div>

            <label>Nueva contraseña</label>
            <div className="input-password-wrap">
              <input
                className="form-input"
                type={showPass ? 'text' : 'password'}
                placeholder="Mínimo 8 caracteres"
                value={newPass}
                onChange={e => setNewPass(e.target.value)}
                autoComplete="new-password"
              />
            </div>

            {newPass && (
              <div className="pass-strength">
                <div className="pass-strength-bar">
                  {[1,2,3,4].map(i => (
                    <div key={i} className={`pass-strength-seg ${strength(newPass) >= i ? `strength-${strength(newPass)}` : ''}`} />
                  ))}
                </div>
                <span className="pass-strength-label">{strengthLabel[strength(newPass)]}</span>
              </div>
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
              {confirm && (
                <span className="pass-match">{confirm === newPass ? '✅' : '❌'}</span>
              )}
            </div>

            {msg && (
              <div className={`form-msg ${msg.startsWith('✅') ? 'form-msg--ok' : 'form-msg--error'}`}>
                {msg}
              </div>
            )}

            <button
              className="btn-primary"
              onClick={handleChangePass}
              disabled={loading || !current || !newPass || !confirm}
            >
              {loading ? '⏳ Guardando...' : '🔑 Actualizar contraseña'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
