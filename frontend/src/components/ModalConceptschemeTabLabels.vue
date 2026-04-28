<template>
  <ModalConceptschemeTab
    :data="data"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :on-add="() => adminUiStore.openLabelModal(ModalMode.ADD)"
    :on-edit="onEdit"
    :on-delete="onDelete"
  />
  <ModalLabel
    :key="labelModalKey"
    :title="t('components.modalLabel.title', { item: selectedConceptscheme?.label })"
    @add="emit('add', $event)"
    @edit="emit('edit', $event)"
  />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.label')" @confirm="confirmDelete" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { TableRow } from '@components/ModalConceptscheme.vue';
import { ModalMode, type Label } from '@models/util';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import { useLabelStore } from '@stores/label';
import { ref } from 'vue';

defineProps<{
  data: TableRow<Label>[];
}>();

const emit = defineEmits<{
  add: [Label];
  edit: [Label];
  delete: [Label];
}>();

const { t } = useI18n();

const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const adminUiStore = useAdminUiStore();
const { labelModalKey } = storeToRefs(adminUiStore);
const labelStore = useLabelStore();
const { selectedLabel } = storeToRefs(labelStore);

const modalDeleteIsOpen = ref(false);

type GenericRow = {
  isAddRow?: boolean;
};

const mainColumn = {
  accessorKey: 'label',
  header: t('grid.columns.labels.label'),
  cell: (row: GenericRow) => (row as TableRow<Label>).label,
};

const extraColumns = [
  {
    accessorKey: 'language',
    header: t('grid.columns.labels.language'),
    cell: (row: GenericRow) => t('lists.languages.' + (row as TableRow<Label>).language),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: (row: GenericRow) => t('lists.labelTypes.' + (row as TableRow<Label>).type),
  },
];

const onEdit = (row: GenericRow) => {
  const selected = row as TableRow<Label>;
  adminUiStore.openLabelModal(ModalMode.EDIT);
  labelStore.setSelectedLabel(selected as Label);
};

const onDelete = (row: GenericRow) => {
  labelStore.setSelectedLabel(row as Label);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', selectedLabel.value as Label);
  modalDeleteIsOpen.value = false;
};
</script>
