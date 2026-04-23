import type { Concept } from '@models/concept';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useConceptStore = defineStore('concept', () => {
  const apiService = new ApiService();
  const concepts = ref<Record<string, Concept>>({});

  const getConcept = async (schemeId: string, id: number): Promise<Concept | undefined> => {
    if (!concepts.value[`${schemeId}-${id}`]) {
      // Fetch concept from API if not already in store
      concepts.value[`${schemeId}-${id}`] = await apiService.getConceptByConceptschemeAndId(schemeId, id);
    }
    return concepts.value[`${schemeId}-${id}`];
  };

  const setConcept = async (schemeId: string, id: number, concept: Concept) => {
    concepts.value[`${schemeId}-${id}`] = concept;
  };

  return { concepts, getConcept, setConcept };
});
