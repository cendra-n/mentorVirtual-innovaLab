interface Props {
  onLogout: () => void
}

/**
 * Botón de cerrar sesión dentro de Perfil. En desktop ya existe uno
 * en la Sidebar, pero esa se oculta en mobile — este queda accesible
 * en las dos plataformas sin depender de la sidebar.
 */
export default function CerrarSesionCard({ onLogout }: Props) {
  return (
    <div className="profile-card">
      <button className="btn-secondary btn-full" onClick={onLogout}>
        🚪 Cerrar sesión
      </button>
    </div>
  )
}