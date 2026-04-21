<template>
  <div class="flex w-full flex-1 flex-col divide-y divide-accented min-h-0 rounded-lg border border-default">
    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:pagination="pagination"
      sticky
      class="flex-1 min-h-0 rounded-t-lg"
      :data="providers"
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
import type { Provider } from '@models/provider';
import type { TableColumn } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { h, computed, ref, useTemplateRef, resolveComponent } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const apiService = new ApiService();

const providers = ref<Provider[]>([]);

try {
  providers.value = await apiService.getProviders();
} catch (error) {
  console.error(t('errors.fetch.title'), error);
  toast.add({
    title: t('errors.fetch.title'),
    description: t('errors.fetch.description'),
    icon: 'i-lucide-alert-triangle',
    color: 'error',
  });
}

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<Provider> }>('tableRef');
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const UButton = resolveComponent('UButton');
const columns: TableColumn<Provider>[] = [
  {
    accessorKey: 'id',
    header: t('grid.columns.labels.id'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'conceptscheme_uri',
    header: t('grid.columns.labels.conceptschemeUri'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'uri_pattern',
    header: t('grid.columns.labels.uriPattern'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'default_language',
    header: t('grid.columns.labels.defaultLanguage'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'id_generation_strategy',
    header: t('grid.columns.labels.idGenerationStrategy'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'subject',
    header: t('grid.columns.labels.subject'),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'expand_strategy',
    header: t('grid.columns.labels.expandStrategy'),
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
          to: { name: 'AdminProvider', params: { id: row.original.id } },
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
