import { useState } from 'react'
import MentorBot from './MentorBot'

interface Props {
  onSubmit: (text: string) => void
  onClose: () => void
  loading: boolean
}

export default function NewGoalModal({ onSubmit, onClose, loading }: Props) {
  const [text, setText] = useState('')
  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <MentorBot mood={loading ? 'pensativo' : 'ayudando'} size={56} />
          <div>
            <h2 className="modal-title">¿Qué querés aprender?</h2>
            <p className="modal-sub">
              Contame tu meta y {mentorName} te arma un plan personalizado
            </p>
          </div>
        </div>

        <textarea
          className="modal-textarea"
          placeholder="Ej: Quiero aprender a usar la computadora para buscar trabajo..."
          value={text}
          onChange={e => setText(e.target.value)}
          rows={4}
          disabled={loading}
        />

        {loading && (
          <div className="modal-loading">
            <MentorBot mood="pensativo" size={40} />
            <span>Armando tu plan personalizado...</span>
          </div>
        )}

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose} disabled={loading}>
            Cancelar
          </button>
          <button
            className="btn-primary"
            onClick={() => onSubmit(text)}
            disabled={!text.trim() || loading}
          >
            {loading ? 'Generando...' : '✨ Crear mi plan'}
          </button>
        </div>
      </div>
    </div>
  )
}
