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

    <ModalLanguage :key="languageModalKey" />
    <ModalDelete
      v-model:open="modalDeleteIsOpen"
      :entity="t('entities.language')"
      :item="`${selectedLanguage?.id} (${selectedLanguage?.name})`"
      @confirm="deleteLanguage"
    />
  </div>
</template>

<script setup lang="ts">
import type { Language } from '@models/language';
import { ModalMode } from '@models/util';
import type { TableColumn } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useLanguageStore } from '@stores/language';
import { useListStore } from '@stores/list';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { storeToRefs } from 'pinia';
import { computed, h, ref, resolveComponent, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

const UButton = resolveComponent('UButton');

const { t } = useI18n();
const toast = useToast();
const apiService = new ApiService();

const adminUiStore = useAdminUiStore();
const { languageModalKey } = storeToRefs(adminUiStore);
const listStore = useListStore();
const { languages } = storeToRefs(listStore);
const languageStore = useLanguageStore();
const { selectedLanguage } = storeToRefs(languageStore);

const LANGUAGE_LOADING_KEY = 'language-fetch';

const modalDeleteIsOpen = ref(false);
const deleteLanguage = async () => {
  if (!selectedLanguage.value?.id) return;

  try {
    adminUiStore.startLoading('deleteLanguage');
    await apiService.deleteLanguage(selectedLanguage.value.id);
    toast.add({
      title: t('api.success.delete.title', { item: 'Language' }),
      description: t('api.success.delete.description', { item: 'language' }),
      icon: 'i-lucide-check',
      color: 'success',
    });
    languageStore.resetSelectedLanguage();
    listStore.fetchLanguages();
  } catch (error) {
    console.error(t('api.errors.delete.title', { item: 'Language' }), error);
    toast.add({
      title: t('api.errors.delete.title', { item: 'language' }),
      description: t('api.errors.delete.description', { item: 'language' }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    modalDeleteIsOpen.value = false;
    adminUiStore.stopLoading('deleteLanguage');
  }
};

// Initial fetch
await listStore.fetchLanguages();

adminUiStore.$onAction(({ name }) => {
  // Refresh languages list after closing the language modal
  if (name === 'closeLanguageModal') {
    listStore.fetchLanguages();
  }
});

const tableRef = useTemplateRef<{ tableApi: import('@tanstack/vue-table').Table<Language> }>('tableRef');
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
    cell: ({ row }) =>
      h('div', { class: 'flex items-center gap-1' }, [
        h(UButton, {
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          title: t('grid.columns.actions.edit'),
          onClick: async () => {
            try {
              adminUiStore.startLoading(LANGUAGE_LOADING_KEY);
              const language = await languageStore.getLanguage(row.original.id!, true);
              languageStore.setSelectedLanguage(language);
              adminUiStore.openLanguageModal(ModalMode.EDIT);
            } catch (error) {
              console.error(t('api.errors.fetch.title', { item: 'language' }), error);
            } finally {
              adminUiStore.stopLoading(LANGUAGE_LOADING_KEY);
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
            languageStore.setSelectedLanguage(row.original);
            modalDeleteIsOpen.value = true;
          },
        }),
      ]),
  },
];
</script>
