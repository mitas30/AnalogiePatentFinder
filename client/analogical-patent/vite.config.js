import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import dotenv from 'dotenv'

dotenv.config()

const API_URL=process.env.DOCKER_API_URL || process.env.VITE_API_URL;
console.log("API_URLは",API_URL)

// https://vitejs.dev/config/
// viteの設定ファイル
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server:{
    host:'0.0.0.0',
    port:5173,
    proxy:{
      '/api':{
        target: API_URL,
        changeOrigin:true,
      }
    }
  },
  logLevel: 'info',
})
