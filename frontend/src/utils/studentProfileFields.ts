/**
 * Mapa español → inglés de los campos de StudentProfile, según la
 * tarjeta de Trello "BE - Refactorización general" (en progreso, sin
 * mergear todavía). Mientras el backend no termine de migrar, el
 * frontend manda y lee AMBOS nombres, para que funcione antes y
 * después del cambio sin necesitar otro deploy coordinado.
 *
 * Si en algún momento el backend confirma que ya migró del todo, se
 * puede sacar el nombre en español de acá y de cada lugar que lo usa.
 */
export const STUDENT_PROFILE_FIELD_MAP: Record<string, string> = {
  fecha_nacimiento: 'birth_date',
  nivel_educativo: 'education_level',
  estado_laboral: 'employment_status',
  genero: 'user_gender',
  objetivo_principal: 'primary_objective',
  disponibilidad_tiempo: 'time_availability',
  zona_horaria: 'time_zone',
  intereses: 'user_interests',
  cursos_inscriptos: 'enrolled_courses',
  frecuencia_entradas: 'entry_frecuency',
  racha_actual_dias: 'current_streaks_days',
  racha_maxima_dias: 'max_streaks_days',
  tiempo_acumulado_app_minutos: 'app_time_min',
  tiempo_interaccion_mentor_minutos: 'mentor_interaction_time_min',
  cantidad_videos_vistos: 'watched_videos_count',
  tiempo_api_youtube_minutos: 'youtube_api_time_min',
  desafios_completados: 'completed_challenges',
  cursos_completados: 'complete_courses',
}

/**
 * Para escribir (POST/PATCH): recibe un objeto con claves en español
 * y devuelve uno con ambas claves (español + inglés) apuntando al
 * mismo valor. El backend, tenga la versión que tenga, va a leer la
 * que reconozca e ignorar la otra.
 */
export function withEnglishFallback<T extends Record<string, any>>(datos: T): Record<string, any> {
  const out: Record<string, any> = { ...datos }
  for (const key of Object.keys(datos)) {
    const enKey = STUDENT_PROFILE_FIELD_MAP[key]
    if (enKey) out[enKey] = (datos as Record<string, any>)[key]
  }
  return out
}

/**
 * Para leer (GET): dado el objeto crudo que devuelve el backend y el
 * nombre en español de un campo, devuelve el valor exista con el
 * nombre viejo o con el nuevo.
 */
export function readField(data: any, campoEspanol: string) {
  if (!data) return undefined
  if (data[campoEspanol] !== undefined) return data[campoEspanol]
  const enKey = STUDENT_PROFILE_FIELD_MAP[campoEspanol]
  return enKey ? data[enKey] : undefined
}
