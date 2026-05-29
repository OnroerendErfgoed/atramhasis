import type { Concept, Match } from '@models/concept';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useMatchStore = defineStore('match', () => {
  const adminUiStore = useAdminUiStore();
  const { matchModalIsOpen } = storeToRefs(adminUiStore);

  const matches = ref<Record<string, Match>>({});
  const linkedConcepts = ref<Record<string, Concept>>({});
  const selectedMatch = ref<string>();

  const getMatch = (uri: string): Match | undefined => matches.value[uri];
  const getLinkedConcept = (matchUri: string): Concept | undefined => linkedConcepts.value[matchUri];

  const setMatch = (match: Match, linkedConcept?: Concept) => {
    matches.value[match.uri] = match;
    if (linkedConcept) {
      linkedConcepts.value[match.uri] = linkedConcept;
    }
  };

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

  return {
    selectedMatch,
    setSelectedMatch,
    resetSelectedMatch,
    getMatch,
    setMatch,
    getLinkedConcept,
    matches,
    linkedConcepts,
  };
});
