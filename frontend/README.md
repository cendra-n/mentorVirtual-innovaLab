# Mentor Virtual Adaptativo — Frontend

Frontend React + TypeScript + Vite para la plataforma de acompañamiento educativo con IA.

---

## 🧩 Stack y Componentes

### Tecnologías base
- **React 18** + **TypeScript** + **Vite 5** con HMR
- **@vitejs/plugin-react-swc** — compilación ultra rápida con SWC
- **Obelisco v2** (`@gcba/obelisco-v2`) — design system oficial del GCBA

### Páginas
| Página | Descripción |
|--------|-------------|
| `Login` | Login por email + JWT, registro con validación, indicador fuerza de contraseña |
| `Dashboard` | Vista principal con hero banner, lista de metas y acceso al tutor |
| `GoalDetail` | Plan de aprendizaje con pasos, videos YouTube en modal y robot tutor por paso |
| `TutorPage` | Subir PDFs y hacer preguntas al tutor RAG |
| `Profile` | Ver y editar perfil, cambiar contraseña |
| `AdminPanel` | Gestión de usuarios y estadísticas (solo ADMIN/staff) |

### Componentes
| Componente | Descripción |
|------------|-------------|
| `MentorBot` | Robot SVG animado con 8 estados emocionales (feliz, pensativo, ayudando, etc.) |
| `Sidebar` | Navegación lateral con streak y acceso al panel admin para staff |
| `MentorChat` | Chat flotante con el mentor, respuestas contextuales |
| `TutorFloatingChat` | Robot por paso — busca en libros del usuario y responde con RAG |
| `GoalCard` | Tarjeta de meta con progreso y botón eliminar (según rol) |
| `WeekStreak` | Calendario semanal de actividad |
| `NewGoalModal` | Modal para crear nueva meta con generación IA |

### Servicios
- `api.ts` — capa de comunicación con el backend Django vía `/api/*` (proxy Vite → Django)

---

## 🚀 Levantar en desarrollo

```bash
npm install
npm run dev
```

Vite levanta en `http://localhost:5173` con HMR. Las llamadas a `/api/*` van via proxy al backend Django en `:8000`.

### Con Docker
```bash
docker compose up frontend
```

---

## ⚙️ Variables de entorno

Creá un archivo `.env` en la raíz del frontend (o en la raíz del proyecto):

```bash
VITE_APP_NAME=Mentor Virtual     # Nombre mostrado en el header y título
VITE_MENTOR_NAME=Pulso           # Nombre del robot mentor
VITE_API_URL=http://localhost:8000  # Solo referencia, no se usa directamente (el proxy maneja las llamadas)
```

> Las variables de Vite deben empezar con `VITE_` para ser accesibles en el código React.

---

## 🔌 Proxy al backend

El `vite.config.ts` redirige todas las llamadas `/api/*` al backend Django sin CORS:

```ts
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',  // nombre del servicio Docker
      changeOrigin: true,
    }
  }
}
```

En desarrollo local sin Docker cambiar el target a `http://localhost:8000`.

---

## 🏗️ Build para producción

```bash
npm run build
```

Genera el directorio `dist/` que Nginx sirve estáticamente en producción.

---

## 🔍 ESLint — Configuración recomendada para producción

Para habilitar reglas con type-checking en `eslint.config.js`:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      tseslint.configs.recommendedTypeChecked,
      tseslint.configs.stylisticTypeChecked,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
])
```

Plugins adicionales recomendados:  2
  3
  4
  5
  6
  7
  8  2
  3
  4
  5
  6
  7
  8
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
 37
 38
 39
 40
 41
 42
 43
 44
 45
 46
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:  2
  3
  4
  5
  6
  7
  8
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
 37
 38
 39
 40
 41
 42
 43
 44
 45
 46
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
 37
 38
 39
 40
 41
 42
 43
 44
 45
 46
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)
  2
  3
  4
  5
  6
  7
  8
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
 37
 38
 39
 40
 41
 42
 43
 44
 45
 46
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([

```js
import reactX   from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

// En extends:
reactX.configs['recommended-typescript'],
reactDom.configs.recommended,
```

---

## 📦 Dependencias principales

```bash
npm install @gcba/obelisco-v2   # Design system GCBA
```

El resto de dependencias están en `package.json`.
