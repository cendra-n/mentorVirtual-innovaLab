import feliz from '../assets/moods/feliz.svg'
import enfocado from '../assets/moods/enfocado.svg'
import megaRacha from '../assets/moods/mega_racha.svg'
import pensativo from '../assets/moods/pensativo.svg'
import sorprendido from '../assets/moods/sorprendido.svg'
import triste from '../assets/moods/triste.svg'
import zen from '../assets/moods/zen.svg'

// Registro de poses de Pulso entregadas por UX (frontend/src/assets/moods/).
// Nombre de la pose = nombre real del archivo, sin inventar sinónimos,
// para que agregar una pose nueva sea solo: poner el archivo + una línea acá.
export type PulsoPose =
  | 'feliz'
  | 'enfocado'
  | 'mega_racha'
  | 'pensativo'
  | 'sorprendido'
  | 'triste'
  | 'zen'

const POSES: Record<PulsoPose, string> = {
  feliz,
  enfocado,
  mega_racha: megaRacha,
  pensativo,
  sorprendido,
  triste,
  zen,
}

interface Props {
  pose: PulsoPose
  size?: number
  className?: string
  alt?: string
}

/**
 * Ilustración de cuerpo completo de Pulso en una pose/estado puntual.
 * Son PNGs exportados de Figma envueltos en SVG (no vector editable ni
 * animable por partes) — a diferencia de PulsoConCampana.tsx, que sí es
 * SVG vectorial armado a mano. Para eso no sirve este componente.
 */
export default function PulsoMascota({ pose, size = 160, className = '', alt }: Props) {
  return (
    <img
      src={POSES[pose]}
      width={size}
      alt={alt || `Pulso — ${pose}`}
      className={`pulso-mascota ${className}`}
    />
  )
}
