function LogoIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="8" r="4" /><path d="M2 21c0-4 3.5-7 7-7s7 3 7 7" />
      <line x1="19" y1="8" x2="19" y2="14" /><line x1="16" y1="11" x2="22" y2="11" />
    </svg>
  )
}

function CheckCircleIcon() {
  return (
    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#26874A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

interface Props {
  onComplete: () => void
}

export default function PasoExito({ onComplete }: Props) {
  return (
    <div className="auth-page">
      <header className="auth-header">
        <div className="auth-header-logo">
          <div className="auth-header-logo-icon">
            <LogoIcon />
          </div>
          <span>{import.meta.env.VITE_APP_NAME || 'Impulsa'}</span>
        </div>
      </header>
      <div className="auth-card-wrapper">
        <div className="auth-card onboarding-card onboarding-success">
          <CheckCircleIcon />
          <h2 className="auth-title">¡Completado!</h2>
          <h3 className="onboarding-success-sub">¡Todo listo para comenzar un nuevo viaje de conocimientos!</h3>
          <p className="auth-subtitle">¡Registro exitoso! Hemos personalizado el perfil con tus preferencias, inicia sesión ahora y comienza una aventura llena de conocimientos y retos nuevos.</p>
          <button className="btn-primary btn-full auth-submit-btn" onClick={onComplete}>
            Iniciar Sesión
          </button>
        </div>
      </div>
    </div>
  )
}