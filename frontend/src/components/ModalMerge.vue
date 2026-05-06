<template>
  <UModal
    v-model:open="mergeModalIsOpen"
    :dismissible="false"
    :title="capitalize(t('components.modalMerge.title', { concept: selectedConcept?.label ?? '' }))"
    :description="t('components.modalMerge.description')"
    class="max-w-4xl"
  >
    <template #body>
      <ALoader v-if="isFullscreenLoading" :message="t('components.modalMerge.loading')" />
      <UTable
        ref="table"
        v-model:row-selection="rowSelection"
        class="flex-1 min-h-0 rounded-lg border border-default"
        :data="tableData"
        :columns="columns"
        @select="onSelect"
      />
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.merge')" :disabled="!Object.keys(rowSelection).length" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { Match } from '@models/concept';
import type { TableColumn, TableRow } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptStore } from '@stores/concept';
import { useMatchStore } from '@stores/match';
import { storeToRefs } from 'pinia';
import { capitalize, h, onMounted, ref, resolveComponent, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

const UButton = resolveComponent('UButton');
const UCheckbox = resolveComponent('UCheckbox');

const toast = useToast();
const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { mergeModalIsOpen, isFullscreenLoading } = storeToRefs(adminUiStore);
const conceptStore = useConceptStore();
const { selectedConcept } = storeToRefs(conceptStore);
const matchStore = useMatchStore();

const apiService = new ApiService();
const GET_MATCH_LOADING_KEY = 'get-match';

const table = useTemplateRef('table');
const rowSelection = ref<Record<string, boolean>>({});

const onSelect = (e: Event, row: TableRow<Match>) => {
  row.toggleSelected(!row.getIsSelected());
  console.log(rowSelection.value);
};

const columns: TableColumn<Match>[] = [
  {
    id: 'select',
    header: ({ table }) =>
      h(UCheckbox, {
        modelValue: table.getIsSomePageRowsSelected() ? 'indeterminate' : table.getIsAllPageRowsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') => table.toggleAllPageRowsSelected(!!value),
        'aria-label': 'Select all',
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        modelValue: row.getIsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') => row.toggleSelected(!!value),
        'aria-label': 'Select row',
      }),
  },
  {
    accessorKey: 'label',
    header: t('grid.columns.labels.match'),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.matchType'),
  },
  {
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    meta: {
      class: {
        th: 'w-24',
      },
    },
    cell: ({ row }) => {
      const match = row.original;
      return h(UButton, {
        as: 'a',
        href: match.uri,
        target: '_blank',
        label: t('grid.columns.actions.view'),
        icon: 'i-lucide-eye',
        color: 'primary',
        variant: 'outline',
        size: 'xs',
      });
    },
  },
];

const tableData = ref<Match[]>([]);
const getMatch = async (uri: string): Promise<Match> => {
  const match = matchStore.getMatch(uri);
  if (match) return match;

  const byUri = await apiService.getByUri<{ id: string; concept_scheme: { id: string } }>(uri);
  const concept = await conceptStore.getConcept(byUri.concept_scheme.id, Number(byUri.id));

  matchStore.setMatch({ uri, label: concept?.label || uri });

  return { label: concept?.label || uri, uri: concept?.uri || uri };
};

onMounted(async () => {
  if (!selectedConcept.value) return;

  try {
    adminUiStore.startLoading(GET_MATCH_LOADING_KEY);
    tableData.value = await Promise.all(
      Object.entries(selectedConcept.value?.matches ?? {})
        .map(([type, matches]) => {
          return matches.map(async (uri: string) => {
            const match = await getMatch(uri);
            return {
              label: match.label,
              type: t(`lists.matchTypes.${type}`),
              uri: match.uri,
            };
          });
        })
        .flat()
    );
  } catch (error) {
    console.error(error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.match') }),
      description: t('api.errors.fetch.description', { item: t('entities.match') }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    adminUiStore.stopLoading(GET_MATCH_LOADING_KEY);
  }
});

// Save handler
const save = async () => {
  if (!selectedConcept.value) return;
};
</script>
