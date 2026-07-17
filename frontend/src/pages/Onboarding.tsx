import { useOnboarding } from '../hooks/useOnboarding'
import PasoIntereses from '../components/onboarding/PasoIntereses'
import PasoEmpleo from '../components/onboarding/PasoEmpleo'
import PasoEducacion from '../components/onboarding/PasoEducacion'
import PasoHorario from '../components/onboarding/PasoHorario'
import PasoRecordatorios from '../components/onboarding/PasoRecordatorios'
import PasoExito from '../components/onboarding/PasoExito'

interface Props {
  accessToken: string
  onComplete: () => void
}

/**
 * Flujo de Onboarding (6 pasos). Cada paso vive en su propio archivo
 * dentro de components/onboarding/; toda la lógica de estado y
 * guardado vive en el hook useOnboarding. Este componente solo
 * decide qué paso mostrar.
 */
export default function Onboarding({ accessToken, onComplete }: Props) {
  const {
    paso,
    intereses, toggleInteres,
    estadoLaboral, setEstadoLaboral,
    nivelEducativo, setNivelEducativo,
    horario, setHorario,
    recordatorios, setRecordatorios,
    loading,
    siguiente, atras,
  } = useOnboarding(accessToken)

  if (paso === 1) return <PasoIntereses intereses={intereses} toggleInteres={toggleInteres} onNext={siguiente} loading={loading} />
  if (paso === 2) return <PasoEmpleo estadoLaboral={estadoLaboral} setEstadoLaboral={setEstadoLaboral} onNext={siguiente} onBack={atras} loading={loading} />
  if (paso === 3) return <PasoEducacion nivelEducativo={nivelEducativo} setNivelEducativo={setNivelEducativo} onNext={siguiente} onBack={atras} loading={loading} />
  if (paso === 4) return <PasoHorario horario={horario} setHorario={setHorario} onNext={siguiente} onBack={atras} loading={loading} />
  if (paso === 5) return <PasoRecordatorios recordatorios={recordatorios} setRecordatorios={setRecordatorios} onNext={siguiente} onBack={atras} loading={loading} />
  if (paso === 6) return <PasoExito onComplete={onComplete} />

  return null
}