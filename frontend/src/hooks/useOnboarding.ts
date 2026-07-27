import { useState } from 'react'
import { apiUpdateStudentProfile } from '../services/api'
import { ESTADO_LABORAL_MAP, DISPONIBILIDAD_MAP, NivelEducativo } from '../utils/onboardingData'

/**
 * Toda la lógica del flujo de Onboarding: estado de cada paso,
 * navegación (siguiente/atrás), y guardado hacia el backend.
 * Separado de la UI para que los componentes de cada paso queden
 * simples y la lógica se pueda testear/editar sin tocar el JSX.
 */
export function useOnboarding(accessToken: string) {
  const [paso, setPaso] = useState(1)
  const [intereses, setIntereses] = useState<string[]>([])
  const [estadoLaboral, setEstadoLaboral] = useState<string>('')
  const [nivelEducativo, setNivelEducativo] = useState<NivelEducativo>('')
  const [horario, setHorario] = useState<string>('')
  const [recordatorios, setRecordatorios] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(false)

  const toggleInteres = (label: string) =>
    setIntereses(prev => prev.includes(label) ? prev.filter(i => i !== label) : [...prev, label])

  const guardarPaso = async (datos: Record<string, any>) => {
    try {
      await apiUpdateStudentProfile(accessToken, datos)
    } catch {
      console.warn('No se pudo guardar el paso, continuando igual.')
    }
  }

  const siguiente = async () => {
    setLoading(true)
    if (paso === 1) {
      await guardarPaso({ user_interests: intereses })
    } else if (paso === 2) {
      const valorBackend = ESTADO_LABORAL_MAP[estadoLaboral]
      if (valorBackend) await guardarPaso({ employment_status: valorBackend })
    } else if (paso === 3) {
      // No mandamos nada al backend si no se eligió nada, o si el
      // usuario explícitamente prefirió no decirlo.
      if (nivelEducativo && nivelEducativo !== 'prefiero_no_decir') {
        await guardarPaso({ education_level: nivelEducativo })
      }
    } else if (paso === 4) {
      const valorBackend = DISPONIBILIDAD_MAP[horario]
      if (valorBackend) await guardarPaso({ time_availability: valorBackend })
    } else if (paso === 5) {
      // TODO: backend no tiene campo para recordatorios todavía.
      // Guardamos preferencia en localStorage como placeholder.
      localStorage.setItem('recordatorios', recordatorios ? 'true' : 'false')
    }
    setLoading(false)
    if (paso < 6) setPaso(p => p + 1)
  }

  const atras = () => setPaso(p => p - 1)

  return {
    paso,
    intereses, toggleInteres,
    estadoLaboral, setEstadoLaboral,
    nivelEducativo, setNivelEducativo,
    horario, setHorario,
    recordatorios, setRecordatorios,
    loading,
    siguiente, atras,
  }
}