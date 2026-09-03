<template>
  <UApp :toaster="{ position: 'top-right' }">
    <RouterView />
    <ALoader v-if="adminUiStore.isFullscreenLoading" />
  </UApp>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { useAuthStore } from '@stores/auth';
import { useListStore } from '@stores/list';
import { onBeforeMount } from 'vue';

const adminUiStore = useAdminUiStore();
const listStore = useListStore();
const authStore = useAuthStore();

onBeforeMount(async () => {
  await authStore.fetchUserInfo();
  await listStore.getAll();
});
</script>
