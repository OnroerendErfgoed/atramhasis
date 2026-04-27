import { useApiError } from '@composables/useApiError';
import type { Conceptscheme } from '@models/conceptscheme';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useConceptschemeStore = defineStore('conceptscheme', () => {
  const apiService = new ApiService();
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

  return { conceptschemes, selectedConceptscheme, getConceptscheme, setConceptscheme, resetSelectedConceptscheme };
});
