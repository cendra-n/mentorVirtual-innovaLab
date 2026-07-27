#!/usr/bin/env bash
#
# git-helper.sh — Asistente interactivo de Git para Mentor Virtual
# Menú simple para las operaciones de branch/log/PR del día a día,
# con chequeos de seguridad para no perder trabajo sin commitear.
#
# Uso:  ./git-helper.sh
#

set -uo pipefail

# ----- Colores -----
if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
  C_RED=$'\033[31m'; C_CYAN=$'\033[36m'; C_DIM=$'\033[2m'
else
  C_RESET=""; C_BOLD=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_CYAN=""; C_DIM=""
fi

info()  { echo "${C_CYAN}›${C_RESET} $*"; }
ok()    { echo "${C_GREEN}✓${C_RESET} $*"; }
warn()  { echo "${C_YELLOW}!${C_RESET} $*"; }
err()   { echo "${C_RED}✗${C_RESET} $*"; }

pause() { echo; read -rp "${C_DIM}[Enter] para volver al menú...${C_RESET}"; }

# ----- Verificación de que estamos en un repo git -----
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  err "No estás dentro de un repositorio git."
  exit 1
fi

# ----- Helpers -----
current_branch() { git rev-parse --abbrev-ref HEAD 2>/dev/null; }

has_changes() {
  ! git diff --quiet || ! git diff --cached --quiet || \
  [[ -n "$(git ls-files --others --exclude-standard)" ]]
}

changes_summary() {
  local mod staged untracked
  mod=$(git diff --name-only | wc -l | tr -d ' ')
  staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
  untracked=$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')
  echo "${mod} modificados, ${staged} en stage, ${untracked} sin trackear"
}

confirm() {
  local prompt="${1:-¿Seguro?}"
  read -rp "${prompt} [s/N] " r
  [[ "$r" =~ ^[sSyY]$ ]]
}

# Valida un nombre de branch contra la convención del equipo.
# Formato esperado: <tipo>/<area>-<descripcion>  (minúsculas, guiones, una sola barra)
valida_convencion() {
  local name="$1"
  local regex='^(feature|fix|refactor|test|chore|docs)/[a-z0-9]+(-[a-z0-9]+)*$'
  [[ "$name" =~ $regex ]]
}

# =====================================================================
#  OPERACIONES
# =====================================================================

ver_ramas() {
  echo "${C_BOLD}Ramas locales:${C_RESET}"
  git branch
  echo
  echo "${C_BOLD}Ramas remotas:${C_RESET}"
  git branch -r
  echo
  echo "${C_BOLD}Rama actual:${C_RESET} ${C_GREEN}$(current_branch)${C_RESET}"
}

ver_estado() {
  git status
}

cambiar_rama() {
  info "Ramas disponibles:"
  git branch -a | sed 's/remotes\/origin\///' | sort -u | grep -v 'HEAD' | sed 's/^/   /'
  echo
  read -rp "Rama a la que cambiar: " destino
  [[ -z "$destino" ]] && { warn "Cancelado."; return; }

  if has_changes; then
    warn "Tenés cambios sin commitear ($(changes_summary))."
    echo "  1) Stashear (guardar) y cambiar"
    echo "  2) Llevarme los cambios a la otra rama (checkout normal)"
    echo "  3) Cancelar"
    read -rp "Opción: " opt
    case "$opt" in
      1)
        git stash push -m "auto-stash antes de ir a $destino" \
          && info "Cambios guardados en stash."
        git checkout "$destino" && ok "En $destino. Recuperá con la opción Stash del menú."
        ;;
      2)
        if git checkout "$destino"; then
          ok "En $destino con los cambios encima."
        else
          err "Git frenó el checkout (los cambios chocan con la rama destino). Usá stash."
        fi
        ;;
      *) warn "Cancelado." ;;
    esac
  else
    git checkout "$destino" && ok "Ahora en $destino."
  fi
}

