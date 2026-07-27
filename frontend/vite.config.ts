import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// vite.config.ts corre en Node (no en el browser), así que puede leer
// cualquier variable de entorno del proceso — no hace falta el prefijo VITE_
// acá (ese prefijo solo aplica a lo que se expone al cliente vía import.meta.env).
// BACKEND_INTERNAL_URL es la URL que el proceso de Vite (dentro del contenedor
// frontend) usa para hablar con el backend por la red interna de Docker —
// por eso el default es el nombre del servicio ('backend'), no 'localhost'.
const backendTarget = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // HMR polling para Windows con Docker (inotify no se propaga entre host y contenedor)
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/admin': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/static': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
