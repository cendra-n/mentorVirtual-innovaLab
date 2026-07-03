import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import MentorChat from '../components/MentorChat'
import GoalCard from '../components/GoalCard'
import WeekStreak from '../components/WeekStreak'
import NewGoalModal from '../components/NewGoalModal'
import MentorBot from '../components/MentorBot'
import GoalDetail from './GoalDetail'
import AdminPanel from './AdminPanel'
import Profile from './Profile'
import TutorPage from './TutorPage'
import ChatPage from './ChatPage'
import {
  apiMe, apiGetGoals, apiCreateGoal, apiStreak, apiDeleteGoal
} from '../services/api'

interface Props { onLogout: () => void }

export default function Dashboard({ onLogout }: Props) {
  const [activePage, setActivePage] = useState('inicio')
  const [user, setUser] = useState<any>(null)
  const [goals, setGoals] = useState<any[]>([])
  const [streak, setStreak] = useState<any>({ current_streak: 0, longest_streak: 0 })
  const [showModal, setShowModal] = useState(false)
  const [goalLoading, setGoalLoading] = useState(false)
  const [selectedGoal, setSelectedGoal] = useState<number | null>(null)
  const [showAdmin, setShowAdmin] = useState(false)

  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  const loadData = async () => {
    apiMe().then(setUser)
    apiGetGoals().then(d => setGoals(d.goals || []))
    apiStreak().then(setStreak)
  }

  useEffect(() => { loadData() }, [])

  const handleCreateGoal = async (text: string) => {
    setGoalLoading(true)
    try {
      const res = await apiCreateGoal(text)
      if (res.goal) {
        await loadData()
        setShowModal(false)
        setSelectedGoal(res.goal.id)
      }
    } catch {
    }
    setGoalLoading(false)
  }

  const handleDeleteGoal = async (id: number) => {
    await apiDeleteGoal(id)
    await loadData()
  }

  const userRole = user?.role || 'STUDENT'
  const canDelete = userRole === 'ADMIN' || userRole === 'PROFESSOR' || user?.is_staff

  const displayName = user?.first_name || user?.username || 'Brenda'

  // Vista admin
  if (showAdmin) {
    return (
      <div className={`dashboard ${activePage === 'chat' ? 'dashboard--chat-full' : ''}`}>
        <Sidebar
          active="admin"
          onNav={(p) => { setShowAdmin(false); setActivePage(p) }}
          user={user}
          streak={streak.current_streak}
          onLogout={onLogout}
          onAdmin={() => setShowAdmin(true)}
        />
        <AdminPanel onBack={() => setShowAdmin(false)} />
        <div className="dashboard-right">
          <WeekStreak currentStreak={streak.current_streak} longestStreak={streak.longest_streak} lastActivity={streak.last_activity} />
          <MentorChat />
        </div>
      </div>
    )
  }

  // Vista de detalle
  if (selectedGoal) {
    return (
      <div className="dashboard">
        <Sidebar
          active={activePage}
          onNav={(p) => { setActivePage(p); setSelectedGoal(null) }}
          user={user}
          streak={streak.current_streak}
          onLogout={onLogout}
          onAdmin={() => setShowAdmin(true)}
        />
        <GoalDetail
          goalId={selectedGoal}
          onBack={() => setSelectedGoal(null)}
        />
        <div className="dashboard-right">
          <WeekStreak
            currentStreak={streak.current_streak}
            longestStreak={streak.longest_streak}
            lastActivity={streak.last_activity}
          />
          <MentorChat />
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <Sidebar
        active={activePage}
        onNav={setActivePage}
        user={user}
        streak={streak.current_streak}
        onLogout={onLogout}
        onAdmin={() => setShowAdmin(true)}
      />

      <main className="dashboard-main">
        {activePage === 'perfil' && <Profile user={user} />}
        {activePage === 'lecciones' && <TutorPage />}
        {activePage === 'chat' && <ChatPage />}
        {activePage !== 'perfil' && activePage !== 'lecciones' && activePage !== 'chat' && <>
          <header className="dash-header">
            <div>
              <h1 className="dash-greeting">¡Hola {displayName}! 👋</h1>
              <p className="dash-sub">¿Qué te gustaría aprender hoy?</p>
            </div>
            <div className="dash-header-right">
              <button className="icon-btn">🔔</button>
              <div className="avatar-circle">{displayName.charAt(0).toUpperCase()}</div>
            </div>
          </header>

          <div className="hero-banner">
            <div className="hero-text">
              <h2>Sigue aprendiendo a tu ritmo</h2>
              <p>¿Listo para tu sesión de hoy?<br />
                Explorá los temas del día y avanzá cuando y donde quieras.</p>
              <button className="btn-primary hero-btn" onClick={() => setShowModal(true)}>
                🤖 Nueva meta de aprendizaje
              </button>
            </div>
            <MentorBot mood="emocionado" size={120} className="hero-bot" />
          </div>

          {goals.length > 0 && (
            <section className="dash-section">
              <div className="section-head">
                <h3>Continuá donde lo dejaste</h3>
                <button className="link-btn">Ver más →</button>
              </div>
              <div className="goals-list">
                {goals.slice(0, 3).map(g => (
                  <GoalCard
                    key={g.id}
                    goal={g}
                    onClick={setSelectedGoal}
                    onDelete={handleDeleteGoal}
                    canDelete={canDelete}
                  />
                ))}
              </div>
            </section>
          )}

          {goals.length === 0 && (
            <div className="empty-state">
              <MentorBot mood="ayudando" size={80} />
              <h3>¡Empezá tu primer plan!</h3>
              <p>Contame qué querés aprender y {mentorName} te arma un camino personalizado.</p>
              <button className="btn-primary" onClick={() => setShowModal(true)}>
                ✨ Crear mi primer plan
              </button>
            </div>
          )}
        </>}</main>

      {activePage !== 'chat' && (
        <div className="dashboard-right">
          <WeekStreak
            currentStreak={streak.current_streak}
            longestStreak={streak.longest_streak}
            lastActivity={streak.last_activity}
          />
          <MentorChat />
        </div>
      )}

      {showModal && (
        <NewGoalModal
          onSubmit={handleCreateGoal}
          onClose={() => !goalLoading && setShowModal(false)}
          loading={goalLoading}
        />
      )}
    </div>
  )
}
