import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/kelpie-carbon/dashboard/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
})
