import { useState, useEffect } from 'react'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import './App.css'

export default function App() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  )

  const handleLogin = (access: string, refresh: string) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    setToken(access)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)
  }

if (!token) {
  return <Login onLogin={handleLogin} />
}

return <Dashboard onLogout={handleLogout} />
}
