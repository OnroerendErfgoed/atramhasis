<template>
  <ModalTabTable
    :data="membersData"
    :main-column="mainColumn"
    :hide-edit="true"
    @add="() => adminUiStore.openRelationModal()"
    @edit="console.log"
    @delete="console.log"
  />
  <ModalRelation :key="relationModalKey" :title="t('components.modalRelation.title', { item: '' })" :scheme="scheme" />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

import { storeToRefs } from 'pinia';
import { useAdminUiStore } from '@stores/admin-ui';
import type { TableRow } from '@components/ModalTabTable.vue';
import type { Relation } from '@models/concept';

defineProps<{
  scheme: string;
  membersData: TableRow<Relation>[];
  membersOfData: TableRow<Relation>[];
  broaderData: TableRow<Relation>[];
  narrowerData: TableRow<Relation>[];
  relatedData: TableRow<Relation>[];
  subordinateArraysData: TableRow<Relation>[];
  superordinatesData: TableRow<Relation>[];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { relationModalKey } = storeToRefs(adminUiStore);

const mainColumn = {
  accessorKey: 'label',
  header: t('grid.columns.labels.broader'),
  cell: (row: TableRow<Relation>) => row.label,
};
</script>
