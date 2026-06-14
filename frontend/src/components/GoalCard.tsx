interface Goal {
  id: number
  goal_text: string
  status: string
  total_steps: number
  completed_steps: number
}

interface Props {
  goal: Goal
  onClick: (id: number) => void
  onDelete?: (id: number) => void
  canDelete?: boolean
}

export default function GoalCard({ goal, onClick, onDelete, canDelete }: Props) {
  const pct = goal.total_steps > 0
    ? Math.round((goal.completed_steps / goal.total_steps) * 100)
    : 0

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm(`¿Eliminar "${goal.goal_text}"?`)) {
      onDelete?.(goal.id)
    }
  }

  return (
    <div className="goal-card" onClick={() => onClick(goal.id)}>
      <div className="goal-card-thumb">
        <span className="goal-emoji">🎯</span>
      </div>
      <div className="goal-card-body">
        <span className={`goal-badge goal-badge--${goal.status}`}>
          {goal.status === 'active' ? 'En progreso' : goal.status}
        </span>
        <h3 className="goal-title">{goal.goal_text}</h3>
        <div className="goal-progress-bar">
          <div className="goal-progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <p className="goal-steps">{goal.completed_steps} / {goal.total_steps} pasos</p>
      </div>
      <div className="goal-card-actions">
        <button className="goal-continue-btn">Continuar</button>
        {canDelete && (
          <button className="goal-delete-btn" onClick={handleDelete} title="Eliminar meta">
            🗑️
          </button>
        )}
      </div>
    </div>
  )
}
