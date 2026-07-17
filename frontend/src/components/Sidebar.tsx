import MentorBot from './MentorBot'

interface Props {
  active: string
  onNav: (page: string) => void
  user: { username: string; first_name?: string; is_staff?: boolean } | null
  streak: number
  onLogout: () => void
  onAdmin?: () => void
}

const NAV = [
  { id: 'chat',      icon: '🤖', label: 'Chatea con Pulso' },
  { id: 'inicio',    icon: '⌂', label: 'Inicio' },
  { id: 'lecciones', icon: '📖', label: 'Lecciones' },
  { id: 'desafios',  icon: '🏆', label: 'Desafíos' },
  { id: 'logros',    icon: '⭐', label: 'Logros' },
  { id: 'perfil',    icon: '👤', label: 'Perfil' },
]
export default function Sidebar({ active, onNav, user, streak, onLogout, onAdmin }: Props) {
  const appName = import.meta.env.VITE_APP_NAME || 'Impulsa'
  const displayName = user?.first_name || user?.username || 'Usuario'

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">
          <MentorBot mood="feliz" size={32} />
        </div>
        <span className="logo-text">{appName}</span>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        {NAV.map(item => (
          <button
            key={item.id}
            className={`nav-item ${active === item.id ? 'nav-item--active' : ''}`}
            onClick={() => onNav(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Usuario + streak abajo */}
      <div className="sidebar-bottom">
        <div className="user-card">
          <div className="user-avatar">
            {displayName.charAt(0).toUpperCase()}
          </div>
          <div className="user-info">
            <span className="user-name">{displayName}</span>
            <button className="logout-btn" onClick={onLogout}>Salir</button>
          </div>
        </div>

        {user?.is_staff && onAdmin && (
          <button className="admin-sidebar-btn" onClick={onAdmin}>
            ⚙️ Panel admin
          </button>
        )}

        {streak > 0 && (
          <div className="streak-card">
            <div className="streak-title">🔥 ¡Seguí aprendiendo!</div>
            <div className="streak-sub">Estás en racha</div>
            <div className="streak-count">{streak} días consecutivos</div>
            <div className="streak-bar">
              <div className="streak-fill" style={{ width: `${Math.min(streak * 10, 100)}%` }} />
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
