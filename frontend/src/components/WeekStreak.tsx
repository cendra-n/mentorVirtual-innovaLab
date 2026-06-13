interface Props {
  currentStreak: number
  longestStreak: number
  lastActivity: string | null
}

const DAYS = ['L', 'M', 'M', 'J', 'V']

export default function WeekStreak({ currentStreak, longestStreak, lastActivity }: Props) {
  // Marcamos los días activos de esta semana (simplificado)
  const today = new Date().getDay() // 0=dom, 1=lun...
  const todayIdx = today === 0 ? 4 : Math.min(today - 1, 4)
  const active = DAYS.map((_, i) => i <= todayIdx && currentStreak > (todayIdx - i))

  return (
    <div className="week-streak">
      <div className="week-streak-title">ESTA SEMANA</div>
      <div className="week-days">
        {DAYS.map((d, i) => (
          <div key={i} className="week-day">
            <span className="week-day-label">{d}</span>
            <div className={`week-day-box ${active[i] ? 'week-day-box--done' : ''}`}>
              {active[i] && <span>✓</span>}
            </div>
          </div>
        ))}
      </div>
      <p className="week-streak-msg">
        {currentStreak > 0
          ? `¡Llevas ${currentStreak} días! ¡Cada paso te acerca más a tu meta!`
          : '¡Empezá hoy tu racha!'}
      </p>
    </div>
  )
}
