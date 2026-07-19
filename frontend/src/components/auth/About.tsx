import MentorBot from '../MentorBot'

interface Props {
  onBack: () => void
}

/**
 * Pantalla "Acerca de". Reemplaza toda la página de Login mientras está
 * activa (sin header/footer propio, solo el cuadro central) — así se
 * definió explícitamente: no tiene sentido duplicar el header de auth acá.
 *
 * Nombre siempre por VITE_APP_NAME/VITE_MENTOR_NAME, nunca hardcodeado:
 * todavía no se confirmó el nombre final ("Impulsa") ni el copyright
 * (innova.lab) hasta que se cierre el convenio.
 */
export default function About({ onBack }: Props) {
  const appName = import.meta.env.VITE_APP_NAME || 'Impulsa'

  return (
    <div className="auth-page about-page">
      <div className="auth-card-wrapper">
        <div className="auth-card about-card">
          <div className="about-head">
            <MentorBot mood="pensativo" size={88} />
            <h1 className="auth-title">Acerca de {appName}</h1>
          </div>

          {/* TODO: reemplazar por el texto institucional definitivo, una
              vez que se confirme nombre/convenio con innova.lab. */}
          <div className="about-body">
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent fermentum,
              urna a tincidunt ultrices, lorem nisl efficitur arcu, vitae blandit mi sapien
              non nisi. Sed euismod, nibh vel commodo varius, justo sapien aliquet enim,
              a placerat est nulla nec ipsum.
            </p>
            <p>
              Curabitur sodales ligula in libero. Sed dignissim lacinia nunc. Curabitur
              tortor. Pellentesque nibh. Aenean quam. In scelerisque sem at dolor.
              Maecenas mattis. Sed convallis tristique sem.
            </p>
            <p>
              Proin ut ligula vel nunc egestas porttitor. Morbi lectus risus, iaculis vel,
              suscipit quis, luctus non, massa. Fusce ac turpis quis ligula lacinia aliquet.
            </p>
          </div>

          <button className="btn-primary btn-full auth-submit-btn" onClick={onBack}>
            ← Volver
          </button>
        </div>
      </div>
    </div>
  )
}
