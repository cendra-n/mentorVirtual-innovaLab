import { useState } from 'react'
import { motion } from 'framer-motion'
import PulsoMascota from '../components/PulsoMascota'
import PulsoHero from '../components/landing/PulsoHero'
import About from '../components/auth/About'
// Poses de Pulso en 3D para las feature cards — generadas con IA a partir
// de los assets oficiales de UX (assets/moods/), mismo estilo que el video
// del hero. Si UX pide volver a la ilustración plana, reemplazar por
// <PulsoMascota pose="..." /> como estaba antes.
import pulso3dEnfocado from '../assets/pulso-3d/enfocado.jpg'
import pulso3dZen from '../assets/pulso-3d/zen.jpg'
import pulso3dRacha from '../assets/pulso-3d/racha.jpg'
import '../styles/landing.css'

interface Props {
  onIniciarSesion: () => void
  onRegistrarse: () => void
}

// Avatares del social proof del hero (mockup de UX).
const AVATARES = [
  { id: '1', initials: 'JS', color: '#3B82F6' },
  { id: '2', initials: 'AM', color: '#10B981' },
  { id: '3', initials: 'TR', color: '#F59E0B' },
]

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
}

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.18 } },
}

/**
 * Landing page pública (mockup de UX/UI "Landin Page").
 * Versión combinada: estructura y estilos base propios + animaciones y
 * elementos flotantes del hero tomados del prototipo de Gerardo
 * (landing_page_mentor). El video 3D de Pulso reemplaza a la ilustración
 * estática del mockup (pendiente de validación con UX).
 */
export default function Landing({ onIniciarSesion, onRegistrarse }: Props) {
  const appName = import.meta.env.VITE_APP_NAME || 'Impulsa'
  const [showAbout, setShowAbout] = useState(false)

  if (showAbout) {
    return <About onBack={() => setShowAbout(false)} />
  }

  return (
    <motion.div
      className="landing-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <header className="landing-header">
        <div className="landing-logo">
          <span className="landing-logo-icon" aria-hidden="true">🎓</span>
          {appName}
        </div>
        <div className="landing-header-actions">
          <button className="landing-btn landing-btn-ghost" onClick={onIniciarSesion}>
            Iniciar Sesión
          </button>
          <button className="landing-btn landing-btn-primary" onClick={onRegistrarse}>
            Registrarse
          </button>
        </div>
      </header>

      <motion.section
        className="landing-hero"
        initial="hidden"
        animate="visible"
        variants={stagger}
      >
        <div className="landing-hero-text">
          <motion.span className="landing-badge" variants={fadeInUp}>
            ✨ Nueva plataforma de aprendizaje
          </motion.span>
          <motion.h1 variants={fadeInUp}>
            Potencia tu Futuro con <span className="landing-highlight">{appName}</span>
          </motion.h1>
          <motion.p variants={fadeInUp}>
            {appName} es un espacio digital diseñado para apoyarte en tu camino
            profesional. Conectá con <strong>Pulso</strong>, tu mentor virtual con IA,
            y acelerá tu crecimiento.
          </motion.p>
          <motion.div variants={fadeInUp}>
            <motion.button
              className="landing-btn landing-btn-primary landing-btn-lg"
              onClick={onRegistrarse}
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              Comenzar con Pulso →
            </motion.button>
          </motion.div>
          <motion.div className="landing-social-proof" variants={fadeInUp}>
            <span className="landing-avatars" aria-hidden="true">
              {AVATARES.map((a, i) => (
                <span
                  key={a.id}
                  className="landing-avatar"
                  style={{ backgroundColor: a.color, zIndex: AVATARES.length - i }}
                >
                  {a.initials}
                </span>
              ))}
            </span>
            Más de <strong>10 estudiantes</strong> ya aprenden con Pulso
          </motion.div>
        </div>
        <motion.div
          className="landing-hero-image"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <PulsoHero onComenzar={onRegistrarse} />
        </motion.div>
      </motion.section>

      <motion.section
        className="landing-features"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={stagger}
      >
        <motion.span className="landing-eyebrow" variants={fadeInUp}>
          💬 ¿Por qué elegir a {appName}?
        </motion.span>
        <motion.h2 variants={fadeInUp}>Pulso lo hace diferente</motion.h2>
        <motion.p className="landing-features-sub" variants={fadeInUp}>
          No es solo una plataforma de cursos, es un compañero de aprendizaje que
          te conoce, te reta y celebra cada logro.
        </motion.p>

        <div className="landing-feature-grid">
          <motion.article className="landing-feature-card" variants={fadeInUp}>
            <div className="landing-feature-head">
              <img className="landing-feature-img" src={pulso3dEnfocado} alt="Pulso estudiando con su tablet" />
              <span className="landing-feature-tag">Aprende a tu ritmo</span>
            </div>
            <h3>IA Personalizada</h3>
            <p>Pulso adapta cada lección a tu nivel, objetivos y tiempo disponible. No más cursos genéricos.</p>
          </motion.article>

          <motion.article className="landing-feature-card" variants={fadeInUp}>
            <div className="landing-feature-head">
              <img className="landing-feature-img" src={pulso3dZen} alt="Pulso meditando, siempre disponible" />
              <span className="landing-feature-tag">24/7 contigo</span>
            </div>
            <h3>Mentor siempre disponible</h3>
            <p>Preguntale a Pulso lo que quieras, cuando quieras. Explica, corrige y motiva en tiempo real.</p>
          </motion.article>

          <motion.article className="landing-feature-card" variants={fadeInUp}>
            <div className="landing-feature-head">
              <img className="landing-feature-img" src={pulso3dRacha} alt="Pulso celebrando una racha de logros" />
              <span className="landing-feature-tag">Nota tu crecimiento</span>
            </div>
            <h3>Logros y Progreso</h3>
            <p>Completá desafíos, mantené rachas y obtené insignias que demuestran tus conocimientos.</p>
          </motion.article>
        </div>
      </motion.section>

      <motion.section
        className="landing-cta"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.4 }}
        variants={fadeInUp}
      >
        <PulsoMascota pose="feliz" size={80} />
        <div className="landing-cta-text">
          <h2>¿Listo para aprender con Pulso?</h2>
          <p>Registrate gratis y empezá hoy mismo.</p>
        </div>
        <button className="landing-btn landing-btn-light" onClick={onRegistrarse}>
          Comenzar Ahora →
        </button>
      </motion.section>

      <footer className="landing-footer">
        <div className="landing-footer-brand">{appName}</div>
        <p>Impulsa tus metas, potenciá tus habilidades</p>
        <nav className="landing-footer-links">
          <button type="button" className="landing-footer-link" onClick={() => setShowAbout(true)}>Términos</button>
          <button type="button" className="landing-footer-link" onClick={() => setShowAbout(true)}>Privacidad</button>
          <button type="button" className="landing-footer-link" onClick={() => setShowAbout(true)}>Contacto</button>
        </nav>
        <p className="landing-footer-copy">
          © 2026 {appName} — Innova · Talento Tech. Todos los derechos reservados.
        </p>
      </footer>
    </motion.div>
  )
}
