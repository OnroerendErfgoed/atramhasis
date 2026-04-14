<template>
  <div class="flex min-h-screen w-full bg-muted/30">
    <USidebar
      v-model:open="open"
      collapsible="icon"
      rail
      :ui="{
        root: 'border-r border-default',
        container: 'h-screen',
        inner: 'bg-neutral-950 text-white divide-white/10',
        header: 'px-4 py-5',
        body: 'px-3 py-2',
        footer: 'px-3 py-4',
      }"
    >
      <template #header="{ state }">
        <RouterLink to="/" class="flex items-center gap-3 overflow-hidden">
          <img src="/static/img/atramlogo.png" alt="Atramhasis" class="h-10 w-auto shrink-0" />

          <div v-if="state === 'expanded'" class="min-w-0">
            <p class="truncate text-[11px] font-semibold uppercase tracking-[0.28em] text-white/50">Admin</p>
            <p class="truncate text-sm font-semibold text-white">Atramhasis</p>
          </div>
        </RouterLink>
      </template>

      <template #default="{ state }">
        <div class="space-y-4">
          <div class="border-b border-white/10 pb-4">
            <div
              class="flex rounded-2xl border border-white/15 bg-linear-to-br from-white/10 to-white/5 p-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]"
              :class="state === 'expanded' ? 'items-center gap-3' : 'justify-center'"
            >
              <div
                class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-emerald-200 text-xl font-semibold tracking-[-0.02em] text-slate-900"
              >
                JD
              </div>

              <div v-if="state === 'expanded'" class="min-w-0 text-left">
                <p class="truncate text-xl leading-tight font-medium text-white">John Doe</p>
                <UBadge
                  color="neutral"
                  variant="outline"
                  size="sm"
                  class="mt-1 border-white/25 bg-slate-700/30 text-sm font-medium text-white/90"
                >
                  Admin
                </UBadge>
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
              link: 'min-h-11 rounded-lg px-3 text-sm text-white/80 hover:bg-white/5 hover:text-white data-[active=true]:bg-white/10 data-[active=true]:text-white',
              label: 'px-3 text-[11px] font-semibold uppercase tracking-[0.24em] text-white/35',
              content: 'border border-white/10 bg-neutral-900',
              childLink: 'text-white/70 hover:text-white',
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
            class="w-full justify-start text-white/70 hover:bg-white/5 hover:text-white"
            :label="state === 'expanded' ? 'Back to homepage' : undefined"
            :ui="{ leadingIcon: 'size-4' }"
            @click="navigateToHomepage"
          />

          <UButton
            color="neutral"
            variant="ghost"
            icon="i-lucide-log-out"
            class="w-full justify-start text-white/70 hover:bg-white/5 hover:text-white"
            :label="state === 'expanded' ? 'Log out' : undefined"
            :ui="{ leadingIcon: 'size-4' }"
            @click.prevent
          />
        </div>
      </template>
    </USidebar>

    <UMain class="min-w-0 flex-1">
      <div class="flex min-h-screen flex-col">
        <header class="flex h-16 items-center gap-3 border-b border-default bg-default/95 px-4 backdrop-blur">
          <UButton
            icon="i-lucide-panel-left"
            color="neutral"
            variant="ghost"
            aria-label="Toggle sidebar"
            @click="open = !open"
          />

          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-highlighted">
              {{ currentSectionTitle }}
            </h1>
          </div>
        </header>

        <main class="min-h-0 flex-1 overflow-auto p-6">
          <div class="mx-auto w-full max-w-7xl">
            <Suspense>
              <template #fallback>
                <div class="flex items-center justify-center py-20">
                  <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-primary" />
                </div>
              </template>
              <RouterView />
            </Suspense>
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

const open = ref(true);
const route = useRoute();

const navigationItems = computed<NavigationMenuItem[][]>(() => [
  [
    {
      label: 'Concept schemes',
      icon: 'i-lucide-book-marked',
      to: { name: 'AdminConceptschemes' },
    },
    {
      label: 'Providers',
      icon: 'i-lucide-database',
      disabled: true,
    },
    {
      label: 'Languages',
      icon: 'i-lucide-languages',
      disabled: true,
    },
    {
      label: 'Users',
      icon: 'i-lucide-users',
      disabled: true,
    },
  ],
]);

const sectionTitles: Record<string, string> = {
  AdminConceptschemes: 'Manage concept schemes',
};

const currentSectionTitle = computed(() => {
  const routeName = typeof route.name === 'string' ? route.name : '';
  return sectionTitles[routeName] ?? 'Atramhasis administration';
});

const navigateToHomepage = () => {
  window.location.assign('/');
};
</script>
