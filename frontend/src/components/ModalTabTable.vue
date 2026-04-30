<template>
  <UTable class="flex-1 min-h-0 rounded-lg border border-default" :data="data" :columns="columns" />
</template>

<script lang="ts">
export type TableRow<T> = T & {
  isAddRow?: boolean;
};
</script>

<script setup lang="ts" generic="T">
import type { TableColumn } from '@nuxt/ui';
import { computed, h, resolveComponent, type VNode } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

type BaseColumn = {
  accessorKey?: string;
  id?: string;
  header: string;
  cell: (row: TableRow<T>) => string | VNode;
};

type MainColumn = BaseColumn & {
  accessorKey: string;
};

const props = defineProps<{
  data: TableRow<T>[];
  mainColumn: MainColumn;
  extraColumns?: BaseColumn[];
  hideEdit?: boolean;
  onAdd: () => void;
  onEdit: (row: TableRow<T>) => void;
  onDelete: (row: TableRow<T>) => void;
}>();

const UButton = resolveComponent('UButton');

const columns = computed<TableColumn<TableRow<T>>[]>(() => {
  const mainColumn: TableColumn<TableRow<T>> = {
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
        td: 'w-full whitespace-normal break-words [word-break:break-word]',
      },
    },
  };

  const extraColumns: TableColumn<TableRow<T>>[] = (props.extraColumns ?? []).map((column) => ({
    accessorKey: column.accessorKey,
    id: column.id,
    header: column.header,
    cell: ({ row }) => (row.original.isAddRow ? '' : column.cell(row.original)),
  }));

  const actionsColumn: TableColumn<TableRow<T>> = {
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return '';
      }

      const actionButtons = [
        !props.hideEdit
          ? h(UButton, {
              label: t('grid.columns.actions.edit'),
              icon: 'i-lucide-pencil',
              color: 'primary',
              variant: 'outline',
              size: 'xs',
              onClick: () => props.onEdit(row.original),
            })
          : null,
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': t('grid.columns.actions.delete'),
          onClick: () => props.onDelete(row.original),
        }),
      ];

      return h('div', { class: 'flex items-center gap-1' }, actionButtons);
    },
  };

  return [mainColumn, ...extraColumns, actionsColumn];
});
</script>
