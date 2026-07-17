import { useState, useEffect } from 'react'
import { withEnglishFallback, readField } from '../../utils/studentProfileFields'

interface Props {
  user: any
}

const BASE = '/api'
const headers = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

/**
 * Tarjeta "Información personal" (columna principal de Perfil).
 * Incluye edición de datos básicos, avatar, y hace su propio fetch
 * del perfil de estudiante (para la fecha de nacimiento).
 */
export default function InfoPersonalCard({ user }: Props) {
  const [editMode, setEditMode] = useState(false)
  const [editEmail, setEditEmail] = useState(user?.email || '')
  const [editPhone, setEditPhone] = useState(user?.phone || '')
  const [editFechaNac, setEditFechaNac] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [profileMsg, setProfileMsg] = useState('')

  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '')
  const [avatarEdit, setAvatarEdit] = useState(false)
  const [avatarMsg, setAvatarMsg] = useState('')

  const displayName = user?.first_name || user?.username || '...'

  useEffect(() => {
    fetch(`${BASE}/auth/profile/student/update/`, { headers: headers() })
      .then(r => r.json())
      .then(data => setEditFechaNac(readField(data, 'fecha_nacimiento') || ''))
      .catch(() => { })
  }, [])

  const handleSaveProfile = async () => {
    setProfileMsg('')
    setSavingProfile(true)
    try {
      await fetch(`${BASE}/auth/me/`, {
        method: 'PATCH',
        headers: headers(),
        body: JSON.stringify({ email: editEmail, phone: editPhone }),
      })
      await fetch(`${BASE}/auth/profile/student/update/`, {
        method: 'PATCH',
        headers: headers(),
        body: JSON.stringify(withEnglishFallback({ fecha_nacimiento: editFechaNac })),
      })
      setProfileMsg('✅ Perfil actualizado.')
      setEditMode(false)
    } catch {
      setProfileMsg('❌ No se pudo guardar. Intentá de nuevo.')
    }
    setSavingProfile(false)
  }

  return (
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
                    headers: headers(),
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
  )
}