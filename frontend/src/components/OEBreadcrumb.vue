<template>
  <UBreadcrumb :items="items" />
</template>

<script setup lang="ts">
import type { BreadcrumbItem } from '@nuxt/ui';
import type { UrlParams } from '@vueuse/core';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const currentRoute = useRoute();
const router = useRouter();

const items = computed(() => {
  const paths = currentRoute.path.split('/');
  paths.shift(); // Remove the first empty string from the split
  const crumbs: BreadcrumbItem[] = [];
  console.log(paths);
  paths.forEach((path, i) => {
    const route = router.resolve({ path: `/${paths.slice(0, i + 1).join('/')}` });
    const breadcrumbLabel = route.meta.breadcrumb as (params?: UrlParams) => string;
    if (!breadcrumbLabel || !crumbs.every((b) => b.label !== breadcrumbLabel(currentRoute.params))) return;
    crumbs.push({
      label: (breadcrumbLabel ? breadcrumbLabel(currentRoute.params) : '').toUpperCase(),
      href: route.fullPath,
    });
  });
  return crumbs;
});
</script>
