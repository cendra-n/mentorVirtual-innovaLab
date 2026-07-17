import OnboardingLayout from './OnboardingLayout'
import PulsoConCampana from '../PulsoConCampana'

interface Props {
  recordatorios: boolean | null
  setRecordatorios: (v: boolean) => void
  onNext: () => void
  onBack: () => void
  loading: boolean
}

export default function PasoRecordatorios({ recordatorios, setRecordatorios, onNext, onBack, loading }: Props) {
  return (
    <OnboardingLayout
      paso={5} total={6}
      titulo="¿Deseas que te enviemos recordatorios de tus clases?"
      subtitulo="Mantente al día con tus metas. Podés cambiarlo cuando quieras desde los ajustes."
      onNext={onNext} onBack={onBack} loading={loading}
      nextDisabled={recordatorios === null}
      hideHint
    >
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '8px' }}>
        <PulsoConCampana size={90} />
      </div>

      <div className="onboarding-recordatorios">
        <button
          type="button"
          className={`onboarding-recordatorio-card ${recordatorios === true ? 'onboarding-recordatorio-card--active' : ''}`}
          onClick={() => setRecordatorios(true)}
        >
          <span className="onboarding-recordatorio-icon">✅</span>
          <div>
            <strong>¡Sí, activar recordatorios!</strong>
            <p>Recomendado para mantener tus metas</p>
          </div>
        </button>
        <button
          type="button"
          className={`onboarding-recordatorio-card ${recordatorios === false ? 'onboarding-recordatorio-card--active' : ''}`}
          onClick={() => setRecordatorios(false)}
        >
          <span className="onboarding-recordatorio-icon">🔕</span>
          <div>
            <strong>No, por ahora</strong>
            <p>Puedes activarlo desde los ajustes</p>
          </div>
        </button>
      </div>
    </OnboardingLayout>
  )
}