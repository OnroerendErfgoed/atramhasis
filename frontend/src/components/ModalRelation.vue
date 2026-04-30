<template>
  <UModal
    v-model:open="relationModalIsOpen"
    :dismissible="false"
    :title="title"
    :description="capitalize(t('components.modalRelation.description'))"
  >
    <template #body>
      <UTree :items="treeItems" virtualize @select="onSelect" />
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.add')" @click="add" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { storeToRefs } from 'pinia';
import { capitalize, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { TreeItem } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { ConceptTypeEnum } from '@models/util';
import type { Tree } from '@models/tree';

const props = defineProps<{
  title: string;
  scheme: string;
}>();

const emit = defineEmits<{
  add: [void];
}>();

const { t } = useI18n();

const apiService = new ApiService();

const adminUiStore = useAdminUiStore();
const { relationModalIsOpen } = storeToRefs(adminUiStore);

const treeItems = ref<TreeItem[]>([]);

const formatTreeItems = (items: Tree[]): TreeItem[] => {
  return items.map((item) => ({
    id: item.id,
    label: item.label,
    icon: item.type === ConceptTypeEnum.COLLECTION ? 'i-lucide-folder' : 'i-lucide-file',
    children: item.children ? formatTreeItems(item.children) : undefined,
  }));
};

const onSelect = (e: Event, item: TreeItem) => {
  console.log('Selected item:', item);
};

onMounted(async () => {
  const data = await apiService.getTreeByConceptscheme(props.scheme);
  treeItems.value = formatTreeItems(data);
});

const add = () => {
  emit('add');
};
</script>
