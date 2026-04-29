import type { Language } from '@models/language';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useLanguageStore = defineStore('language', () => {
  const adminUiStore = useAdminUiStore();
  const { languageModalIsOpen } = storeToRefs(adminUiStore);

  const languages = ref<Record<string, Language>>({});
  const selectedLanguage = ref<Language>();

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

  return { languages, selectedLanguage, setSelectedLanguage, resetSelectedLanguage, setLanguage };
});
