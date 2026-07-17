interface Props {
  active: string
  onNav: (page: string) => void
}

// Se usan escapes Unicode (\u{...}) en vez de pegar el emoji directo,
// porque los emojis como texto plano se corrompen fácil al guardar el
// archivo con un encoding distinto a UTF-8 (mismo problema que ya
// tenían con ñ/á en PowerShell, pero para emojis).
const TABS = [
  { id: 'inicio',    icon: '\u{1F3E0}', label: 'Inicio' },
  { id: 'lecciones', icon: '\u{1F4D6}', label: 'Lecciones' },
  { id: 'desafios',  icon: '\u{1F3C6}', label: 'Desafíos' },
  { id: 'logros',    icon: '\u{2B50}',  label: 'Logros' },
  { id: 'perfil',    icon: '\u{1F464}', label: 'Perfil' },
]

/**
 * Navegación mobile: barra inferior fija con las 5 secciones
 * principales + botón flotante para el chat con Pulso.
 *
 * Solo se muestra en pantallas chicas (ver .mobile-tabbar y
 * .mobile-chat-fab en el CSS, ocultas por default y visibles
 * recién bajo @media max-width: 700px) — en desktop sigue
 * funcionando la <Sidebar> de siempre, sin tocarla.
 *
 * "Desafíos" y "Logros" todavía no tienen pantalla propia en
 * Dashboard.tsx (caen al contenido de Inicio por ahora) — el botón
 * ya está preparado, falta la pantalla del lado del dashboard.
 */
export default function MobileNav({ active, onNav }: Props) {
  return (
    <>
      <button
        className="mobile-chat-fab"
        onClick={() => onNav('chat')}
        aria-label="Chatea con Pulso"
      >
        🤖
      </button>

      <nav className="mobile-tabbar">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`mobile-tab ${active === tab.id ? 'mobile-tab--active' : ''}`}
            onClick={() => onNav(tab.id)}
          >
            <span className="mobile-tab-icon">{tab.icon}</span>
            <span className="mobile-tab-label">{tab.label}</span>
          </button>
        ))}
      </nav>
    </>
  )
}