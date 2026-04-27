<template>
  <UTable class="flex-1 min-h-0 rounded-lg border border-default" :data="data" :columns="columns" />
  <ModalSource
    :key="sourceModalKey"
    :title="t('components.modalSource.title', { item: selectedConceptscheme?.label })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { TableColumn } from '@nuxt/ui';
import { h, resolveComponent } from 'vue';
import { ModalMode, type Source } from '@models/util';
import type { TableRow } from '@components/ModalConceptscheme.vue';
import DOMPurify from 'dompurify';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useSourceStore } from '@stores/source';

defineProps<{
  data: TableRow<Source>[];
}>();

const emit = defineEmits<{
  add: [Source];
  edit: [Source];
  delete: [Source];
}>();

const UButton = resolveComponent('UButton');

const { t } = useI18n();

const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const adminUiStore = useAdminUiStore();
const { sourceModalKey } = storeToRefs(adminUiStore);
const sourceStore = useSourceStore();

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
          onClick: () => adminUiStore.openSourceModal(ModalMode.ADD),
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
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          onClick: () => {
            adminUiStore.openSourceModal(ModalMode.EDIT);
            sourceStore.setSelectedSource(row.original);
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
