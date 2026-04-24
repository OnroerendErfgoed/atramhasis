<template>
  <UModal
    v-model:open="conceptschemeModalIsOpen"
    :title="t('components.modalProvider.title')"
    :description="t('components.modalProvider.description')"
  >
    <template #body>
      <UForm class="space-y-4">
        <pre>{{ selectedConceptscheme }}</pre>
      </UForm>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" class="cursor-pointer" @click="close" />
        <UButton :label="t('actions.save')" class="cursor-pointer" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptschemeModalIsOpen } = storeToRefs(adminUiStore);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);

const save = () => {
  console.log('Save button clicked');
};
</script>
