<template>
  <UModal
    v-model:open="conceptschemeModalIsOpen"
    :title="t('components.modalConceptscheme.title', { conceptscheme: selectedConceptscheme?.label })"
    :description="t('components.modalConceptscheme.description', { tab: tabs[+activeTab]?.label })"
    class="max-w-4xl"
  >
    <template #body>
      <UTabs v-model="activeTab" color="neutral" variant="link" :items="tabs" class="w-full">
        <template #labels>
          <ModalConceptschemeTabLabels :data="labelsWithAddRow" @add="addLabel" />
        </template>

        <template #notes>
          <ModalConceptschemeTabNotes :data="notesWithAddRow" @add="addNote" />
        </template>

        <template #sources>
          <ModalConceptschemeTabSources :data="sourcesWithAddRow" @add="addSource" />
        </template>
      </UTabs>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" class="cursor-pointer" @click="close" />
        <UButton :label="t('actions.save')" class="cursor-pointer" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script lang="ts">
export type TableRow<T> = T & {
  isAddRow?: boolean;
};
</script>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import type { TabsItem } from '@nuxt/ui';
import { computed, ref } from 'vue';
import { type Label, type Note, type Source } from '@models/util';

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptschemeModalIsOpen } = storeToRefs(adminUiStore);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);

const activeTab = ref('0');
const tabs = ref<TabsItem[]>([
  {
    label: t('components.modalConceptscheme.tabs.labels'),
    slot: 'labels',
  },
  {
    label: t('components.modalConceptscheme.tabs.notes'),
    slot: 'notes',
  },
  {
    label: t('components.modalConceptscheme.tabs.sources'),
    slot: 'sources',
  },
]);

const save = () => {
  console.log('Save button clicked');
};

const addLabel = () => {
  console.log('Add label clicked');
};

const addNote = () => {
  console.log('Add note clicked');
};

const addSource = () => {
  console.log('Add source clicked');
};

/* Table data */
const labelsWithAddRow = computed<TableRow<Label>[]>(() => [
  ...((selectedConceptscheme.value?.labels ?? []) as TableRow<Label>[]),
  {
    isAddRow: true,
  } as TableRow<Label>,
]);

const notesWithAddRow = computed<TableRow<Note>[]>(() => [
  ...((selectedConceptscheme.value?.notes ?? []) as TableRow<Note>[]),
  {
    isAddRow: true,
  } as TableRow<Note>,
]);

const sourcesWithAddRow = computed<TableRow<Source>[]>(() => [
  ...((selectedConceptscheme.value?.sources ?? []) as TableRow<Source>[]),
  {
    isAddRow: true,
  } as TableRow<Source>,
]);
</script>
