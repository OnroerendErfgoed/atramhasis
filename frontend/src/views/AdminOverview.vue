<template>
  <div class="flex flex-1">
    <USidebar
      v-model:open="open"
      :ui="{
        container: 'h-full',
        inner: 'bg-elevated/25 divide-transparent',
        body: 'py-0',
      }"
    >
      <template #header>
        <img src="/atramlogo.png" alt="Atramhasis Logo" class="h-8 w-auto px-3" />
        ATRAMHASIS
      </template>
    </USidebar>

    <UMain class="flex-1">
      <RouterView />
    </UMain>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const open = ref(true);
</script>
