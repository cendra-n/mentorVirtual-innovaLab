interface Props {
  active: boolean
  label: string
  avatar: string
  onClick: () => void
}

/** Tarjeta de selección de género, usada en el formulario de registro. */
export default function GeneroCard({ active, label, avatar, onClick }: Props) {
  return (
    <button
      type="button"
      className={`genero-card ${active ? 'genero-card--active' : ''}`}
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
    >
      <img src={avatar} alt="" className="genero-card-avatar" />
      <span className="genero-card-label">{label}</span>
    </button>
  )
}