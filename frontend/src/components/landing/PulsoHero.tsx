import { useState } from 'react'
import { motion } from 'framer-motion'
import PulsoMascota from '../PulsoMascota'

interface Props {
  onComenzar: () => void
}

/**
 * Pulso del hero de la Landing, con los elementos flotantes que pide el
 * mockup de UX: tarjeta de "Racha activa", chip de "+75 XP" y el globo
 * de chat "¡Hola! Soy Pulso...".
 *
 * El centro es un video corto de Pulso en 3D (saluda → levita → pulgar
 * arriba, generado con IA a partir de los assets oficiales de UX, idea
 * original de Gerardo). Se reproduce una vez y queda congelado en la
 * pose final. Si el video no puede cargarse/reproducirse, cae a la
 * ilustración estática oficial (PulsoMascota pose "feliz").
 */
export default function PulsoHero({ onComenzar }: Props) {
  const [videoFailed, setVideoFailed] = useState(false)

  return (
    <div className="landing-pulso-hero">
      {videoFailed ? (
        <>
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 3.2, repeat: Infinity, ease: 'easeInOut' }}
          >
            <PulsoMascota pose="feliz" size={300} alt="Pulso, tu mentor virtual con IA" />
          </motion.div>
          <div className="landing-pulso-shadow" aria-hidden="true" />
        </>
      ) : (
        <video
          className="landing-pulso-video"
          src="/pulso-hero.mp4"
          autoPlay
          muted
          playsInline
          preload="auto"
          onError={() => setVideoFailed(true)}
          aria-label="Pulso, tu mentor virtual con IA, saludando"
        />
      )}

      {/* Tarjeta flotante: racha activa */}
      <motion.div
        className="landing-float-card landing-float-racha"
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 2.6, repeat: Infinity, ease: 'easeInOut' }}
        aria-hidden="true"
      >
        <span className="landing-float-check">✓</span>
        <span>
          <strong>Racha activa</strong>
          <small>12 días consecutivos 🔥</small>
        </span>
      </motion.div>

      {/* Chip flotante: XP */}
      <motion.div
        className="landing-float-card landing-float-xp"
        animate={{ y: [0, -7, 0] }}
        transition={{ duration: 2.9, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
        aria-hidden="true"
      >
        ⚡ +75 XP
      </motion.div>

      {/* Globo de chat de Pulso */}
      <motion.div
        className="landing-float-card landing-float-chat"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1.1 }}
      >
        <p>
          👋 ¡Hola! Soy <strong>Pulso</strong>, tu mentor virtual. ¿Comenzamos hoy?
        </p>
        <button type="button" onClick={onComenzar} aria-label="Responder a Pulso: Sí, vamos">
          Sí, vamos 🚀
        </button>
      </motion.div>
    </div>
  )
}
