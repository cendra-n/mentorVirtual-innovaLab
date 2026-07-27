import { useState, useEffect } from 'react'
import { apiGeoCountries, apiGeoProvinces, apiUpdateProfile } from '../../services/api'
import GeoLocalityAutocomplete from '../GeoLocalityAutocomplete'

interface Props {
  user: any
  onUserUpdated?: () => void
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
export default function InfoPersonalCard({ user, onUserUpdated }: Props) {
  const [editMode, setEditMode] = useState(false)
  const [editEmail, setEditEmail] = useState(user?.email || '')
  const [editPhone, setEditPhone] = useState(user?.phone || '')
  const [editFechaNac, setEditFechaNac] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [profileMsg, setProfileMsg] = useState('')

  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '')
  const [avatarEdit, setAvatarEdit] = useState(false)
  const [avatarMsg, setAvatarMsg] = useState('')

  // País/provincia/localidad de residencia (Poly) — opcionales, mismo criterio que en Registro.
  const [countries, setCountries] = useState<{ country_id: number; country_name: string }[]>([])
  const [provinces, setProvinces] = useState<{ province_id: number; province_name: string }[]>([])
  const [editCountry, setEditCountry] = useState<number | ''>('')
  const [editProvince, setEditProvince] = useState<number | ''>('')
  const [editLocality, setEditLocality] = useState<number | ''>('')
  const [editLocalityName, setEditLocalityName] = useState('')
  const [geoLoading, setGeoLoading] = useState(false)

  const displayName = user?.first_name || user?.username || '...'

  useEffect(() => {
    setEditFechaNac(user?.birth_date || '')
    setEditCountry(user?.country_residence?.country_id || '')
    setEditProvince(user?.province_residence?.province_id || '')
    setEditLocality(user?.locality_residence?.locality_id || '')
    setEditLocalityName(user?.locality_residence?.locality_name || '')
  }, [user])

  useEffect(() => {
    apiGeoCountries().then(res => {
      if (res.ok && Array.isArray(res.data)) setCountries(res.data)
    }).catch(() => { })
  }, [])

  useEffect(() => {
    if (!editCountry) { setProvinces([]); return }
    setGeoLoading(true)
    apiGeoProvinces(editCountry).then(res => {
      if (res.ok && Array.isArray(res.data)) setProvinces(res.data)
    }).catch(() => { }).finally(() => setGeoLoading(false))
  }, [editCountry])

  const handleSaveProfile = async () => {
    setProfileMsg('')
    setSavingProfile(true)
    try {
      await apiUpdateProfile({
        email: editEmail,
        phone: editPhone,
        ...(editCountry  ? { country: editCountry }   : { country: null }),
        ...(editProvince ? { province: editProvince } : { province: null }),
        ...(editLocality ? { locality: editLocality } : { locality: null }),
      })
      await fetch(`${BASE}/auth/profile/student/update/`, {
        method: 'PATCH',
        headers: headers(),
        body: JSON.stringify({ birth_date: editFechaNac }),
      })
      setProfileMsg('✅ Perfil actualizado.')
      setEditMode(false)
      onUserUpdated?.()
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
                    onUserUpdated?.()
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
        <div className="profile-field">
          <label>País</label>
          <select
            className="form-input"
            value={editCountry}
            onChange={e => { setEditCountry(e.target.value ? Number(e.target.value) : ''); setEditProvince(''); setEditLocality(''); setEditLocalityName('') }}
            disabled={!editMode}
          >
            <option value="">Sin especificar</option>
            {countries.map(c => (
              <option key={c.country_id} value={c.country_id}>{c.country_name}</option>
            ))}
          </select>
        </div>
        <div className="profile-field">
          <label>Provincia</label>
          <select
            className="form-input"
            value={editProvince}
            onChange={e => { setEditProvince(e.target.value ? Number(e.target.value) : ''); setEditLocality(''); setEditLocalityName('') }}
            disabled={!editMode || !editCountry || geoLoading}
          >
            <option value="">{geoLoading ? 'Cargando...' : 'Sin especificar'}</option>
            {provinces.map(p => (
              <option key={p.province_id} value={p.province_id}>{p.province_name}</option>
            ))}
          </select>
        </div>
        <div className="profile-field">
          <label>Localidad</label>
          <GeoLocalityAutocomplete
            provinceId={editProvince}
            value={editLocality}
            valueName={editLocalityName}
            onChange={(id, name) => { setEditLocality(id); setEditLocalityName(name) }}
            disabled={!editMode || !editProvince}
            className="form-input"
            placeholder={!editMode ? '—' : (!editProvince ? 'Elegí una provincia primero' : 'Escribí para buscar...')}
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