crear_rama() {
  echo "${C_BOLD}Convención:${C_RESET} <tipo>/<area>-<descripcion>"
  echo "${C_DIM}tipos: feature fix refactor test chore docs | minúsculas, guiones, una sola barra${C_RESET}"
  echo "${C_DIM}ej: feature/auth-jwt-refresh${C_RESET}"
  echo
  read -rp "Nombre de la rama nueva: " nombre
  [[ -z "$nombre" ]] && { warn "Cancelado."; return; }

  if ! valida_convencion "$nombre"; then
    warn "'$nombre' no cumple la convención del equipo."
    confirm "¿Crearla igual?" || { warn "Cancelado."; return; }
  fi

  echo
  echo "Base de la rama nueva:"
  echo "  1) Desde donde estoy ahora ($(current_branch)) — se lleva mis cambios sin commitear"
  echo "  2) Desde develop (limpia)"
  echo "  3) Desde main (limpia)"
  echo "  4) Desde otra rama"
  read -rp "Opción: " base

  case "$base" in
    1)
      git checkout -b "$nombre" && ok "Creada $nombre desde $(current_branch) anterior."
      ;;
    2|3)
      local rama_base="develop"; [[ "$base" == "3" ]] && rama_base="main"
      if has_changes; then
        err "Tenés cambios sin commitear; no puedo salir limpio a $rama_base."
        warn "Commiteá o stasheá primero, o usá la opción 1 (desde acá)."
        return
      fi
      git checkout "$rama_base" && git pull origin "$rama_base" \
        && git checkout -b "$nombre" && ok "Creada $nombre desde $rama_base actualizado."
      ;;
    4)
      read -rp "Rama base: " rama_base
      git checkout "$rama_base" && git checkout -b "$nombre" \
        && ok "Creada $nombre desde $rama_base."
      ;;
    *) warn "Cancelado."; return ;;
  esac

  echo
  if confirm "¿Subir $nombre al remoto ahora (push -u)?"; then
    git push -u origin "$nombre" && ok "Subida y trackeando origin/$nombre."
  else
    info "Queda solo local. La subís cuando quieras con la opción 'Actualizar remoto'."
  fi
}

ver_log() {
  echo "Vista de log:"
  echo "  1) Grafo de todas las ramas (oneline)   ← recomendada"
  echo "  2) Log completo de la rama actual"
  echo "  3) Con archivos tocados por commit (--stat)"
  echo "  4) Con diff completo (-p)"
  echo "  5) Filtrar por autor"
  echo "  6) Filtrar por archivo/carpeta"
  echo "  7) Últimos N commits (oneline)"
  read -rp "Opción: " opt
  echo
  case "$opt" in
    1) git log --oneline --graph --all --decorate ;;
    2) git log ;;
    3) git log --oneline --stat ;;
    4) git log -p ;;
    5) read -rp "Autor: " a; git log --oneline --author="$a" ;;
    6) read -rp "Ruta (ej backend/users/migrations/): " p; git log --oneline -- "$p" ;;
    7) read -rp "Cuántos: " n; git log --oneline -"${n:-10}" ;;
    *) warn "Opción inválida." ;;
  esac
}

ver_diff() {
  echo "  1) Cambios sin stage (working tree)"
  echo "  2) Cambios en stage (lo que iría al commit)"
  echo "  3) Todo (working + stage)"
  echo "  4) Diff contra otra rama"
  read -rp "Opción: " opt
  echo
  case "$opt" in
    1) git diff ;;
    2) git diff --cached ;;
    3) git diff HEAD ;;
    4) read -rp "Rama a comparar: " r; git diff "$r" ;;
    *) warn "Opción inválida." ;;
  esac
}

commitear() {
  if ! has_changes; then
    info "No hay cambios para commitear. Working tree limpio."
    return
  fi
  echo "${C_BOLD}Estado actual:${C_RESET}"
  git status --short
  echo
  echo "  1) Agregar TODO (git add -A) y commitear"
  echo "  2) Elegir archivos a agregar"
  echo "  3) Cancelar"
  read -rp "Opción: " opt
  case "$opt" in
    1) git add -A ;;
    2)
      git status --short
      read -rp "Archivos (separados por espacio): " files
      # shellcheck disable=SC2086
      git add $files
      ;;
    *) warn "Cancelado."; return ;;
  esac
  read -rp "Mensaje del commit: " msg
  [[ -z "$msg" ]] && { warn "Mensaje vacío, cancelado."; return; }
  git commit -m "$msg" && ok "Commit hecho."
}

