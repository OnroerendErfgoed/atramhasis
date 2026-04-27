<template>
  <ModalConceptschemeTab
    :data="data"
    :main-column="mainColumn"
    :on-add="() => adminUiStore.openSourceModal(ModalMode.ADD)"
    :on-edit="onEdit"
    :on-delete="onDelete"
  />
  <ModalSource
    :key="sourceModalKey"
    :title="t('components.modalSource.title', { item: selectedConceptscheme?.label })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
  <ModalDelete
    v-model:open="modalDeleteIsOpen"
    entity="source"
    :item="`${selectedSource?.citation}`"
    @confirm="confirmDelete"
  />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { h, ref } from 'vue';
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
const { selectedSource } = storeToRefs(sourceStore);

const modalDeleteIsOpen = ref(false);

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
  sourceStore.setSelectedSource(row as Source);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', sourceStore.selectedSource as Source);
  modalDeleteIsOpen.value = false;
};
</script>
