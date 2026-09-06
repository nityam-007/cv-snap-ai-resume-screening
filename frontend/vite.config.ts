import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 3000,
  },
  define: {
    // Polyfill process.env for CJS packages that reference it in browser builds
    'process.env': {},
    global: 'globalThis',
  },
});
