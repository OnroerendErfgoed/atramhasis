<template>
  <div class="flex w-full flex-1 flex-col divide-y divide-accented min-h-0 rounded-lg border border-default">
    <!-- Toolbar -->
    <div class="flex justify-end px-4 py-3.5 gap-2">
      <UInput v-model="globalFilter" placeholder="Zoek concept" icon="i-lucide-search" class="w-64" />
      <USelect v-model="typeFilter" :items="typeFilterItems" placeholder="Type" class="w-36" />
    </div>

    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:row-selection="rowSelection"
      v-model:pagination="pagination"
      v-model:global-filter="globalFilter"
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
            <UButton
              icon="i-lucide-copy"
              color="neutral"
              variant="ghost"
              size="xs"
              class="p-0.5"
              aria-label="Kopieer URI"
              @click="copyUri(row.original.uri)"
            />
          </div>
        </div>
      </template>
    </UTable>

    <!-- Footer -->
    <div class="flex items-center justify-between px-4 py-3.5">
      <p class="text-sm text-muted">{{ selectedCount }} of {{ totalCount }} row(s) selected.</p>

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
import { h, ref, computed, resolveComponent, useTemplateRef } from 'vue';
import { useRoute } from 'vue-router';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { useClipboard } from '@vueuse/core';
import type { TableColumn } from '@nuxt/ui';
import type { Concept } from '@models/concept';
import { ApiService } from '@services/api.service';

const UCheckbox = resolveComponent('UCheckbox');
const UButton = resolveComponent('UButton');
const UBadge = resolveComponent('UBadge');
const USelect = resolveComponent('USelect');
const UInput = resolveComponent('UInput');
const UTable = resolveComponent('UTable');
const UPagination = resolveComponent('UPagination');

const toast = useToast();
const route = useRoute();
const { copy } = useClipboard();
const apiService = new ApiService();

const schemeId = route.params.id as string;

interface ConceptRow {
  id: string;
  uri: string;
  label: string;
  type: 'concept' | 'collection';
}

const concepts = ref<Concept[]>([]);
const typeFilter = ref('');

const fetchConcepts = async () => {
  try {
    concepts.value = await apiService.getConceptscheme(schemeId, {
      type: typeFilter.value || 'all',
      sort: '+label',
    });
  } catch (error) {
    console.error('Error fetching concepts:', error);
    toast.add({
      title: 'Failed to fetch concepts.',
      description: 'Please try again later.',
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

await fetchConcepts();

const tableData = computed<ConceptRow[]>(() => {
  let rows = concepts.value.map((c) => ({
    id: c.id,
    uri: c.uri,
    label: c.label,
    type: c.type,
  }));
  if (typeFilter.value) {
    rows = rows.filter((r) => r.type === typeFilter.value);
  }
  return rows;
});

const typeFilterItems = [
  { label: 'Concept', value: 'concept' },
  { label: 'Collection', value: 'collection' },
];

const globalFilter = ref('');

const expandedRows = ref<Record<string, boolean>>({});
const toggleExpand = (id: string) => {
  expandedRows.value[id] = !expandedRows.value[id];
};

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<ConceptRow> }>('tableRef');
const rowSelection = ref<Record<string, boolean>>({});
const selectedCount = computed(() => tableRef.value?.tableApi?.getFilteredSelectedRowModel().rows.length ?? 0);
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const columns: TableColumn<ConceptRow>[] = [
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
    header: 'Label',
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'id',
    header: 'ID',
  },
  {
    accessorKey: 'type',
    header: 'Type',
    cell: ({ row }) =>
      h(UBadge, {
        label: row.original.type === 'concept' ? 'Concept' : 'Collection',
        color: 'neutral',
        variant: 'outline',
        size: 'sm',
      }),
  },
  {
    id: 'actions',
    header: 'Acties',
    cell: ({ row }) =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          label: 'Merge',
          icon: 'i-lucide-git-merge',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          disabled: row.original.type !== 'concept',
        }),
        h(UButton, {
          as: 'a',
          href: '#',
          label: 'Bewerken',
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
        }),
        h(UButton, {
          as: 'a',
          href: '#',
          label: 'View',
          icon: 'i-lucide-external-link',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': 'Verwijderen',
        }),
      ]),
  },
];

const copyUri = (uri: string) => {
  copy(uri);
  toast.add({
    title: 'URI gekopieerd naar klembord.',
    icon: 'i-lucide-check',
    color: 'success',
  });
};
</script>
