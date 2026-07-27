import { useState, useEffect } from 'react'
import { apiRegister, apiUpdateStudentProfile, parseFieldErrors, apiGeoCountries, apiGeoProvinces } from '../services/api'
import { getPasswordChecks, calcularEdad } from '../utils/authValidation'

export type Genero = 'F' | 'M' | 'ND'
export type RegisterField = 'email' | 'username' | 'password' | 'confirm' | 'fechaNacimiento' | 'genero' | 'terminos'
export type RegisterFieldErrors = Partial<Record<RegisterField, string>>

/**
 * Toda la lógica del formulario de Registro: estado, validación campo
 * por campo, y el submit en dos pasos (crear cuenta + completar perfil).
 */
export function useRegisterForm(onRegisterSuccess: (access: string, refresh: string) => void) {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [fechaNacimiento, setFechaNacimiento] = useState('')
  const [genero, setGenero] = useState<Genero | ''>('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [aceptaTerminos, setAceptaTerminos] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<RegisterFieldErrors>({})
  const [generalError, setGeneralError] = useState('')
  const [loading, setLoading] = useState(false)

  // País/provincia — opcionales, no bloquean el registro (Poly).
  const [countries, setCountries] = useState<{ country_id: number; country_name: string }[]>([])
  const [provinces, setProvinces] = useState<{ province_id: number; province_name: string }[]>([])
  const [country, setCountry] = useState<number | ''>('')
  const [province, setProvince] = useState<number | ''>('')
  const [locality, setLocality] = useState<number | ''>('')
  const [localityName, setLocalityName] = useState('')
  const [geoLoading, setGeoLoading] = useState(false)

  useEffect(() => {
    apiGeoCountries().then(res => {
      if (res.ok && Array.isArray(res.data)) setCountries(res.data)
    }).catch(() => { /* opcional: si falla, el registro sigue sin país */ })
  }, [])

  useEffect(() => {
    setLocality(''); setLocalityName('')
    if (!country) { setProvinces([]); setProvince(''); return }
    setGeoLoading(true)
    apiGeoProvinces(country).then(res => {
      if (res.ok && Array.isArray(res.data)) setProvinces(res.data)
    }).catch(() => { }).finally(() => setGeoLoading(false))
  }, [country])

  const validateField = (field: RegisterField): string | undefined => {
    switch (field) {
      case 'username':
        if (!username.trim()) return 'El nombre de usuario es obligatorio.'
        if (/\s/.test(username)) return 'El nombre de usuario no puede contener espacios.'
        if (username.trim().length < 3) return 'Debe tener al menos 3 caracteres.'
        // Recuperado de la rama vieja fix/qa-bugs-validacion / feature/registro-rediseno-figma,
        // que se había perdido al reescribir este componente.
        if (username.trim().length > 150) return 'El nombre de usuario no puede superar los 150 caracteres.'
        // Coincide con la validación del backend (RegisterRequestSerializer.validate):
        // un username compuesto únicamente por números no es válido.
        if (/^\d+$/.test(username.trim())) return 'El nombre de usuario no puede estar compuesto únicamente por números.'
        if (!/^[A-Za-z0-9_]+$/.test(username)) return 'Solo letras, números y guion bajo.'
        return undefined

      case 'fechaNacimiento':
        if (!fechaNacimiento) return 'La fecha de nacimiento es obligatoria.'
        if (new Date(fechaNacimiento).getFullYear() < 1900) return 'Ingresá una fecha válida (año mínimo 1900).'
        if (new Date(fechaNacimiento).getFullYear() > new Date().getFullYear()) return 'Ingresá una fecha válida.'
        if (calcularEdad(fechaNacimiento) < 18) return 'Tenés que ser mayor de 18 años para registrarte.'
        return undefined

      case 'email':
        if (!email.trim()) return 'El email es obligatorio.'
        if (/\s/.test(email)) return 'El email no puede contener espacios.'
        if (!/^\S+@\S+\.\S+$/.test(email)) return 'El email no es válido.'
        return undefined

      case 'genero':
        if (!genero) return 'Elegí una opción.'
        return undefined

      case 'password': {
        if (!password) return 'La contraseña es obligatoria.'
        const c = getPasswordChecks(password)
        if (!c.length) return 'Debe tener al menos 8 caracteres.'
        if (!c.upper) return 'Debe incluir al menos una mayúscula.'
        if (!c.lower) return 'Debe incluir al menos una minúscula.'
        if (!c.number) return 'Debe incluir al menos un número.'
        if (!c.special) return 'Debe incluir al menos un carácter especial.'
        return undefined
      }

      case 'confirm':
        if (!confirm) return 'Confirmá tu contraseña.'
        if (confirm !== password) return 'Las contraseñas no coinciden.'
        return undefined

      case 'terminos':
        if (!aceptaTerminos) return 'Tenés que aceptar los términos para continuar.'
        return undefined
    }
  }

  const validateAll = (): RegisterFieldErrors => {
    const fields: RegisterField[] = ['username', 'fechaNacimiento', 'email', 'genero', 'password', 'confirm', 'terminos']
    const errors: RegisterFieldErrors = {}
    for (const f of fields) {
      const err = validateField(f)
      if (err) errors[f] = err
    }
    return errors
  }

  const handleBlur = (field: RegisterField) => {
    const err = validateField(field)
    setFieldErrors(prev => ({ ...prev, [field]: err }))
  }

  const clearFieldError = (field: RegisterField) => {
    if (fieldErrors[field]) setFieldErrors(prev => ({ ...prev, [field]: undefined }))
  }

  // Deshabilitamos el botón hasta que todos los campos obligatorios
  // tengan algún valor cargado, mismo criterio que en Login (BUG-FE-006).
  // No reemplaza la validación completa (que sigue corriendo al submit),
  // solo evita que se pueda intentar enviar el formulario vacío.
  const isSubmitDisabled =
    loading ||
    !username.trim() ||
    !email.trim() ||
    !fechaNacimiento ||
    !genero ||
    !password ||
    !confirm ||
    !aceptaTerminos

  const handleSubmit = async () => {
    setGeneralError('')
    const errors = validateAll()
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }
    setFieldErrors({})
    setLoading(true)
    try {
      // Normalizamos el email también en Registro, para que ambos flujos
      // sean 100% consistentes entre sí (y con lo que espera el backend).
      const normalizedEmail = email.trim().toLowerCase()
      // El backend guarda el username en minúsculas (RegisterRequestSerializer);
      // lo normalizamos acá también para que lo que el usuario ve coincida
      // con lo que va a quedar guardado.
      const normalizedUsername = username.trim().toLowerCase()
      const res = await apiRegister(normalizedUsername, normalizedEmail, password, confirm, {
        country: country || null,
        province: province || null,
        locality: locality || null,
      })
      if (res.ok && res.data.access) {
        try {
          await apiUpdateStudentProfile(res.data.access, {
            birth_date: fechaNacimiento,
            user_gender: genero,
          })
        } catch {
          // Si falla este segundo paso, no bloqueamos el acceso: la cuenta
          // ya se creó bien. La persona puede completar fecha/género después
          // desde su perfil. Solo lo dejamos registrado en consola.
          console.warn('No se pudo guardar fecha de nacimiento/género; la cuenta se creó igual.')
        }
        onRegisterSuccess(res.data.access, res.data.refresh)
        return
      }
      const backendErrors = parseFieldErrors(res.data)
      const mapped: RegisterFieldErrors = {}
      if (backendErrors.email) mapped.email = backendErrors.email
      if (backendErrors.username) mapped.username = backendErrors.username
      if (backendErrors.password) mapped.password = backendErrors.password
      if (backendErrors.password_confirm) mapped.confirm = backendErrors.password_confirm
      if (Object.keys(mapped).length > 0) {
        setFieldErrors(mapped)
      } else {
        setGeneralError(res.data.detail || res.data.message || 'Ocurrió un error, intentá de nuevo.')
      }
    } catch {
      setGeneralError('No se pudo conectar al servidor.')
    }
    setLoading(false)
  }

  const reset = () => {
    setFieldErrors({})
    setGeneralError('')
    setPassword('')
    setConfirm('')
  }

  return {
    email, setEmail,
    username, setUsername,
    fechaNacimiento, setFechaNacimiento,
    genero, setGenero,
    password, setPassword,
    confirm, setConfirm,
    aceptaTerminos, setAceptaTerminos,
    fieldErrors, clearFieldError, handleBlur,
    generalError,
    loading,
    isSubmitDisabled,
    handleSubmit,
    reset,
    countries, provinces, country, setCountry, province, setProvince, geoLoading,
    locality, localityName, setLocality, setLocalityName,
  }
}