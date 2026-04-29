<template>
  <div
    class="mx-auto flex w-full max-w-4xl flex-1 flex-col min-h-0 divide-y divide-accented rounded-lg border border-default"
  >
    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:pagination="pagination"
      sticky
      class="flex-1 min-h-0 rounded-t-lg"
      :data="languages"
      :columns="columns"
      :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
    />

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
import type { Language } from '@models/language';
import type { Provider } from '@models/provider';
import type { TableColumn } from '@nuxt/ui';
import { useListStore } from '@stores/list';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { storeToRefs } from 'pinia';
import { computed, h, ref, resolveComponent, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

const UButton = resolveComponent('UButton');

const { t } = useI18n();
const listStore = useListStore();
const { languages } = storeToRefs(listStore);

// Initial fetch
await listStore.fetchLanguages();

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<Provider> }>('tableRef');
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const columns: TableColumn<Language>[] = [
  {
    accessorKey: 'id',
    header: t('grid.columns.labels.id'),
  },
  {
    accessorKey: 'name',
    header: t('grid.columns.labels.name'),
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
    cell: () =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          title: t('grid.columns.actions.edit'),
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'outline',
          size: 'xs',
          title: t('grid.columns.actions.delete'),
        }),
      ]),
  },
];
</script>
