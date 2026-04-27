<template>
  <UTable class="flex-1 min-h-0 rounded-lg border border-default" :data="data" :columns="columns" />
  <ModalLabel
    :key="labelModalKey"
    :title="t('components.modalLabel.title', { item: selectedConceptscheme?.label })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { TableColumn } from '@nuxt/ui';
import { h, resolveComponent } from 'vue';
import { ModalMode, type Label } from '@models/util';
import type { TableRow } from '@components/ModalConceptscheme.vue';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useLabelStore } from '@stores/label';

defineProps<{
  data: TableRow<Label>[];
}>();

const emit = defineEmits<{
  add: [Label];
  edit: [Label];
  delete: [Label];
}>();

const UButton = resolveComponent('UButton');

const { t } = useI18n();

const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const adminUiStore = useAdminUiStore();
const { labelModalKey } = storeToRefs(adminUiStore);
const labelStore = useLabelStore();

const columns: TableColumn<TableRow<Label>>[] = [
  {
    accessorKey: 'label',
    header: t('grid.columns.labels.label'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return h(UButton, {
          label: t('actions.add'),
          icon: 'i-lucide-plus',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          class: 'cursor-pointer',
          onClick: () => adminUiStore.openLabelModal(ModalMode.ADD),
        });
      }

      return row.original.label;
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
    cell: ({ row }) => (row.original.isAddRow ? '' : t('lists.labelTypes.' + row.original.type)),
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
            adminUiStore.openLabelModal(ModalMode.EDIT);
            labelStore.setSelectedLabel(row.original);
          },
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': t('grid.columns.actions.delete'),
        }),
      ]);
    },
  },
];
</script>
