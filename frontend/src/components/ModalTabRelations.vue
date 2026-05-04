<template>
  <ModalTabTable
    v-for="relation in data"
    :key="relation.key"
    :data="relation.data"
    :main-column="getMainColumn(relation.label)"
    :hide-edit="true"
    :on-add="() => adminUiStore.openRelationModal()"
    :on-edit="console.log"
    :on-delete="console.log"
    class="mb-3"
  />
  <ModalRelation :key="relationModalKey" :scheme="scheme" />
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import type { TableRow } from '@components/ModalTabTable.vue';
import type { Relation } from '@models/concept';
import type { RelationData } from '@components/ModalConcept.vue';

defineProps<{
  scheme: string;
  data: RelationData[];
}>();

const adminUiStore = useAdminUiStore();
const { relationModalKey } = storeToRefs(adminUiStore);

const getMainColumn = (label: string) => ({
  accessorKey: 'label',
  header: label,
  cell: (row: TableRow<Relation>) => row.label,
});
</script>
