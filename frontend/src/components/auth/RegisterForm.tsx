import { useState } from 'react'
import { useRegisterForm } from '../../hooks/useRegisterForm'
import { getPasswordChecks } from '../../utils/authValidation'
import GeneroCard from './GeneroCard'
import { UserIcon, CalendarIcon, MailIcon, LockIcon, RocketIcon, GoogleIcon, EyeIcon, EyeOffIcon, CheckIcon, UserPlusIcon } from './AuthIcons'
import avatarFem from '../../assets/avatar-femenino.svg'
import avatarMasc from '../../assets/avatar-masculino.svg'
import avatarNoDecir from '../../assets/avatar-prefiero-no-decir.svg'

interface Props {
  onRegisterSuccess: (access: string, refresh: string) => void
}

export default function RegisterForm({ onRegisterSuccess }: Props) {
  const {
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
  } = useRegisterForm(onRegisterSuccess)

  const [showPass, setShowPass] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [googleClicked, setGoogleClicked] = useState(false)

  const checks = getPasswordChecks(password)

  return (
    <>
      <div className="auth-icon-circle"><UserPlusIcon /></div>
      <h2 className="auth-title">Crea tu cuenta</h2>
      <p className="auth-subtitle">Únete a la plataforma líder en mentoría virtual y potencia tu carrera</p>

      <div className="auth-form">
        <label className={fieldErrors.username ? 'auth-label--error' : ''}>Ingresa un nombre de usuario</label>
        <div className="auth-input-wrap">
          <span className="auth-input-icon"><UserIcon /></span>
          <input
            className={`auth-input auth-input--with-toggle ${fieldErrors.username ? 'auth-input--error' : ''}`}
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
                max={new Date(new Date().setFullYear(new Date().getFullYear() - 18)).toISOString().split('T')[0]}
                min="1900-01-01"
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
                className={`auth-input auth-input--with-toggle ${fieldErrors.password ? 'auth-input--error' : ''}`}
                type={showPass ? 'text' : 'password'}
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

        {/* El botón permanece deshabilitado hasta que todos los campos
            obligatorios tengan algún valor cargado, mismo criterio que
            en Login (BUG-FE-006), para prevenir envíos vacíos. */}
        <button className="btn-primary btn-full auth-submit-btn" onClick={handleSubmit} disabled={isSubmitDisabled}>
          <RocketIcon /> {loading ? 'Un momento...' : 'Crear mi cuenta!'}
        </button>

        <div className="auth-divider">O REGÍSTRATE CON</div>
        <button className="auth-google-btn" type="button" onClick={() => setGoogleClicked(true)}>
          <GoogleIcon /> Google
        </button>
        {googleClicked && (
          <span className="auth-forgot-note">Próximamente disponible.</span>
        )}
      </div>
    </>
  )
}