import { useState } from 'react'
import { useLoginForm } from '../../hooks/useLoginForm'
import { EyeIcon, EyeOffIcon, MailIcon, LockIcon, RocketIcon, GoogleIcon } from './AuthIcons'

interface Props {
  onLogin: (access: string, refresh: string) => void
  mentorName: string
}

export default function LoginForm({ onLogin, mentorName }: Props) {
  const {
    email, setEmail,
    password, setPassword,
    fieldErrors,
    generalError,
    loading,
    isSubmitDisabled,
    handleSubmit,
  } = useLoginForm(onLogin)

  const [showPass, setShowPass] = useState(false)
  const [forgotClicked, setForgotClicked] = useState(false)
  const [googleClicked, setGoogleClicked] = useState(false)

  return (
    <>
      <h2 className="auth-title">Inicia Sesión</h2>
      <p className="auth-subtitle">Impulsa tu nuevo camino con la ayuda de {mentorName}</p>

      <form
        className="auth-form"
        onSubmit={e => { e.preventDefault(); handleSubmit() }}
      >
        <label>Correo Electrónico</label>
        <div className="auth-input-wrap">
          <span className="auth-input-icon"><MailIcon /></span>
          <input
            className={`auth-input auth-input--with-toggle ${fieldErrors.password ? 'auth-input--error' : ''}`}
            type="email"
            placeholder="tucorreoelectrónico@gmail.com"
            value={email}
            onChange={e => setEmail(e.target.value)}
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
          />
          <button type="button" className="auth-input-toggle" onClick={() => setShowPass(!showPass)} tabIndex={-1}>
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

        {/* BUG-FE-008: type="submit" dentro de un <form> real con onSubmit
            hace que Enter funcione sin importar si los campos se llenaron
            tipeando o por autocompletado del navegador/gestor de contraseñas. */}
        {/* BUG-FE-006: el botón permanece deshabilitado hasta que Email y
            Contraseña contengan datos válidos. */}
        <button type="submit" className="btn-primary btn-full auth-submit-btn" disabled={isSubmitDisabled}>
          <RocketIcon /> {loading ? 'Un momento...' : 'Iniciar sesión'}
        </button>

        <div className="auth-divider">O INICIA CON GOOGLE</div>
        <button className="auth-google-btn" type="button" onClick={() => setGoogleClicked(true)}>
          <GoogleIcon /> Google
        </button>
        {googleClicked && (
          <span className="auth-forgot-note">Próximamente disponible.</span>
        )}
      </form>
    </>
  )
}