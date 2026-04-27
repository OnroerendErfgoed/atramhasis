<template>
  <UTable class="flex-1 min-h-0 rounded-lg border border-default" :data="data" :columns="columns" />
  <ModalNote
    :key="noteModalKey"
    :title="t('components.modalNote.title', { item: selectedConceptscheme?.label })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { TableColumn } from '@nuxt/ui';
import { h, resolveComponent } from 'vue';
import { ModalMode, type Note } from '@models/util';
import type { TableRow } from '@components/ModalConceptscheme.vue';
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

const UButton = resolveComponent('UButton');

const { t } = useI18n();

const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const adminUiStore = useAdminUiStore();
const { noteModalKey } = storeToRefs(adminUiStore);
const noteStore = useNoteStore();

const columns: TableColumn<TableRow<Note>>[] = [
  {
    accessorKey: 'note',
    header: t('grid.columns.labels.note'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return h(UButton, {
          label: t('actions.add'),
          icon: 'i-lucide-plus',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          class: 'cursor-pointer',
          onClick: () => adminUiStore.openNoteModal(ModalMode.ADD),
        });
      }

      return h('div', {
        innerHTML: DOMPurify.sanitize(row.original.note, { USE_PROFILES: { html: true } }),
      });
    },
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'language',
    header: t('grid.columns.labels.language'),
    cell: ({ row }) => (row.original.isAddRow ? '' : t('lists.languages.' + row.original.language)),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: ({ row }) => (row.original.isAddRow ? '' : t('lists.noteTypes.' + row.original.type)),
  },
  {
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return '';
      }

      return h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          onClick: () => {
            adminUiStore.openNoteModal(ModalMode.EDIT);
            noteStore.setSelectedNote(row.original);
          },
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': t('grid.columns.actions.delete'),
          onClick: () => {
            emit('delete', row.original);
          },
        }),
      ]);
    },
  },
];
</script>