actualizar_local() {
  local br; br="$(current_branch)"
  echo "  1) Pull de la rama actual ($br)"
  echo "  2) Fetch + prune (traer refs sin mergear)"
  echo "  3) Pull con rebase (historia más limpia)"
  read -rp "Opción: " opt
  echo
  case "$opt" in
    1)
      if has_changes; then
        warn "Tenés cambios sin commitear; un pull podría frenar o ensuciar. Commiteá/stasheá antes."
        confirm "¿Seguir igual?" || return
      fi
      git pull origin "$br"
      ;;
    2) git fetch origin --prune && ok "Refs actualizados (no se mergeó nada)." ;;
    3)
      if has_changes; then warn "Stasheá o commiteá antes de un rebase."; return; fi
      git pull --rebase origin "$br"
      ;;
    *) warn "Opción inválida." ;;
  esac
}

actualizar_remoto() {
  local br; br="$(current_branch)"
  local upstream
  upstream=$(git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null || echo "")

  if [[ -z "$upstream" ]]; then
    warn "La rama '$br' no tiene upstream en el remoto."
    if confirm "¿Subirla con push -u origin $br?"; then
      git push -u origin "$br" && ok "Subida y trackeando."
    fi
    return
  fi

  info "Push de $br → $upstream"
  git push && ok "Remoto actualizado."
}

ver_prs() {
  if ! command -v gh >/dev/null 2>&1; then
    warn "No tenés instalado el GitHub CLI (gh), necesario para ver PRs desde la terminal."
    echo "  Instalación: https://cli.github.com/"
    echo "  Después: gh auth login"
    return
  fi
  if ! gh auth status >/dev/null 2>&1; then
    warn "gh está instalado pero no autenticado. Corré: gh auth login"
    return
  fi
  echo "  1) Listar PRs abiertos"
  echo "  2) Listar todos los PRs (incl. cerrados/mergeados)"
  echo "  3) Ver detalle de un PR"
  echo "  4) PRs que apuntan a la rama actual"
  read -rp "Opción: " opt
  echo
  case "$opt" in
    1) gh pr list ;;
    2) gh pr list --state all ;;
    3) read -rp "Número de PR: " n; gh pr view "$n" ;;
    4) gh pr list --base "$(current_branch)" ;;
    *) warn "Opción inválida." ;;
  esac
}

gestionar_stash() {
  echo "  1) Ver lista de stashes"
  echo "  2) Guardar cambios actuales (stash push)"
  echo "  3) Recuperar el último (stash pop)"
  echo "  4) Aplicar uno sin borrarlo (stash apply)"
  echo "  5) Ver contenido de un stash"
  echo "  6) Borrar un stash"
  read -rp "Opción: " opt
  echo
  case "$opt" in
    1) git stash list ;;
    2) read -rp "Mensaje (opcional): " m; git stash push -m "${m:-wip}" && ok "Guardado." ;;
    3) git stash pop && ok "Recuperado (se aplicó sobre $(current_branch))." ;;
    4) read -rp "Índice (ej 0): " i; git stash apply "stash@{${i:-0}}" ;;
    5) read -rp "Índice (ej 0): " i; git stash show -p "stash@{${i:-0}}" ;;
    6) read -rp "Índice (ej 0): " i; confirm "¿Borrar stash@{$i}?" && git stash drop "stash@{$i}" ;;
    *) warn "Opción inválida." ;;
  esac
}

sincronizar() {
  local br; br="$(current_branch)"
  echo "Traer a '$br' lo último de la rama de integración:"
  echo "  1) Merge desde develop"
  echo "  2) Merge desde main"
  echo "  3) Rebase sobre develop"
  read -rp "Opción: " opt

  if has_changes; then
    err "Tenés cambios sin commitear. Commiteá o stasheá antes de mergear/rebasear."
    return
  fi

  case "$opt" in
    1) git fetch origin develop && git merge origin/develop ;;
    2) git fetch origin main && git merge origin/main ;;
    3) git fetch origin develop && git rebase origin/develop ;;
    *) warn "Opción inválida."; return ;;
  esac
  warn "Si hubo conflictos, resolvelos y después: git add <archivos> && git commit (o git rebase --continue)."
  warn "Recordá el cuidado con migraciones (numeración) antes de mergear hacia la rama del equipo."
}

backup_rama() {
  local br; br="$(current_branch)"
  local nombre="backup/${br//\//-}-$(date +%Y%m%d-%H%M)"
  git branch "$nombre" && ok "Backup creado: $nombre (apunta al estado actual de $br)."
  info "Si todo sale bien después, lo borrás con: git branch -D $nombre"
}

