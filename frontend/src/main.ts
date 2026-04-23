import './assets/css/main.css';
import App from './App.vue';
import router from './router';
import ui from '@nuxt/ui/vue-plugin';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import i18n from './i18n';

const app = createApp(App);

app.use(i18n);
app.use(createPinia());
app.use(router);
app.use(ui);

app.mount('#app');
