import { useState } from 'react'
import { apiLogin, apiRegister, parseFieldErrors, apiUpdateStudentProfile } from '../services/api'
import avatarFem from '../assets/avatar-femenino.svg'
import avatarMasc from '../assets/avatar-masculino.svg'
import avatarNoDecir from '../assets/avatar-prefiero-no-decir.svg'

interface Props {
  onLogin: (access: string, refresh: string) => void
}

// ── Tipos ──────────────────────────────────────────────────────────────────────
type Field = 'email' | 'username' | 'password' | 'confirm' | 'fechaNacimiento' | 'genero' | 'terminos'
type FieldErrors = Partial<Record<Field, string>>
type Genero = 'F' | 'M' | 'ND'

function getPasswordChecks(pass: string) {
  return {
    number: /[0-9]/.test(pass),
    upper: /[A-Z]/.test(pass),
    lower: /[a-z]/.test(pass),
    special: /[^A-Za-z0-9]/.test(pass),
    length: pass.length >= 8,
  }
}

// Calcula la edad exacta a partir de una fecha en formato YYYY-MM-DD (el que da <input type="date">)
function calcularEdad(fechaISO: string): number {
  const hoy = new Date()
  const nacimiento = new Date(fechaISO)
  let edad = hoy.getFullYear() - nacimiento.getFullYear()
  const aunNoCumplio =
    hoy.getMonth() < nacimiento.getMonth() ||
    (hoy.getMonth() === nacimiento.getMonth() && hoy.getDate() < nacimiento.getDate())
  if (aunNoCumplio) edad--
  return edad
}

// ── Íconos (SVG inline, sin librerías externas) ─────────────────────────────────
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

function MailIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 6-10 7L2 6" />
    </svg>
  )
}

function LockIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  )
}

function UserIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 4-7 8-7s8 3 8 7" />
    </svg>
  )
}

function CalendarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  )
}

function UserPlusIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="8" r="4" />
      <path d="M2 21c0-4 3.5-7 7-7s7 3 7 7" />
      <line x1="19" y1="8" x2="19" y2="14" />
      <line x1="16" y1="11" x2="22" y2="11" />
    </svg>
  )
}

function RocketIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
      <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
      <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
      <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function GoogleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.69-2.26 1.1-3.71 1.1-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.14c-.22-.69-.35-1.42-.35-2.14s.13-1.45.35-2.14V7.02H2.18A10.93 10.93 0 0 0 1 12c0 1.77.43 3.45 1.18 4.98l3.66-2.84z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.02l3.66 2.84c.87-2.6 3.3-4.48 6.16-4.48z" />
    </svg>
  )
}

// ── Header compartido (login + registro) ───────────────────────────────────────
function AuthHeader({ mode, switchMode }: { mode: 'login' | 'register'; switchMode: (m: 'login' | 'register') => void }) {
  return (
    <header className="auth-header">
      <div className="auth-header-logo">
        <div className="auth-header-logo-icon">
          <UserPlusIcon />
        </div>
        <span>Impulsa</span>
      </div>
      <nav className="auth-header-nav">
        <a href="#" className="auth-header-link">Acerca de Impulsa</a>
        <button
          className={`auth-header-btn ${mode === 'login' ? 'auth-header-btn--active' : ''}`}
          onClick={() => switchMode('login')}
        >
          Iniciar Sesión
        </button>
        <button
          className={`auth-header-btn ${mode === 'register' ? 'auth-header-btn--secondary-active' : 'auth-header-btn--secondary'}`}
          onClick={() => switchMode('register')}
        >
          Registrarse
        </button>
      </nav>
    </header>
  )
}

// ── Tarjeta de selección de género ──────────────────────────────────────────────
function GeneroCard({ active, label, avatar, onClick }: { active: boolean; label: string; avatar: string; onClick: () => void }) {
  return (
    <button
      type="button"
      className={`genero-card ${active ? 'genero-card--active' : ''}`}
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
    >
      <img src={avatar} alt="" className="genero-card-avatar" />
      <span className="genero-card-label">{label}</span>
    </button>
  )
}