borrar_rama() {
  warn "Operación destructiva. Antes de borrar, pensá: ¿esta rama fue base de otras / tiene PR abierto?"
  echo "  Si sí → NO borrar (ver convención: branches legacy se dejan)."
  echo
  read -rp "Rama a borrar: " rama
  [[ -z "$rama" ]] && { warn "Cancelado."; return; }
  if [[ "$rama" == "$(current_branch)" ]]; then
    err "No podés borrar la rama en la que estás parado."
    return
  fi

  if confirm "¿Dejar un backup local antes de borrar ($rama)?"; then
    git branch "backup/${rama//\//-}-$(date +%Y%m%d-%H%M)" "$rama" && ok "Backup hecho."
  fi

  echo "  1) Borrar solo local"
  echo "  2) Borrar local + remoto"
  read -rp "Opción: " opt
  case "$opt" in
    1) git branch -d "$rama" || { warn "Tiene commits sin mergear."; confirm "¿Forzar (-D)?" && git branch -D "$rama"; } ;;
    2)
      git branch -d "$rama" || { warn "Sin mergear."; confirm "¿Forzar local (-D)?" && git branch -D "$rama"; }
      warn "Borrar del remoto cierra PRs que apunten a esta rama."
      confirm "¿Borrar también origin/$rama?" && git push origin --delete "$rama"
      ;;
    *) warn "Cancelado." ;;
  esac
}

# =====================================================================
#  MENÚ PRINCIPAL
# =====================================================================

menu() {
  clear
  local br estado
  br="$(current_branch)"
  if has_changes; then estado="${C_YELLOW}$(changes_summary)${C_RESET}"; else estado="${C_GREEN}limpio${C_RESET}"; fi

  echo "${C_BOLD}╔══════════════════════════════════════════════╗${C_RESET}"
  echo "${C_BOLD}║        Git Helper — Mentor Virtual           ║${C_RESET}"
  echo "${C_BOLD}╚══════════════════════════════════════════════╝${C_RESET}"
  echo "Rama: ${C_GREEN}${br}${C_RESET}   |   Estado: ${estado}"
  echo "──────────────────────────────────────────────"
  echo "  ${C_BOLD}1${C_RESET}) Ver ramas (local + remoto)"
  echo "  ${C_BOLD}2${C_RESET}) Ver estado (git status)"
  echo "  ${C_BOLD}3${C_RESET}) Cambiar de rama"
  echo "  ${C_BOLD}4${C_RESET}) Crear rama nueva  ${C_DIM}(valida convención)${C_RESET}"
  echo "  ${C_BOLD}5${C_RESET}) Ver git log"
  echo "  ${C_BOLD}6${C_RESET}) Ver cambios / diff"
  echo "  ${C_BOLD}7${C_RESET}) Commitear cambios"
  echo "  ${C_BOLD}8${C_RESET}) Actualizar local (pull/fetch)"
  echo "  ${C_BOLD}9${C_RESET}) Actualizar remoto (push)"
  echo " ${C_BOLD}10${C_RESET}) Ver Pull Requests  ${C_DIM}(gh)${C_RESET}"
  echo " ${C_BOLD}11${C_RESET}) Stash (guardar/recuperar cambios)"
  echo " ${C_BOLD}12${C_RESET}) Sincronizar con develop/main"
  echo " ${C_BOLD}13${C_RESET}) Backup de la rama actual"
  echo " ${C_BOLD}14${C_RESET}) Borrar rama  ${C_DIM}(con cuidado)${C_RESET}"
  echo "  ${C_BOLD}0${C_RESET}) Salir"
  echo "──────────────────────────────────────────────"
  read -rp "Opción: " choice
  echo

  case "$choice" in
    1) ver_ramas ;;
    2) ver_estado ;;
    3) cambiar_rama ;;
    4) crear_rama ;;
    5) ver_log ;;
    6) ver_diff ;;
    7) commitear ;;
    8) actualizar_local ;;
    9) actualizar_remoto ;;
    10) ver_prs ;;
    11) gestionar_stash ;;
    12) sincronizar ;;
    13) backup_rama ;;
    14) borrar_rama ;;
    0) echo "Chau."; exit 0 ;;
    *) warn "Opción inválida." ;;
  esac
  pause
}

while true; do
  menu
done
