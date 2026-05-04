<template>
  <UModal
    v-model:open="conceptModalIsOpen"
    :dismissible="false"
    :title="t('components.modalConcept.title', { conceptscheme: selectedConceptscheme?.label })"
    :description="t('components.modalConcept.description', { mode: isEditMode ? t('actions.edit') : t('actions.add') })"
    class="max-w-4xl"
  >
    <template #body>
      <div class="flex h-[34rem] w-full flex-col">
        <UForm class="space-y-4 rounded-md bg-muted p-4">
          <div class="grid grid-cols-3 gap-4">
            <UFormField
              name="concept-conceptscheme"
              size="lg"
              :label="t('components.modalConcept.form.conceptscheme.label')"
            >
              <USelect
                v-model="form.conceptscheme"
                :items="conceptschemeOptions"
                class="w-full"
                :disabled="isEditMode"
              />
            </UFormField>

            <UFormField name="concept-type" size="lg" :label="t('components.modalConcept.form.type.label')">
              <USelect v-model="form.type" :items="conceptTypes" class="w-full" />
            </UFormField>
            <UFormField
              v-if="isEditMode"
              name="concept-id"
              size="lg"
              :label="t('components.modalConcept.form.id.label')"
            >
              <UInput :model-value="form.id" class="w-full" disabled />
            </UFormField>
          </div>
        </UForm>
        <UTabs v-model="activeTab" color="neutral" variant="link" :items="tabs">
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

          <template #relations>
            <ModalTabRelations
              :scheme="form.conceptscheme"
              :scheme-uri="formConceptschemeUri"
              :data="form.type === ConceptTypeEnum.CONCEPT ? conceptRelations : collectionRelations"
              @add="addRelation"
              @delete="deleteRelation"
            />
            <UFormField
              v-if="form.type === ConceptTypeEnum.COLLECTION"
              class="mb-3"
              name="concept-infer-relations"
              size="lg"
              :label="t('components.modalConcept.form.inferConceptRelations.label')"
            >
              <URadioGroup v-model="form.infer_concept_relations" orientation="horizontal" :items="yesNoOptions" />
            </UFormField>
          </template>

          <template #matches>
            <ModalTabMatches :matches="form.matches" @add="addMatch" @delete="deleteMatch" />
          </template>
        </UTabs>
      </div>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.save')" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script lang="ts">
export type RelationKey =
  | 'members'
  | 'member_of'
  | 'broader'
  | 'narrower'
  | 'related'
  | 'subordinate_arrays'
  | 'superordinates';

export type RelationData = {
  label: string;
  data: TableRow<Relation>[];
  key: RelationKey;
};
</script>

<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui';
import { useAdminUiStore } from '@stores/admin-ui';
import { cloneDeep } from 'lodash-es';
import { storeToRefs } from 'pinia';
import { capitalize, computed, onBeforeMount, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
// import { ApiService } from '@services/api.service';
import { useApiError } from '@composables/useApiError';
import type { ConceptForm, Match, MatchForm, Relation } from '@models/concept';
import { ConceptTypeEnum, ModalMode, type Label, type Note, type Source } from '@models/util';
import { useConceptStore } from '@stores/concept';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { useListStore } from '@stores/list';
import type { TableRow } from './ModalTabTable.vue';

const toast = useToast();
const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptModalIsOpen, conceptModalMode, relationModalType } = storeToRefs(adminUiStore);
const isEditMode = computed(() => conceptModalMode.value === ModalMode.EDIT);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const conceptStore = useConceptStore();
const { selectedConcept } = storeToRefs(conceptStore);
const listStore = useListStore();
const { conceptTypes, conceptschemeOptions, yesNoOptions } = storeToRefs(listStore);

// const apiService = new ApiService();
const { handleApiError } = useApiError();
const CONCEPT_MODAL_LOADING_KEY = 'concept-modal-submit';

// Form state
const form = ref<ConceptForm>({
  conceptscheme: `${selectedConceptscheme.value?.id}`,
  type: ConceptTypeEnum.CONCEPT,
  id: undefined,
  labels: [],
  notes: [],
  sources: [],
  members: [],
  member_of: [],
  broader: [],
  narrower: [],
  related: [],
  subordinate_arrays: [],
  superordinates: [],
  infer_concept_relations: undefined,
  matches: {
    narrow: [],
    broad: [],
    related: [],
    close: [],
    exact: [],
  },
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedConcept.value) {
    const conceptClone = cloneDeep(selectedConcept.value);
    form.value = {
      conceptscheme: `${selectedConceptscheme.value?.id}`,
      type: conceptClone.type,
      id: conceptClone.id,
      labels: conceptClone.labels ?? [],
      notes: conceptClone.notes ?? [],
      sources: conceptClone.sources ?? [],
      members: conceptClone.members ?? [],
      member_of: conceptClone.member_of ?? [],
      broader: conceptClone.broader ?? [],
      narrower: conceptClone.narrower ?? [],
      related: conceptClone.related ?? [],
      subordinate_arrays: conceptClone.subordinate_arrays ?? [],
      superordinates: conceptClone.superordinates ?? [],
      infer_concept_relations: conceptClone.infer_concept_relations,
      matches: Object.keys(conceptClone.matches ?? {}).length
        ? conceptClone.matches
        : {
            narrow: [],
            broad: [],
            related: [],
            close: [],
            exact: [],
          },
    };
  }
});

