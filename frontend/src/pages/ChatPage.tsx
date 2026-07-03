import { useState, useEffect, useRef } from 'react'
import MentorBot, { MoodType } from '../components/MentorBot'

interface Message {
  from: 'user' | 'bot'
  text: string
  mood?: MoodType
}

const getMood = (text: string): MoodType => {
  if (/buen|genial|perfecto|excelente|gracias/i.test(text)) return 'emocionado'
  if (/\?|cómo|qué|por qué|cuándo/i.test(text)) return 'pensativo'
  if (/hola|buenas|hey/i.test(text)) return 'guiñando'
  if (/ayuda|ayudame|no entiendo/i.test(text)) return 'ayudando'
  if (/triste|mal|difícil|no puedo/i.test(text)) return 'triste'
  return 'feliz'
}

const getBotResponse = (text: string): string => {
  if (/recomiend/i.test(text)) return '¡Claro! Basándome en tus metas, te recomiendo empezar con algo concreto y alcanzable. ¿Querés crear una meta nueva?'
  if (/concept/i.test(text)) return '¡Con gusto! Escribime el concepto que querés entender y lo explicamos juntos paso a paso.'
  if (/desafío/i.test(text)) return '🏆 Los desafíos te ayudan a mantener el ritmo. ¡Mirá la sección Desafíos para ver los disponibles!'
  return '¡Buena pregunta! Estoy acá para ayudarte. Podés también crear una meta nueva y te armo un plan personalizado. 💪'
}

// TODO: no existe endpoint de backend para historial de conversaciones (grupo `tutor`
// solo tiene ask_step/books). Por ahora guardamos las últimas preguntas en localStorage
// como accesos rápidos, no como conversaciones completas persistidas.
function loadRecientes(): string[] {
  try {
    const raw = localStorage.getItem('chat_recientes')
    if (raw) return JSON.parse(raw)
  } catch { }
  return []
}

export default function ChatPage() {
  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [recientes, setRecientes] = useState<string[]>(loadRecientes())
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const guardarReciente = (text: string) => {
    const next = [text, ...recientes.filter(r => r !== text)].slice(0, 5)
    setRecientes(next)
    localStorage.setItem('chat_recientes', JSON.stringify(next))
  }

  const send = async (text: string) => {
    if (!text.trim()) return
    const userMsg: Message = { from: 'user', text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    guardarReciente(text)

    const mood = getMood(text)

    // TODO: reemplazar por integración real con el tutor (POST /api/tutor/ask_step/)
    await new Promise(r => setTimeout(r, 800))
    const botMsg: Message = { from: 'bot', text: getBotResponse(text), mood }
    setMessages(prev => [...prev, botMsg])
    setLoading(false)
  }

  return (
    <div className="chatpage">
      <aside className="chatpage-sidebar">
        <h3 className="chatpage-sidebar-title">Últimas Conversaciones</h3>
        {recientes.length === 0 && (
          <p className="chatpage-sidebar-empty">Todavía no tenés conversaciones.</p>
        )}
        <ul className="chatpage-recientes-list">
          {recientes.map((r, i) => (
            <li key={i}>
              <button className="chatpage-reciente-item" onClick={() => send(r)}>
                {r}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <div className="chatpage-main">
        {messages.length === 0 ? (
          <div className="chatpage-empty">
            <MentorBot mood="feliz" size={90} />
            <p className="chatpage-empty-title">¿Qué vamos a estudiar hoy?</p>
          </div>
        ) : (
          <div className="chatpage-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble chat-bubble--${msg.from}`}>
                {msg.from === 'bot' && msg.mood && (
                  <MentorBot mood={msg.mood} size={28} className="bubble-avatar" />
                )}
                <span>{msg.text}</span>
              </div>
            ))}
            {loading && (
              <div className="chat-bubble chat-bubble--bot">
                <MentorBot mood="pensativo" size={28} className="bubble-avatar" />
                <span className="typing"><span /><span /><span /></span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}

        <div className="chatpage-input-row">
          <button className="chatpage-input-plus" title="Adjuntar (próximamente)">+</button>
          <input
            className="chatpage-input"
            placeholder={`Preguntale algo a ${mentorName}...`}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send(input)}
          />
          <button className="chatpage-send" onClick={() => send(input)}>➤</button>
        </div>
      </div>
    </div>
  )
}