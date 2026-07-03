import mascotaBot from '../assets/mascota-bot.svg'

// MentorBot — el robot mentor
// TODO: la carita nueva (Figma) es una imagen estática única; no tiene variantes
// por mood todavía. Si UX/UI entrega variantes para cada estado emocional,
// volver a implementar el swap por mood.

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

export default function MentorBot({ mood = 'feliz', size = 80, className = '' }: Props) {
  const name = import.meta.env.VITE_MENTOR_NAME || 'Pulso'

  return (
    <img
      src={mascotaBot}
      width={size}
      height={size}
      className={className}
      alt={`${name} — mascota`}
    />
  )
}