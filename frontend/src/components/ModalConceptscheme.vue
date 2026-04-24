<template>
  <UModal
    v-model:open="conceptschemeModalIsOpen"
    :title="t('components.modalConceptscheme.title', { conceptscheme: selectedConceptscheme?.label })"
    :description="t('components.modalConceptscheme.description', { tab: tabs[+activeTab]?.label })"
    class="max-w-4xl"
  >
    <template #body>
      <UTabs v-model="activeTab" color="neutral" variant="link" :items="tabs" class="w-full">
        <template #labels>
          <UTable
            class="flex-1 min-h-0 rounded-lg border border-default"
            :data="labelsWithAddRow"
            :columns="labelColumns"
          />
        </template>

        <template #notes>
          <pre>{{ selectedConceptscheme }}</pre>
        </template>

        <template #sources>
          <pre>{{ selectedConceptscheme }}</pre>
        </template>
      </UTabs>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" class="cursor-pointer" @click="close" />
        <UButton :label="t('actions.save')" class="cursor-pointer" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptschemeStore } from '@stores/conceptscheme';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import type { TableColumn, TabsItem } from '@nuxt/ui';
import { computed, h, ref, resolveComponent } from 'vue';
import { LabelEnum, type Label } from '@models/util';

const UButton = resolveComponent('UButton');

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { conceptschemeModalIsOpen } = storeToRefs(adminUiStore);
const conceptschemeStore = useConceptschemeStore();
const { selectedConceptscheme } = storeToRefs(conceptschemeStore);

const activeTab = ref('0');
const tabs = ref<TabsItem[]>([
  {
    label: t('components.modalConceptscheme.tabs.labels'),
    slot: 'labels',
  },
  {
    label: t('components.modalConceptscheme.tabs.notes'),
    slot: 'notes',
  },
  {
    label: t('components.modalConceptscheme.tabs.sources'),
    slot: 'sources',
  },
]);

const save = () => {
  console.log('Save button clicked');
};

const addLabel = () => {
  console.log('Add label clicked');
};

type LabelTableRow = Label & {
  isAddRow?: boolean;
};

const labelsWithAddRow = computed<LabelTableRow[]>(() => [
  ...((selectedConceptscheme.value?.labels ?? []) as LabelTableRow[]),
  {
    label: '',
    language: '',
    type: LabelEnum.PREF,
    isAddRow: true,
  },
]);

const labelColumns: TableColumn<LabelTableRow>[] = [
  {
    accessorKey: 'label',
    header: t('grid.columns.labels.label'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return h(UButton, {
          label: t('actions.add'),
          icon: 'i-lucide-plus',
          color: 'primary',
          variant: 'outline',
          size: 'xs',
          class: 'cursor-pointer',
          onClick: addLabel,
        });
      }

      return row.original.label;
    },
    meta: {
      class: {
        th: 'w-full',
        td: 'w-full',
      },
    },
  },
  {
    accessorKey: 'language',
    header: t('grid.columns.labels.language'),
    cell: ({ row }) => (row.original.isAddRow ? '' : t('languages.' + row.original.language)),
  },
  {
    accessorKey: 'type',
    header: t('grid.columns.labels.type'),
    cell: ({ row }) => (row.original.isAddRow ? '' : t('labelTypes.' + row.original.type)),
  },
  {
    id: 'actions',
    header: t('grid.columns.labels.actions'),
    cell: ({ row }) => {
      if (row.original.isAddRow) {
        return '';
      }

      return h('div', { class: 'flex items-center gap-1' }, [
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
      ]);
    },
  },
];
</script>
