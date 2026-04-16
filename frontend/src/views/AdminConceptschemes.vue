<template>
  <div class="flex w-full flex-col h-full min-h-0">
    <!-- Toolbar -->
    <div class="flex items-center justify-between py-3.5">
      <div class="flex items-center gap-2">
        <USelect v-model="bulkAction" :items="bulkActionItems" placeholder="Bulk actie" class="w-44" />
        <UButton label="Toepassen" color="primary" variant="outline" />
      </div>

      <UInput v-model="globalFilter" placeholder="Zoek conceptschema" icon="i-lucide-search" class="w-64" />
    </div>

    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:row-selection="rowSelection"
      v-model:pagination="pagination"
      v-model:global-filter="globalFilter"
      class="flex-1 min-h-0 overflow-auto"
      :ui="{
        thead: 'sticky top-0 z-10 bg-default',
      }"
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
    <div class="flex items-center justify-between border-t border-default pt-4 mt-4">
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
import { getPaginationRowModel } from '@tanstack/vue-table';
import { useClipboard } from '@vueuse/core';
import type { TableColumn } from '@nuxt/ui';
import type { ConceptScheme } from '@models/conceptscheme';
import { ApiService } from '@services/api.service';

const UCheckbox = resolveComponent('UCheckbox');
const UBadge = resolveComponent('UBadge');
const UButton = resolveComponent('UButton');
const USelect = resolveComponent('USelect');
const UInput = resolveComponent('UInput');
const UTable = resolveComponent('UTable');
const UPagination = resolveComponent('UPagination');

const toast = useToast();
const { copy } = useClipboard();
const apiService = new ApiService();

type PublicationStatus = 'published' | 'hidden' | 'draft';

interface ConceptSchemeRow {
  id: string;
  uri: string;
  label: string;
  publicationStatus: PublicationStatus;
}

const conceptschemes = ref<ConceptScheme[]>([]);

try {
  conceptschemes.value = await apiService.getConceptschemes();
} catch (error) {
  console.error('Error fetching conceptschemes:', error);
  toast.add({
    title: 'Failed to fetch conceptschemes.',
    description: 'Please try again later.',
    icon: 'i-lucide-alert-triangle',
    color: 'error',
  });
}

const tableData = computed<ConceptSchemeRow[]>(() =>
  conceptschemes.value.map((cs) => ({
    id: cs.id,
    uri: cs.uri,
    label: cs.label,
    publicationStatus: 'draft' as PublicationStatus,
  }))
);

const bulkAction = ref('');
const bulkActionItems = [
  { label: 'Publiceren', value: 'publish' },
  { label: 'Verbergen', value: 'hide' },
  { label: 'Verwijderen', value: 'delete' },
];

const globalFilter = ref('');

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<ConceptSchemeRow> }>('tableRef');
const rowSelection = ref<Record<string, boolean>>({});
const selectedCount = computed(() => tableRef.value?.tableApi?.getFilteredSelectedRowModel().rows.length ?? 0);
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const publicationStatusConfig: Record<PublicationStatus, { label: string; color: 'info' | 'neutral' | 'warning' }> = {
  published: { label: 'Published', color: 'info' },
  hidden: { label: 'Hidden', color: 'neutral' },
  draft: { label: 'Draft', color: 'neutral' },
};

const columns: TableColumn<ConceptSchemeRow>[] = [
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
    header: 'Label',
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'publicationStatus',
    header: 'Publicatie',
    cell: ({ row }) => {
      const status = row.getValue('publicationStatus') as PublicationStatus;
      const config = publicationStatusConfig[status];
      return h(UBadge, { variant: 'subtle', color: config.color }, () => config.label);
    },
  },
  {
    id: 'actions',
    header: 'Acties',
    cell: () =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          as: 'a',
          href: '#',
          label: 'Bekijken',
          icon: 'i-lucide-eye',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
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
          label: 'Toegang',
          icon: 'i-lucide-users',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
        }),
        h(UButton, {
          as: 'a',
          href: '#',
          label: 'Publicatie',
          icon: 'i-lucide-upload',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
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
