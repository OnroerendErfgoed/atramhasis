<template>
  <ModalRelation :key="relationModalKey" :title="t('components.modalRelation.title', { item: '' })" :scheme="scheme" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';

defineProps<{
  scheme: string;
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { relationModalKey } = storeToRefs(adminUiStore);
</script>
