<template>
  <ModalTabTable
    :data="data"
    :main-column="mainColumn"
    :on-add="() => adminUiStore.openSourceModal(ModalMode.ADD)"
    :on-edit="onEdit"
    :on-delete="onDelete"
  />
  <ModalSource
    :key="sourceModalKey"
    :title="t('components.modalSource.title', { item: tabTitle })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.source')" @confirm="confirmDelete" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { h, ref } from 'vue';
import type { TableRow } from '@components/ModalTabTable.vue';
import { ModalMode, type Source } from '@models/util';
import DOMPurify from 'dompurify';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useSourceStore } from '@stores/source';

defineProps<{
  data: TableRow<Source>[];
  tabTitle: string;
}>();

const emit = defineEmits<{
  add: [Source];
  edit: [Source];
  delete: [Source];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { sourceModalKey } = storeToRefs(adminUiStore);
const sourceStore = useSourceStore();
const { selectedSource } = storeToRefs(sourceStore);

const modalDeleteIsOpen = ref(false);

const mainColumn = {
  accessorKey: 'citation',
  header: t('grid.columns.labels.source'),
  cell: (row: TableRow<Source>) =>
    h('div', {
      innerHTML: DOMPurify.sanitize(row.citation, { USE_PROFILES: { html: true } }),
    }),
};

const onEdit = (row: TableRow<Source>) => {
  adminUiStore.openSourceModal(ModalMode.EDIT);
  sourceStore.setSelectedSource(row);
};

const onDelete = (row: TableRow<Source>) => {
  sourceStore.setSelectedSource(row);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', selectedSource.value as Source);
  modalDeleteIsOpen.value = false;
};
</script>
