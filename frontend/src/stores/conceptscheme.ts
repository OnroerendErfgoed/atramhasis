import type { Conceptscheme } from '@models/conceptscheme';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useConceptschemeStore = defineStore('conceptscheme', () => {
  const apiService = new ApiService();
  const conceptschemes = ref<Record<string, Conceptscheme>>({});

  const getConceptscheme = async (schemeId: string, refresh = false): Promise<Conceptscheme | undefined> => {
    if (refresh || !conceptschemes.value[schemeId]) {
      // Fetch concept from API if not already in store or if refresh is requested
      conceptschemes.value[schemeId] = await apiService.getConceptscheme(schemeId);
    }
    return conceptschemes.value[schemeId];
  };

  const setConceptscheme = async (schemeId: string, conceptscheme: Conceptscheme) => {
    conceptschemes.value[schemeId] = conceptscheme;
  };

  return { conceptschemes, getConceptscheme, setConceptscheme };
});
