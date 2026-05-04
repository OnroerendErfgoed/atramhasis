<template>
  <UModal v-model:open="relationModalIsOpen" :dismissible="false" :title="t('components.modalRelation.title')">
    <template #body>
      <ALoader v-if="isFullscreenLoading" mode="fullscreen" />
      <UTree :items="treeItems" virtualize @select="onSelect" />
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.add')" :disabled="!selectedItem" @click="add" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useAdminUiStore } from '@stores/admin-ui';
import { storeToRefs } from 'pinia';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { TreeItem } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { ConceptTypeEnum } from '@models/util';
import type { Tree } from '@models/tree';
import type { Relation } from '@models/concept';

const props = defineProps<{
  scheme: string;
  schemeUri: string;
}>();

const emit = defineEmits<{
  add: [Relation];
}>();

const { t } = useI18n();

const apiService = new ApiService();

const adminUiStore = useAdminUiStore();
const { isFullscreenLoading, relationModalIsOpen } = storeToRefs(adminUiStore);

const RELATION_MODAL_LOADING_KEY = 'relation-modal-fetch-tree';
const treeItems = ref<TreeItem[]>([]);
const selectedItem = ref<TreeItem>();

const formatTreeItems = (items: Tree[]): TreeItem[] => {
  return items.map((item) => ({
    id: item.concept_id,
    label: item.label,
    type: item.type,
    icon: item.type === ConceptTypeEnum.COLLECTION ? 'i-lucide-folder' : 'i-lucide-file',
    children: item.children ? formatTreeItems(item.children) : undefined,
  }));
};

const onSelect = (e: Event, item: TreeItem) => {
  selectedItem.value = item;
};

onMounted(async () => {
  adminUiStore.startLoading(RELATION_MODAL_LOADING_KEY);
  const data = await apiService.getTreeByConceptscheme(props.scheme);
  treeItems.value = formatTreeItems(data);
  adminUiStore.stopLoading(RELATION_MODAL_LOADING_KEY);
});

const add = () => {
  if (!selectedItem.value) return;

  const relation: Relation = {
    id: selectedItem.value.id,
    label: selectedItem.value.label ?? '',
    type: selectedItem.value.type,
    uri: `${props.schemeUri}/${selectedItem.value.id}`,
  };
  emit('add', relation);
  adminUiStore.closeRelationModal();
};
</script>
