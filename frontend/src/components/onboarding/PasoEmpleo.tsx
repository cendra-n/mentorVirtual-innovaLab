import OnboardingLayout from './OnboardingLayout'
import OpcionCard from './OpcionCard'
import { ESTADOS_LABORALES } from '../../utils/onboardingData'

interface Props {
  estadoLaboral: string
  setEstadoLaboral: (v: string) => void
  onNext: () => void
  onBack: () => void
  loading: boolean
}

export default function PasoEmpleo({ estadoLaboral, setEstadoLaboral, onNext, onBack, loading }: Props) {
  return (
    <OnboardingLayout
      paso={2} total={6}
      titulo="Cuéntanos un poco de ti..."
      subtitulo="Selecciona tu estado de empleabilidad actualmente, o si estás estudiando."
      onNext={onNext} onBack={onBack} onSkip={onNext} loading={loading}
      hideHint
    >
      <div className="onboarding-grid onboarding-grid--3">
        {ESTADOS_LABORALES.map(label => (
          <OpcionCard key={label} label={label} selected={estadoLaboral === label} onClick={() => setEstadoLaboral(label)} />
        ))}
      </div>
    </OnboardingLayout>
  )
}