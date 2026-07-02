import { useState, useEffect } from 'react'
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
  const [current, setCurrent] = useState('')
  const [newPass, setNewPass] = useState('')
  const [confirm, setConfirm] = useState('')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [profile, setProfile] = useState<any>(null)
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '')
  const [avatarEdit, setAvatarEdit] = useState(false)
  const [avatarMsg, setAvatarMsg] = useState('')


  const displayName = user?.first_name || user?.username || '...'
  useEffect(() => {
    fetch(`${BASE}/auth/profile/student/update/`, { headers: h() })
      .then(r => r.json())
      .then(setProfile)
      .catch(() => { })
  }, [])

  const handleChangePass = async () => {
    setMsg('')
    if (!current) { setMsg('❌ Ingresá tu contraseña actual.'); return }
    if (newPass.length < 8) { setMsg('❌ La nueva contraseña debe tener al menos 8 caracteres.'); return }
    if (newPass !== confirm) { setMsg('❌ Las contraseñas no coinciden.'); return }

    setLoading(true)
    try {
      const res = await fetch(`${BASE}/auth/change_password/`, {
        method: 'POST',
        headers: h(),
        body: JSON.stringify({
          current_password: current,
          new_password: newPass,
          confirm_password: confirm,
        }),
      }).then(r => r.json())

      if (res.message) {
        setMsg('✅ ' + res.message)
        setCurrent(''); setNewPass(''); setConfirm('')
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

{/* ── Tarjeta principal ── */}
        <div className="profile-card">
          <div className="profile-avatar-row">
            <div className="profile-avatar-wrap">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt={displayName}
                  className="profile-avatar-img"
                  onError={e => { (e.target as HTMLImageElement).src = ''; setAvatarUrl('') }}
                />
              ) : (
                <div className="profile-avatar">
                  {displayName.charAt(0).toUpperCase()}
                </div>
              )}
              <button className="profile-avatar-edit-btn" title="Cambiar foto" onClick={() => setAvatarEdit(!avatarEdit)}>
                ✏️
              </button>
            </div>
            <div>
              <h2 className="profile-name">{displayName}</h2>
              <p className="profile-username">@{user?.username}</p>
              {user?.role === 'ADMIN' && <span className="profile-badge">⚙️ Administrador</span>}
              {user?.role === 'PROFESSOR' && <span className="profile-badge">👨‍🏫 Profesor</span>}
            </div>
            <MentorBot mood="guiñando" size={56} className="profile-bot" />
          </div>

          {avatarEdit && (
            <div className="profile-avatar-edit">
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--marino)', marginBottom: 4, display: 'block' }}>
                URL de tu foto de perfil
              </label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  className="form-input"
                  type="url"
                  autoComplete="off"
                  placeholder="https://ejemplo.com/mi-foto.jpg"
                  value={avatarUrl}
                  onChange={e => setAvatarUrl(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button
                  className="btn-primary"
                  onClick={async () => {
                    try {
                      const res = await fetch(`${BASE}/auth/me/`, {
                        method: 'PUT',
                        headers: h(),
                        body: JSON.stringify({
                          email: user?.email,
                          phone: user?.phone || '',
                          avatar_url: avatarUrl,
                        }),
                      }).then(r => r.json())
                      if (res.user) {
                        setAvatarMsg('✅ Foto actualizada.')
                        setAvatarEdit(false)
                      } else {
                        setAvatarMsg('❌ No se pudo guardar.')
                      }
                    } catch {
                      setAvatarMsg('❌ No se pudo conectar.')
                    }
                  }}
                >
                  Guardar
                </button>
              </div>
              {avatarMsg && <span style={{ fontSize: 12, color: 'var(--gris-medio)' }}>{avatarMsg}</span>}
            </div>
          )}

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
              <span className="profile-info-label">Teléfono</span>
              <span className="profile-info-value">{user?.phone || '—'}</span>
            </div>
          </div>
        </div>

        {/* ── Estadísticas ── */}
        {profile && (
          <div className="profile-card">
            <h3 className="profile-section-title">📊 Mis estadísticas</h3>
            <div className="profile-stats-grid">
              <div className="profile-stat-box">
                <span className="profile-stat-value">{profile.racha_actual_dias ?? 0}</span>
                <span className="profile-stat-label">🔥 Racha actual</span>
              </div>
              <div className="profile-stat-box">
                <span className="profile-stat-value">{profile.racha_maxima_dias ?? 0}</span>
                <span className="profile-stat-label">🏆 Racha máxima</span>
              </div>
              <div className="profile-stat-box">
                <span className="profile-stat-value">{profile.cantidad_videos_vistos ?? 0}</span>
                <span className="profile-stat-label">🎬 Videos vistos</span>
              </div>
              <div className="profile-stat-box">
                <span className="profile-stat-value">{profile.desafios_completados ?? 0}</span>
                <span className="profile-stat-label">⚡ Desafíos</span>
              </div>
            </div>
          </div>
        )}

        {/* ── Preferencias ── */}
        {profile && (
          <div className="profile-card">
            <h3 className="profile-section-title">🎯 Mis preferencias</h3>
            <div className="profile-info-grid">
              {profile.intereses?.length > 0 && (
                <div className="profile-info-item">
                  <span className="profile-info-label">Intereses</span>
                  <span className="profile-info-value">{profile.intereses.join(', ')}</span>
                </div>
              )}
              {profile.nivel_educativo && (
                <div className="profile-info-item">
                  <span className="profile-info-label">Nivel educativo</span>
                  <span className="profile-info-value">{profile.nivel_educativo.replace(/_/g, ' ')}</span>
                </div>
              )}
              {profile.disponibilidad_tiempo && (
                <div className="profile-info-item">
                  <span className="profile-info-label">Disponibilidad</span>
                  <span className="profile-info-value">{profile.disponibilidad_tiempo}</span>
                </div>
              )}
              {profile.objetivo_principal && (
                <div className="profile-info-item">
                  <span className="profile-info-label">Objetivo</span>
                  <span className="profile-info-value">{profile.objetivo_principal.replace(/_/g, ' ')}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Cambiar contraseña ── */}
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
                  {[1, 2, 3, 4].map(i => (
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