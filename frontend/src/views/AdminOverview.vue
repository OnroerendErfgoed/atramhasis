<template>
  <div class="flex h-screen w-full bg-muted/30">
    <USidebar
      v-model:open="open"
      collapsible="icon"
      rail
      :menu="{
        ui: {
          overlay: 'bg-primary-100 backdrop-blur-[2px]',
          content: 'bg-primary-950 text-white divide-y divide-primary-700/30',
          header: 'px-4 py-5',
          body: 'px-3 py-2',
          footer: 'px-3 py-4',
          title: 'text-white',
          description: 'text-primary-100/70',
          close:
            'text-primary-100/70 hover:text-white hover:bg-primary-200/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-200/70',
        },
      }"
      :ui="{
        root: 'border-r border-default',
        container: 'h-screen',
        inner: 'bg-primary-950 text-white divide-y divide-primary-700/30',
        header: 'px-4 py-5',
        body: 'px-3 py-2',
        footer: 'px-3 py-4',
      }"
    >
      <template #header="{ state }">
        <RouterLink
          to="/"
          class="flex overflow-hidden"
          :class="state === 'expanded' ? 'items-center gap-3' : 'items-center justify-center'"
        >
          <img
            src="/static/img/atramlogo.png"
            alt="Atramhasis"
            class="shrink-0 object-contain"
            :class="state === 'expanded' ? 'h-10 w-auto' : 'h-10 w-10'"
          />

          <div v-if="state === 'expanded'" class="min-w-0">
            <p class="truncate text-[11px] font-semibold uppercase tracking-[0.28em] text-primary-100/55">Admin</p>
            <p class="truncate text-sm font-semibold text-white">Atramhasis</p>
          </div>
        </RouterLink>
      </template>

      <template #default="{ state }">
        <div class="space-y-4">
          <div class="border-b border-primary-700/30 pb-4">
            <div
              class="flex"
              :class="
                state === 'expanded'
                  ? 'items-center gap-3 rounded-2xl border border-primary-100/18 bg-primary-50/7 p-3 shadow-[inset_0_1px_0_color-mix(in_srgb,var(--ui-color-primary-50)_10%,transparent)] backdrop-blur-xs'
                  : 'justify-center py-1'
              "
            >
              <div
                class="flex shrink-0 items-center justify-center rounded-full bg-primary-300/34 font-semibold tracking-[-0.02em] text-primary-100"
                :class="state === 'expanded' ? 'h-14 w-14 text-xl' : 'h-12 w-12 text-lg'"
              >
                {{ userInitials }}
              </div>

              <div v-if="state === 'expanded'" class="min-w-0 text-left">
                <p class="text-xl leading-tight font-medium text-white wrap-break-word">{{ userDisplayName }}</p>
              </div>
            </div>
          </div>

          <UNavigationMenu
            :items="navigationItems"
            orientation="vertical"
            :collapsed="state === 'collapsed'"
            tooltip
            highlight
            class="w-full"
            :ui="{
              link: 'min-h-11 rounded-lg px-3 text-sm text-primary-50/82 hover:bg-primary-200/10 hover:text-white focus-visible:bg-primary-200/10 focus-visible:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-200/70 data-[active=true]:bg-primary-200/22 data-[active=true]:text-white data-[disabled=true]:cursor-not-allowed data-[disabled=true]:bg-transparent data-[disabled=true]:text-primary-100/38 [&_svg]:text-current [&_.iconify]:text-current [&_svg]:opacity-90 [&_.iconify]:opacity-90 data-[active=true]:[&_svg]:opacity-100 data-[active=true]:[&_.iconify]:opacity-100 data-[disabled=true]:[&_svg]:opacity-55 data-[disabled=true]:[&_.iconify]:opacity-55',
              label: 'px-3 text-[11px] font-semibold uppercase tracking-[0.24em] text-primary-100/42',
              content: 'border border-primary-100/14 bg-primary-950/75',
              childLink:
                'text-primary-50/72 hover:bg-primary-200/10 hover:text-white focus-visible:bg-primary-200/10 focus-visible:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-200/70',
            }"
          />
        </div>
      </template>

      <template #footer="{ state }">
        <div class="space-y-2">
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-lucide-house"
            class="w-full text-primary-50/72 hover:bg-primary-200/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-200/70"
            :class="state === 'expanded' ? 'justify-start' : 'justify-center px-0'"
            :label="state === 'expanded' ? t('overview.goToHomepage') : undefined"
            :ui="{ leadingIcon: 'size-4' }"
            @click="navigateToHomepage"
          />
        </div>
      </template>
    </USidebar>

    <UMain class="min-w-0 flex-1">
      <div class="flex h-full flex-col">
        <ABreadcrumb v-if="showBreadcrumb" />
        <header class="flex h-16 items-center gap-3 border-b border-default bg-default/95 px-4 backdrop-blur">
          <UButton
            icon="i-lucide-panel-left"
            color="neutral"
            variant="ghost"
            class="text-neutral-700 hover:bg-primary-50 hover:text-neutral-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-200/70"
            :aria-label="t('overview.toggleSidebar')"
            @click="open = !open"
          />

          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-neutral-900">
              {{ currentSectionTitle }}
            </h1>
          </div>

          <div v-if="currentSectionActions?.length > 0" class="ml-auto flex items-center gap-2">
            <UButton
              v-for="(action, index) in currentSectionActions"
              :key="index"
              :label="action.label"
              :icon="action.icon"
              color="primary"
              size="sm"
              @click="action.onClick"
            />
          </div>
        </header>

        <main class="min-h-0 flex-1 overflow-hidden p-6">
          <div class="mx-auto flex h-full w-full flex-col">
            <RouterView v-slot="{ Component, route: currentRoute }">
              <Suspense timeout="0">
                <component :is="Component" :key="currentRoute.fullPath" />
                <template #fallback>
                  <div class="flex items-center justify-center py-20">
                    <ALoader mode="inline" />
                  </div>
                </template>
              </Suspense>
            </RouterView>
          </div>
        </main>
      </div>
    </UMain>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import type { NavigationMenuItem } from '@nuxt/ui';
