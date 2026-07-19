import { useState } from 'react'
import AuthHeader from '../components/auth/AuthHeader'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'
import About from '../components/auth/About'

interface Props {
  onLogin: (access: string, refresh: string) => void
  onRegisterSuccess: (access: string, refresh: string) => void
}

/**
 * Pantalla de Login/Registro. Toda la lógica y el JSX de cada modo viven en sus propios archivos (LoginForm, RegisterForm, y los hooks useLoginForm/useRegisterForm), 
 * para que se puedan editar por separado sin generar conflictos de merge entre sí.
 */
export default function Login({ onLogin, onRegisterSuccess }: Props) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [showAbout, setShowAbout] = useState(false)
  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'pulso'

  const switchMode = (m: 'login' | 'register') => setMode(m)

  if (showAbout) {
    return <About onBack={() => setShowAbout(false)} />
  }

  return (
    <div className="auth-page">
      <AuthHeader mode={mode} switchMode={switchMode} onAbout={() => setShowAbout(true)} />

      <div className="auth-card-wrapper">
        <div className="auth-card">
          {mode === 'login' ? (
            <LoginForm onLogin={onLogin} mentorName={mentorName} />
          ) : (
            <RegisterForm onRegisterSuccess={onRegisterSuccess} />
          )}
        </div>
      </div>
    </div>
  )
}