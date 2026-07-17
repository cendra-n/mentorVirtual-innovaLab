import OnboardingLayout from './OnboardingLayout'
import { HORARIOS } from '../../utils/onboardingData'

interface Props {
  horario: string
  setHorario: (v: string) => void
  onNext: () => void
  onBack: () => void
  loading: boolean
}

export default function PasoHorario({ horario, setHorario, onNext, onBack, loading }: Props) {
  return (
    <OnboardingLayout
      paso={4} total={6}
      titulo="¿En qué horario deseas aprender?"
      subtitulo="Ajustaremos los recordatorios de tus clases según tu disponibilidad."
      onNext={onNext} onBack={onBack} loading={loading}
      hideHint
    >
      <div className="onboarding-grid onboarding-grid--1">
        {HORARIOS.map(({ label, sub }) => (
          <button
            key={label}
            type="button"
            // Clase propia (no la de OpcionCard) — ver onboarding.css para
            // el detalle de por qué esto importa (bug de colisión de clases).
            className={`onboarding-horario-card ${horario === label ? 'onboarding-horario-card--active' : ''}`}
            onClick={() => setHorario(label)}
          >
            <span className="onboarding-horario-label">{label}</span>
            <span className="onboarding-horario-sub">{sub}</span>
          </button>
        ))}
      </div>
    </OnboardingLayout>
  )
}