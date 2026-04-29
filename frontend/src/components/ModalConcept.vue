<template>
  <UModal
    v-model:open="conceptModalIsOpen"
    :dismissible="false"
    :title="t('components.modalConcept.title', { conceptscheme: selectedConceptscheme?.label })"
    :description="t('components.modalConcept.description', { mode: isEditMode ? t('actions.edit') : t('actions.add') })"
    class="max-w-4xl"
  >
    <template #body>
      <UForm class="space-y-4 rounded-md bg-muted p-4">
        <div class="grid grid-cols-3 gap-4">
          <UFormField
            name="concept-conceptscheme"
            size="lg"
            :label="t('components.modalConcept.form.conceptscheme.label')"
          >
            <USelect v-model="form.conceptscheme" :items="conceptschemeOptions" class="w-full" :disabled="isEditMode" />
          </UFormField>

          <UFormField name="concept-type" size="lg" :label="t('components.modalConcept.form.type.label')">
            <USelect v-model="form.type" :items="conceptTypes" class="w-full" />
          </UFormField>
          <UFormField v-if="isEditMode" name="concept-id" size="lg" :label="t('components.modalConcept.form.id.label')">
            <UInput :model-value="form.id" class="w-full" disabled />
          </UFormField>
        </div>
      </UForm>
      <UTabs v-model="activeTab" color="neutral" variant="link" :items="tabs" class="w-full">
        <template #labels>
          <ModalTabLabels
            :data="labelsWithAddRow"
            :tab-title="selectedConcept?.label ?? ''"
            @add="addLabel"
            @edit="editLabel"
            @delete="deleteLabel"
          />
        </template>

        <template #notes>
          <ModalTabNotes
            :data="notesWithAddRow"
            :tab-title="selectedConcept?.label ?? ''"
            @add="addNote"
            @edit="editNote"
            @delete="deleteNote"
          />
        </template>

        <template #sources>
          <ModalTabSources
            :data="sourcesWithAddRow"
            :tab-title="selectedConcept?.label ?? ''"
            @add="addSource"
            @edit="editSource"
            @delete="deleteSource"
          />
        </template>

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
import { capitalize, computed, onBeforeMount, ref } from 'vue';
// import { ApiService } from '@services/api.service';
import { useApiError } from '@composables/useApiError';
import { useConceptStore } from '@stores/concept';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { ConceptTypeEnum, ModalMode, type Label, type Note, type Source } from '@models/util';
import { useListStore } from '@stores/list';
import type { ConceptForm } from '@models/concept';
import type { TableRow } from './ModalTabTable.vue';

const toast = useToast();
const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptModalIsOpen, conceptModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => conceptModalMode.value === ModalMode.EDIT);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const conceptStore = useConceptStore();
const { selectedConcept } = storeToRefs(conceptStore);
const listStore = useListStore();
const { conceptTypes, conceptschemeOptions } = storeToRefs(listStore);

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

// Form state
const form = ref<ConceptForm>({
  conceptscheme: selectedConceptscheme.value?.id as string,
  type: ConceptTypeEnum.CONCEPT,
  id: undefined,
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedConcept.value) {
    form.value = {
      conceptscheme: selectedConceptscheme.value?.id as string,
      type: selectedConcept.value.type,
      id: selectedConcept.value.id,
    };
  }
});

/* Grid actions */
const addLabel = (label: Label) => {
  selectedConcept.value?.labels.push(label);
};
const editLabel = (label: Label) => {
  const index = labelsWithAddRow.value.findIndex((l) => l.id === label.id);
  if (index !== undefined && index >= 0) {
    delete label.id;
    selectedConcept.value!.labels[index] = label;
  }
};
const deleteLabel = (label: Label) => {
  const index = labelsWithAddRow.value.findIndex((l) => l.id === label.id);
  if (index !== undefined && index >= 0) {
    selectedConcept.value!.labels.splice(index, 1);
  }
};

const addNote = (note: Note) => {
  selectedConcept.value?.notes.push(note);
};
const editNote = (note: Note) => {
  const index = notesWithAddRow.value.findIndex((n) => n.id === note.id);
  if (index !== undefined && index >= 0) {
    delete note.id;
    selectedConcept.value!.notes[index] = note;
  }
};
const deleteNote = (note: Note) => {
  const index = notesWithAddRow.value.findIndex((n) => n.id === note.id);
  if (index !== undefined && index >= 0) {
    selectedConcept.value!.notes.splice(index, 1);
  }
};

const addSource = (source: Source) => {
  selectedConcept.value?.sources.push(source);
};
const editSource = (source: Source) => {
  const index = sourcesWithAddRow.value.findIndex((s) => s.id === source.id);
  if (index !== undefined && index >= 0) {
    delete source.id;
    selectedConcept.value!.sources[index] = source;
  }
};
const deleteSource = (source: Source) => {
  const index = sourcesWithAddRow.value.findIndex((s) => s.id === source.id);
  if (index !== undefined && index >= 0) {
    selectedConcept.value!.sources.splice(index, 1);
  }
};

/* Table data */
const labelsWithAddRow = computed<TableRow<Label>[]>(() => [
  ...((selectedConcept.value?.labels?.map((label, i) => ({
    ...label,
    id: i + 1,
  })) ?? []) as TableRow<Label>[]),
  {
    isAddRow: true,
  } as TableRow<Label>,
]);

const notesWithAddRow = computed<TableRow<Note>[]>(() => [
  ...((selectedConcept.value?.notes?.map((note, i) => ({
    ...note,
    id: i + 1,
  })) ?? []) as TableRow<Note>[]),
  {
    isAddRow: true,
  } as TableRow<Note>,
]);

const sourcesWithAddRow = computed<TableRow<Source>[]>(() => [
  ...((selectedConcept.value?.sources?.map((source, i) => ({
    ...source,
    id: i + 1,
  })) ?? []) as TableRow<Source>[]),
  {
    isAddRow: true,
  } as TableRow<Source>,
]);
</script>
