<template>
  <div class="flex w-full flex-1 flex-col divide-y divide-accented min-h-0 rounded-lg border border-default">
    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:pagination="pagination"
      sticky
      class="flex-1 min-h-0 rounded-t-lg"
      :data="tableData"
      :columns="columns"
      :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
    >
      <template #label-cell="{ row }">
        <div>
          <ULink
            :to="{ name: 'AdminConceptscheme', params: { id: row.original.id } }"
            class="font-medium text-primary hover:underline"
          >
            {{ row.original.label }}
          </ULink>
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

<script lang="ts">
export interface ConceptSchemeRow {
  id: string;
  uri: string;
  label: string;
}
</script>

<script setup lang="ts">
import { h, ref, computed, resolveComponent, useTemplateRef } from 'vue';
import { getPaginationRowModel } from '@tanstack/vue-table';
import type { TableColumn } from '@nuxt/ui';
import type { ConceptScheme } from '@models/conceptscheme';
import { ApiService } from '@services/api.service';
import { useI18n } from 'vue-i18n';

const UButton = resolveComponent('UButton');

const { t } = useI18n();
const toast = useToast();
const apiService = new ApiService();

const conceptschemes = ref<ConceptScheme[]>([]);

const fetchConceptschemes = async () => {
  try {
    conceptschemes.value = await apiService.getConceptschemes();
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: 'conceptschemes' }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: 'conceptschemes' }),
      description: t('api.errors.fetch.description', { item: 'conceptschemes' }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

// Initial fetch
await fetchConceptschemes();

const tableData = computed<ConceptSchemeRow[]>(() =>
  conceptschemes.value.map((cs) => ({
    id: cs.id,
    uri: cs.uri,
    label: cs.label,
  }))
);

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<ConceptSchemeRow> }>('tableRef');
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const columns: TableColumn<ConceptSchemeRow>[] = [
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
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: ({ row }) =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          as: 'a',
          to: { name: 'AdminConceptscheme', params: { id: row.original.id } },
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
      ]),
  },
];
</script>
