<template>
  <ModalTabTable
    v-for="relation in data"
    :key="relation.key"
    :data="relation.data"
    :main-column="getMainColumn(relation.label)"
    :hide-edit="true"
    :on-add="() => adminUiStore.openRelationModal(relation.key)"
    :on-delete="onDelete"
    class="mb-3"
  />
  <ModalRelation :key="relationModalKey" :scheme="scheme" :scheme-uri="schemeUri" @add="emit('add', $event)" />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.relation')" @confirm="confirmDelete" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import type { TableRow } from '@components/ModalTabTable.vue';
import type { Relation } from '@models/concept';
import type { RelationData } from '@components/ModalConcept.vue';
import { ref } from 'vue';

defineProps<{
  scheme: string;
  schemeUri: string;
  data: RelationData[];
}>();

const emit = defineEmits<{
  add: [Relation];
  delete: [Relation];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { relationModalKey } = storeToRefs(adminUiStore);
const modalDeleteIsOpen = ref(false);
const selectedRelation = ref<Relation>();

const getMainColumn = (label: string) => ({
  accessorKey: 'label',
  header: label,
  cell: (row: TableRow<Relation>) => row.label,
});

const onDelete = (row: TableRow<Relation>) => {
  selectedRelation.value = row;
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', selectedRelation.value as Relation);
  modalDeleteIsOpen.value = false;
};
</script>
