<template>
  <ModalTabTable
    class="mb-5"
    :data="matchesBroadWithAddRow"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="() => adminUiStore.openMatchModal(ModalMode.ADD, MatchTypeEnum.BROAD)"
    :on-edit="console.log"
    :on-delete="console.log"
  />
  <ModalTabTable
    class="mb-5"
    :data="matchesCloseWithAddRow"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="() => adminUiStore.openMatchModal(ModalMode.ADD, MatchTypeEnum.CLOSE)"
    :on-edit="console.log"
    :on-delete="console.log"
  />
  <ModalTabTable
    class="mb-5"
    :data="matchesExactWithAddRow"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="() => adminUiStore.openMatchModal(ModalMode.ADD, MatchTypeEnum.EXACT)"
    :on-edit="console.log"
    :on-delete="console.log"
  />
  <ModalTabTable
    class="mb-5"
    :data="matchesNarrowWithAddRow"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="() => adminUiStore.openMatchModal(ModalMode.ADD, MatchTypeEnum.NARROW)"
    :on-edit="console.log"
    :on-delete="console.log"
  />
  <ModalTabTable
    class="mb-5"
    :data="matchesRelatedWithAddRow"
    :main-column="mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="() => adminUiStore.openMatchModal(ModalMode.ADD, MatchTypeEnum.RELATED)"
    :on-edit="console.log"
    :on-delete="console.log"
  />
  <ModalMatch
    :key="matchModalKey"
    :title="t('components.modalMatch.title', { item: '' })"
    :type="adminUiStore.matchModalType"
  />
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

import type { TableRow } from '@components/ModalTabTable.vue';
import type { Match, Matches } from '@models/concept';
import { useAdminUiStore } from '@stores/admin-ui';
import { computed } from 'vue';
import { MatchTypeEnum, ModalMode } from '@models/util';
import { storeToRefs } from 'pinia';

const props = defineProps<{
  matches: Matches;
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { matchModalKey } = storeToRefs(adminUiStore);

const mainColumn = {
  accessorKey: 'label',
  header: t('grid.columns.labels.match', { type: t('grid.columns.labels.matchTypes.broad') }),
  cell: (row: TableRow<Match>) => row.label,
};

const extraColumns = [
  {
    accessorKey: 'uri',
    header: t('grid.columns.labels.uri'),
    cell: (row: TableRow<Match>) => row.uri,
  },
];

const withAddRow = <T extends object>(items: T[]): TableRow<T>[] => [
  ...items,
  {
    isAddRow: true,
  } as TableRow<T>,
];

const toMatchRows = (items: string[] = []): Match[] =>
  items.map((uri) => ({
    label: uri,
    uri,
  }));

const matchesBroadWithAddRow = computed<TableRow<Match>[]>(() => withAddRow(toMatchRows(props.matches.broad)));
const matchesCloseWithAddRow = computed<TableRow<Match>[]>(() => withAddRow(toMatchRows(props.matches.close)));
const matchesExactWithAddRow = computed<TableRow<Match>[]>(() => withAddRow(toMatchRows(props.matches.exact)));
const matchesNarrowWithAddRow = computed<TableRow<Match>[]>(() => withAddRow(toMatchRows(props.matches.narrow)));
const matchesRelatedWithAddRow = computed<TableRow<Match>[]>(() => withAddRow(toMatchRows(props.matches.related)));
</script>
