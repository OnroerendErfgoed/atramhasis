<template>
  <div class="flex w-full flex-1 flex-col divide-y divide-accented min-h-0 rounded-lg border border-default">
    <!-- Toolbar -->
    <div class="flex justify-end px-4 py-3.5 gap-2">
      <UInput
        v-model="labelFilter"
        :placeholder="t('placeholders.conceptScheme.label')"
        icon="i-lucide-search"
        class="w-64"
        @keydown.enter="fetchConcepts"
      />
      <UInput
        v-model="matchFilter"
        :placeholder="t('placeholders.conceptScheme.match')"
        icon="i-lucide-search"
        class="w-64"
        @keydown.enter="fetchConcepts"
      />
      <USelectMenu
        v-model="typeFilter"
        :items="conceptTypes"
        :placeholder="t('placeholders.conceptScheme.type')"
        class="w-36"
        :search-input="false"
        clear
      />
    </div>

    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:pagination="pagination"
      sticky
      class="flex-1 min-h-0"
      :ui="{ tr: 'data-[expanded=true]:bg-elevated/50' }"
      :data="tableData"
      :columns="columns"
      :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
    >
      <template #label-cell="{ row }">
        <div>
          <a href="#" class="font-medium text-primary hover:underline">
            {{ row.original.label }}
          </a>
          <div class="mt-0.5 flex items-center gap-1 text-xs text-muted">
            <span>{{ row.original.uri }}</span>
            <ClipboardCopy
              :text="row.original.uri"
              :aria-label="t('components.clipboardCopy.copy', { item: 'URI' }, 2)"
            />
          </div>
        </div>
      </template>
      <template #expanded="{ row }">
        <ConceptExpanded :scheme-id="schemeId" :concept-id="+row.original.id" />
      </template>
    </UTable>

    <!-- Footer -->
    <div class="flex items-center justify-between px-4 py-3.5">
      <p class="text-sm text-muted">{{ t('grid.rowsTotal', { n: totalCount }) }}</p>

      <UPagination
        :page="currentPage"
        :items-per-page="pagination.pageSize"
        :total="totalFiltered"
        show-edges
        :sibling-count="1"
        @update:page="(p: number) => tableRef?.tableApi?.setPageIndex(p - 1)"
      />
    </div>

    <ModalConcept :key="conceptModalKey" />
  </div>
</template>

<script setup lang="ts">
import { h, ref, computed, resolveComponent, useTemplateRef, capitalize, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getPaginationRowModel } from '@tanstack/vue-table';
import type { TableColumn } from '@nuxt/ui';
import type { Concept, OverviewConcept } from '@models/concept';
import { ApiService } from '@services/api.service';
import { useI18n } from 'vue-i18n';
import { useAdminUiStore } from '@stores/admin-ui';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';
import { useConceptschemeStore } from '@stores/conceptscheme';
import type { Conceptscheme } from '@models/conceptscheme';
import { ConceptTypeEnum, ModalMode } from '@models/util';
import { useConceptStore } from '@stores/concept';

const UButton = resolveComponent('UButton');
const UBadge = resolveComponent('UBadge');

const { t } = useI18n();
const toast = useToast();
const route = useRoute();

const CONCEPT_LOADING_KEY = 'concept-fetch';

const adminUiStore = useAdminUiStore();
const { conceptModalKey } = storeToRefs(adminUiStore);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const conceptStore = useConceptStore();
const listStore = useListStore();
const { conceptTypes } = storeToRefs(listStore);
const apiService = new ApiService();

const schemeId = route.params.id as string;

const concepts = ref<OverviewConcept[]>([]);
const typeFilter = ref<(typeof conceptTypes.value)[number]>();
const labelFilter = ref('');
const matchFilter = ref('');

const fetchConceptscheme = async () => {
  try {
    const conceptscheme = (await conceptschemeStore.getConceptscheme(schemeId)) as Conceptscheme;
    conceptschemeStore.setSelectedConceptscheme(conceptscheme);
    adminUiStore.setBreadcrumbLabel(schemeId, conceptscheme.label);
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.conceptscheme', 1) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.conceptscheme', 1) }),
      description: t('api.errors.fetch.description', { item: t('entities.conceptscheme', 1) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

const fetchConcepts = async () => {
  try {
    concepts.value = await apiService.getConceptsByConceptscheme(schemeId, {
      label: labelFilter.value || undefined,
      match: matchFilter.value || undefined,
    });
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.concept', 2) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.concept', 2) }),
      description: t('api.errors.fetch.description', { item: t('entities.concept', 2) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

// Initial fetch
await fetchConceptscheme();
await fetchConcepts();

const tableData = computed<OverviewConcept[]>(() => {
  let rows = concepts.value.map((c) => ({
    id: c.id,
    uri: c.uri,
    label: c.label,
    type: c.type,
  }));
  if (typeFilter.value) {
    rows = rows.filter((r) => r.type === typeFilter.value?.value);
  }
  return rows;
});

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<OverviewConcept> }>('tableRef');
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const columns: TableColumn<OverviewConcept>[] = [
  {
    id: 'expand',
    cell: ({ row }) =>
      h(UButton, {
        icon: 'i-lucide-chevron-down',
        color: 'neutral',
        variant: 'ghost',
        size: 'xs',
        ui: {
          leadingIcon: ['transition-transform', row.getIsExpanded() ? 'duration-200 rotate-180' : ''],
        },
        onClick: async () => row.toggleExpanded(),
      }),
  },
  {
    accessorKey: 'label',
    header: t('grid.columns.labels.label'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'id',
    header: t('grid.columns.labels.id'),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: ({ row }) =>
      h(UBadge, {
        label: capitalize(row.original.type),
        color: 'neutral',
        variant: 'outline',
        size: 'sm',
      }),
  },
  {
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: ({ row }) =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          label: t('grid.columns.actions.merge'),
          icon: 'i-lucide-git-merge',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          disabled: row.original.type !== ConceptTypeEnum.CONCEPT,
        }),
        h(UButton, {
          as: 'a',
          href: '#',
          label: t('grid.columns.actions.view'),
          icon: 'i-lucide-eye',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
        }),
        h(UButton, {
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          onClick: async () => {
            try {
              adminUiStore.startLoading(CONCEPT_LOADING_KEY);
              const concept = await conceptStore.getConcept(
                selectedConceptscheme.value?.id as string,
                row.original.id,
                true
              );
              conceptStore.setSelectedConcept(concept as Concept);
              adminUiStore.openConceptModal(ModalMode.EDIT);
            } catch (error) {
              console.error(t('api.errors.fetch.title', { item: t('entities.concept') }), error);
            } finally {
              adminUiStore.stopLoading(CONCEPT_LOADING_KEY);
            }
          },
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': t('grid.columns.actions.delete'),
        }),
      ]),
  },
];

watch([labelFilter, matchFilter], ([newLabel, newMatch]) => {
  if (newLabel === '' && newMatch === '') {
    fetchConcepts();
  }
});
</script>
