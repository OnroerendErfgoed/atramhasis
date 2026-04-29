<template>
  <ModalTabTable
    :data="data"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :on-add="() => adminUiStore.openNoteModal(ModalMode.ADD)"
    :on-edit="onEdit"
    :on-delete="onDelete"
  />
  <ModalNote
    :key="noteModalKey"
    :title="t('components.modalNote.title', { item: tabTitle })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.note')" @confirm="confirmDelete" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { h, ref } from 'vue';
import type { TableRow } from '@components/ModalTabTable.vue';
import { ModalMode, type Note } from '@models/util';
import DOMPurify from 'dompurify';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useNoteStore } from '@stores/note';

defineProps<{
  data: TableRow<Note>[];
  tabTitle: string;
}>();

const emit = defineEmits<{
  add: [Note];
  edit: [Note];
  delete: [Note];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { noteModalKey } = storeToRefs(adminUiStore);
const noteStore = useNoteStore();
const { selectedNote } = storeToRefs(noteStore);

const modalDeleteIsOpen = ref(false);

const mainColumn = {
  accessorKey: 'note',
  header: t('grid.columns.labels.note'),
  cell: (row: TableRow<Note>) =>
    h('div', {
      innerHTML: DOMPurify.sanitize(row.note, { USE_PROFILES: { html: true } }),
    }),
};

const extraColumns = [
  {
    accessorKey: 'language',
    header: t('grid.columns.labels.language'),
    cell: (row: TableRow<Note>) => t('lists.languages.' + row.language),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: (row: TableRow<Note>) => t('lists.noteTypes.' + row.type),
  },
];

const onEdit = (row: TableRow<Note>) => {
  adminUiStore.openNoteModal(ModalMode.EDIT);
  noteStore.setSelectedNote(row);
};

const onDelete = (row: TableRow<Note>) => {
  noteStore.setSelectedNote(row);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', selectedNote.value as Note);
  modalDeleteIsOpen.value = false;
};
</script>
