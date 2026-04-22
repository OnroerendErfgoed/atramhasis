<template>
  <UBreadcrumb v-if="items.every((item) => !!item.label)" :items="items" class="px-4 py-2">
    <template #separator>
      <span class="mx-2 text-muted">/</span>
    </template>
    <template #item-leading="{ index }">
      <UIcon v-if="index === 0" name="i-lucide-arrow-left" class="shrink-0 text-muted" />
    </template>
  </UBreadcrumb>
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
  paths.forEach((path, i) => {
    const route = router.resolve({ path: `/${paths.slice(0, i + 1).join('/')}` });
    const breadcrumbLabel = route.meta.breadcrumb as (params?: UrlParams) => string;
    if (!breadcrumbLabel || !crumbs.every((b) => b.label !== breadcrumbLabel(currentRoute.params))) return;
    crumbs.push({
      label: breadcrumbLabel ? breadcrumbLabel(currentRoute.params) : '',
      href: i < paths.length - 1 ? route.fullPath : undefined,
    });
  });
  return crumbs;
});
</script>
