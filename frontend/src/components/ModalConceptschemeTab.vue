<template>
  <UTable class="flex-1 min-h-0 rounded-lg border border-default" :data="data" :columns="columns" />
  <slot name="modal" />
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
import { computed, h, resolveComponent, type VNode } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

type GenericRow = {
  isAddRow?: boolean;
};

type BaseColumn = {
  accessorKey?: string;
  id?: string;
  header: string;
  cell: (row: GenericRow) => string | VNode;
};

type MainColumn = BaseColumn & {
  accessorKey: string;
};

const props = defineProps<{
  data: GenericRow[];
  mainColumn: MainColumn;
  extraColumns?: BaseColumn[];
  onAdd: () => void;
  onEdit: (row: GenericRow) => void;
  onDelete: (row: GenericRow) => void;
}>();

const UButton = resolveComponent('UButton');

const columns = computed<TableColumn<GenericRow>[]>(() => {
  const mainColumn: TableColumn<GenericRow> = {
    accessorKey: props.mainColumn.accessorKey,
    header: props.mainColumn.header,
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return h(UButton, {
          label: t('actions.add'),
          icon: 'i-lucide-plus',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          onClick: props.onAdd,
        });
      }

      return props.mainColumn.cell(row.original);
    },
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  };

  const extraColumns: TableColumn<GenericRow>[] = (props.extraColumns ?? []).map((column) => ({
    accessorKey: column.accessorKey,
    id: column.id,
    header: column.header,
    cell: ({ row }) => (row.original.isAddRow ? '' : column.cell(row.original)),
  }));

  const actionsColumn: TableColumn<GenericRow> = {
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
          onClick: () => props.onEdit(row.original),
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': t('grid.columns.actions.delete'),
          onClick: () => props.onDelete(row.original),
        }),
      ]);
    },
  };

  return [mainColumn, ...extraColumns, actionsColumn];
});
</script>
