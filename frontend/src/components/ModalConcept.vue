<template>
  <UModal
    v-model:open="conceptModalIsOpen"
    :dismissible="false"
    :title="t('components.modalConcept.title', { conceptscheme: selectedConceptscheme?.label })"
    :description="t('components.modalConcept.description', { mode: isEditMode ? t('actions.edit') : t('actions.add') })"
    class="max-w-4xl"
  >
    <template #body>
      <UTabs v-model="activeTab" color="neutral" variant="link" :items="tabs" class="w-full">
        <template #labels> labels </template>

        <template #notes> notes </template>

        <template #sources> sources </template>

        <template #relations> relations </template>

        <template #matches> matches </template>
      </UTabs>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.save')" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import type { TabsItem } from '@nuxt/ui';
import { capitalize, computed, ref } from 'vue';
// import { ApiService } from '@services/api.service';
import { useApiError } from '@composables/useApiError';
import { useConceptStore } from '@stores/concept';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { ModalMode } from '@models/util';

const toast = useToast();
const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptModalIsOpen, conceptModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => conceptModalMode.value === ModalMode.EDIT);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const conceptStore = useConceptStore();
const { selectedConcept } = storeToRefs(conceptStore);

// const apiService = new ApiService();
const { handleApiError } = useApiError();
const CONCEPT_MODAL_LOADING_KEY = 'concept-modal-submit';

const activeTab = ref('0');
const tabs = ref<TabsItem[]>([
  {
    label: t('components.modalConcept.tabs.labels'),
    slot: 'labels',
  },
  {
    label: t('components.modalConcept.tabs.notes'),
    slot: 'notes',
  },
  {
    label: t('components.modalConcept.tabs.sources'),
    slot: 'sources',
  },
  {
    label: t('components.modalConcept.tabs.relations'),
    slot: 'relations',
  },
  {
    label: t('components.modalConcept.tabs.matches'),
    slot: 'matches',
  },
]);

// Save handler
const save = async () => {
  if (!selectedConcept.value) return;
  try {
    adminUiStore.startLoading(CONCEPT_MODAL_LOADING_KEY);

    // await apiService.updateConcept(selectedConcept.value);
    toast.add({
      title: t('api.success.update.title', { item: capitalize(t('entities.concept')) }),
      description: t('api.success.update.description', { item: t('entities.concept') }),
      icon: 'i-lucide-check-circle',
      color: 'success',
    });
    adminUiStore.closeConceptModal();
  } catch (error) {
    handleApiError(error);
  } finally {
    adminUiStore.stopLoading(CONCEPT_MODAL_LOADING_KEY);
  }
};
</script>
