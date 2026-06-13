import { useState, useRef, useEffect } from 'react'
import MentorBot, { MoodType } from './MentorBot'

interface Props {
  stepId: number
  stepTitle: string
  stepDescription: string
  goalText: string
}

const BASE = '/api'
const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

interface Message {
  from: 'user' | 'bot'
  text: string
  source?: string
}

const FRASES_INVITACION = [
  '¿Tenés dudas? ¡Preguntame!',
  '¿Algo no quedó claro? ¡Estoy acá!',
  '¿Querés que te explique algo?',
  '¡Preguntame lo que quieras!',
]

export default function TutorFloatingChat({ stepId, stepTitle, stepDescription, goalText }: Props) {
  const [open, setOpen]         = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [mood, setMood]         = useState<MoodType>('feliz')
  const [frase]                 = useState(() => FRASES_INVITACION[Math.floor(Math.random() * FRASES_INVITACION.length)])
  const [bounce, setBounce]     = useState(false)
  const messagesEndRef          = useRef<HTMLDivElement>(null)
  const chatRef                 = useRef<HTMLDivElement>(null)
  const mentorName              = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  // Bounce cada 5 segundos cuando está cerrado
  useEffect(() => {
    if (open) return
    const interval = setInterval(() => {
      setBounce(true)
      setTimeout(() => setBounce(false), 800)
    }, 5000)
    return () => clearInterval(interval)
  }, [open])

  // Mensaje inicial al abrir — solo una vez
  useEffect(() => {
    if (!open) return
    if (messages.length === 0) {
      setMessages([{
        from: 'bot',
        text: `¡Hola! Soy ${mentorName}. Estoy acá para ayudarte con "${stepTitle}". ¿Qué querés que te explique?`,
      }])
    }
  }, [open])

  // Scroll solo dentro del chat, sin mover la página
  useEffect(() => {
    if (messages.length === 0) return
    const el = messagesEndRef.current
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [messages])

  const handleOpen = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setOpen(true)
  }

  const handleClose = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setOpen(false)
  }

  const handleAsk = async (e?: React.MouseEvent) => {
    e?.preventDefault()
    e?.stopPropagation()
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { from: 'user', text: question }])
    setLoading(true)
    setMood('pensativo')

    try {
      const res = await fetch(`${BASE}/tutor/ask_step/`, {
        method: 'POST',
        headers: h(),
        body: JSON.stringify({
          question,
          step_title:       stepTitle,
          step_description: stepDescription,
          goal_text:        goalText,
        }),
      }).then(r => r.json())

      if (res.answer) {
        setMood('ayudando')
        setMessages(prev => [...prev, {
          from:   'bot',
          text:   res.answer,
          source: res.source,
        }])
      } else {
        setMood('triste')
        setMessages(prev => [...prev, {
          from: 'bot',
          text: '😔 No pude encontrar una respuesta. Intentá reformular la pregunta.',
        }])
      }
    } catch {
      setMood('sorprendido')
      setMessages(prev => [...prev, {
        from: 'bot',
        text: '❌ Hubo un problema de conexión. Intentá de nuevo.',
      }])
    }
    setLoading(false)
    setTimeout(() => setMood('feliz'), 3000)
  }

  const handleQuick = (e: React.MouseEvent, q: string) => {
    e.preventDefault()
    e.stopPropagation()
    setInput(q)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAsk()
    }
  }

  return (
    <div className="tutor-float-wrap" ref={chatRef}>

      {/* ── Botón invitación ── */}
      {!open && (
        <button
          className={`tutor-invite-btn ${bounce ? 'tutor-invite-btn--bounce' : ''}`}
          onClick={handleOpen}
        >
          <div className="tutor-invite-bot">
            <MentorBot mood="guiñando" size={48} />
            <div className="tutor-invite-pulse" />
          </div>
          <div className="tutor-invite-text">
            <span className="tutor-invite-main">{frase}</span>
            <span className="tutor-invite-sub">Tocame y te explico este paso 👆</span>
          </div>
          <span className="tutor-invite-arrow">→</span>
        </button>
      )}

      {/* ── Chat flotante ── */}
      {open && (
        <div className="tutor-float-chat">
          {/* Header */}
          <div className="tutor-float-header">
            <MentorBot mood={mood} size={40} className={loading ? 'mentor-thinking' : ''} />
            <div className="tutor-float-header-info">
              <span className="tutor-float-name">{mentorName}</span>
              <span className="tutor-float-status">
                {loading ? '⏳ Pensando...' : '● En línea'}
              </span>
            </div>
            <button className="tutor-float-close" onClick={handleClose}>✕</button>
          </div>

          {/* Contexto del paso */}
          <div className="tutor-float-context">
            <span className="tutor-float-context-label">📌 Estás en:</span>
            <span className="tutor-float-context-step">{stepTitle}</span>
          </div>

          {/* Mensajes — scroll contenido acá adentro */}
          <div className="tutor-float-messages" onWheel={e => e.stopPropagation()}>
            {messages.map((msg, i) => (
              <div key={i} className={`tutor-float-bubble tutor-float-bubble--${msg.from}`}>
                {msg.from === 'bot' && (
                  <MentorBot mood={mood} size={24} className="tutor-float-avatar" />
                )}
                <div className="tutor-float-bubble-body">
                  <p>{msg.text}</p>
                  {msg.source && (
                    <span className="tutor-float-source">📚 {msg.source}</span>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="tutor-float-bubble tutor-float-bubble--bot">
                <MentorBot mood="pensativo" size={24} className="tutor-float-avatar" />
                <div className="tutor-float-bubble-body">
                  <span className="typing"><span/><span/><span/></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick replies */}
          <div className="tutor-float-quick">
            {[
              '¿Podés explicarlo más fácil?',
              '¿Me das un ejemplo?',
              '¿Para qué sirve esto?',
            ].map((q, i) => (
              <button key={i} className="tutor-float-quick-btn" onClick={e => handleQuick(e, q)}>
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="tutor-float-input-row">
            <input
              className="tutor-float-input"
              placeholder="Escribí tu pregunta..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              autoFocus
            />
            <button
              className="tutor-float-send"
              onClick={handleAsk}
              disabled={loading || !input.trim()}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
