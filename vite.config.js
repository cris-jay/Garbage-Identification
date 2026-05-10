import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/',
  server: {
    proxy: {
      '/api': {
        target: 'https://8ea7c3f2-97b7-4361-a46b-01a3a2f7b3ee.up.railway.app',
        changeOrigin: true
      }
    }
  }
})