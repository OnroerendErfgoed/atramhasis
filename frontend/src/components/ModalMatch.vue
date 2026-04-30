<template>
  <UModal
    v-model:open="matchModalIsOpen"
    :dismissible="false"
    :title="title"
    :description="capitalize(t('components.modalMatch.description'))"
  >
    <template #body> form </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.add')" @click="add" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { storeToRefs } from 'pinia';
import { capitalize } from 'vue';
import { useI18n } from 'vue-i18n';

defineProps<{
  title: string;
}>();

const emit = defineEmits<{
  add: [void];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { matchModalIsOpen } = storeToRefs(adminUiStore);

const add = () => {
  emit('add');
};
</script>
