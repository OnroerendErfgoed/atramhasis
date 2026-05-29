import ui from '@nuxt/ui/vite';
import vue from '@vitejs/plugin-vue';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'path';
import { URL, fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite';

import vueDevTools from 'vite-plugin-vue-devtools';

const outDir = resolve(__dirname, '../atramhasis/static');
const developmentIniPath = resolve(__dirname, '../development.ini');

function getAtramhasisUrlFromIni(defaultUrl: string): string {
  if (!existsSync(developmentIniPath)) {
    return defaultUrl;
  }

  const content = readFileSync(developmentIniPath, 'utf-8');
  const match = content.match(/^\s*atramhasis\.url\s*=\s*(.+)\s*$/m);
  return match?.[1]?.trim() || defaultUrl;
}

const atramhasisUrl = getAtramhasisUrlFromIni('http://localhost:6543');

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    vueDevTools(),
    ui(),
    VueI18nPlugin({
      include: resolve(__dirname, './src/locales/**'),
    }),
    viteStaticCopy({
      targets: [
        { src: 'static/**/*', dest: '.', rename: { stripBase: 1 } },
        {
          src: 'node_modules/foundation-sites/js/**/*',
          dest: '.',
        },
        {
          src: 'node_modules/d3/d3.min.js',
          dest: '.',
        },
      ],
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
      '@composables': fileURLToPath(new URL('./src/composables', import.meta.url)),
      '@services': fileURLToPath(new URL('./src/services', import.meta.url)),
      '@stores': fileURLToPath(new URL('./src/stores', import.meta.url)),
      '@models': fileURLToPath(new URL('./src/models', import.meta.url)),
      '@enums': fileURLToPath(new URL('./src/enums', import.meta.url)),
      '@views': fileURLToPath(new URL('./src/views', import.meta.url)),
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    cors: true,
    origin: atramhasisUrl,
  },
});
