import OnboardingLayout from './OnboardingLayout'
import OpcionCard from './OpcionCard'
import { INTERESES } from '../../utils/onboardingData'

interface Props {
  intereses: string[]
  toggleInteres: (label: string) => void
  onNext: () => void
  loading: boolean
}

export default function PasoIntereses({ intereses, toggleInteres, onNext, loading }: Props) {
  return (
    <OnboardingLayout
      paso={1} total={6}
      titulo="¿Qué tipo de contenido te gustaría aprender?"
      subtitulo="Selecciona las categorías que más te interesan para personalizar tu experiencia."
      onNext={onNext} onSkip={onNext} loading={loading}
    >
      <div className="onboarding-grid">
        {INTERESES.map(({ label, emoji }) => (
          <OpcionCard key={label} label={label} emoji={emoji} selected={intereses.includes(label)} onClick={() => toggleInteres(label)} />
        ))}
      </div>
    </OnboardingLayout>
  )
}