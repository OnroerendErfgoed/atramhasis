import type { Concept } from '@models/concept';
import type { Label, Note, Source } from '@models/util';
import { ApiService } from '@services/api.service';
import { useMatchStore } from '@stores/match';
import { isEmpty, isEqual, omitBy, uniqWith } from 'lodash-es';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';
import { useAdminUiStore } from './admin-ui';

export const useConceptStore = defineStore('concept', () => {
  const apiService = new ApiService();
  const adminUiStore = useAdminUiStore();
  const matchStore = useMatchStore();
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

  const setConcept = async (schemeId: string, concept: Concept) => {
    concepts.value[`${schemeId}-${concept.id}`] = concept;
  };

  const setSelectedConcept = (concept: Concept) => {
    selectedConcept.value = concept;
  };

  const resetSelectedConcept = () => (selectedConcept.value = undefined);

  const isEqualIgnoringEmptyFields = (left: Label | Note | Source, right: Label | Note | Source): boolean =>
    isEqual(omitBy(left, isEmpty), omitBy(right, isEmpty));

  const mergeWithSelectedConcept = (matchUris: string[]): Concept | undefined => {
    if (!selectedConcept.value) {
      return;
    }

    // Get linked concepts for the provided match URIs to have access to their labels, notes, and sources for merging
    const linkedConcepts = matchUris
      .map((uri) => matchStore.getLinkedConcept(uri))
      .filter((concept): concept is Concept => concept !== undefined);

    // Merge labels, notes and sources from linked concepts into selected concept, ensuring uniqueness
    selectedConcept.value.labels = uniqWith(
      [...selectedConcept.value.labels, ...linkedConcepts.flatMap((c) => c.labels)],
      isEqualIgnoringEmptyFields
    );

    selectedConcept.value.notes = uniqWith(
      [...selectedConcept.value.notes, ...linkedConcepts.flatMap((c) => c.notes)],
      isEqualIgnoringEmptyFields
    );
    selectedConcept.value.sources = uniqWith(
      [...selectedConcept.value.sources, ...linkedConcepts.flatMap((c) => c.sources)],
      isEqualIgnoringEmptyFields
    );

    return selectedConcept.value;
  };

  watch(conceptModalIsOpen, (open) => {
    if (!open && conceptModalIsOpen.value) {
      resetSelectedConcept();
    }
  });

  return {
    concepts,
    selectedConcept,
    getConcept,
    setConcept,
    setSelectedConcept,
    resetSelectedConcept,
    mergeWithSelectedConcept,
  };
});
