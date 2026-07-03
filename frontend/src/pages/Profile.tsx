import { useState, useEffect } from 'react'

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

interface Props {
  user: any
}

const BASE = '/api'
const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

type Notificaciones = { correo: boolean; push: boolean }
type Preferencias = { idioma: string; modoOscuro: boolean }

function loadNotificaciones(): Notificaciones {
  try {
    const raw = localStorage.getItem('notificaciones_prefs')
    if (raw) return JSON.parse(raw)
  } catch { }
  return { correo: true, push: false }
}

function loadPreferencias(): Preferencias {
  try {
    const raw = localStorage.getItem('ui_preferencias')
    if (raw) return JSON.parse(raw)
  } catch { }
  return { idioma: 'es', modoOscuro: false }
}

export default function Profile({ user }: Props) {
  // ── Contraseña ──
  const [current, setCurrent] = useState('')
  const [newPass, setNewPass] = useState('')
  const [confirm, setConfirm] = useState('')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  // ── Perfil / edición ──
  const [profile, setProfile] = useState<any>(null)
  const [editMode, setEditMode] = useState(false)
  const [editEmail, setEditEmail] = useState(user?.email || '')
  const [editPhone, setEditPhone] = useState(user?.phone || '')
  const [editFechaNac, setEditFechaNac] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [profileMsg, setProfileMsg] = useState('')

  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '')
  const [avatarEdit, setAvatarEdit] = useState(false)
  const [avatarMsg, setAvatarMsg] = useState('')

  // ── Notificaciones / preferencias (localStorage, sin backend todavía) ──
  const [notificaciones, setNotificaciones] = useState<Notificaciones>(loadNotificaciones())
  const [preferencias, setPreferencias] = useState<Preferencias>(loadPreferencias())

  // ── Logros ──
  const [logros, setLogros] = useState<any[]>([])
  const [logrosLoading, setLogrosLoading] = useState(true)

  // ── Metas (para progreso general / resumen de actividad) ──
  const [goals, setGoals] = useState<any[]>([])

  const displayName = user?.first_name || user?.username || '...'

  useEffect(() => {
    fetch(`${BASE}/auth/profile/student/update/`, { headers: h() })
      .then(r => r.json())
      .then(data => {
        setProfile(data)
        setEditFechaNac(data?.fecha_nacimiento || '')
      })
      .catch(() => { })

    fetch(`${BASE}/progress/logros/`, { headers: h() })
      .then(r => r.json())
      // TODO: confirmar shape exacto de la respuesta con backend (nombre del array, campos de cada logro)
      .then(data => setLogros(Array.isArray(data) ? data : data?.logros || data?.results || []))
      .catch(() => { })
      .finally(() => setLogrosLoading(false))

    fetch(`${BASE}/goals/`, { headers: h() })
      .then(r => r.json())
      // TODO: confirmar shape exacto (campo de progreso, campo de completado) con backend
      .then(data => setGoals(Array.isArray(data) ? data : data?.goals || data?.results || []))
      .catch(() => { })
  }, [])

  useEffect(() => {
    localStorage.setItem('notificaciones_prefs', JSON.stringify(notificaciones))
  }, [notificaciones])

  useEffect(() => {
    localStorage.setItem('ui_preferencias', JSON.stringify(preferencias))
  }, [preferencias])

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

  const handleSaveProfile = async () => {
    setProfileMsg('')
    setSavingProfile(true)
    try {
      await fetch(`${BASE}/auth/me/`, {
        method: 'PATCH',
        headers: h(),
        body: JSON.stringify({ email: editEmail, phone: editPhone }),
      })
      await fetch(`${BASE}/auth/profile/student/update/`, {
        method: 'PATCH',
        headers: h(),
        body: JSON.stringify({ fecha_nacimiento: editFechaNac }),
      })
      setProfileMsg('✅ Perfil actualizado.')
      setEditMode(false)
    } catch {
      setProfileMsg('❌ No se pudo guardar. Intentá de nuevo.')
    }
    setSavingProfile(false)
  }

  function getPasswordChecks(pass: string) {
    return {
      number: /[0-9]/.test(pass),
      upper: /[A-Z]/.test(pass),
      lower: /[a-z]/.test(pass),
      special: /[^A-Za-z0-9]/.test(pass),
      length: pass.length >= 8,
    }
  }
  const checks = getPasswordChecks(newPass)

  // ── Cálculos derivados (con datos que sí existen) ──
  // TODO: reemplazar por endpoint real de "progreso general" cuando exista en backend
  const goalsCompletados = goals.filter(g => g?.completado || g?.progreso >= 100).length
  const progresoGeneral = goals.length > 0
    ? Math.round(goals.reduce((acc, g) => acc + (g?.progreso ?? 0), 0) / goals.length)
    : 0
  const moduloActual = goals.find(g => !(g?.completado || g?.progreso >= 100))

  return (
    <div className="profile-page profile-page--nuevo">
      <div className="profile-header">
        <h1 className="detail-title">Mi Perfil</h1>
      </div>

      <div className="profile-layout">
        {/* ══ Columna principal ══ */}
        <div className="profile-main-col">

          {/* ── Información personal ── */}
          <div className="profile-card">
            <div className="profile-card-header">
              <h3 className="profile-section-title">Información personal</h3>
              {!editMode ? (
                <button className="btn-outline-sm" onClick={() => setEditMode(true)}>
                  ✏️ Editar perfil
                </button>
              ) : (
                <button className="btn-primary-sm" onClick={handleSaveProfile} disabled={savingProfile}>
                  {savingProfile ? 'Guardando...' : 'Guardar cambios'}
                </button>
              )}
            </div>

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
                  <div className="profile-avatar">{displayName.charAt(0).toUpperCase()}</div>
                )}
                <button className="profile-avatar-edit-btn" title="Cambiar foto" onClick={() => setAvatarEdit(!avatarEdit)}>
                  ✏️
                </button>
              </div>
              <div>
                <h2 className="profile-name">{displayName}</h2>
                <p className="profile-username">{user?.email}</p>
                <span className="profile-badge">
                  {user?.role === 'ADMIN' ? '⚙️ Administrador'
                    : user?.role === 'PROFESSOR' ? '👨‍🏫 Profesor'
                      : '🎓 Estudiante'}
                </span>
              </div>
            </div>

            {avatarEdit && (
              <div className="profile-avatar-edit">
                <label className="profile-avatar-edit-label">URL de tu foto de perfil</label>
                <div className="profile-avatar-edit-row">
                  <input
                    className="form-input"
                    type="url"
                    autoComplete="off"
                    placeholder="https://ejemplo.com/mi-foto.jpg"
                    value={avatarUrl}
                    onChange={e => setAvatarUrl(e.target.value)}
                  />
                  <button
                    className="btn-primary"
                    onClick={async () => {
                      try {
                        const res = await fetch(`${BASE}/auth/me/`, {
                          method: 'PATCH',
                          headers: h(),
                          body: JSON.stringify({ avatar_url: avatarUrl }),
                        }).then(r => r.json())
                        if (res.user || res.avatar_url) {
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
                {avatarMsg && <span className="profile-avatar-edit-msg">{avatarMsg}</span>}
              </div>
            )}

            <div className="profile-fields-grid">
              <div className="profile-field">
                <label>Nombre de Usuario</label>
                <input className="form-input" value={user?.username || ''} disabled />
              </div>
              <div className="profile-field">
                <label>Fecha de Nacimiento</label>
                <input
                  className="form-input"
                  type="date"
                  value={editFechaNac}
                  onChange={e => setEditFechaNac(e.target.value)}
                  disabled={!editMode}
                />
              </div>
              <div className="profile-field">
                <label>Email</label>
                <input
                  className="form-input"
                  type="email"
                  value={editEmail}
                  onChange={e => setEditEmail(e.target.value)}
                  disabled={!editMode}
                />
              </div>
              <div className="profile-field">
                <label>Teléfono</label>
                <input
                  className="form-input"
                  value={editPhone}
                  onChange={e => setEditPhone(e.target.value)}
                  disabled={!editMode}
                  placeholder="—"
                />
              </div>
            </div>
            {profileMsg && (
              <div className={`form-msg ${profileMsg.startsWith('✅') ? 'form-msg--ok' : 'form-msg--error'}`}>
                {profileMsg}
              </div>
            )}
          </div>

          {/* ── Notificaciones ── */}
          <div className="profile-card">
            <h3 className="profile-section-title">Notificaciones</h3>
            <div className="toggle-row">
              <div className="toggle-row-icon toggle-row-icon--blue">📧</div>
              <div className="toggle-row-text">
                <strong>Notificaciones por correo</strong>
                <p>Recibe actualizaciones, recordatorios y novedades en tu correo electrónico.</p>
              </div>
              <button
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
              <button
                className={`switch ${notificaciones.push ? 'switch--on' : ''}`}
                onClick={() => setNotificaciones(p => ({ ...p, push: !p.push }))}
                aria-pressed={notificaciones.push}
              >
                <span className="switch-knob" />
              </button>
            </div>
          </div>

          {/* ── Seguridad ── */}
          <div className="profile-card">
            <h3 className="profile-section-title">Seguridad</h3>
            <div className="security-row">
              <div className="toggle-row-icon toggle-row-icon--orange">🔒</div>
              <div className="toggle-row-text">
                <strong>Cambiar contraseña</strong>
                <p>Actualiza tu contraseña de acceso.</p>
              </div>
            </div>

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

              <button
                className="btn-primary"
                onClick={handleChangePass}
                disabled={loading || !current || !newPass || !confirm}
              >
                {loading ? '⏳ Guardando...' : '🔑 Actualizar contraseña'}
              </button>
            </div>
          </div>

          {/* ── Mis logros ── */}
          <div className="profile-card">
            <div className="profile-card-header">
              <h3 className="profile-section-title">Mis logros</h3>
              <button className="link-btn">Ver todo →</button>
            </div>
            {logrosLoading && <p className="profile-empty-note">Cargando logros...</p>}
            {!logrosLoading && logros.length === 0 && (
              <p className="profile-empty-note">Todavía no desbloqueaste logros. ¡Seguí aprendiendo!</p>
            )}
            {!logrosLoading && logros.length > 0 && (
              <div className="logros-grid">
                {logros.slice(0, 4).map((l, i) => (
                  <div key={l?.id ?? i} className="logro-box">
                    <div className="logro-icon">{l?.icono || '🏆'}</div>
                    {/* TODO: confirmar campos exactos (nombre/titulo, fecha) con backend */}
                    <strong className="logro-nombre">{l?.nombre || l?.titulo || 'Logro'}</strong>
                    <span className="logro-fecha">{l?.fecha || l?.fecha_obtenido || ''}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Preferencias ── */}
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
              <div className="toggle-row-icon toggle-row-icon--dark">🌙</div>
              <div className="toggle-row-text">
                <strong>Modo oscuro</strong>
                <p>Activa el tema oscuro para mayor comodidad visual.</p>
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
        </div>

        {/* ══ Columna lateral ══ */}
        <div className="profile-side-col">
          <div className="profile-card profile-progress-card">
            <h3 className="profile-section-title">Tu progreso general</h3>
            <div className="progress-ring-wrap">
              <div className="progress-ring" style={{ background: `conic-gradient(var(--azul) ${progresoGeneral * 3.6}deg, var(--gris-borde) 0deg)` }}>
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

          <div className="profile-card profile-help-card">
            <h3 className="profile-section-title">💬 ¿Necesitás ayuda?</h3>
            <p>Accedé a la documentación, tutoriales y soporte personalizado.</p>
            <button className="btn-primary btn-full">Centro de apoyo ↗</button>
          </div>

          <div className="profile-card">
            <h3 className="profile-section-title">Resumen de actividad</h3>
            <div className="activity-row">
              <span>Metas completadas</span>
              <strong>{goalsCompletados}</strong>
            </div>
            <div className="activity-row">
              <span>Videos vistos</span>
              <strong>{profile?.cantidad_videos_vistos ?? 0}</strong>
            </div>
            <div className="activity-row">
              <span>Logros obtenidos</span>
              <strong>{logros.length}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}