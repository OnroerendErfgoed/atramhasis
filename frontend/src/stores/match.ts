import type { Match } from '@models/concept';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useMatchStore = defineStore('match', () => {
  const adminUiStore = useAdminUiStore();
  const { matchModalIsOpen } = storeToRefs(adminUiStore);

  const matches = ref<Record<string, Match>>({});
  const selectedMatch = ref<string>();

  const getMatch = (uri: string): Match | undefined => matches.value[uri];

  const setMatch = (match: Match) => {
    matches.value[match.uri] = match;
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

  return { selectedMatch, setSelectedMatch, resetSelectedMatch, getMatch, setMatch, matches };
});
