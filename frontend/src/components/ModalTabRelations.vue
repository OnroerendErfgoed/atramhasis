<template>
  <ModalTabTable
    v-for="relation in data"
    :key="relation.key"
    :data="relation.data"
    :main-column="getMainColumn(relation.label)"
    :hide-edit="true"
    :on-add="() => adminUiStore.openRelationModal(relation.key)"
    :on-delete="console.log"
    class="mb-3"
  />
  <ModalRelation :key="relationModalKey" :scheme="scheme" :scheme-uri="schemeUri" @add="emit('add', $event)" />
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import type { TableRow } from '@components/ModalTabTable.vue';
import type { Relation } from '@models/concept';
import type { RelationData } from '@components/ModalConcept.vue';

defineProps<{
  scheme: string;
  schemeUri: string;
  data: RelationData[];
}>();

const emit = defineEmits<{
  add: [Relation];
  delete: [Relation];
}>();

const adminUiStore = useAdminUiStore();
const { relationModalKey } = storeToRefs(adminUiStore);

const getMainColumn = (label: string) => ({
  accessorKey: 'label',
  header: label,
  cell: (row: TableRow<Relation>) => row.label,
});
</script>
