import { useState } from 'react'
import { apiUpdateStudentProfile } from '../services/api'

interface Props {
  accessToken: string
  onComplete: () => void
}

// ── Tipos ──────────────────────────────────────────────────────────────────────
type EstadoLaboral = 'activo' | 'desempleado' | ''
type NivelEducativo =
  | 'primario_completo' | 'primario_incompleto'
  | 'secundario_completo' | 'secundario_incompleto'
  | 'terciario_completo' | 'terciario_incompleto' | 'terciario_en_curso'
  | 'universitario_completo' | 'universitario_incompleto' | 'universitario_en_curso'
  | ''
type Disponibilidad = 'baja' | 'media' | 'alta' | ''

// ── Mapeos frontend → backend ───────────────────────────────────────────────
// TODO: backend debería actualizar EstadoLaboralEnum para incluir 'estudio'
// y 'prefiero_no_decir'. Por ahora mapeamos así:
const ESTADO_LABORAL_MAP: Record<string, EstadoLaboral> = {
  'Trabajo':          'activo',
  'Estudio':          'activo',      // TODO: mapeo provisional
  'Prefiero no decir': '',
}

// TODO: backend debería actualizar DisponibilidadTiempoEnum para incluir
// franjas horarias (mañana/tarde/noche). Por ahora mapeamos así:
const DISPONIBILIDAD_MAP: Record<string, Disponibilidad> = {
  'Mañana': 'baja',    // TODO: mapeo provisional
  'Tarde':  'media',   // TODO: mapeo provisional
  'Noche':  'alta',    // TODO: mapeo provisional
}

