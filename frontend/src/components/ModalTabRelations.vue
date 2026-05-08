<template>
  <ModalTabTable
    v-for="relation in data"
    :key="relation.key"
    :data="relation.data"
    :main-column="getMainColumn(relation.label)"
    :hide-edit="true"
    :on-add="() => onAdd(relation.key)"
    :on-delete="(row) => onDelete(row, relation.key)"
    class="mb-3"
  />
  <ModalRelation
    :key="relationModalKey"
    :scheme="conceptscheme.id"
    :scheme-uri="conceptscheme.uri"
    @add="emit('add', { relation: $event, type: selectionType as RelationTypeEnum })"
  />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.relation')" @confirm="confirmDelete" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import type { TableRow } from '@components/ModalTabTable.vue';
import type { Relation } from '@models/concept';
import type { RelationData } from '@components/ModalConcept.vue';
import { RelationTypeEnum } from '@models/util';
import { ref } from 'vue';
import { useRelationStore } from '@stores/relation';
import type { Conceptscheme } from '@models/conceptscheme';

defineProps<{
  conceptscheme: Conceptscheme;
  data: RelationData[];
}>();

const emit = defineEmits<{
  add: [{ relation: Relation; type: RelationTypeEnum }];
  delete: [{ relation: Relation; type: RelationTypeEnum }];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { relationModalKey } = storeToRefs(adminUiStore);
const relationStore = useRelationStore();
const { selectedRelation, selectionType } = storeToRefs(relationStore);
const modalDeleteIsOpen = ref(false);

const getMainColumn = (label: string) => ({
  accessorKey: 'label',
  header: label,
  cell: (row: TableRow<Relation>) => row.label,
});

const onAdd = (type: RelationTypeEnum) => {
  adminUiStore.openRelationModal();
  relationStore.setSelectionType(type);
};

const onDelete = (row: TableRow<Relation>, relationKey: RelationTypeEnum) => {
  relationStore.setSelectedRelation(row);
  relationStore.setSelectionType(relationKey);
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', { relation: selectedRelation.value as Relation, type: selectionType.value as RelationTypeEnum });
  modalDeleteIsOpen.value = false;
};
</script>
