import { useApiError } from '@composables/useApiError';
import type { Conceptscheme } from '@models/conceptscheme';
import { ApiService } from '@services/api.service';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';
import { useAdminUiStore } from '@stores/admin-ui';

export const useConceptschemeStore = defineStore('conceptscheme', () => {
  const apiService = new ApiService();
  const adminUiStore = useAdminUiStore();
  const { conceptschemeModalIsOpen } = storeToRefs(adminUiStore);

  const conceptschemes = ref<Record<string, Conceptscheme>>({});
  const selectedConceptscheme = ref<Conceptscheme>();
  const { handleApiError } = useApiError();

  const getConceptscheme = async (schemeId: string, refresh = false): Promise<Conceptscheme | undefined> => {
    try {
      if (refresh || !conceptschemes.value[schemeId]) {
        // Fetch concept from API if not already in store or if refresh is requested
        conceptschemes.value[schemeId] = await apiService.getConceptscheme(schemeId);
      }
      return conceptschemes.value[schemeId];
    } catch (error) {
      handleApiError(error);
      return Promise.reject(error);
    }
  };

  const setConceptscheme = (schemeId: string, conceptscheme: Conceptscheme) => {
    conceptschemes.value[schemeId] = conceptscheme;
  };

  const resetSelectedConceptscheme = () => (selectedConceptscheme.value = undefined);

  watch(conceptschemeModalIsOpen, (open) => {
    if (!open && conceptschemeModalIsOpen.value) {
      resetSelectedConceptscheme();
    }
  });

  return { conceptschemes, selectedConceptscheme, getConceptscheme, setConceptscheme, resetSelectedConceptscheme };
});
