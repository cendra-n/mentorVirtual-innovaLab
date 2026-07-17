import OnboardingLayout from './OnboardingLayout'
import OpcionCard from './OpcionCard'
import { NIVELES_EDUCATIVOS, NivelEducativo } from '../../utils/onboardingData'

interface Props {
  nivelEducativo: NivelEducativo
  setNivelEducativo: (v: NivelEducativo) => void
  onNext: () => void
  onBack: () => void
  loading: boolean
}

export default function PasoEducacion({ nivelEducativo, setNivelEducativo, onNext, onBack, loading }: Props) {
  return (
    <OnboardingLayout
      paso={3} total={6}
      titulo="¿Cuál es tu nivel educativo?"
      subtitulo="Selecciona el nivel más alto que alcanzaste."
      onNext={onNext} onBack={onBack} onSkip={onNext} loading={loading}
      hideHint
    >
      <div className="onboarding-grid onboarding-grid--3">
        {NIVELES_EDUCATIVOS.map(({ label, value }) => (
          <OpcionCard key={label} label={label} selected={nivelEducativo === value} onClick={() => setNivelEducativo(value)} />
        ))}
      </div>
    </OnboardingLayout>
  )
}