import { ReactNode } from 'react'

function LogoIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="8" r="4" /><path d="M2 21c0-4 3.5-7 7-7s7 3 7 7" />
      <line x1="19" y1="8" x2="19" y2="14" /><line x1="16" y1="11" x2="22" y2="11" />
    </svg>
  )
}

interface Props {
  paso: number
  total: number
  titulo: string
  subtitulo?: string
  children: ReactNode
  onNext: () => void
  onBack?: () => void
  onSkip?: () => void
  nextLabel?: string
  nextDisabled?: boolean
  loading?: boolean
  hideHint?: boolean
}

/** Layout compartido de todos los pasos del onboarding (header, barra de progreso, card, acciones). */
export default function OnboardingLayout({
  paso, total, titulo, subtitulo, children, onNext, onBack, onSkip,
  nextLabel = 'Siguiente →', nextDisabled = false, loading = false, hideHint = false,
}: Props) {
  return (
    <div className="auth-page">
      <header className="auth-header">
        <div className="auth-header-logo">
          <div className="auth-header-logo-icon">
            <LogoIcon />
          </div>
          <span>Impulsa</span>
        </div>
        <span className="onboarding-paso-label">Paso {paso}/{total}</span>
      </header>

      <div className="onboarding-progress-bar">
        <div className="onboarding-progress-fill" style={{ width: `${(paso / total) * 100}%` }} />
      </div>

      <div className="auth-card-wrapper">
        <div className="auth-card onboarding-card">
          <h2 className="auth-title">{titulo}</h2>
          {subtitulo && <p className="auth-subtitle">{subtitulo}</p>}

          <div className="onboarding-content">{children}</div>

          {!hideHint && <p className="onboarding-multi-hint">Puedes elegir más de una opción.</p>}

          <div className="onboarding-actions">
            {onBack && (
              <button className="onboarding-btn-back" onClick={onBack}>
                ← Atrás
              </button>
            )}
            <button
              className="btn-primary onboarding-btn-next"
              onClick={onNext}
              disabled={nextDisabled || loading}
            >
              {loading ? 'Guardando...' : nextLabel}
            </button>
            {onSkip && (
              <button className="onboarding-btn-skip" onClick={onSkip}>
                Omitir
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}