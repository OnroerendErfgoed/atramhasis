import type { Concept } from '@models/concept';
import { ApiService } from '@services/api.service';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';
import { useAdminUiStore } from './admin-ui';

export const useConceptStore = defineStore('concept', () => {
  const apiService = new ApiService();
  const adminUiStore = useAdminUiStore();
  const { conceptModalIsOpen } = storeToRefs(adminUiStore);

  const concepts = ref<Record<string, Concept>>({});
  const selectedConcept = ref<Concept>();

  const getConcept = async (schemeId: string, id: number, refresh = false): Promise<Concept | undefined> => {
    if (refresh || !concepts.value[`${schemeId}-${id}`]) {
      // Fetch concept from API if not already in store or if refresh is requested
      concepts.value[`${schemeId}-${id}`] = await apiService.getConceptByConceptschemeAndId(schemeId, id);
    }
    return concepts.value[`${schemeId}-${id}`];
  };

  const setConcept = async (schemeId: string, id: number, concept: Concept) => {
    concepts.value[`${schemeId}-${id}`] = concept;
  };

  const resetSelectedConcept = () => (selectedConcept.value = undefined);

  watch(conceptModalIsOpen, (open) => {
    if (!open && conceptModalIsOpen.value) {
      resetSelectedConcept();
    }
  });

  return { concepts, selectedConcept, getConcept, setConcept, resetSelectedConcept };
});
