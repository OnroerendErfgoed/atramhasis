<template>
  <ModalConceptschemeTab
    :data="data"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :on-add="() => adminUiStore.openNoteModal(ModalMode.ADD)"
    :on-edit="onEdit"
    :on-delete="onDelete"
  />
  <ModalNote
    :key="noteModalKey"
    :title="t('components.modalNote.title', { item: selectedConceptscheme?.label })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
  <ModalDelete
    v-model:open="modalDeleteIsOpen"
    entity="note"
    :item="`${selectedNote?.note}`"
    @confirm="confirmDelete"
  />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { h, ref } from 'vue';
import type { TableRow } from '@components/ModalConceptscheme.vue';
import { ModalMode, type Note } from '@models/util';
import DOMPurify from 'dompurify';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useNoteStore } from '@stores/note';

defineProps<{
  data: TableRow<Note>[];
}>();

const emit = defineEmits<{
  add: [Note];
  edit: [Note];
  delete: [Note];
}>();

const { t } = useI18n();

const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const adminUiStore = useAdminUiStore();
const { noteModalKey } = storeToRefs(adminUiStore);
const noteStore = useNoteStore();
const { selectedNote } = storeToRefs(noteStore);

const modalDeleteIsOpen = ref(false);

type GenericRow = {
  isAddRow?: boolean;
};

const mainColumn = {
  accessorKey: 'note',
  header: t('grid.columns.labels.note'),
  cell: (row: GenericRow) =>
    h('div', {
      innerHTML: DOMPurify.sanitize((row as TableRow<Note>).note, { USE_PROFILES: { html: true } }),
    }),
};

const extraColumns = [
  {
    accessorKey: 'language',
    header: t('grid.columns.labels.language'),
    cell: (row: GenericRow) => t('lists.languages.' + (row as TableRow<Note>).language),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: (row: GenericRow) => t('lists.noteTypes.' + (row as TableRow<Note>).type),
  },
];

const onEdit = (row: GenericRow) => {
  const selected = row as TableRow<Note>;
  adminUiStore.openNoteModal(ModalMode.EDIT);
  noteStore.setSelectedNote(selected as Note);
};

const onDelete = (row: GenericRow) => {
  noteStore.setSelectedNote(row as Note);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', noteStore.selectedNote as Note);
  modalDeleteIsOpen.value = false;
};
</script>
