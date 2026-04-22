import type { Language } from '@models/language';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

export const useLanguageStore = defineStore('language', () => {
  const { t } = useI18n();
  const toast = useToast();
  const apiService = new ApiService();

  const languages = ref<Language[]>([]);

  const fetchLanguages = async () => {
    try {
      const data = await apiService.getLanguages();
      languages.value = data.sort((a, b) => a.name.localeCompare(b.name));
    } catch (error) {
      console.error(t('errors.fetch.title', { item: 'languages' }), error);
      toast.add({
        title: t('errors.fetch.title', { item: 'languages' }),
        description: t('errors.fetch.description', { item: 'languages' }),
        icon: 'i-lucide-alert-triangle',
        color: 'error',
      });
    }
  };

  return { languages, fetchLanguages };
});
