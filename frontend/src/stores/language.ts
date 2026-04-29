import { useApiError } from '@composables/useApiError';
import type { Language } from '@models/language';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useLanguageStore = defineStore('language', () => {
  const apiService = new ApiService();
  const adminUiStore = useAdminUiStore();
  const { languageModalIsOpen } = storeToRefs(adminUiStore);

  const languages = ref<Record<string, Language>>({});
  const selectedLanguage = ref<Language>();

  const { handleApiError } = useApiError();

  const getLanguage = async (languageId: string, refresh = false): Promise<Language> => {
    try {
      if (refresh || !languages.value[languageId]) {
        // Fetch language from API if not already in store or if refresh is requested
        languages.value[languageId] = await apiService.getLanguage(languageId);
      }
      return languages.value[languageId];
    } catch (error) {
      handleApiError(error);
      return Promise.reject(error);
    }
  };

  const setLanguage = (languageId: string, language: Language) => {
    languages.value[languageId] = language;
  };

  const setSelectedLanguage = (language: Language) => {
    selectedLanguage.value = language;
  };

  const resetSelectedLanguage = () => {
    selectedLanguage.value = undefined;
  };

  watch(languageModalIsOpen, (open) => {
    if (!open && selectedLanguage.value) {
      resetSelectedLanguage();
    }
  });

  return { languages, selectedLanguage, setSelectedLanguage, resetSelectedLanguage, getLanguage, setLanguage };
});
