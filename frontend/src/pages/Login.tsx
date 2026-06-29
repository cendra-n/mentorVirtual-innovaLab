import { useState } from 'react'
import MentorBot from '../components/MentorBot'
import { apiLogin, apiRegister, parseFieldErrors } from '../services/api'

function EyeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EyeOffIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 11 8 11 8a18.45 18.45 0 0 1-3.06 4.16M6.61 6.61A18.45 18.45 0 0 0 1 13s4 8 11 8a10.43 10.43 0 0 0 5.39-1.49" />
      <line x1="2" y1="2" x2="22" y2="22" />
    </svg>
  )
}
interface Props {
  onLogin: (access: string, refresh: string) => void
}

type Field = 'email' | 'username' | 'password' | 'confirm'
type FieldErrors = Partial<Record<Field, string>>

function getPasswordChecks(pass: string) {
  return {
    length: pass.length >= 8,
    upper: /[A-Z]/.test(pass),
    number: /[0-9]/.test(pass),
    special: /[^A-Za-z0-9]/.test(pass),
  }
}

export default function Login({ onLogin }: Props) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')  // solo para registro
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [generalError, setGeneralError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  const appName = import.meta.env.VITE_APP_NAME || 'Mentor Virtual'
  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  // ── Validación por campo ───────────────────────────────────────────────────
  const validateField = (field: Field): string | undefined => {
    switch (field) {
      case 'email':
        if (!email.trim()) return 'El email es obligatorio.'
        if (/\s/.test(email)) return 'El email no puede contener espacios.'
        if (!/^\S+@\S+\.\S+$/.test(email)) return 'El email no es válido.'
        return undefined

      case 'username':
        if (mode !== 'register') return undefined
        if (!username.trim()) return 'El nombre de usuario es obligatorio.'
        if (/\s/.test(username)) return 'El nombre de usuario no puede contener espacios.'
        if (username.trim().length < 3) return 'Debe tener al menos 3 caracteres.'
        if (!/^[A-Za-z0-9_]+$/.test(username)) return 'Solo se permiten letras, números y guion bajo.'
        return undefined

      case 'password':
        if (!password) return 'La contraseña es obligatoria.'
        if (mode === 'register') {
          const c = getPasswordChecks(password)
          if (!c.length) return 'Debe tener al menos 8 caracteres.'
          if (!c.upper) return 'Debe incluir al menos una mayúscula.'
          if (!c.number) return 'Debe incluir al menos un número.'
          if (!c.special) return 'Debe incluir al menos un carácter especial.'
        }
        return undefined

      case 'confirm':
        if (mode !== 'register') return undefined
        if (!confirm) return 'Confirmá tu contraseña.'
        if (confirm !== password) return 'Las contraseñas no coinciden.'
        return undefined
    }
  }

  const validateAll = (): FieldErrors => {
    const fields: Field[] = mode === 'login' ? ['email', 'password'] : ['email', 'username', 'password', 'confirm']
    const errors: FieldErrors = {}
    for (const f of fields) {
      const err = validateField(f)
      if (err) errors[f] = err
    }
    return errors
  }

  const handleBlur = (field: Field) => {
    const err = validateField(field)
    setFieldErrors(prev => ({ ...prev, [field]: err }))
  }

  // Limpia el error del campo apenas el usuario empieza a corregirlo;
  // el chequeo fino se vuelve a hacer en el próximo blur o submit.
  const clearFieldError = (field: Field) => {
    if (fieldErrors[field]) {
      setFieldErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

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
      const res = mode === 'login'
        ? await apiLogin(email, password)
        : await apiRegister(username, email, password, confirm)

      if (res.ok && res.data.access) {
        onLogin(res.data.access, res.data.refresh)
        return
      }

      // Mapear errores del backend (formato Django: { campo: ["mensaje"] }) a nuestros campos
      const backendErrors = parseFieldErrors(res.data)
      const mapped: FieldErrors = {}
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

  const switchMode = (m: 'login' | 'register') => {
    setMode(m)
    setFieldErrors({})
    setGeneralError('')
    setPassword('')
    setConfirm('')
  }

  const checks = getPasswordChecks(password)

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="login-brand">
          <MentorBot mood="feliz" size={72} />
          <h1>{appName}</h1>
          <p>Tu mentor personal de aprendizaje</p>
        </div>
        <div className="login-features-list">
          {[
            '📋 Planes personalizados con IA',
            '🎬 Videos para cada paso',
            '🏆 Logros y racha diaria',
            '💬 Mentor siempre disponible',
          ].map((f, i) => <p key={i}>{f}</p>)}
        </div>
      </div>

      <div className="login-right">
        <div className="login-card">
          {/* Tabs */}
          <div className="login-tabs">
            <button className={`login-tab ${mode === 'login' ? 'login-tab--active' : ''}`} onClick={() => switchMode('login')}>
              Ingresar
            </button>
            <button className={`login-tab ${mode === 'register' ? 'login-tab--active' : ''}`} onClick={() => switchMode('register')}>
              Registrarse
            </button>
          </div>

          <div className="login-card-header">
            <MentorBot mood={loading ? 'pensativo' : mode === 'login' ? 'guiñando' : 'emocionado'} size={52} />
            <div>
              <h2>{mode === 'login' ? `¡Hola! Soy ${mentorName}` : '¡Creá tu cuenta!'}</h2>
              <p>{mode === 'login' ? 'Ingresá con tu email para continuar' : 'Empezá tu camino hoy'}</p>
            </div>
          </div>

          <div className="login-form">

            {/* Email — siempre visible */}
            <label>Email</label>
            <input
              className="form-input"
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={e => { setEmail(e.target.value); clearFieldError('email') }}
              onKeyDown={e => e.key === 'Enter' && mode === 'login' && handleSubmit()}
              onBlur={() => handleBlur('email')}
              autoComplete="email"
            />
            {fieldErrors.email && <span className="form-error">⚠️ {fieldErrors.email}</span>}

            {/* Username — solo en registro */}
            {mode === 'register' && (
              <>
                <label>Nombre de usuario</label>
                <input
                  className="form-input"
                  placeholder="Tu nombre de usuario"
                  value={username}
                  onChange={e => { setUsername(e.target.value); clearFieldError('username') }}
                  onBlur={() => handleBlur('username')}
                  autoComplete="username"
                />
                {fieldErrors.username && <span className="form-error">⚠️ {fieldErrors.username}</span>}
              </>
            )}

            <label>Contraseña</label>
            <div className="input-password-wrap">
              <input
                className="form-input"
                type={showPass ? 'text' : 'password'}
                placeholder="Mínimo 8 caracteres"
                value={password}
                onChange={e => { setPassword(e.target.value); clearFieldError('password') }}
                onKeyDown={e => e.key === 'Enter' && mode === 'login' && handleSubmit()}
                onBlur={() => handleBlur('password')}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              />
              <button className="toggle-pass" onClick={() => setShowPass(!showPass)} tabIndex={-1}>
                {showPass ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
            {fieldErrors.password && <span className="form-error">⚠️ {fieldErrors.password}</span>}

            {mode === 'register' && (
              <>
                <label>Confirmá tu contraseña</label>
                <div className="input-password-wrap">
                  <input
                    className="form-input"
                    type={showPass ? 'text' : 'password'}
                    placeholder="Repetí la contraseña"
                    value={confirm}
                    onChange={e => { setConfirm(e.target.value); clearFieldError('confirm') }}
                    onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                    onBlur={() => handleBlur('confirm')}
                    autoComplete="new-password"
                  />
                  {confirm && (
                    <span className="pass-match">{confirm === password ? '✅' : '❌'}</span>
                  )}
                </div>
                {fieldErrors.confirm && <span className="form-error">⚠️ {fieldErrors.confirm}</span>}

                {/* Checklist de requisitos — cada uno se tilda a medida que se cumple */}
                {password && (
                  <ul className="pass-requirements">
                    <li className={checks.length ? 'req-ok' : ''}>Mínimo 8 caracteres</li>
                    <li className={checks.upper ? 'req-ok' : ''}>Al menos una mayúscula</li>
                    <li className={checks.number ? 'req-ok' : ''}>Al menos un número</li>
                    <li className={checks.special ? 'req-ok' : ''}>Al menos un carácter especial</li>
                  </ul>
                )}
              </>
            )}

            {generalError && <div className="form-error">⚠️ {generalError}</div>}

            <button
              className="btn-primary btn-full"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? '⏳ Un momento...' : mode === 'login' ? '→ Ingresar' : '✨ Crear cuenta'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}