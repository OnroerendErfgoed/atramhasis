<template>
  <UApp :toaster="{ position: 'top-right' }">
    <RouterView />
  </UApp>
</template>

<script setup lang="ts">
import { useListStore } from '@stores/list';
import { onBeforeMount } from 'vue';

const listStore = useListStore();

onBeforeMount(async () => {
  await listStore.getAll();
});
</script>
