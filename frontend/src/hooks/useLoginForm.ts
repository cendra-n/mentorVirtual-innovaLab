import { useState } from 'react'
import { apiLogin, parseFieldErrors } from '../services/api'

export type LoginFieldErrors = Partial<Record<'email' | 'password', string>>

/**
 * Toda la lógica del formulario de Login: estado, validación y submit.
 * Se separó de Registro porque son flujos con campos y reglas muy
 * distintas — mantenerlos juntos en un solo hook obligaba a llenar
 * todo de "if (mode === ...)".
 */
export function useLoginForm(onLogin: (access: string, refresh: string) => void) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<LoginFieldErrors>({})
  const [generalError, setGeneralError] = useState('')
  const [loading, setLoading] = useState(false)

  const validate = (): LoginFieldErrors => {
    const errors: LoginFieldErrors = {}
    if (!email.trim()) errors.email = 'El email es obligatorio.'
    else if (/\s/.test(email)) errors.email = 'El email no puede contener espacios.'
    else if (!/^\S+@\S+\.\S+$/.test(email)) errors.email = 'El email no es válido.'
    if (!password) errors.password = 'La contraseña es obligatoria.'
    return errors
  }

  const clearFieldError = (field: keyof LoginFieldErrors) => {
    if (fieldErrors[field]) setFieldErrors(prev => ({ ...prev, [field]: undefined }))
  }

  // BUG-FE-006: deshabilitamos el botón hasta que Email y Contraseña
  // contengan datos válidos, manteniendo consistencia con Registro.
  const isSubmitDisabled = loading || !email.trim() || !password.trim()

  const handleSubmit = async () => {
    setGeneralError('')
    const errors = validate()
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }
    setFieldErrors({})
    setLoading(true)
    try {
      // BUG-FE-009: el email se normaliza a minúsculas antes de mandarlo al
      // backend, igual que en Registro, para que el login funcione sin
      // importar cómo el usuario escriba mayúsculas/minúsculas.
      const normalizedEmail = email.trim().toLowerCase()
      const res = await apiLogin(normalizedEmail, password)
      if (res.ok && res.data.access) {
        onLogin(res.data.access, res.data.refresh)
        return
      }
      const backendErrors = parseFieldErrors(res.data)
      if (Object.keys(backendErrors).length > 0) {
        setFieldErrors(backendErrors as LoginFieldErrors)
      } else {
        // BUG-FE-007: el backend manda el mensaje bajo la clave "error"
        // (no "detail" ni "message"), así que se prioriza ese campo.
        setGeneralError(res.data.error || res.data.detail || res.data.message || 'Email o contraseña incorrectos.')
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
  }

  return {
    email, setEmail,
    password, setPassword,
    fieldErrors, clearFieldError,
    generalError,
    loading,
    isSubmitDisabled,
    handleSubmit,
    reset,
  }
}