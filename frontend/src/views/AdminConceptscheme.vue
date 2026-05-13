<template>
  <div class="flex w-full flex-1 flex-col divide-y divide-accented min-h-0 rounded-lg border border-default">
    <!-- Toolbar -->
    <div class="flex justify-end px-4 py-3.5 gap-2">
      <UInput
        v-model="labelFilter"
        :placeholder="t('views.adminConceptscheme.form.labelFilter.placeholder')"
        icon="i-lucide-search"
        class="w-64"
        @keydown.enter="fetchConcepts"
      />
      <UTooltip :text="t('views.adminConceptscheme.form.matchFilter.tooltip')">
        <UInput
          v-model="matchFilter"
          :placeholder="t('views.adminConceptscheme.form.matchFilter.placeholder')"
          icon="i-lucide-search"
          class="w-64"
          @keydown.enter="fetchConcepts"
        />
      </UTooltip>
      <USelectMenu
        v-model="typeFilter"
        :items="conceptTypes"
        :placeholder="t('views.adminConceptscheme.form.typeFilter.placeholder')"
        class="w-36"
        :search-input="false"
        clear
      />
    </div>

    <!-- Table -->
    <UTable
      ref="tableRef"
      v-model:pagination="pagination"
      v-model:sorting="sorting"
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
        <ConceptExpanded :scheme-id="schemeId" :concept-id="row.original.id" />
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

    <ModalConcept :key="conceptModalKey" />
    <ModalMerge :key="mergeModalKey" />
    <ModalDelete
      v-model:open="modalDeleteIsOpen"
      :entity="t('entities.concept')"
      :item="`${selectedConcept?.label} (${selectedConcept?.id}) from scheme ${selectedConceptscheme?.id}`"
      @confirm="deleteConcept"
    />
  </div>
</template>

<script setup lang="ts">
import type { Concept, OverviewConcept } from '@models/concept';
import type { Conceptscheme } from '@models/conceptscheme';
import { ConceptTypeEnum, ModalMode } from '@models/util';
import SortableHeader from '@components/SortableHeader.vue';
import type { TableColumn } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptStore } from '@stores/concept';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { useListStore } from '@stores/list';
import { getPaginationRowModel } from '@tanstack/vue-table';
import { storeToRefs } from 'pinia';
import { capitalize, computed, h, onMounted, ref, resolveComponent, useTemplateRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

const UButton = resolveComponent('UButton');
const UBadge = resolveComponent('UBadge');

const { t } = useI18n();
const toast = useToast();
const router = useRouter();
const route = useRoute();

const CONCEPT_LOADING_KEY = 'concept-fetch';

const adminUiStore = useAdminUiStore();
const { conceptModalKey, mergeModalKey } = storeToRefs(adminUiStore);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);
const conceptStore = useConceptStore();
const { selectedConcept } = storeToRefs(conceptStore);
const listStore = useListStore();
const { conceptTypes } = storeToRefs(listStore);
const apiService = new ApiService();

const schemeId = route.params.id as string;

const concepts = ref<OverviewConcept[]>([]);
const typeFilter = ref<(typeof conceptTypes.value)[number]>();
const labelFilter = ref('');
const matchFilter = ref('');

