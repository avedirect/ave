import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2020',
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        // Keep the animation libs out of the critical bundle so the
        // above-the-fold paint is not blocked by them.
        manualChunks(id: string) {
          if (id.includes('node_modules/gsap')) return 'gsap'
          if (id.includes('node_modules/framer-motion') || id.includes('node_modules/motion-dom'))
            return 'motion'
          if (id.includes('node_modules/hls.js')) return 'hls'
          return undefined
        },
      },
    },
  },
})
