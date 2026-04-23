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

    <ModalProvider v-model:open="adminUiStore.addProviderModalIsOpen" />
  </div>
</template>

<script setup lang="ts">
import type { Provider } from '@models/provider';
import type { TableColumn } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@/stores/admin-ui';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { h, computed, ref, useTemplateRef, resolveComponent } from 'vue';
import { useI18n } from 'vue-i18n';

const UButton = resolveComponent('UButton');

const { t } = useI18n();
const toast = useToast();
const apiService = new ApiService();
const adminUiStore = useAdminUiStore();

const providers = ref<Provider[]>([]);

const fetchProviders = async () => {
  try {
    providers.value = await apiService.getProviders();
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: 'providers' }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: 'providers' }),
      description: t('api.errors.fetch.description', { item: 'providers' }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

// Initial fetch
await fetchProviders();

adminUiStore.$onAction(({ name }) => {
  // Refresh providers list after closing the add provider modal
  if (name === 'closeAddProviderModal') {
    fetchProviders();
  }
});

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<Provider> }>('tableRef');
const totalCount = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const totalFiltered = computed(() => tableRef.value?.tableApi?.getFilteredRowModel().rows.length ?? 0);
const currentPage = computed(() => (tableRef.value?.tableApi?.getState().pagination.pageIndex ?? 0) + 1);

const pagination = ref({
  pageIndex: 0,
  pageSize: 15,
});

const columns: TableColumn<Provider>[] = [
  {
    accessorKey: 'id',
    header: t('grid.columns.labels.id'),
  },
  {
    accessorKey: 'conceptscheme_uri',
    header: t('grid.columns.labels.conceptschemeUri'),
    meta: {
      class: {
        th: 'max-w-3xs truncate',
        td: 'max-w-3xs truncate',
      },
    },
  },
  {
    accessorKey: 'uri_pattern',
    header: t('grid.columns.labels.uriPattern'),
    meta: {
      class: {
        th: 'max-w-3xs truncate',
        td: 'max-w-3xs truncate',
      },
    },
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
  },
  {
    accessorKey: 'default_language',
    header: t('grid.columns.labels.defaultLanguage'),
  },
  {
    accessorKey: 'id_generation_strategy',
    header: t('grid.columns.labels.idGenerationStrategy'),
  },
  {
    accessorKey: 'subject',
    header: t('grid.columns.labels.subject'),
  },
  {
    accessorKey: 'expand_strategy',
    header: t('grid.columns.labels.expandStrategy'),
  },
  {
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: () =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          as: 'a',
          href: '#',
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
          class: 'cursor-pointer',
          title: t('grid.columns.actions.delete'),
        }),
      ]),
  },
];
</script>