import { useAdminUiStore } from '@/stores/admin-ui';
import { useI18n } from 'vue-i18n';
import { ModalMode } from '@models/util';
import { useAuthStore } from '@stores/auth';
import { storeToRefs } from 'pinia';

const { t } = useI18n();
const adminUiStore = useAdminUiStore();

const open = ref(true);
const route = useRoute();

const routesWithBreadcrumb = ['AdminConceptscheme'];
const showBreadcrumb = computed(() => routesWithBreadcrumb.includes(route.name as string));

const authStore = useAuthStore();
const { userInfo } = storeToRefs(authStore);
const userDisplayName = computed(() => {
  const username = userInfo.value?.username || 'Admin';
  return username.replaceAll(',', '').trim();
});
const userInitials = computed(() => {
  const parts = userDisplayName.value.split(' ').filter(Boolean).slice(0, 2);
  if (!parts.length) {
    return 'A';
  }
  return parts.map((part) => part[0]?.toUpperCase() || '').join('');
});

const navigationItems = computed<NavigationMenuItem[][]>(() => [
  [
    {
      label: t('overview.nav.conceptschemes'),
      icon: 'i-lucide-book-marked',
      to: { name: 'AdminConceptschemes' },
    },
    {
      label: t('overview.nav.providers'),
      icon: 'i-lucide-database',
      to: { name: 'AdminProviders' },
    },
    {
      label: t('overview.nav.languages'),
      icon: 'i-lucide-languages',
      to: { name: 'AdminLanguages' },
    },
  ],
]);

const sectionTitles = computed<Record<string, string>>(() => ({
  AdminConceptschemes: t('header.titles.conceptschemes'),
  AdminConceptscheme: t('header.titles.conceptscheme', {
    item: adminUiStore.breadcrumbLabels[route.params.id as string] || '',
  }),
  AdminProviders: t('header.titles.providers'),
  AdminLanguages: t('header.titles.languages'),
}));

const currentSectionTitle = computed(() => {
  const routeName = typeof route.name === 'string' ? route.name : '';
  return sectionTitles.value[routeName] ?? 'Atramhasis administration';
});

const currentSectionActions = computed(() => {
  const routeName = typeof route.name === 'string' ? route.name : '';
  switch (routeName) {
    case 'AdminProviders':
      return [
        {
          label: t('overview.actions.addProvider'),
          icon: 'i-lucide-plus',
          onClick: () => adminUiStore.openProviderModal(ModalMode.ADD),
        },
      ];
    case 'AdminConceptscheme':
      return [
        {
          label: t('overview.actions.addConcept'),
          icon: 'i-lucide-plus',
          onClick: () => adminUiStore.openConceptModal(ModalMode.ADD),
        },
      ];
    case 'AdminLanguages':
      return [
        {
          label: t('overview.actions.addLanguage'),
          icon: 'i-lucide-plus',
          onClick: () => adminUiStore.openLanguageModal(ModalMode.ADD),
        },
      ];
    default:
      return [];
  }
});

const navigateToHomepage = () => {
  window.location.assign('/');
};
</script>
