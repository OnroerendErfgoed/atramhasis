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
        :items="typeFilterItems"
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
import type { Concept } from '@models/concept';
import { ApiService } from '@services/api.service';
import { useI18n } from 'vue-i18n';
import ClipboardCopy from '@components/ClipboardCopy.vue';
import type { ListType } from '@models/util';

const UButton = resolveComponent('UButton');
const UBadge = resolveComponent('UBadge');
const USelectMenu = resolveComponent('USelectMenu');
const UInput = resolveComponent('UInput');
const UTable = resolveComponent('UTable');
const UPagination = resolveComponent('UPagination');

const { t } = useI18n();
const toast = useToast();
const route = useRoute();
const apiService = new ApiService();

const schemeId = route.params.id as string;

const concepts = ref<Concept[]>([]);
const typeFilter = ref<ListType>();
const labelFilter = ref('');
const matchFilter = ref('');

const fetchConcepts = async () => {
  try {
    concepts.value = await apiService.getConceptscheme(schemeId, {
      label: labelFilter.value || undefined,
      match: matchFilter.value || undefined,
    });
  } catch (error) {
    console.error(t('errors.fetch.title'), error);
    toast.add({
      title: t('errors.fetch.title'),
      description: t('errors.fetch.description'),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

await fetchConcepts();

const tableData = computed<Concept[]>(() => {
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

const typeFilterItems: ListType[] = [
  { label: 'Concept', value: 'concept' },
  { label: 'Collection', value: 'collection' },
];

const expandedRows = ref<Record<string, boolean>>({});
const toggleExpand = (id: string) => {
  expandedRows.value[id] = !expandedRows.value[id];
};

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<Concept> }>('tableRef');
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const columns: TableColumn<Concept>[] = [
  {
    id: 'expand',
    cell: ({ row }) =>
      h(UButton, {
        icon: expandedRows.value[row.original.id] ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down',
        color: 'neutral',
        variant: 'ghost',
        size: 'xs',
        onClick: () => toggleExpand(row.original.id),
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