export default function Login({ onLogin }: Props) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [fechaNacimiento, setFechaNacimiento] = useState('')
  const [genero, setGenero] = useState<Genero | ''>('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [aceptaTerminos, setAceptaTerminos] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [generalError, setGeneralError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [forgotClicked, setForgotClicked] = useState(false)

  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'pulso'

  // ── Validación de login ────────────────────────────────────────────────────
  const validateLogin = (): FieldErrors => {
    const errors: FieldErrors = {}
    if (!email.trim()) errors.email = 'El email es obligatorio.'
    else if (/\s/.test(email)) errors.email = 'El email no puede contener espacios.'
    else if (!/^\S+@\S+\.\S+$/.test(email)) errors.email = 'El email no es válido.'
    if (!password) errors.password = 'La contraseña es obligatoria.'
    return errors
  }

  // ── Validación de registro, campo por campo ────────────────────────────────
  const validateField = (field: Field): string | undefined => {
    switch (field) {
      case 'username':
        if (!username.trim()) return 'El nombre de usuario es obligatorio.'
        if (/\s/.test(username)) return 'El nombre de usuario no puede contener espacios.'
        if (username.trim().length < 3) return 'Debe tener al menos 3 caracteres.'
        if (!/^[A-Za-z0-9_]+$/.test(username)) return 'Solo letras, números y guion bajo.'
        return undefined

      case 'fechaNacimiento':
        if (!fechaNacimiento) return 'La fecha de nacimiento es obligatoria.'
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

  const validateAllRegister = (): FieldErrors => {
    const fields: Field[] = ['username', 'fechaNacimiento', 'email', 'genero', 'password', 'confirm', 'terminos']
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

  const clearFieldError = (field: Field) => {
    if (fieldErrors[field]) setFieldErrors(prev => ({ ...prev, [field]: undefined }))
  }

  // ── Submit de login ─────────────────────────────────────────────────────────
  const handleLoginSubmit = async () => {
    setGeneralError('')
    const errors = validateLogin()
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }
    setFieldErrors({})
    setLoading(true)
    try {
      const res = await apiLogin(email, password)
      if (res.ok && res.data.access) {
        onLogin(res.data.access, res.data.refresh)
        return
      }
      const backendErrors = parseFieldErrors(res.data)
      if (Object.keys(backendErrors).length > 0) {
        setFieldErrors(backendErrors as FieldErrors)
      } else {
        setGeneralError(res.data.detail || res.data.message || 'Email o contraseña incorrectos.')
      }
    } catch {
      setGeneralError('No se pudo conectar al servidor.')
    }
    setLoading(false)
  }

  // ── Submit de registro (flujo de 2 pasos: register + PATCH de perfil) ──────
  const handleRegisterSubmit = async () => {
    setGeneralError('')
    const errors = validateAllRegister()
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }
    setFieldErrors({})
    setLoading(true)
    try {
      const res = await apiRegister(username, email, password, confirm)
      if (res.ok && res.data.access) {
        try {
          await apiUpdateStudentProfile(res.data.access, {
            fecha_nacimiento: fechaNacimiento,
            genero,
          })
        } catch {
          // Si falla este segundo paso, no bloqueamos el acceso: la cuenta
          // ya se creó bien. La persona puede completar fecha/género después
          // desde su perfil. Solo lo dejamos registrado en consola.
          console.warn('No se pudo guardar fecha de nacimiento/género; la cuenta se creó igual.')
        }
        onLogin(res.data.access, res.data.refresh)
        return
      }
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
    <div className="auth-page">
      <AuthHeader mode={mode} switchMode={switchMode} />

      <div className="auth-card-wrapper">
        <div className="auth-card">
          {mode === 'login' ? (
            <>
              <h2 className="auth-title">Inicia Sesión</h2>
              <p className="auth-subtitle">Impulsa tu nuevo camino con la ayuda de {mentorName}</p>

              <div className="auth-form">
                <label>Correo Electrónico</label>
                <div className="auth-input-wrap">
                  <span className="auth-input-icon"><MailIcon /></span>
                  <input
                    className={`auth-input auth-input--with-toggle ${fieldErrors.password ? 'auth-input--error' : ''}`}
                    type="email"
                    placeholder="tucorreoelectrónico@gmail.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleLoginSubmit()}
                  />
                </div>
                {fieldErrors.email && <span className="form-error">⚠️ {fieldErrors.email}</span>}

                <label>Contraseña</label>
                <div className="auth-input-wrap">
                  <span className="auth-input-icon"><LockIcon /></span>
                  <input
                    className={`auth-input ${fieldErrors.password ? 'auth-input--error' : ''}`}
                    type={showPass ? 'text' : 'password'}
                    placeholder="Ingrese su contraseña..."
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleLoginSubmit()}
                  />
                  <button className="auth-input-toggle" onClick={() => setShowPass(!showPass)} tabIndex={-1}>
                    {showPass ? <EyeOffIcon /> : <EyeIcon />}
                  </button>
                </div>
                {fieldErrors.password && <span className="form-error">⚠️ {fieldErrors.password}</span>}

                <button type="button" className="auth-forgot-link" onClick={() => setForgotClicked(true)}>
                  ¿Olvidaste tu contraseña?
                </button>
                {forgotClicked && (
                  <span className="auth-forgot-note">Esta función va a estar disponible próximamente.</span>
                )}

                {generalError && <div className="form-error">⚠️ {generalError}</div>}

                <button className="btn-primary btn-full auth-submit-btn" onClick={handleLoginSubmit} disabled={loading}>
                  <RocketIcon /> {loading ? 'Un momento...' : 'Iniciar sesión'}
                </button>

                <div className="auth-divider">O INICIA CON GOOGLE</div>
                <button className="auth-google-btn" type="button">
                  <GoogleIcon /> Google
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="auth-icon-circle"><UserPlusIcon /></div>
              <h2 className="auth-title">Crea tu cuenta</h2>
              <p className="auth-subtitle">Únete a la plataforma líder en mentoría virtual y potencia tu carrera</p>

              <div className="auth-form">
                <label className={fieldErrors.username ? 'auth-label--error' : ''}>Ingresa un nombre de usuario</label>
                <div className="auth-input-wrap">
                  <span className="auth-input-icon"><UserIcon /></span>
                  <input
                    className={`auth-input auth-input--with-toggle ${fieldErrors.confirm ? 'auth-input--error' : ''}`}
                    placeholder="Juan01"
                    value={username}
                    onChange={e => { setUsername(e.target.value); clearFieldError('username') }}
                    onBlur={() => handleBlur('username')}
                  />
                </div>
                {fieldErrors.username && <span className="form-error">⚠️ {fieldErrors.username}</span>}

                <div className="auth-row">
                  <div className="auth-col">
                    <label>Fecha de nacimiento</label>
                    <div className="auth-input-wrap">
                      <span className="auth-input-icon"><CalendarIcon /></span>
                      <input
                        className={`auth-input ${fieldErrors.fechaNacimiento ? 'auth-input--error' : ''}`}
                        type="date"
                        value={fechaNacimiento}
                        onChange={e => { setFechaNacimiento(e.target.value); clearFieldError('fechaNacimiento') }}
                        onBlur={() => handleBlur('fechaNacimiento')}
                      />
                    </div>
                    {fieldErrors.fechaNacimiento && <span className="form-error">⚠️ {fieldErrors.fechaNacimiento}</span>}
                  </div>

                  <div className="auth-col">
                    <label className={fieldErrors.email ? 'auth-label--error' : ''}>Correo Electrónico</label>
                    <div className="auth-input-wrap">
                      <span className="auth-input-icon"><MailIcon /></span>
                      <input
                        className={`auth-input ${fieldErrors.email ? 'auth-input--error' : ''}`}
                        type="email"
                        placeholder="tucorreoelectrónico@gmail.com"
                        value={email}
                        onChange={e => { setEmail(e.target.value); clearFieldError('email') }}
                        onBlur={() => handleBlur('email')}
                      />
                    </div>
                    {fieldErrors.email && <span className="form-error">⚠️ {fieldErrors.email}</span>}
                  </div>
                </div>

                <label className="auth-genero-label">Indique su género</label>
                <div className="genero-group">
                  <GeneroCard active={genero === 'F'} label="Femenino" avatar={avatarFem} onClick={() => { setGenero('F'); clearFieldError('genero') }} />
                  <GeneroCard active={genero === 'M'} label="Masculino" avatar={avatarMasc} onClick={() => { setGenero('M'); clearFieldError('genero') }} />
                  <GeneroCard active={genero === 'ND'} label="Prefiero no decir" avatar={avatarNoDecir} onClick={() => { setGenero('ND'); clearFieldError('genero') }} />
                </div>
                {fieldErrors.genero && <span className="form-error">⚠️ {fieldErrors.genero}</span>}

                <div className="auth-row">
                  <div className="auth-col">
                    <label>Contraseña</label>
                    <div className="auth-input-wrap">
                      <span className="auth-input-icon"><LockIcon /></span>
                      <input
                        className={`auth-input auth-input--with-toggle ${fieldErrors.password ? 'auth-input--error' : ''}`} type={showPass ? 'text' : 'password'}
                        placeholder="Ingrese su contraseña..."
                        value={password}
                        onChange={e => { setPassword(e.target.value); clearFieldError('password') }}
                        onBlur={() => handleBlur('password')}
                      />
                      <button className="auth-input-toggle" onClick={() => setShowPass(!showPass)} tabIndex={-1}>
                        {showPass ? <EyeOffIcon /> : <EyeIcon />}
                      </button>
                    </div>
                    {fieldErrors.password && <span className="form-error">⚠️ {fieldErrors.password}</span>}
                  </div>

                  <div className="auth-col">
                    <label>Confirma tu contraseña</label>
                    <div className="auth-input-wrap">
                      <span className="auth-input-icon"><LockIcon /></span>
                      <input
                        className={`auth-input ${fieldErrors.confirm ? 'auth-input--error' : ''}`}
                        type={showConfirm ? 'text' : 'password'}
                        placeholder="Ingrese su contraseña..."
                        value={confirm}
                        onChange={e => { setConfirm(e.target.value); clearFieldError('confirm') }}
                        onBlur={() => handleBlur('confirm')}
                      />
                      <button className="auth-input-toggle" onClick={() => setShowConfirm(!showConfirm)} tabIndex={-1}>
                        {showConfirm ? <EyeOffIcon /> : <EyeIcon />}
                      </button>
                    </div>
                    {fieldErrors.confirm && <span className="form-error">⚠️ {fieldErrors.confirm}</span>}
                  </div>
                </div>

                {password && (
                  <ul className="pass-requirements-figma">
                    <li className={checks.number ? 'req-ok' : ''}><CheckIcon /> Tiene un número</li>
                    <li className={checks.upper ? 'req-ok' : ''}><CheckIcon /> Cuenta con al menos una letra mayúscula</li>
                    <li className={checks.lower ? 'req-ok' : ''}><CheckIcon /> Cuenta con al menos una letra minúscula</li>
                    <li className={checks.special ? 'req-ok' : ''}><CheckIcon /> Tiene un carácter especial (+,-,*,$,...)</li>
                    <li className={checks.length ? 'req-ok' : ''}><CheckIcon /> Tiene 8 o más dígitos</li>
                  </ul>
                )}

                <label className="auth-checkbox-row">
                  <input
                    type="checkbox"
                    checked={aceptaTerminos}
                    onChange={e => { setAceptaTerminos(e.target.checked); clearFieldError('terminos') }}
                  />
                  <span>
                    Al registrarte, aceptas nuestros <a href="#"><strong>Términos de Servicio</strong></a> y la <a href="#"><strong>Política de Privacidad</strong></a>.
                  </span>
                </label>
                {fieldErrors.terminos && <span className="form-error">⚠️ {fieldErrors.terminos}</span>}

                {generalError && <div className="form-error">⚠️ {generalError}</div>}

                <button className="btn-primary btn-full auth-submit-btn" onClick={handleRegisterSubmit} disabled={loading}>
                  <RocketIcon /> {loading ? 'Un momento...' : 'Crear mi cuenta!'}
                </button>

                <div className="auth-divider">O REGÍSTRATE CON</div>
                <button className="auth-google-btn" type="button">
                  <GoogleIcon /> Google
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}