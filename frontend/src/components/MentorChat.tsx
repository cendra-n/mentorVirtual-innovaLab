import { useState } from 'react'
import MentorBot, { MoodType } from './MentorBot'

const QUICK = [
  { icon: '🎓', text: '¿Qué temas me recomendás?' },
  { icon: '💡', text: 'Explicame este concepto' },
  { icon: '🎯', text: 'Recomendame un desafío' },
  { icon: '🤔', text: 'Tengo otra duda' },
]

// Moodea al mentor según el mensaje
const getMood = (text: string): MoodType => {
  if (/buen|genial|perfecto|excelente|gracias/i.test(text)) return 'emocionado'
  if (/\?|cómo|qué|por qué|cuándo/i.test(text)) return 'pensativo'
  if (/hola|buenas|hey/i.test(text)) return 'guiñando'
  if (/ayuda|ayudame|no entiendo/i.test(text)) return 'ayudando'
  if (/triste|mal|difícil|no puedo/i.test(text)) return 'triste'
  return 'feliz'
}

interface Message {
  from: 'user' | 'bot'
  text: string
  mood?: MoodType
}

export default function MentorChat() {
  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'
  const [messages, setMessages] = useState<Message[]>([
    { from: 'bot', text: `¡Hola! Soy ${mentorName}. ¿En qué puedo ayudarte hoy?`, mood: 'feliz' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentMood, setCurrentMood] = useState<MoodType>('feliz')

  const send = async (text: string) => {
    if (!text.trim()) return
    const userMsg: Message = { from: 'user', text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    const mood = getMood(text)
    setCurrentMood(mood)

    // Por ahora respuesta local — en Fase 2 conecta a Claude API
    await new Promise(r => setTimeout(r, 800))
    const botMsg: Message = {
      from: 'bot',
      text: getBotResponse(text),
      mood,
    }
    setMessages(prev => [...prev, botMsg])
    setLoading(false)
  }

  const getBotResponse = (text: string): string => {
    if (/recomiend/i.test(text)) return '¡Claro! Basándome en tus metas, te recomiendo empezar con algo concreto y alcanzable. ¿Querés crear una meta nueva?'
    if (/concept/i.test(text)) return '¡Con gusto! Escribime el concepto que querés entender y lo explicamos juntos paso a paso.'
    if (/desafío/i.test(text)) return '🏆 Los desafíos te ayudan a mantener el ritmo. ¡Mirá la sección Desafíos para ver los disponibles!'
    return `¡Buena pregunta! Estoy acá para ayudarte. Podés también crear una meta nueva y te armo un plan personalizado. 💪`
  }

  return (
    <aside className="mentor-chat">
      {/* Header del chat */}
      <div className="chat-header">
        <div className="chat-bot-info">
          <MentorBot mood={currentMood} size={48} className="chat-bot-avatar" />
          <div>
            <div className="chat-bot-name">{mentorName}</div>
            <div className="chat-bot-status">
              <span className="status-dot" /> En línea
            </div>
          </div>
        </div>
        <button className="chat-menu">···</button>
      </div>

      {/* Mensajes */}
      <div className="chat-messages">
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
            <span className="typing">
              <span/><span/><span/>
            </span>
          </div>
        )}
      </div>

      {/* Quick replies */}
      <div className="chat-quick">
        {QUICK.map((q, i) => (
          <button key={i} className="quick-btn" onClick={() => send(q.text)}>
            {q.icon} {q.text}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="chat-input-row">
        <input
          className="chat-input"
          placeholder="Escribí tu mensaje..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send(input)}
        />
        <button className="chat-send" onClick={() => send(input)}>
          ➤
        </button>
      </div>
    </aside>
  )
}
