import { useState } from 'react'
export default function AyudaCard() {
  const [helpClicked, setHelpClicked] = useState(false)

  return (
    <div className="profile-card profile-help-card">
      <h3 className="profile-section-title">💬 ¿Necesitás ayuda?</h3>
      <p>Accedé a la documentación, tutoriales y soporte personalizado.</p>
      <button className="btn-primary btn-full" onClick={() => setHelpClicked(true)}>
        Centro de apoyo ↗
      </button>
      {helpClicked && (
        <p className="profile-help-note">
          Esta sección va a estar disponible próximamente.
        </p>
      )}
    </div>
  )
}