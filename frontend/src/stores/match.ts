import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useMatchStore = defineStore('match', () => {
  const adminUiStore = useAdminUiStore();
  const { matchModalIsOpen } = storeToRefs(adminUiStore);

  const selectedMatch = ref<string>();

  const setSelectedMatch = (match: string) => {
    selectedMatch.value = match;
  };

  const resetSelectedMatch = () => {
    selectedMatch.value = undefined;
  };

  watch(matchModalIsOpen, (open) => {
    if (!open && selectedMatch.value) {
      resetSelectedMatch();
    }
  });

  return { selectedMatch, setSelectedMatch, resetSelectedMatch };
});
