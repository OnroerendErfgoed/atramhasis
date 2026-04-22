import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/admin',
      name: 'AdminOverview',
      component: () => import('@views/AdminOverview.vue'),
      redirect: { name: 'AdminConceptschemes' },
      children: [
        {
          path: 'conceptschemes',
          name: 'AdminConceptschemes',
          component: () => import('@views/AdminConceptschemes.vue'),
        },
        {
          path: 'providers',
          name: 'AdminProviders',
          component: () => import('@views/AdminProviders.vue'),
          meta: {
            breadcrumb: () => 'PROVIDERS',
          },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'AdminOverview' },
    },
  ],
});

export default router;
