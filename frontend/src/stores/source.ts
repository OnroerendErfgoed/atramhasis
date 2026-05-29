import type { Source } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useSourceStore = defineStore('source', () => {
  const adminUiStore = useAdminUiStore();
  const { sourceModalIsOpen } = storeToRefs(adminUiStore);

  const selectedSource = ref<Source>();

  const setSelectedSource = (source: Source) => {
    selectedSource.value = source;
  };

  const resetSelectedSource = () => {
    selectedSource.value = undefined;
  };

  watch(sourceModalIsOpen, (open) => {
    if (!open && selectedSource.value) {
      resetSelectedSource();
    }
  });

  return { selectedSource, setSelectedSource, resetSelectedSource };
});