// ── Iconos para los pasos ────────────────────────────────────────────────────
function CheckCircleIcon() {
  return (
    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#26874A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

// ── Layout compartido de todos los pasos ────────────────────────────────────
function OnboardingLayout({
  paso, total, titulo, subtitulo, children, onNext, onBack, nextLabel = 'Siguiente →', nextDisabled = false, loading = false, hideHint = false
}: {
  paso: number; total: number; titulo: string; subtitulo?: string
  children: React.ReactNode; onNext: () => void; onBack?: () => void
  nextLabel?: string; nextDisabled?: boolean; loading?: boolean; hideHint?: boolean
}) {
  return (
    <div className="auth-page">
      <header className="auth-header">
        <div className="auth-header-logo">
          <div className="auth-header-logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="9" cy="8" r="4" /><path d="M2 21c0-4 3.5-7 7-7s7 3 7 7" />
              <line x1="19" y1="8" x2="19" y2="14" /><line x1="16" y1="11" x2="22" y2="11" />
            </svg>
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
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Tarjeta de opción seleccionable ────────────────────────────────────────
function OpcionCard({ label, emoji, selected, onClick }: { label: string; emoji?: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      className={`onboarding-opcion-card ${selected ? 'onboarding-opcion-card--active' : ''}`}
      onClick={onClick}
    >
      {emoji && <span className="onboarding-opcion-emoji">{emoji}</span>}
      <span>{label}</span>
    </button>
  )
}

// ── Paso 1: Intereses ────────────────────────────────────────────────────────
const INTERESES = [
  { label: 'Marketing', emoji: '📢' },
  { label: 'Negocios', emoji: '💼' },
  { label: 'Diseño', emoji: '🎨' },
  { label: 'IA', emoji: '🤖' },
  { label: 'Desarrollo Web', emoji: '💻' },
  { label: 'UX/UI', emoji: '🖌️' },
]

// ── Paso 2: Empleabilidad ────────────────────────────────────────────────────
const ESTADOS_LABORALES = ['Trabajo', 'Estudio', 'Prefiero no decir']

// ── Paso 3: Nivel educativo ──────────────────────────────────────────────────
const NIVELES_EDUCATIVOS: { label: string; value: NivelEducativo }[] = [
  { label: 'Primaria incompleta',    value: 'primario_incompleto' },
  { label: 'Primaria completa',      value: 'primario_completo' },
  { label: 'Secundaria incompleta',  value: 'secundario_incompleto' },
  { label: 'Secundaria completa',    value: 'secundario_completo' },
  { label: 'Terciario incompleto',   value: 'terciario_incompleto' },
  { label: 'Terciario completo',     value: 'terciario_completo' },
  { label: 'Actualmente curso en la uni', value: 'universitario_en_curso' },
  { label: 'Universidad completa',   value: 'universitario_completo' },
  { label: 'Prefiero no decir',      value: '' },
]

// ── Paso 4: Horarios ─────────────────────────────────────────────────────────
const HORARIOS = [
  { label: 'Mañana',  sub: '8:00 AM – 12:00 PM' },
  { label: 'Tarde',   sub: '12:00 PM – 6:00 PM' },
  { label: 'Noche',   sub: '6:00 PM – 11:00 PM' },
]

// ── Componente principal ─────────────────────────────────────────────────────
export default function Onboarding({ accessToken, onComplete }: Props) {
  const [paso, setPaso]                   = useState(1)
  const [intereses, setIntereses]         = useState<string[]>([])
  const [estadoLaboral, setEstadoLaboral] = useState<string>('')
  const [nivelEducativo, setNivelEducativo] = useState<NivelEducativo>('')
  const [horario, setHorario]             = useState<string>('')
  const [recordatorios, setRecordatorios] = useState<boolean | null>(null)
  const [loading, setLoading]             = useState(false)

  const toggleInterés = (label: string) =>
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
      await guardarPaso({ intereses })
    } else if (paso === 2) {
      const valorBackend = ESTADO_LABORAL_MAP[estadoLaboral]
      if (valorBackend) await guardarPaso({ estado_laboral: valorBackend })
    } else if (paso === 3) {
      if (nivelEducativo) await guardarPaso({ nivel_educativo: nivelEducativo })
    } else if (paso === 4) {
      const valorBackend = DISPONIBILIDAD_MAP[horario]
      if (valorBackend) await guardarPaso({ disponibilidad_tiempo: valorBackend })
    } else if (paso === 5) {
      // TODO: backend no tiene campo para recordatorios todavía.
      // Guardamos preferencia en localStorage como placeholder.
      localStorage.setItem('recordatorios', recordatorios ? 'true' : 'false')
    }
    setLoading(false)
    if (paso < 6) setPaso(p => p + 1)
  }

  const atras = () => setPaso(p => p - 1)

  // ── Paso 6: Pantalla de éxito ────────────────────────────────────────────
  if (paso === 6) {
    return (
      <div className="auth-page">
        <header className="auth-header">
          <div className="auth-header-logo">
            <div className="auth-header-logo-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="8" r="4" /><path d="M2 21c0-4 3.5-7 7-7s7 3 7 7" />
                <line x1="19" y1="8" x2="19" y2="14" /><line x1="16" y1="11" x2="22" y2="11" />
              </svg>
            </div>
            <span>Impulsa</span>
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

  // ── Pasos 1 al 5 ────────────────────────────────────────────────────────
  if (paso === 1) return (
    <OnboardingLayout
      paso={1} total={6}
      titulo="¿Qué tipo de contenido te gustaría aprender?"
      subtitulo="Selecciona las categorías que más te interesan para personalizar tu experiencia."
      onNext={siguiente} loading={loading}
    >
      <div className="onboarding-grid">
        {INTERESES.map(({ label, emoji }) => (
          <OpcionCard key={label} label={label} emoji={emoji} selected={intereses.includes(label)} onClick={() => toggleInterés(label)} />
        ))}
      </div>
    </OnboardingLayout>
  )

  if (paso === 2) return (
    <OnboardingLayout
      paso={2} total={6}
      titulo="Cuéntanos un poco de ti..."
      subtitulo="Selecciona tu estado de empleabilidad actualmente, o si estás estudiando."
      onNext={siguiente} onBack={atras} loading={loading}
    >
      <div className="onboarding-grid onboarding-grid--3">
        {ESTADOS_LABORALES.map(label => (
          <OpcionCard key={label} label={label} selected={estadoLaboral === label} onClick={() => setEstadoLaboral(label)} />
        ))}
      </div>
    </OnboardingLayout>
  )

  if (paso === 3) return (
    <OnboardingLayout
      paso={3} total={6}
      titulo="¿Cuál es tu nivel educativo?"
      subtitulo="Selecciona el nivel más alto que alcanzaste."
      onNext={siguiente} onBack={atras} loading={loading} hideHint
    >
      <div className="onboarding-grid onboarding-grid--3">
        {NIVELES_EDUCATIVOS.map(({ label, value }) => (
          <OpcionCard key={label} label={label} selected={nivelEducativo === value} onClick={() => setNivelEducativo(value)} />
        ))}
      </div>
    </OnboardingLayout>
  )

  if (paso === 4) return (
    <OnboardingLayout
      paso={4} total={6}
      titulo="¿En qué horario deseas aprender?"
      subtitulo="Ajustaremos los recordatorios de tus clases según tu disponibilidad."
      onNext={siguiente} onBack={atras} loading={loading}
    >
      <div className="onboarding-grid onboarding-grid--1">
        {HORARIOS.map(({ label, sub }) => (
          <button
            key={label}
            type="button"
            className={`onboarding-horario-card ${horario === label ? 'onboarding-opcion-card--active' : ''}`}
            onClick={() => setHorario(label)}
          >
            <span className="onboarding-horario-label">{label}</span>
            <span className="onboarding-horario-sub">{sub}</span>
          </button>
        ))}
      </div>
    </OnboardingLayout>
  )

  if (paso === 5) return (
    <OnboardingLayout
      paso={5} total={6}
      titulo="¿Deseas que te enviemos recordatorios de tus clases?"
      subtitulo="Mantente al día con tus metas, ¡te notificaremos lo importante para alcanzarlas!"
      onNext={siguiente} onBack={atras} loading={loading}
      nextDisabled={recordatorios === null}
    >
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

  return null
}