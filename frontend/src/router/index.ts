import { createRouter, createWebHistory } from 'vue-router';
import { t } from '@/i18n';
import { useBreadcrumbStore } from '@stores/breadcrumb';
import type { UrlParams } from '@vueuse/core';

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
          meta: {
            breadcrumb: () => t('header.titles.conceptschemes'),
          },
        },
        {
          path: 'conceptschemes/:id',
          name: 'AdminConceptScheme',
          component: () => import('@views/AdminConceptScheme.vue'),
          meta: {
            breadcrumb: (params?: UrlParams) => {
              const breadcrumbStore = useBreadcrumbStore();
              return breadcrumbStore.labels[params?.id as string] ?? '';
            },
          },
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
