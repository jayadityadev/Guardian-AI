import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/ingest': {
        target: 'https://guardian-ai-api-c2d5132c.fastapicloud.dev',
        changeOrigin: true,
      },
      '/session': {
        target: 'https://guardian-ai-api-c2d5132c.fastapicloud.dev',
        changeOrigin: true,
      },
      '/sessions': {
        target: 'https://guardian-ai-api-c2d5132c.fastapicloud.dev',
        changeOrigin: true,
      },
      '/health': {
        target: 'https://guardian-ai-api-c2d5132c.fastapicloud.dev',
        changeOrigin: true,
      },
      '/ws': {
        target: 'wss://guardian-ai-api-c2d5132c.fastapicloud.dev',
        ws: true,
      },
    },
  },
})
