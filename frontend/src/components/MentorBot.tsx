// MentorBot — el robot mentor con 8 estados emocionales
// El nombre viene de la variable de entorno VITE_MENTOR_NAME

export type MoodType =
  | 'feliz'
  | 'emocionado'
  | 'pensativo'
  | 'guiñando'
  | 'ayudando'
  | 'sorprendido'
  | 'triste'
  | 'enamorado'

interface Props {
  mood?: MoodType
  size?: number
  className?: string
}

// Expresiones SVG para cada estado emocional
const MOODS: Record<MoodType, { eyes: string; mouth: string; extras?: string }> = {
  feliz: {
    eyes: `<ellipse cx="35" cy="42" rx="7" ry="5" fill="#00D4FF" opacity="0.9"/>
           <ellipse cx="65" cy="42" rx="7" ry="5" fill="#00D4FF" opacity="0.9"/>`,
    mouth: `<path d="M 35 58 Q 50 68 65 58" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>`,
  },
  emocionado: {
    eyes: `<ellipse cx="35" cy="42" rx="7" ry="7" fill="#00D4FF" opacity="0.9"/>
           <ellipse cx="65" cy="42" rx="7" ry="7" fill="#00D4FF" opacity="0.9"/>`,
    mouth: `<path d="M 32 56 Q 50 70 68 56" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    extras: `<line x1="28" y1="28" x2="24" y2="22" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>
             <line x1="32" y1="26" x2="30" y2="20" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>
             <line x1="72" y1="28" x2="76" y2="22" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>
             <line x1="68" y1="26" x2="70" y2="20" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>`,
  },
  pensativo: {
    eyes: `<circle cx="35" cy="42" r="6" fill="#00D4FF" opacity="0.9"/>
           <circle cx="65" cy="43" r="4" fill="#00D4FF" opacity="0.9"/>`,
    mouth: `<path d="M 38 60 Q 50 57 62 60" stroke="#00D4FF" stroke-width="2.5" fill="none" stroke-linecap="round"/>`,
  },
  guiñando: {
    eyes: `<ellipse cx="35" cy="42" rx="7" ry="5" fill="#00D4FF" opacity="0.9"/>
           <path d="M 59 42 Q 65 38 71 42" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    mouth: `<path d="M 36 58 Q 50 66 64 58" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    extras: `<path d="M 72 30 L 78 25" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>
             <text x="74" y="24" font-size="10" fill="#00D4FF">★</text>`,
  },
  ayudando: {
    eyes: `<ellipse cx="35" cy="42" rx="8" ry="6" fill="#00D4FF" opacity="0.9"/>
           <circle cx="65" cy="42" r="5" fill="#00D4FF" opacity="0.9"/>`,
    mouth: `<path d="M 34 57 Q 50 67 66 57" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>`,
  },
  sorprendido: {
    eyes: `<circle cx="35" cy="42" r="8" fill="#00D4FF" opacity="0.9"/>
           <circle cx="65" cy="42" r="8" fill="#00D4FF" opacity="0.9"/>`,
    mouth: `<ellipse cx="50" cy="62" rx="6" ry="7" fill="#00D4FF" opacity="0.8"/>`,
    extras: `<line x1="28" y1="30" x2="24" y2="24" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>
             <line x1="72" y1="30" x2="76" y2="24" stroke="#00D4FF" stroke-width="2" stroke-linecap="round"/>`,
  },
  triste: {
    eyes: `<path d="M 28 46 Q 35 38 42 44" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>
           <path d="M 58 44 Q 65 38 72 46" stroke="#00D4FF" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    mouth: `<path d="M 36 63 Q 50 55 64 63" stroke="#00D4FF" stroke-width="2.5" fill="none" stroke-linecap="round"/>`,
  },
  enamorado: {
    eyes: `<text x="27" y="50" font-size="16" fill="#FF6B9D">♥</text>
           <text x="57" y="50" font-size="16" fill="#FF6B9D">♥</text>`,
    mouth: `<path d="M 35 60 Q 50 70 65 60" stroke="#FF6B9D" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    extras: `<text x="72" y="28" font-size="12" fill="#FF6B9D">♥</text>
             <text x="16" y="35" font-size="9" fill="#FF6B9D">♥</text>`,
  },
}

export default function MentorBot({ mood = 'feliz', size = 80, className = '' }: Props) {
  const m = MOODS[mood]
  const name = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 120"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label={`${name} — ${mood}`}
    >
      {/* Antena */}
      <line x1="50" y1="4" x2="50" y2="16" stroke="#1a2a4a" strokeWidth="3" strokeLinecap="round"/>
      <circle cx="50" cy="4" r="5" fill="#00D4FF"/>

      {/* Cabeza */}
      <rect x="18" y="16" width="64" height="62" rx="20" fill="#f0f4ff"/>
      <rect x="18" y="16" width="64" height="62" rx="20" fill="none" stroke="#1a2a4a" strokeWidth="2.5"/>

      {/* Visor oscuro */}
      <rect x="24" y="26" width="52" height="42" rx="12" fill="#0a1628"/>
      <rect x="24" y="26" width="52" height="42" rx="12" fill="url(#visorGrad)" opacity="0.3"/>

      {/* Ojos y boca según mood */}
      <g dangerouslySetInnerHTML={{ __html: m.eyes + m.mouth + (m.extras || '') }} />

      {/* Orejas */}
      <rect x="10" y="34" width="10" height="16" rx="4" fill="#c8d4f0" stroke="#1a2a4a" strokeWidth="1.5"/>
      <rect x="80" y="34" width="10" height="16" rx="4" fill="#c8d4f0" stroke="#1a2a4a" strokeWidth="1.5"/>

      {/* Cuerpo */}
      <rect x="26" y="80" width="48" height="32" rx="10" fill="#f0f4ff" stroke="#1a2a4a" strokeWidth="2"/>

      {/* Burbuja de chat en el pecho */}
      <rect x="34" y="87" width="32" height="18" rx="8" fill="#00D4FF"/>
      <circle cx="41" cy="96" r="2.5" fill="white"/>
      <circle cx="50" cy="96" r="2.5" fill="white"/>
      <circle cx="59" cy="96" r="2.5" fill="white"/>

      {/* Piernas */}
      <rect x="32" y="112" width="14" height="8" rx="4" fill="#1a2a4a"/>
      <rect x="54" y="112" width="14" height="8" rx="4" fill="#1a2a4a"/>

      <defs>
        <linearGradient id="visorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.15"/>
          <stop offset="100%" stopColor="#000000" stopOpacity="0"/>
        </linearGradient>
      </defs>
    </svg>
  )
}
