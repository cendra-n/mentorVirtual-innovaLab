import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import './App.css'

type Screen = 'login' | 'onboarding' | 'dashboard'

export default function App() {
  const [screen, setScreen] = useState<Screen>(() => {
    // Si ya hay token guardado, va directo al dashboard
    // (el onboarding solo se muestra inmediatamente después de registrarse)
    if (!localStorage.getItem('access_token')) return 'login'
    if (localStorage.getItem('onboarding_pending') === 'true') return 'onboarding'
    return 'dashboard'
  })
  const [onboardingToken, setOnboardingToken] = useState<string | null>(null)

  const handleLogin = (access: string, refresh: string) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    setScreen('dashboard')
  }
  const handleRegisterSuccess = (access: string, refresh: string) => {
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
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setOnboardingToken(null)
    setScreen('login')
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

  return (
    <Login
      onLogin={handleLogin}
      onRegisterSuccess={handleRegisterSuccess}
    />
  )
}