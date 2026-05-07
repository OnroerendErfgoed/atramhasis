<template>
  <ALoader v-if="!matchTableConfigs.length" :message="t('components.modalTabMatches.loading')" />
  <ModalTabTable
    v-for="config in matchTableConfigs"
    :key="config.type"
    :data="config.data"
    :main-column="config.mainColumn"
    :extra-columns="extraColumns"
    :hide-edit="true"
    :on-add="config.onAdd"
    :on-delete="($event) => onDelete($event, config.type)"
    class="mb-3"
  />
  <ModalMatch :key="matchModalKey" @add="emit('add', $event)" />
  <ModalDelete v-model:open="modalDeleteIsOpen" :entity="t('entities.match')" @confirm="confirmDelete" />
</template>

<script setup lang="ts">
import type { TableRow } from '@components/ModalTabTable.vue';
import type { Match, Matches, MatchForm } from '@models/concept';
import { MatchTypeEnum } from '@models/util';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptStore } from '@stores/concept';
import { useMatchStore } from '@stores/match';
import { storeToRefs } from 'pinia';
import { h, ref, resolveComponent, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{ matches: Matches }>();
const emit = defineEmits<{
  add: [MatchForm];
  delete: [Match];
}>();

const { t } = useI18n();
const apiService = new ApiService();

const adminUiStore = useAdminUiStore();
const { matchModalKey } = storeToRefs(adminUiStore);
const conceptStore = useConceptStore();
const matchStore = useMatchStore();

const getMainColumn = (typeLabelKey: string) => ({
  accessorKey: 'label',
  header: t('grid.columns.labels.match', { type: t(typeLabelKey) }),
  cell: (row: TableRow<Match>) => row.label,
});

const extraColumns = [
  {
    accessorKey: 'uri',
    header: t('grid.columns.labels.uri'),
    cell: (row: TableRow<Match>) =>
      h(
        resolveComponent('ULink'),
        {
          href: row.uri,
          target: '_blank',
          external: true,
          class: 'inline-flex items-center gap-1 break-all',
        },
        () => [
          row.uri,
          h(resolveComponent('UIcon'), { name: 'i-lucide-external-link', class: 'shrink-0 size-3.5 opacity-70' }),
        ]
      ),
  },
];

const withAddRow = <T extends object>(items: T[]): TableRow<T>[] => [
  ...items,
  {
    isAddRow: true,
  } as TableRow<T>,
];

const toMatchRows = async (items: string[] = []): Promise<Match[]> => {
  return Promise.all(
    items.map(async (uri) => {
      try {
        const match = matchStore.getMatch(uri);
        if (match) return match;

        const byUri = await apiService.getByUri<{
          id: string;
          concept_scheme: { id: string };
        }>(uri);

        const concept = await conceptStore.getConcept(byUri.concept_scheme.id, Number(byUri.id));
        matchStore.setMatch({ uri, label: concept?.label || uri });
        return { label: concept?.label || uri, uri: concept?.uri || uri };
      } catch {
        // Fall back to raw uri if enrichment fails.
      }

      return { label: uri, uri };
    })
  );
};

const matchConfigItems: Array<{ key: keyof Matches; type: MatchTypeEnum; labelKey: string }> = [
  { key: 'broad', type: MatchTypeEnum.BROAD, labelKey: 'components.modalTabMatches.broad' },
  { key: 'close', type: MatchTypeEnum.CLOSE, labelKey: 'components.modalTabMatches.close' },
  { key: 'exact', type: MatchTypeEnum.EXACT, labelKey: 'components.modalTabMatches.exact' },
  { key: 'narrow', type: MatchTypeEnum.NARROW, labelKey: 'components.modalTabMatches.narrow' },
  { key: 'related', type: MatchTypeEnum.RELATED, labelKey: 'components.modalTabMatches.related' },
];

type MatchTableConfig = {
  type: MatchTypeEnum;
  data: TableRow<Match>[];
  mainColumn: ReturnType<typeof getMainColumn>;
  onAdd: () => void;
};

const matchTableConfigs = ref<MatchTableConfig[]>([]);
const loadMatchTableConfigs = async () => {
  matchTableConfigs.value = await Promise.all(
    matchConfigItems.map(async (item) => ({
      type: item.type,
      data: withAddRow(await toMatchRows(props.matches[item.key] || [])),
      mainColumn: getMainColumn(item.labelKey),
      onAdd: () => adminUiStore.openMatchModal(item.type),
    }))
  );
};

watch(() => props.matches, loadMatchTableConfigs, { deep: true, immediate: true });

// Delete match
const modalDeleteIsOpen = ref(false);
const selectedMatch = ref<Match>();

const onDelete = (row: TableRow<Match>, type: MatchTypeEnum) => {
  selectedMatch.value = { ...row, type };
  modalDeleteIsOpen.value = true;
};
const confirmDelete = () => {
  emit('delete', selectedMatch.value as Match);
  modalDeleteIsOpen.value = false;
};
</script>
