import { useState } from 'react'
import MentorBot from '../components/MentorBot'
import { apiLogin, apiRegister } from '../services/api'

interface Props {
  onLogin: (access: string, refresh: string) => void
}

export default function Login({ onLogin }: Props) {
  const [mode, setMode]         = useState<'login' | 'register'>('login')
  const [email, setEmail]       = useState('')
  const [username, setUsername] = useState('')  // solo para registro
  const [password, setPassword] = useState('')
  const [confirm, setConfirm]   = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [showPass, setShowPass] = useState(false)

  const appName    = import.meta.env.VITE_APP_NAME    || 'Mentor Virtual'
  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  const validate = () => {
    if (!email.trim())                    return 'El email es obligatorio.'
    if (!/\S+@\S+\.\S+/.test(email))     return 'El email no es válido.'
    if (password.length < 8)             return 'La contraseña debe tener al menos 8 caracteres.'
    if (mode === 'register') {
      if (!username.trim())              return 'El nombre de usuario es obligatorio.'
      if (password !== confirm)          return 'Las contraseñas no coinciden.'
    }
    return null
  }

  const handleSubmit = async () => {
    setError('')
    const err = validate()
    if (err) { setError(err); return }

    setLoading(true)
    try {
      const res = mode === 'login'
        ? await apiLogin(email, password)
        : await apiRegister(username, email, password)

      if (res.access) {
        onLogin(res.access, res.refresh)
      } else {
        setError(res.error || res.detail || 'Ocurrió un error, intentá de nuevo.')
      }
    } catch {
      setError('No se pudo conectar al servidor.')
    }
    setLoading(false)
  }

  const switchMode = (m: 'login' | 'register') => {
    setMode(m)
    setError('')
    setPassword('')
    setConfirm('')
  }

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
              onChange={e => setEmail(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && mode === 'login' && handleSubmit()}
              autoComplete="email"
            />

            {/* Username — solo en registro */}
            {mode === 'register' && (
              <>
                <label>Nombre de usuario</label>
                <input
                  className="form-input"
                  placeholder="Tu nombre de usuario"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  autoComplete="username"
                />
              </>
            )}

            <label>Contraseña</label>
            <div className="input-password-wrap">
              <input
                className="form-input"
                type={showPass ? 'text' : 'password'}
                placeholder="Mínimo 8 caracteres"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && mode === 'login' && handleSubmit()}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              />
              <button className="toggle-pass" onClick={() => setShowPass(!showPass)} tabIndex={-1}>
                {showPass ? '🙈' : '👁️'}
              </button>
            </div>

            {mode === 'register' && (
              <>
                <label>Confirmá tu contraseña</label>
                <div className="input-password-wrap">
                  <input
                    className="form-input"
                    type={showPass ? 'text' : 'password'}
                    placeholder="Repetí la contraseña"
                    value={confirm}
                    onChange={e => setConfirm(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                    autoComplete="new-password"
                  />
                  {confirm && (
                    <span className="pass-match">{confirm === password ? '✅' : '❌'}</span>
                  )}
                </div>

                {/* Indicador de fuerza */}
                {password && (
                  <div className="pass-strength">
                    <div className="pass-strength-bar">
                      {[1,2,3,4].map(i => (
                        <div key={i} className={`pass-strength-seg ${getStrength(password) >= i ? `strength-${getStrength(password)}` : ''}`} />
                      ))}
                    </div>
                    <span className="pass-strength-label">{getStrengthLabel(password)}</span>
                  </div>
                )}
              </>
            )}

            {error && <div className="form-error">⚠️ {error}</div>}

            <button
              className="btn-primary btn-full"
              onClick={handleSubmit}
              disabled={loading || !email || !password || (mode === 'register' && !confirm)}
            >
              {loading ? '⏳ Un momento...' : mode === 'login' ? '→ Ingresar' : '✨ Crear cuenta'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function getStrength(pass: string): number {
  let s = 0
  if (pass.length >= 8) s++
  if (/[A-Z]/.test(pass)) s++
  if (/[0-9]/.test(pass)) s++
  if (/[^A-Za-z0-9]/.test(pass)) s++
  return s
}

function getStrengthLabel(pass: string): string {
  return ['', 'Débil', 'Regular', 'Buena', 'Fuerte'][getStrength(pass)]
}
