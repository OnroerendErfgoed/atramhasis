<template>
  <ModalTabTable
    v-for="config in matchTableConfigs"
    :key="config.type"
    :data="config.data"
    :main-column="config.mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="config.onAdd"
    :on-delete="console.log"
    class="mb-3"
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
import { MatchTypeEnum } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';

const props = defineProps<{
  matches: Matches;
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { matchModalKey } = storeToRefs(adminUiStore);

const getMainColumn = (typeLabelKey: string) => ({
  accessorKey: 'label',
  header: t('grid.columns.labels.match', { type: t(typeLabelKey) }),
  cell: (row: TableRow<Match>) => row.label,
});

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

const matchConfigItems: Array<{ key: keyof Matches; type: MatchTypeEnum; labelKey: string }> = [
  { key: 'broad', type: MatchTypeEnum.BROAD, labelKey: 'components.modalTabMatches.broad' },
  { key: 'close', type: MatchTypeEnum.CLOSE, labelKey: 'components.modalTabMatches.close' },
  { key: 'exact', type: MatchTypeEnum.EXACT, labelKey: 'components.modalTabMatches.exact' },
  { key: 'narrow', type: MatchTypeEnum.NARROW, labelKey: 'components.modalTabMatches.narrow' },
  { key: 'related', type: MatchTypeEnum.RELATED, labelKey: 'components.modalTabMatches.related' },
];

const matchTableConfigs = computed(() =>
  matchConfigItems.map((item) => ({
    type: item.type,
    data: withAddRow(toMatchRows(props.matches[item.key] || [])),
    mainColumn: getMainColumn(item.labelKey),
    onAdd: () => adminUiStore.openMatchModal(item.type),
  }))
);
</script>