const fetchConceptscheme = async () => {
  try {
    const conceptscheme = (await conceptschemeStore.getConceptscheme(schemeId)) as Conceptscheme;
    conceptschemeStore.setSelectedConceptscheme(conceptscheme);
    adminUiStore.setBreadcrumbLabel(schemeId, conceptscheme.label);
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.conceptscheme', 1) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.conceptscheme', 1) }),
      description: t('api.errors.fetch.description', { item: t('entities.conceptscheme', 1) }),
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
    console.error(t('api.errors.fetch.title', { item: t('entities.concept', 2) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.concept', 2) }),
      description: t('api.errors.fetch.description', { item: t('entities.concept', 2) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
};

const modalDeleteIsOpen = ref(false);
const deleteConcept = async () => {
  if (!selectedConcept.value?.id) return;

  try {
    adminUiStore.startLoading('deleteConcept');
    await apiService.deleteConcept(selectedConceptscheme.value!.id, selectedConcept.value.id);
    toast.add({
      title: t('api.success.delete.title', { item: capitalize(t('entities.concept', 1)) }),
      description: t('api.success.delete.description', { item: t('entities.concept', 1) }),
      icon: 'i-lucide-check',
      color: 'success',
    });
    conceptStore.resetSelectedConcept();
    await fetchConcepts();
  } catch (error) {
    console.error(t('api.errors.delete.title', { item: capitalize(t('entities.concept', 1)) }), error);
    toast.add({
      title: t('api.errors.delete.title', { item: capitalize(t('entities.concept', 1)) }),
      description: t('api.errors.delete.description', { item: t('entities.concept', 1) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    modalDeleteIsOpen.value = false;
    adminUiStore.stopLoading('deleteConcept');
  }
};

// Initial fetch
await fetchConceptscheme();
await fetchConcepts();

adminUiStore.$onAction(async ({ name }) => {
  // Refresh concepts list after closing the concept modal
  if (name === 'closeConceptModal') {
    await fetchConcepts();
  }
});

onMounted(() => {
  if (route.query.edit) {
    const conceptId = route.query.edit as string;
    const concept = concepts.value.find((c) => c.id === conceptId);
    if (concept) {
      openConceptModal(concept.id);
    }
    router.replace({ query: undefined });
  }
});

const openConceptModal = async (conceptId: string) => {
  try {
    adminUiStore.startLoading(CONCEPT_LOADING_KEY);
    const concept = await conceptStore.getConcept(selectedConceptscheme.value?.id as string, conceptId, true);
    conceptStore.setSelectedConcept(concept as Concept);
    adminUiStore.openConceptModal(ModalMode.EDIT);
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.concept') }), error);
  } finally {
    adminUiStore.stopLoading(CONCEPT_LOADING_KEY);
  }
};

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
const sorting = ref([]);

const onMergeClick = async (row: OverviewConcept) => {
  try {
    adminUiStore.startLoading(CONCEPT_LOADING_KEY);
    const concept = await conceptStore.getConcept(selectedConceptscheme.value?.id as string, row.id, true);

    if (!concept) {
      throw new Error('Concept not found');
    }

    conceptStore.setSelectedConcept(concept);
    const hasMatches = Object.values(concept.matches ?? {}).some((matchArray) => matchArray.length > 0);

    if (hasMatches) {
      adminUiStore.openMergeModal();
    } else {
      toast.add({
        title: t('components.modalMerge.noMatchesTitle'),
        description: t('components.modalMerge.noMatchesDescription'),
        icon: 'i-lucide-info',
        color: 'info',
      });
    }
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.concept') }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.concept') }),
      description: t('api.errors.fetch.description', { item: t('entities.concept') }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    adminUiStore.stopLoading(CONCEPT_LOADING_KEY);
  }
};

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
    header: ({ column }) => h(SortableHeader, { label: t('grid.columns.labels.label'), column }),
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'id',
    header: ({ column }) => h(SortableHeader, { label: t('grid.columns.labels.id'), column }),
  },
  {
    accessorKey: 'type',
    header: ({ column }) => h(SortableHeader, { label: t('grid.columns.labels.type'), column }),
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
          disabled: row.original.type !== ConceptTypeEnum.CONCEPT,
          onClick: async () => onMergeClick(row.original),
        }),
        h(UButton, {
          as: 'a',
          href: row.original.uri,
          target: '_blank',
          label: t('grid.columns.actions.view'),
          icon: 'i-lucide-file-text',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
        }),
        h(UButton, {
          label: t('grid.columns.actions.edit'),
          icon: 'i-lucide-pencil',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          onClick: async () => openConceptModal(row.original.id),
        }),
        h(UButton, {
          icon: 'i-lucide-trash-2',
          color: 'error',
          variant: 'ghost',
          size: 'xs',
          'aria-label': t('grid.columns.actions.delete'),
          onClick: () => {
            conceptStore.setSelectedConcept(row.original as Concept);
            modalDeleteIsOpen.value = true;
          },
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
