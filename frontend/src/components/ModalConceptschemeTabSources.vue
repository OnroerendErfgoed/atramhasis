<template>
  <ModalConceptschemeTab
    :data="data"
    :main-column="mainColumn"
    :on-add="() => adminUiStore.openSourceModal(ModalMode.ADD)"
    :on-edit="onEdit"
    :on-delete="onDelete"
  >
    <template #modal>
      <ModalSource
        :key="sourceModalKey"
        :title="t('components.modalSource.title', { item: selectedConceptscheme?.label })"
        @add="emit('add', $event)"
        @edit="emit('edit', $event)"
      />
    </template>
  </ModalConceptschemeTab>
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { h } from 'vue';
import type { TableRow } from '@components/ModalConceptscheme.vue';
import { ModalMode, type Source } from '@models/util';
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

const { t } = useI18n();

const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const adminUiStore = useAdminUiStore();
const { sourceModalKey } = storeToRefs(adminUiStore);
const sourceStore = useSourceStore();

type GenericRow = {
  isAddRow?: boolean;
};

const mainColumn = {
  accessorKey: 'citation',
  header: t('grid.columns.labels.source'),
  cell: (row: GenericRow) =>
    h('div', {
      innerHTML: DOMPurify.sanitize((row as TableRow<Source>).citation, { USE_PROFILES: { html: true } }),
    }),
};

const onEdit = (row: GenericRow) => {
  const selected = row as TableRow<Source>;
  adminUiStore.openSourceModal(ModalMode.EDIT);
  sourceStore.setSelectedSource(selected as Source);
};

const onDelete = (row: GenericRow) => {
  emit('delete', row as Source);
};
</script>
