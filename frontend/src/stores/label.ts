import type { Label } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useLabelStore = defineStore('label', () => {
  const adminUiStore = useAdminUiStore();
  const { labelModalIsOpen } = storeToRefs(adminUiStore);

  const selectedLabel = ref<Label>();

  const setSelectedLabel = (label: Label) => {
    selectedLabel.value = label;
  };

  const resetSelectedLabel = () => {
    selectedLabel.value = undefined;
  };

  watch(labelModalIsOpen, (open) => {
    if (!open && selectedLabel.value) {
      resetSelectedLabel();
    }
  });

  return { selectedLabel, setSelectedLabel, resetSelectedLabel };
});
