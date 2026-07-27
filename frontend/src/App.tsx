import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Landing from './pages/Landing'
import Onboarding from './pages/Onboarding'
import { apiLogout } from './services/api'
import './App.css'

type Screen = 'landing' | 'login' | 'onboarding' | 'dashboard'

export default function App() {
  const [screen, setScreen] = useState<Screen>(() => {
    // Sin token: primero la landing pública. Con token: directo al dashboard
    // (el onboarding solo se muestra inmediatamente después de registrarse).
    if (!localStorage.getItem('access_token')) return 'landing'
    if (localStorage.getItem('onboarding_pending') === 'true') return 'onboarding'
    return 'dashboard'
  })
  const [onboardingToken, setOnboardingToken] = useState<string | null>(null)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')

  const handleLogin = (access: string, refresh: string) => {
    localStorage.removeItem('chat_recientes')
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    setScreen('dashboard')
  }
  const handleRegisterSuccess = (access: string, refresh: string) => {
    localStorage.removeItem('chat_recientes')
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('onboarding_pending', 'true')
    setOnboardingToken(access)
    setScreen('onboarding')
  }

  const handleOnboardingComplete = () => {
    localStorage.removeItem('onboarding_pending')
    setOnboardingToken(null)
    setScreen('dashboard')
  }

  const handleLogout = () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      apiLogout(refreshToken).catch(() => {})  // best-effort, no bloquea el logout
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('chat_recientes')
    setOnboardingToken(null)
    setScreen('landing')
  }

  if (screen === 'dashboard') {
    return <Dashboard onLogout={handleLogout} />
  }

  if (screen === 'onboarding') {
    return (
      <Onboarding
        accessToken={onboardingToken || localStorage.getItem('access_token') || ''}
        onComplete={handleOnboardingComplete}
      />
    )
  }

  if (screen === 'login') {
    return (
      <Login
        initialMode={authMode}
        onLogin={handleLogin}
        onRegisterSuccess={handleRegisterSuccess}
        onBackToLanding={() => setScreen('landing')}
      />
    )
  }

  return (
    <Landing
      onIniciarSesion={() => { setAuthMode('login'); setScreen('login') }}
      onRegistrarse={() => { setAuthMode('register'); setScreen('login') }}
    />
  )
}
