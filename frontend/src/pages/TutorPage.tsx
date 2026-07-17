import { useState, useEffect, useRef } from 'react'
import MentorBot from '../components/MentorBot'
import { MoodType } from '../components/MentorBot'

const BASE = '/api'
const h = () => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

// ── API ───────────────────────────────────────────────────────────────────────
const apiGetBooks = () =>
  fetch(`${BASE}/tutor/books/`, { headers: h() }).then(r => r.json())

const apiUploadBook = (formData: FormData) =>
  fetch(`${BASE}/tutor/books/`, {
    method: 'POST',
    headers: h(),
    body: formData,
  }).then(r => r.json())

const apiDeleteBook = (id: number) =>
  fetch(`${BASE}/tutor/books/${id}/`, {
    method: 'DELETE',
    headers: h(),
  }).then(r => r.json())

const apiAsk = (bookId: number, question: string) =>
  fetch(`${BASE}/tutor/books/${bookId}/ask/`, {
    method: 'POST',
    headers: { ...h(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  }).then(r => r.json())

// ── Tipos ─────────────────────────────────────────────────────────────────────
interface Book {
  id: number
  title: string
  subject: string
  filename: string
  chunks: number
  created_at: string
}

interface Message {
  from: 'user' | 'bot'
  text: string
  sources?: { page: number; similarity: number }[]
  mood?: MoodType
}

export default function TutorPage() {
  const [books, setBooks]           = useState<Book[]>([])
  const [selectedBook, setSelectedBook] = useState<Book | null>(null)
  const [messages, setMessages]     = useState<Message[]>([])
  const [question, setQuestion]     = useState('')
  const [asking, setAsking]         = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [uploading, setUploading]   = useState(false)
  const [uploadMsg, setUploadMsg]   = useState('')

  // En mobile, .tutor-sidebar (libros + botón de subir PDF) se oculta
  // por default para no romper el layout. Este estado controla si se
  // muestra como panel deslizable encima del chat (ver chat.css).
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  // Upload form
  const [title, setTitle]     = useState('')
  const [subject, setSubject] = useState('')
  const [file, setFile]       = useState<File | null>(null)
  const fileRef               = useRef<HTMLInputElement>(null)
  const messagesEndRef        = useRef<HTMLDivElement>(null)

  const mentorName = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  useEffect(() => {
    apiGetBooks().then(d => setBooks(d.books || []))
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleUpload = async () => {
    if (!file || !title) return
    setUploading(true)
    setUploadMsg('')

    const fd = new FormData()
    fd.append('pdf', file)
    fd.append('title', title)
    fd.append('subject', subject)

    const res = await apiUploadBook(fd)
    if (res.book_id) {
      setUploadMsg(`✅ ${res.message}`)
      await apiGetBooks().then(d => setBooks(d.books || []))
      setTimeout(() => {
        setShowUpload(false)
        setTitle('')
        setSubject('')
        setFile(null)
        setUploadMsg('')
      }, 2000)
    } else {
      setUploadMsg(`❌ ${res.error || 'Error al subir el archivo.'}`)
    }
    setUploading(false)
  }

  const handleSelectBook = (book: Book) => {
    setSelectedBook(book)
    setMobileSidebarOpen(false)
    setMessages([{
      from: 'bot',
      text: `¡Hola! Cargué el libro "${book.title}". ¿Qué querés aprender hoy? Podés preguntarme cualquier cosa que esté en este material.`,
      mood: 'feliz',
    }])
  }

  const handleAsk = async () => {
    if (!question.trim() || !selectedBook || asking) return

    const userMsg: Message = { from: 'user', text: question }
    setMessages(prev => [...prev, userMsg])
    setQuestion('')
    setAsking(true)

    const res = await apiAsk(selectedBook.id, question)

    if (res.answer) {
      setMessages(prev => [...prev, {
        from: 'bot',
        text: res.answer,
        sources: res.sources,
        mood: 'ayudando',
      }])
    } else {
      setMessages(prev => [...prev, {
        from: 'bot',
        text: `❌ ${res.error || 'No pude generar una respuesta.'}`,
        mood: 'triste',
      }])
    }
    setAsking(false)
  }

  const handleDelete = async (book: Book) => {
    if (!confirm(`¿Eliminar "${book.title}"?`)) return
    await apiDeleteBook(book.id)
    await apiGetBooks().then(d => setBooks(d.books || []))
    if (selectedBook?.id === book.id) {
      setSelectedBook(null)
      setMessages([])
    }
  }

  return (
    <div className="tutor-page">

      {/* Botón para abrir el panel de libros en mobile. Solo se ve
          en pantallas chicas (ver .tutor-mobile-toggle en chat.css). */}
      <button
        className="tutor-mobile-toggle"
        onClick={() => setMobileSidebarOpen(true)}
      >
        📚 Mis libros
      </button>

      {/* Fondo oscuro detrás del panel cuando está abierto en mobile */}
      {mobileSidebarOpen && (
        <div
          className="tutor-mobile-backdrop"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* ── Panel izquierdo: libros ── */}
      <div className={`tutor-sidebar ${mobileSidebarOpen ? 'tutor-sidebar--mobile-open' : ''}`}>
        <div className="tutor-sidebar-header">
          <h2 className="tutor-sidebar-title">📚 Mis libros</h2>
          <button className="btn-primary" onClick={() => setShowUpload(true)}>
            + Subir PDF
          </button>
          {/* Solo visible en mobile, cuando el panel está abierto */}
          <button
            className="tutor-mobile-close"
            onClick={() => setMobileSidebarOpen(false)}
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        {books.length === 0 ? (
          <div className="tutor-empty">
            <MentorBot mood="pensativo" size={56} />
            <p>Todavía no subiste ningún libro.</p>
            <button className="btn-primary" onClick={() => setShowUpload(true)}>
              Subir mi primer libro
            </button>
          </div>
        ) : (
          <div className="tutor-books-list">
            {books.map(book => (
              <div
                key={book.id}
                className={`tutor-book-card ${selectedBook?.id === book.id ? 'tutor-book-card--active' : ''}`}
                onClick={() => handleSelectBook(book)}
              >
                <div className="tutor-book-icon">📖</div>
                <div className="tutor-book-info">
                  <p className="tutor-book-title">{book.title}</p>
                  <p className="tutor-book-meta">{book.subject} · {book.chunks} fragmentos</p>
                </div>
                <button
                  className="tutor-book-delete"
                  onClick={e => { e.stopPropagation(); handleDelete(book) }}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Panel derecho: chat ── */}
      <div className="tutor-chat">
        {!selectedBook ? (
          <div className="tutor-chat-empty">
            <MentorBot mood="ayudando" size={80} />
            <h3>Elegí un libro para empezar</h3>
            <p>Seleccioná un libro de la lista o subí uno nuevo para hacerle preguntas al tutor.</p>
          </div>
        ) : (
          <>
            {/* Header del chat */}
            <div className="tutor-chat-header">
              <MentorBot mood={asking ? 'pensativo' : 'feliz'} size={40} />
              <div>
                <p className="tutor-chat-book-title">{selectedBook.title}</p>
                <p className="tutor-chat-book-sub">{selectedBook.subject} · {selectedBook.chunks} fragmentos indexados</p>
              </div>
            </div>

            {/* Mensajes */}
            <div className="tutor-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`tutor-bubble tutor-bubble--${msg.from}`}>
                  {msg.from === 'bot' && (
                    <MentorBot mood={msg.mood || 'feliz'} size={32} className="tutor-bubble-avatar" />
                  )}
                  <div className="tutor-bubble-body">
                    <p>{msg.text}</p>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="tutor-sources">
                        {msg.sources.map((s, j) => (
                          <span key={j} className="tutor-source-tag">
                            📄 Pág. {s.page} ({Math.round(s.similarity * 100)}% relevante)
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {asking && (
                <div className="tutor-bubble tutor-bubble--bot">
                  <MentorBot mood="pensativo" size={32} className="tutor-bubble-avatar" />
                  <div className="tutor-bubble-body">
                    <span className="typing"><span/><span/><span/></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="tutor-input-row">
              <input
                className="chat-input"
                placeholder={`Preguntale algo a ${mentorName} sobre "${selectedBook.title}"...`}
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAsk()}
                disabled={asking}
              />
              <button
                className="chat-send"
                onClick={handleAsk}
                disabled={asking || !question.trim()}
              >
                ➤
              </button>
            </div>
          </>
        )}
      </div>

      {/* ── Modal subir PDF ── */}
      {showUpload && (
        <div className="modal-overlay" onClick={() => !uploading && setShowUpload(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <MentorBot mood={uploading ? 'pensativo' : 'emocionado'} size={52} />
              <div>
                <h2 className="modal-title">Subir libro PDF</h2>
                <p className="modal-sub">El tutor va a indexar el contenido para responder preguntas</p>
              </div>
            </div>

            <div className="login-form">
              <label>Título del libro *</label>
              <input
                className="form-input"
                placeholder="Ej: Matemática para todos"
                value={title}
                onChange={e => setTitle(e.target.value)}
                disabled={uploading}
              />

              <label>Materia</label>
              <input
                className="form-input"
                placeholder="Ej: Matemática, Historia, Lengua..."
                value={subject}
                onChange={e => setSubject(e.target.value)}
                disabled={uploading}
              />

              <label>Archivo PDF *</label>
              <div
                className="pdf-dropzone"
                onClick={() => fileRef.current?.click()}
              >
                {file ? (
                  <span>📄 {file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)</span>
                ) : (
                  <span>📁 Hacé click para seleccionar un PDF</span>
                )}
              </div>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={e => setFile(e.target.files?.[0] || null)}
              />

              {uploading && (
                <div className="modal-loading">
                  <MentorBot mood="pensativo" size={36} />
                  <div>
                    <p>Procesando el PDF...</p>
                    <p style={{ fontSize: '12px', color: 'var(--gris-medio)' }}>Esto puede tardar unos segundos</p>
                  </div>
                </div>
              )}

              {uploadMsg && (
                <div className={`form-msg ${uploadMsg.startsWith('✅') ? 'form-msg--ok' : 'form-msg--error'}`}>
                  {uploadMsg}
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowUpload(false)} disabled={uploading}>
                Cancelar
              </button>
              <button
                className="btn-primary"
                onClick={handleUpload}
                disabled={uploading || !file || !title}
              >
                {uploading ? '⏳ Procesando...' : '📤 Subir y procesar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}