import { UserPlusIcon } from './AuthIcons'

interface Props {
  mode: 'login' | 'register'
  switchMode: (m: 'login' | 'register') => void
  onAbout: () => void
}

/** Header compartido de las pantallas de Login y Registro. */
export default function AuthHeader({ mode, switchMode, onAbout }: Props) {
  const appName = import.meta.env.VITE_APP_NAME || 'Impulsa'

  return (
    <header className="auth-header">
      <div className="auth-header-logo">
        <div className="auth-header-logo-icon">
          <UserPlusIcon />
        </div>
        <span>{appName}</span>
      </div>
      <nav className="auth-header-nav">
        <button type="button" className="auth-header-link" onClick={onAbout}>Acerca de</button>
        <button
          className={`auth-header-btn ${mode === 'login' ? 'auth-header-btn--active' : ''}`}
          onClick={() => switchMode('login')}
        >
          Iniciar Sesión
        </button>
        <button
          className={`auth-header-btn ${mode === 'register' ? 'auth-header-btn--secondary-active' : 'auth-header-btn--secondary'}`}
          onClick={() => switchMode('register')}
        >
          Registrarse
        </button>
      </nav>
    </header>
  )
}