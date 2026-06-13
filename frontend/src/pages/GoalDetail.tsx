import { useState, useEffect } from 'react'
import MentorBot from '../components/MentorBot'
import TutorFloatingChat from '../components/TutorFloatingChat'
import { apiGetGoal, apiCompleteStep, apiVideoView } from '../services/api'

interface Props {
  goalId: number
  onBack: () => void
}

export default function GoalDetail({ goalId, onBack }: Props) {
  const [data, setData]         = useState<any>(null)
  const [loading, setLoading]   = useState(true)
  const [completing, setCompleting] = useState<number | null>(null)
  const [videoModal, setVideoModal] = useState<{ videoId: string; title: string } | null>(null)

  useEffect(() => {
    apiGetGoal(goalId).then(d => {
      setData(d)
      setLoading(false)
    })
  }, [goalId])

  const handleComplete = async (stepId: number) => {
    setCompleting(stepId)
    await apiCompleteStep(stepId, goalId)
    const d = await apiGetGoal(goalId)
    setData(d)
    setCompleting(null)
  }

  const handleVideoClick = async (videoDbId: number, stepId: number, youtubeVideoId: string, title: string) => {
    await apiVideoView(videoDbId, stepId)
    setVideoModal({ videoId: youtubeVideoId, title })
  }

  if (loading) return (
    <div className="detail-loading">
      <MentorBot mood="pensativo" size={64} />
      <p>Cargando tu plan...</p>
    </div>
  )

  const { goal, steps, logros } = data
  const completed = steps.filter((s: any) => s.completed).length
  const pct = steps.length > 0 ? Math.round((completed / steps.length) * 100) : 0

  return (
    <div className="goal-detail">

      {/* ── Modal YouTube ── */}
      {videoModal && (
        <div className="modal-overlay" onClick={() => setVideoModal(null)}>
          <div className="video-modal" onClick={e => e.stopPropagation()}>
            <div className="video-modal-header">
              <p className="video-modal-title">{videoModal.title}</p>
              <button className="close-btn" onClick={() => setVideoModal(null)}>✕</button>
            </div>
            <div className="video-modal-player">
              <iframe
                src={`https://www.youtube.com/embed/${videoModal.videoId}?autoplay=1`}
                title={videoModal.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="detail-header">
        <button className="back-btn" onClick={onBack}>← Volver</button>
        <div className="detail-title-row">
          <div>
            <h1 className="detail-title">{goal.goal_text}</h1>
            <p className="detail-sub">{completed} de {steps.length} pasos completados</p>
          </div>
          <MentorBot mood={pct === 100 ? 'emocionado' : pct > 50 ? 'guiñando' : 'ayudando'} size={64} />
        </div>
        <div className="detail-progress-bar">
          <div className="detail-progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <p className="detail-pct">{pct}% completado</p>
      </div>

      <div className="detail-body">
        {/* Pasos */}
        <div className="detail-steps">
          <h2 className="detail-section-title">Tu plan de aprendizaje</h2>
          {steps.map((step: any, i: number) => (
            <div key={step.id} className={`step-card ${step.completed ? 'step-card--done' : ''}`}>
              <div className="step-number">{step.completed ? '✓' : i + 1}</div>
              <div className="step-body">
                <h3 className="step-title">{step.title}</h3>
                <p className="step-desc">{step.description}</p>

                {/* Videos del paso */}
                {step.videos && step.videos.length > 0 && (
                  <div className="step-videos">
                    {step.videos.map((v: any) => (
                      <button
                        key={v.id}
                        className="video-card"
                        onClick={() => handleVideoClick(v.id, step.id, v.video_id, v.title)}
                      >
                        {v.thumbnail && (
                          <img src={v.thumbnail} alt={v.title} className="video-thumb" />
                        )}
                        <div className="video-info">
                          <div className="video-play">▶</div>
                          <div>
                            <p className="video-title">{v.title}</p>
                            <p className="video-channel">{v.channel}</p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {!step.completed && (
                  <button
                    className="btn-complete"
                    onClick={() => handleComplete(step.id)}
                    disabled={completing === step.id}
                  >
                    {completing === step.id ? 'Guardando...' : '✓ Marcar como completado'}
                  </button>
                )}

                {/* Robot tutor por paso */}
                <TutorFloatingChat
                  stepId={step.id}
                  stepTitle={step.title}
                  stepDescription={step.description || ''}
                  goalText={goal.goal_text}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Logros */}
        {logros && logros.length > 0 && (
          <div className="detail-logros">
            <h2 className="detail-section-title">Logros</h2>
            <div className="logros-grid">
              {logros.map((l: any) => (
                <div key={l.id} className={`logro-card ${l.unlocked ? 'logro-card--unlocked' : ''}`}>
                  <span className="logro-icon">{l.icon}</span>
                  <p className="logro-name">{l.name}</p>
                  <p className="logro-desc">{l.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
