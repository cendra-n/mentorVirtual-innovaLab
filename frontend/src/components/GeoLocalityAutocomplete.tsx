import { useState, useEffect, useRef } from 'react'
import { apiGeoLocalities } from '../services/api'

interface Localidad {
  locality_id: number
  locality_name: string
}

interface Props {
  provinceId: number | '' | null
  value: number | ''
  valueName?: string
  onChange: (localityId: number | '', localityName: string) => void
  disabled?: boolean
  className?: string
  placeholder?: string
}

/**
 * Autocompletado de localidad. Reemplaza al <select> nativo — con miles de
 * localidades por país (y varios cientos en provincias grandes como Buenos
 * Aires), un select cargaba solo la primera tanda alfabética y el usuario
 * nunca podía llegar a nada que no empezara con las primeras letras.
 * Acá se busca por texto contra el backend (?search=), con debounce.
 */
export default function GeoLocalityAutocomplete({
  provinceId, value, valueName, onChange, disabled, className, placeholder,
}: Props) {
  const [query, setQuery] = useState(valueName || '')
  const [suggestions, setSuggestions] = useState<Localidad[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const wrapRef = useRef<HTMLDivElement>(null)

  // Si cambia el valor seleccionado desde afuera (ej. precarga desde el
  // perfil), reflejarlo en el texto mostrado.
  useEffect(() => {
    setQuery(valueName || '')
  }, [valueName])

  // Ojo: NO hay un useEffect acá que limpie `query` cuando cambia `provinceId`.
  // Ya existía uno antes y causaba un bug: en la carga inicial, provinceId y
  // valueName cambian juntos (los dos vienen del mismo fetch de /me/), y ese
  // efecto se ejecutaba DESPUÉS del de arriba, pisando el valor recién
  // sincronizado con un string vacío — por eso la localidad guardada nunca
  // se veía aunque estuviera bien persistida. El padre (Register/Perfil) ya
  // limpia `valueName`/`locality` explícitamente cuando el usuario cambia de
  // provincia a mano, así que no hace falta duplicar esa limpieza acá.
  useEffect(() => {
    setSuggestions([])
  }, [provinceId])

  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  const handleInput = (text: string) => {
    setQuery(text)
    onChange('', '') // cualquier tipeo invalida la selección anterior hasta elegir una sugerencia
    if (debounceRef.current) clearTimeout(debounceRef.current)

    if (!provinceId || text.trim().length < 2) {
      setSuggestions([])
      setOpen(false)
      return
    }

    debounceRef.current = setTimeout(() => {
      setLoading(true)
      apiGeoLocalities(provinceId, text.trim()).then(res => {
        if (res.ok && Array.isArray(res.data?.results)) {
          setSuggestions(res.data.results)
          setOpen(true)
        }
      }).finally(() => setLoading(false))
    }, 300)
  }

  const handleSelect = (loc: Localidad) => {
    setQuery(loc.locality_name)
    onChange(loc.locality_id, loc.locality_name)
    setOpen(false)
    setSuggestions([])
  }

  return (
    <div ref={wrapRef} style={{ position: 'relative' }}>
      <input
        type="text"
        className={className}
        placeholder={placeholder || 'Escribí para buscar...'}
        value={query}
        disabled={disabled}
        onChange={e => handleInput(e.target.value)}
        onFocus={() => suggestions.length > 0 && setOpen(true)}
        autoComplete="off"
      />
      {open && (
        <div className="geo-autocomplete-dropdown">
          {loading && <div className="geo-autocomplete-item geo-autocomplete-item--muted">Buscando...</div>}
          {!loading && suggestions.length === 0 && (
            <div className="geo-autocomplete-item geo-autocomplete-item--muted">Sin resultados</div>
          )}
          {!loading && suggestions.map(s => (
            <button
              type="button"
              key={s.locality_id}
              className="geo-autocomplete-item"
              onClick={() => handleSelect(s)}
            >
              {s.locality_name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
