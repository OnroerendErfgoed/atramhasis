<template>
  <UApp :toaster="{ position: 'top-right' }">
    <RouterView />
  </UApp>
</template>

<script setup lang="ts">
import { useLanguageStore } from '@stores/language';
import { onBeforeMount } from 'vue';

const languageStore = useLanguageStore();

onBeforeMount(async () => {
  await languageStore.fetchLanguages();
});
</script>
