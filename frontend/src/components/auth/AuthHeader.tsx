import { UserPlusIcon } from './AuthIcons'

interface Props {
  mode: 'login' | 'register'
  switchMode: (m: 'login' | 'register') => void
}

/** Header compartido de las pantallas de Login y Registro. */
export default function AuthHeader({ mode, switchMode }: Props) {
  return (
    <header className="auth-header">
      <div className="auth-header-logo">
        <div className="auth-header-logo-icon">
          <UserPlusIcon />
        </div>
        <span>Impulsa</span>
      </div>
      <nav className="auth-header-nav">
        <a href="#" className="auth-header-link">Acerca de Impulsa</a>
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