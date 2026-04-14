import ui from '@nuxt/ui/vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import { URL, fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';

import vueDevTools from 'vite-plugin-vue-devtools';

const outDir = resolve(__dirname, '../atramhasis/static');

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    vueDevTools(),
    ui(),
    viteStaticCopy({
      targets: [{ src: 'static/**/*', dest: '.', rename: { stripBase: 1 } }],
    }),
  ],
  build: {
    outDir,
    manifest: 'dist/.vite/manifest.json',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, './src/main.ts'),
      },
      output: {
        entryFileNames: 'dist/[name].[hash].js',
        chunkFileNames: 'dist/[name].[hash].js',
        assetFileNames: 'dist/[name].[hash].[ext]',
        sourcemap: false,
      },
    },
  },
  resolve: {
    alias: {
      '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      '@services': fileURLToPath(new URL('./src/services', import.meta.url)),
      '@models': fileURLToPath(new URL('./src/models', import.meta.url)),
      '@views': fileURLToPath(new URL('./src/views', import.meta.url)),
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    cors: true,
    origin: 'http://local.onroerenderfgoed.be:6543',
  },
});
