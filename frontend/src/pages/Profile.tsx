import InfoPersonalCard from '../components/profile/InfoPersonalCard'
import NotificacionesCard from '../components/profile/NotificacionesCard'
import SeguridadCard from '../components/profile/SeguridadCard'
import LogrosCard from '../components/profile/LogrosCard'
import PreferenciasCard from '../components/profile/PreferenciasCard'
import ProgresoCard from '../components/profile/ProgresoCard'
import ResumenActividadCard from '../components/profile/ResumenActividadCard'
import AyudaCard from '../components/profile/AyudaCard'
import CerrarSesionCard from '../components/profile/CerrarSesionCard'

interface Props {
  user: any
  onLogout: () => void
  onUserUpdated?: () => void
}

/**
 * Pantalla de Perfil. Cada sección vive en su propio componente
 * dentro de components/profile/, para que distintas personas puedan
 * trabajar en tarjetas distintas sin generar conflictos de merge.
 */
export default function Profile({ user, onLogout, onUserUpdated }: Props) {
  return (
    <div className="profile-page profile-page--nuevo">
      <div className="profile-header">
        <h1 className="detail-title">Mi Perfil</h1>
      </div>

      <div className="profile-layout">
        {/* ══ Columna principal ══ */}
        <div className="profile-main-col">
          <InfoPersonalCard user={user} onUserUpdated={onUserUpdated} />
          <NotificacionesCard />
          <SeguridadCard />
          <LogrosCard />
          <PreferenciasCard />
        </div>

        {/* ══ Columna lateral ══ */}
        <div className="profile-side-col">
          <ProgresoCard />
          <AyudaCard />
          <ResumenActividadCard />
        </div>
      </div>

      {/* Fuera de la grilla de 2 columnas, a ancho completo — para
          que no quede "flotando" a media altura entre las columnas.
          Visible en desktop y mobile (en desktop ya existe otro
          botón de "Salir" en la Sidebar, pero esa se oculta en
          mobile, así que este queda como respaldo en las dos). */}
      <div className="profile-logout-row">
        <CerrarSesionCard onLogout={onLogout} />
      </div>
    </div>
  )
} 