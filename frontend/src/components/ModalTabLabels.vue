<template>
  <ModalTabTable
    :data="data"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    @add="() => adminUiStore.openLabelModal(ModalMode.ADD)"
    @edit="onEdit"
    @delete="onDelete"
  />
  <ModalLabel
    :key="labelModalKey"
    :title="t('components.modalLabel.title', { item: tabTitle })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.label')" @confirm="confirmDelete" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { TableRow } from '@components/ModalTabTable.vue';
import { ModalMode, type Label } from '@models/util';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useLabelStore } from '@stores/label';
import { ref } from 'vue';

defineProps<{
  data: TableRow<Label>[];
  tabTitle: string;
}>();

const emit = defineEmits<{
  add: [Label];
  edit: [Label];
  delete: [Label];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { labelModalKey } = storeToRefs(adminUiStore);
const labelStore = useLabelStore();
const { selectedLabel } = storeToRefs(labelStore);

const modalDeleteIsOpen = ref(false);

const mainColumn = {
  accessorKey: 'label',
  header: t('grid.columns.labels.label'),
  cell: (row: TableRow<Label>) => row.label,
};

const extraColumns = [
  {
    accessorKey: 'language',
    header: t('grid.columns.labels.language'),
    cell: (row: TableRow<Label>) => t('lists.languages.' + row.language),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: (row: TableRow<Label>) => t('lists.labelTypes.' + row.type),
  },
];

const onEdit = (row: TableRow<Label>) => {
  adminUiStore.openLabelModal(ModalMode.EDIT);
  labelStore.setSelectedLabel(row);
};

const onDelete = (row: TableRow<Label>) => {
  labelStore.setSelectedLabel(row);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', selectedLabel.value as Label);
  modalDeleteIsOpen.value = false;
};
</script>
