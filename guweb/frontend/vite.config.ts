import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.ts'),
        home: resolve(__dirname, 'src/pages/home.ts'),
        profile: resolve(__dirname, 'src/pages/profile.ts'),
        beatmap: resolve(__dirname, 'src/pages/beatmap.ts'),
        leaderboard: resolve(__dirname, 'src/pages/leaderboard.ts'),
        score: resolve(__dirname, 'src/pages/score.ts')
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
