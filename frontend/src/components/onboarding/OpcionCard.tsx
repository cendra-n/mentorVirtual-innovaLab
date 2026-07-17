interface Props {
  label: string
  emoji?: string
  selected: boolean
  onClick: () => void
}

/** Tarjeta de opción seleccionable, usada en los pasos de Intereses, Empleo y Educación. */
export default function OpcionCard({ label, emoji, selected, onClick }: Props) {
  return (
    <button
      type="button"
      className={`onboarding-opcion-card ${selected ? 'onboarding-opcion-card--active' : ''}`}
      onClick={onClick}
    >
      {emoji && <span className="onboarding-opcion-emoji">{emoji}</span>}
      <span>{label}</span>
    </button>
  )
}