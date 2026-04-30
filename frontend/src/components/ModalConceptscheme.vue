<template>
  <UModal
    v-model:open="conceptschemeModalIsOpen"
    :dismissible="false"
    :title="t('components.modalConceptscheme.title', { conceptscheme: selectedConceptscheme?.label })"
    :description="t('components.modalConceptscheme.description', { tab: tabs[+activeTab]?.label })"
    class="max-w-4xl"
  >
    <template #body>
      <UTabs v-model="activeTab" color="neutral" variant="link" :items="tabs" class="flex h-[34rem] w-full flex-col">
        <template #labels>
          <ModalTabLabels
            :data="labelsWithAddRow"
            :tab-title="selectedConceptscheme?.label ?? ''"
            @add="addLabel"
            @edit="editLabel"
            @delete="deleteLabel"
          />
        </template>

        <template #notes>
          <ModalTabNotes
            :data="notesWithAddRow"
            :tab-title="selectedConceptscheme?.label ?? ''"
            @add="addNote"
            @edit="editNote"
            @delete="deleteNote"
          />
        </template>

        <template #sources>
          <ModalTabSources
            :data="sourcesWithAddRow"
            :tab-title="selectedConceptscheme?.label ?? ''"
            @add="addSource"
            @edit="editSource"
            @delete="deleteSource"
          />
        </template>
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
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import type { TabsItem } from '@nuxt/ui';
import { capitalize, computed, onBeforeMount, ref } from 'vue';
import { type Label, type Note, type Source } from '@models/util';
import { ApiService } from '@services/api.service';
import { useApiError } from '@composables/useApiError';
import type { TableRow } from '@components/ModalTabTable.vue';
import type { ConceptschemeForm } from '@models/conceptscheme';
import { cloneDeep } from 'lodash-es';

const toast = useToast();
const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptschemeModalIsOpen } = storeToRefs(adminUiStore);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);

const apiService = new ApiService();
const { handleApiError } = useApiError();
const CONCEPTSCHEME_MODAL_LOADING_KEY = 'conceptscheme-modal-submit';

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

// Save handler
const save = async () => {
  if (!selectedConceptscheme.value) return;
  try {
    adminUiStore.startLoading(CONCEPTSCHEME_MODAL_LOADING_KEY);

    await apiService.updateConceptscheme({ ...selectedConceptscheme.value, ...form.value });
    toast.add({
      title: t('api.success.update.title', { item: capitalize(t('entities.conceptscheme')) }),
      description: t('api.success.update.description', { item: t('entities.conceptscheme') }),
      icon: 'i-lucide-check-circle',
      color: 'success',
    });
    adminUiStore.closeConceptschemeModal();
  } catch (error) {
    handleApiError(error);
  } finally {
    adminUiStore.stopLoading(CONCEPTSCHEME_MODAL_LOADING_KEY);
  }
};

// Form state
const form = ref<ConceptschemeForm>({
  labels: [],
  notes: [],
  sources: [],
});

// Initial population of form when editing
onBeforeMount(() => {
  if (selectedConceptscheme.value) {
    const conceptschemeClone = cloneDeep(selectedConceptscheme.value);
    form.value = {
      labels: conceptschemeClone.labels ?? [],
      notes: conceptschemeClone.notes ?? [],
      sources: conceptschemeClone.sources ?? [],
    };
  }
});

/* Grid actions */
const addLabel = (label: Label) => {
  form.value.labels.push(label);
};
const editLabel = (label: Label) => {
  const index = labelsWithAddRow.value.findIndex((l) => l.id === label.id);
  if (index !== undefined && index >= 0) {
    delete label.id;
    form.value.labels[index] = label;
  }
};
const deleteLabel = (label: Label) => {
  const index = labelsWithAddRow.value.findIndex((l) => l.id === label.id);
  if (index !== undefined && index >= 0) {
    form.value.labels.splice(index, 1);
  }
};

const addNote = (note: Note) => {
  form.value.notes.push(note);
};
const editNote = (note: Note) => {
  const index = notesWithAddRow.value.findIndex((n) => n.id === note.id);
  if (index !== undefined && index >= 0) {
    delete note.id;
    form.value.notes[index] = note;
  }
};
const deleteNote = (note: Note) => {
  const index = notesWithAddRow.value.findIndex((n) => n.id === note.id);
  if (index !== undefined && index >= 0) {
    form.value.notes.splice(index, 1);
  }
};

const addSource = (source: Source) => {
  form.value.sources.push(source);
};
const editSource = (source: Source) => {
  const index = sourcesWithAddRow.value.findIndex((s) => s.id === source.id);
  if (index !== undefined && index >= 0) {
    delete source.id;
    form.value.sources[index] = source;
  }
};
const deleteSource = (source: Source) => {
  const index = sourcesWithAddRow.value.findIndex((s) => s.id === source.id);
  if (index !== undefined && index >= 0) {
    form.value.sources.splice(index, 1);
  }
};

/* Table data */
const labelsWithAddRow = computed<TableRow<Label>[]>(() => [
  ...((form.value.labels.map((label, i) => ({
    ...label,
    id: i + 1,
  })) ?? []) as TableRow<Label>[]),
  {
    isAddRow: true,
  } as TableRow<Label>,
]);

const notesWithAddRow = computed<TableRow<Note>[]>(() => [
  ...((form.value.notes.map((note, i) => ({
    ...note,
    id: i + 1,
  })) ?? []) as TableRow<Note>[]),
  {
    isAddRow: true,
  } as TableRow<Note>,
]);

const sourcesWithAddRow = computed<TableRow<Source>[]>(() => [
  ...((form.value.sources.map((source, i) => ({
    ...source,
    id: i + 1,
  })) ?? []) as TableRow<Source>[]),
  {
    isAddRow: true,
  } as TableRow<Source>,
]);
</script>
