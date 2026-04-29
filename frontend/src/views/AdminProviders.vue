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

    <ModalProvider :key="providerModalKey" />
    <ModalDelete
      v-model:open="modalDeleteIsOpen"
      :entity="t('entities.provider')"
      :item="`${selectedProvider?.id} (${selectedProvider?.conceptscheme_uri})`"
      @confirm="deleteProvider"
    />
  </div>
</template>

<script setup lang="ts">
import type { Provider } from '@models/provider';
import type { TableColumn } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@/stores/admin-ui';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { h, computed, ref, useTemplateRef, resolveComponent, capitalize } from 'vue';
import { useI18n } from 'vue-i18n';
import { ModalMode } from '@models/util';
import { useProviderStore } from '@stores/provider';
import { storeToRefs } from 'pinia';

const UButton = resolveComponent('UButton');

const { t } = useI18n();
const toast = useToast();
const apiService = new ApiService();
const adminUiStore = useAdminUiStore();
const { providerModalKey } = storeToRefs(adminUiStore);

const providerStore = useProviderStore();
const { selectedProvider } = storeToRefs(providerStore);
const providers = ref<Provider[]>([]);

const PROVIDER_LOADING_KEY = 'provider-fetch';

const fetchProviders = async () => {
  try {
    providers.value = (await apiService.getProviders()).sort((a, b) => a.id!.localeCompare(b.id!));
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.provider', 2) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.provider', 2) }),
      description: t('api.errors.fetch.description', { item: t('entities.provider', 2) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

const modalDeleteIsOpen = ref(false);
const deleteProvider = async () => {
  if (!selectedProvider.value?.id) return;

  try {
    adminUiStore.startLoading('deleteProvider');
    await apiService.deleteProvider(selectedProvider.value.id);
    toast.add({
      title: t('api.success.delete.title', { item: capitalize(t('entities.provider', 1)) }),
      description: t('api.success.delete.description', { item: t('entities.provider', 1) }),
      icon: 'i-lucide-check',
      color: 'success',
    });
    providerStore.resetSelectedProvider();
    fetchProviders();
  } catch (error) {
    console.error(t('api.errors.delete.title', { item: capitalize(t('entities.provider', 1)) }), error);
    toast.add({
      title: t('api.errors.delete.title', { item: capitalize(t('entities.provider', 1)) }),
      description: t('api.errors.delete.description', { item: t('entities.provider', 1) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    modalDeleteIsOpen.value = false;
    adminUiStore.stopLoading('deleteProvider');
  }
};

// Initial fetch
await fetchProviders();

adminUiStore.$onAction(({ name }) => {
  // Refresh providers list after closing the provider modal
  if (name === 'closeProviderModal') {
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
    cell: ({ row }) =>
      h('div', { class: 'flex items-center gap-1' }, [
        ...(!row.original.subject?.includes('external')
          ? [
              h(UButton, {
                label: t('grid.columns.actions.edit'),
                icon: 'i-lucide-pencil',
                color: 'primary',
                variant: 'outline',
                size: 'xs',
                title: t('grid.columns.actions.edit'),
                onClick: async () => {
                  try {
                    adminUiStore.startLoading(PROVIDER_LOADING_KEY);
                    const provider = await providerStore.getProvider(row.original.id!, true);
                    providerStore.setSelectedProvider(provider);
                    adminUiStore.openProviderModal(ModalMode.EDIT);
                  } catch (error) {
                    console.error(t('api.errors.fetch.title', { item: t('entities.provider', 1) }), error);
                  } finally {
                    adminUiStore.stopLoading(PROVIDER_LOADING_KEY);
                  }
                },
              }),
              h(UButton, {
                icon: 'i-lucide-trash-2',
                color: 'error',
                variant: 'outline',
                size: 'xs',
                title: t('grid.columns.actions.delete'),
                onClick: () => {
                  providerStore.setSelectedProvider(row.original);
                  modalDeleteIsOpen.value = true;
                },
              }),
            ]
          : []),
      ]),
  },
];
</script>
