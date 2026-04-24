<template>
  <UTable class="flex-1 min-h-0 rounded-lg border border-default" :data="data" :columns="columns" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { TableColumn } from '@nuxt/ui';
import { h, resolveComponent } from 'vue';
import { type Source } from '@models/util';
import type { TableRow } from '@components/ModalConceptscheme.vue';
import DOMPurify from 'dompurify';

defineProps<{
  data: TableRow<Source>[];
}>();

const emit = defineEmits<{
  add: [void];
  edit: [Source];
  delete: [Source];
}>();

const UButton = resolveComponent('UButton');

const { t } = useI18n();

const columns: TableColumn<TableRow<Source>>[] = [
  {
    accessorKey: 'citation',
    header: t('grid.columns.labels.source'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return h(UButton, {
          label: t('actions.add'),
          icon: 'i-lucide-plus',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          class: 'cursor-pointer',
          onClick: () => emit('add'),
        });
      }
      return h('div', {
        innerHTML: DOMPurify.sanitize(row.original.citation, { USE_PROFILES: { html: true } }),
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
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return '';
      }

      return h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          as: 'a',
          href: '#',
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
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
