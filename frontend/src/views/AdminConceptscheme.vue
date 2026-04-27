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
  </div>
</template>

<script setup lang="ts">
import { h, ref, computed, resolveComponent, useTemplateRef, capitalize, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getPaginationRowModel } from '@tanstack/vue-table';
import type { TableColumn } from '@nuxt/ui';
import type { OverviewConcept } from '@models/concept';
import { ApiService } from '@services/api.service';
import { useI18n } from 'vue-i18n';
import { useAdminUiStore } from '@stores/admin-ui';
import type { Conceptscheme } from '@models/conceptscheme';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';

const UButton = resolveComponent('UButton');
const UBadge = resolveComponent('UBadge');

const { t } = useI18n();
const toast = useToast();
const route = useRoute();

const adminUiStore = useAdminUiStore();
const listStore = useListStore();
const { conceptTypes } = storeToRefs(listStore);
const apiService = new ApiService();

const schemeId = route.params.id as string;

const conceptscheme = ref<Conceptscheme>();
const concepts = ref<OverviewConcept[]>([]);
const typeFilter = ref<(typeof conceptTypes.value)[number]>();
const labelFilter = ref('');
const matchFilter = ref('');

const fetchConceptscheme = async () => {
  try {
    conceptscheme.value = await apiService.getConceptscheme(schemeId);
    adminUiStore.setBreadcrumbLabel(schemeId, conceptscheme.value.label);
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: 'conceptscheme' }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: 'conceptscheme' }),
      description: t('api.errors.fetch.description', { item: 'conceptscheme' }),
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
    console.error(t('api.errors.fetch.title', { item: 'concepts' }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: 'concepts' }),
      description: t('api.errors.fetch.description', { item: 'concepts' }),
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
          disabled: row.original.type !== 'concept',
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
          as: 'a',
          href: '#',
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
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
