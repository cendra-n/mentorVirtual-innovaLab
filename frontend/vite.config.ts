import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',      // necesario para que Docker exponga el puerto
    port: 5173,
    proxy: {
      // Todas las llamadas a /api/* van al Django en dev
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        // Si el Django corre local (fuera de Docker): 'http://localhost:8000'
      },
      '/admin': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
