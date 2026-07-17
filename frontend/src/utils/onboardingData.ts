// ── Tipos ──────────────────────────────────────────────────────────────────────
export type EstadoLaboral = 'activo' | 'desempleado' | ''
export type NivelEducativo =
  | 'primario_completo' | 'primario_incompleto'
  | 'secundario_completo' | 'secundario_incompleto'
  | 'terciario_completo' | 'terciario_incompleto' | 'terciario_en_curso'
  | 'universitario_completo' | 'universitario_incompleto' | 'universitario_en_curso'
  | 'prefiero_no_decir' | ''
export type Disponibilidad = 'baja' | 'media' | 'alta' | ''

// ── Mapeos frontend → backend ───────────────────────────────────────────────
// TODO: backend debería actualizar EstadoLaboralEnum para incluir 'estudio'
// y 'prefiero_no_decir'. Por ahora mapeamos así:
export const ESTADO_LABORAL_MAP: Record<string, EstadoLaboral> = {
  'Trabajo': 'activo',
  'Estudio': 'activo',      // TODO: mapeo provisional
  'Prefiero no decir': '',
}

// TODO: backend debería actualizar DisponibilidadTiempoEnum para incluir
// franjas horarias (mañana/tarde/noche). Por ahora mapeamos así:
export const DISPONIBILIDAD_MAP: Record<string, Disponibilidad> = {
  'Mañana': 'baja',    // TODO: mapeo provisional
  'Tarde': 'media',   // TODO: mapeo provisional
  'Noche': 'alta',    // TODO: mapeo provisional
}

// ── Paso 1: Intereses ────────────────────────────────────────────────────────
export const INTERESES = [
  { label: 'Marketing', emoji: '📢' },
  { label: 'Negocios', emoji: '💼' },
  { label: 'Diseño', emoji: '🎨' },
  { label: 'IA', emoji: '🤖' },
  { label: 'Desarrollo Web', emoji: '💻' },
  { label: 'UX/UI', emoji: '🖌️' },
]

// ── Paso 2: Empleabilidad ────────────────────────────────────────────────────
export const ESTADOS_LABORALES = ['Trabajo', 'Estudio', 'Prefiero no decir']

// ── Paso 3: Nivel educativo ──────────────────────────────────────────────────
export const NIVELES_EDUCATIVOS: { label: string; value: NivelEducativo }[] = [
  { label: 'Primaria incompleta', value: 'primario_incompleto' },
  { label: 'Primaria completa', value: 'primario_completo' },
  { label: 'Secundaria incompleta', value: 'secundario_incompleto' },
  { label: 'Secundaria completa', value: 'secundario_completo' },
  { label: 'Terciario incompleto', value: 'terciario_incompleto' },
  { label: 'Terciario completo', value: 'terciario_completo' },
  { label: 'Actualmente curso en la uni', value: 'universitario_en_curso' },
  { label: 'Universidad completa', value: 'universitario_completo' },
  { label: 'Prefiero no decir', value: 'prefiero_no_decir' },
]

// ── Paso 4: Horarios ─────────────────────────────────────────────────────────
export const HORARIOS = [
  { label: 'Mañana', sub: '8:00 AM – 12:00 PM' },
  { label: 'Tarde', sub: '12:00 PM – 6:00 PM' },
  { label: 'Noche', sub: '6:00 PM – 11:00 PM' },
]