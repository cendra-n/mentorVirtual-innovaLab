import { useState, useEffect } from 'react'
import MentorBot from '../components/MentorBot'

interface Props {
  onBack: () => void
}

const BASE = '/api'
const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

// ── API calls ────────────────────────────────────────────────────────────────
const apiUsers     = () => fetch(`${BASE}/admin/users/`,          { headers: h() }).then(r => r.json())
const apiUserDetail= (id: number) => fetch(`${BASE}/admin/users/${id}/`, { headers: h() }).then(r => r.json())
const apiSetPass   = (id: number, password: string) =>
  fetch(`${BASE}/admin/users/${id}/set_password/`, {
    method: 'POST', headers: h(), body: JSON.stringify({ password })
  }).then(r => r.json())
const apiToggleActive = (id: number, is_active: boolean) =>
  fetch(`${BASE}/admin/users/${id}/`, {
    method: 'PATCH', headers: h(), body: JSON.stringify({ is_active })
  }).then(r => r.json())
const apiStats     = () => fetch(`${BASE}/admin/stats/`,          { headers: h() }).then(r => r.json())

export default function AdminPanel({ onBack }: Props) {
  const [tab, setTab]         = useState<'usuarios' | 'stats'>('usuarios')
  const [users, setUsers]     = useState<any[]>([])
  const [stats, setStats]     = useState<any>(null)
  const [selected, setSelected] = useState<any>(null)
  const [newPass, setNewPass] = useState('')
  const [confirm, setConfirm] = useState('')
  const [msg, setMsg]         = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (tab === 'usuarios') apiUsers().then(d => setUsers(d.users || []))
    if (tab === 'stats')    apiStats().then(setStats)
  }, [tab])

  const handleSetPass = async () => {
    if (newPass !== confirm) { setMsg('❌ Las contraseñas no coinciden.'); return }
    if (newPass.length < 8)  { setMsg('❌ Mínimo 8 caracteres.'); return }
    setLoading(true)
    const res = await apiSetPass(selected.id, newPass)
    setMsg(res.message || res.error || '✅ Contraseña actualizada.')
    setNewPass('')
    setConfirm('')
    setLoading(false)
  }

  const handleToggle = async (user: any) => {
    await apiToggleActive(user.id, !user.is_active)
    apiUsers().then(d => setUsers(d.users || []))
  }

  return (
    <div className="admin-panel">
      {/* Header */}
      <div className="admin-header">
        <button className="back-btn" onClick={onBack}>← Volver al dashboard</button>
        <div className="admin-title-row">
          <MentorBot mood="pensativo" size={40} />
          <div>
            <h1 className="admin-title">Panel de administración</h1>
            <p className="admin-sub">Gestión de usuarios y estadísticas</p>
          </div>
        </div>
        <div className="admin-tabs">
          <button className={`admin-tab ${tab === 'usuarios' ? 'admin-tab--active' : ''}`} onClick={() => setTab('usuarios')}>👥 Usuarios</button>
          <button className={`admin-tab ${tab === 'stats'    ? 'admin-tab--active' : ''}`} onClick={() => setTab('stats')}>📊 Estadísticas</button>
        </div>
      </div>

      <div className="admin-body">
        {/* ── Tab Usuarios ── */}
        {tab === 'usuarios' && (
          <div className="admin-users">
            <div className="users-list">
              <h2 className="admin-section-title">Usuarios ({users.length})</h2>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th><th>Usuario</th><th>Email</th><th>Staff</th><th>Activo</th><th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} className={selected?.id === u.id ? 'row-selected' : ''}>
                      <td>{u.id}</td>
                      <td><strong>{u.username}</strong></td>
                      <td>{u.email || '—'}</td>
                      <td>{u.is_staff ? '✅' : '—'}</td>
                      <td>
                        <button
                          className={`badge-btn ${u.is_active ? 'badge-btn--green' : 'badge-btn--red'}`}
                          onClick={() => handleToggle(u)}
                        >
                          {u.is_active ? 'Activo' : 'Inactivo'}
                        </button>
                      </td>
                      <td>
                        <button className="action-btn" onClick={() => { setSelected(u); setMsg('') }}>
                          ✏️ Gestionar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Panel de usuario seleccionado */}
            {selected && (
              <div className="user-detail-panel">
                <div className="user-detail-header">
                  <div className="user-detail-avatar">{selected.username.charAt(0).toUpperCase()}</div>
                  <div>
                    <h3>{selected.username}</h3>
                    <p>{selected.email || 'Sin email'}</p>
                  </div>
                  <button className="close-btn" onClick={() => setSelected(null)}>✕</button>
                </div>

                <div className="user-detail-info">
                  <div className="info-row"><span>ID</span><strong>{selected.id}</strong></div>
                  <div className="info-row"><span>Staff</span><strong>{selected.is_staff ? 'Sí' : 'No'}</strong></div>
                  <div className="info-row"><span>Activo</span><strong>{selected.is_active ? 'Sí' : 'No'}</strong></div>
                  <div className="info-row"><span>Registro</span><strong>{new Date(selected.date_joined).toLocaleDateString('es-AR')}</strong></div>
                </div>

                <div className="change-pass-section">
                  <h4>Cambiar contraseña</h4>
                  <label>Nueva contraseña</label>
                  <input
                    className="form-input"
                    type="password"
                    placeholder="Mínimo 8 caracteres"
                    value={newPass}
                    onChange={e => setNewPass(e.target.value)}
                  />
                  <label>Confirmá la contraseña</label>
                  <input
                    className="form-input"
                    type="password"
                    placeholder="Repetí la contraseña"
                    value={confirm}
                    onChange={e => setConfirm(e.target.value)}
                  />
                  {msg && <div className={`form-msg ${msg.startsWith('❌') ? 'form-msg--error' : 'form-msg--ok'}`}>{msg}</div>}
                  <button
                    className="btn-primary"
                    onClick={handleSetPass}
                    disabled={loading || !newPass || !confirm}
                  >
                    {loading ? 'Guardando...' : '🔑 Actualizar contraseña'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Tab Stats ── */}
        {tab === 'stats' && stats && (
          <div className="admin-stats">
            <div className="stats-grid">
              {[
                { label: 'Usuarios totales',  value: stats.total_users,  icon: '👥' },
                { label: 'Metas creadas',     value: stats.total_goals,  icon: '🎯' },
                { label: 'Pasos completados', value: stats.total_steps_completed, icon: '✅' },
                { label: 'Videos vistos',     value: stats.total_video_views,     icon: '🎬' },
              ].map((s, i) => (
                <div key={i} className="stat-box">
                  <span className="stat-box-icon">{s.icon}</span>
                  <span className="stat-box-value">{s.value ?? '—'}</span>
                  <span className="stat-box-label">{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
