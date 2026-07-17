/**
 * Chequeos de requisitos de contraseña, compartidos entre el hook de
 * registro y el checklist visual que se muestra mientras se escribe.
 */
export function getPasswordChecks(pass: string) {
  return {
    number: /[0-9]/.test(pass),
    upper: /[A-Z]/.test(pass),
    lower: /[a-z]/.test(pass),
    special: /[^A-Za-z0-9]/.test(pass),
    length: pass.length >= 8,
  }
}

/** Calcula la edad exacta a partir de una fecha en formato YYYY-MM-DD. */
export function calcularEdad(fechaISO: string): number {
  const hoy = new Date()
  const nacimiento = new Date(fechaISO)
  let edad = hoy.getFullYear() - nacimiento.getFullYear()
  const aunNoCumplio =
    hoy.getMonth() < nacimiento.getMonth() ||
    (hoy.getMonth() === nacimiento.getMonth() && hoy.getDate() < nacimiento.getDate())
  if (aunNoCumplio) edad--
  return edad
}