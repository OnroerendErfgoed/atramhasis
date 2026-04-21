import './assets/css/main.css';
import App from './App.vue';
import router from './router';
import ui from '@nuxt/ui/vue-plugin';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createI18n } from 'vue-i18n';
import en from './locales/en.json';

const i18n = createI18n({
  legacy: false, // use Composition API mode
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en },
});

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(ui);
app.use(i18n);

app.mount('#app');