const formConceptschemeUri = computed(() => {
  const scheme = conceptschemeOptions.value.find((cs) => cs.value === form.value.conceptscheme);
  return scheme ? scheme.uri : '';
});

const activeTab = ref('0');
const tabs = computed<TabsItem[]>(() => [
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
    disabled: form.value.type === ConceptTypeEnum.COLLECTION,
  },
]);

// Reset matches when switching to collection type, as collections cannot have matches
watch(
  () => form.value.type,
  (newValue) => {
    if (
      activeTab.value === tabs.value.findIndex((t) => t.slot === 'matches').toString() &&
      newValue === ConceptTypeEnum.COLLECTION
    ) {
      activeTab.value = '0';
      form.value.matches = {
        narrow: [],
        broad: [],
        related: [],
        close: [],
        exact: [],
      };
    }
  }
);

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

const addRelation = (relation: Relation) => {
  if (form.value[relationModalType.value]?.find((r) => r.id === relation.id)) {
    return;
  }
  form.value[relationModalType.value]?.push(relation);
};
const deleteRelation = (relation: Relation) => {
  const index = form.value[relationModalType.value]?.findIndex((r) => r.id === relation.id);
  if (index !== undefined && index >= 0) {
    form.value[relationModalType.value]?.splice(index, 1);
  }
};

const addMatch = (match: MatchForm) => {
  form.value.matches[match.type] = form.value.matches[match.type]
    .concat(match.labels)
    .filter((uri, index, self) => self.indexOf(uri) === index);
};
const deleteMatch = (match: Match) => {
  form.value.matches[match.type!] = form.value.matches[match.type!].filter((label) => label !== match.uri);
};

/* Table data */
const withAddRow = <T extends { id?: string }>(items: T[]): TableRow<T>[] => [
  ...items.map((item, i) => ({
    ...item,
    id: item.id ?? `${i + 1}`,
  })),
  {
    isAddRow: true,
  } as TableRow<T>,
];

const labelsWithAddRow = computed<TableRow<Label>[]>(() => withAddRow(form.value.labels));
const notesWithAddRow = computed<TableRow<Note>[]>(() => withAddRow(form.value.notes));
const sourcesWithAddRow = computed<TableRow<Source>[]>(() => withAddRow(form.value.sources));

const membersWithAddRow = computed<TableRow<Relation>[]>(() => withAddRow(form.value.members || []));
const memberOfWithAddRow = computed<TableRow<Relation>[]>(() => withAddRow(form.value.member_of || []));
const broaderWithAddRow = computed<TableRow<Relation>[]>(() => withAddRow(form.value.broader || []));
const narrowerWithAddRow = computed<TableRow<Relation>[]>(() => withAddRow(form.value.narrower || []));
const relatedWithAddRow = computed<TableRow<Relation>[]>(() => withAddRow(form.value.related || []));
const subordinateArraysWithAddRow = computed<TableRow<Relation>[]>(() =>
  withAddRow(form.value.subordinate_arrays || [])
);
const superordinatesWithAddRow = computed<TableRow<Relation>[]>(() => withAddRow(form.value.superordinates || []));

/* Relation modal data */
const conceptRelations = computed<RelationData[]>(() => [
  {
    label: t('components.modalTabRelations.broader'),
    data: broaderWithAddRow.value,
    key: 'broader',
  },
  {
    label: t('components.modalTabRelations.narrower'),
    data: narrowerWithAddRow.value,
    key: 'narrower',
  },
  {
    label: t('components.modalTabRelations.related'),
    data: relatedWithAddRow.value,
    key: 'related',
  },
  {
    label: t('components.modalTabRelations.memberOf'),
    data: memberOfWithAddRow.value,
    key: 'member_of',
  },
  {
    label: t('components.modalTabRelations.subordinateArrays'),
    data: subordinateArraysWithAddRow.value,
    key: 'subordinate_arrays',
  },
]);

const collectionRelations = computed<RelationData[]>(() => [
  {
    label: t('components.modalTabRelations.members'),
    data: membersWithAddRow.value,
    key: 'members',
  },
  {
    label: t('components.modalTabRelations.memberOf'),
    data: memberOfWithAddRow.value,
    key: 'member_of',
  },
  {
    label: t('components.modalTabRelations.superordinates'),
    data: superordinatesWithAddRow.value,
    key: 'superordinates',
  },
]);
</script>
