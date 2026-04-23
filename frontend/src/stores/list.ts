import type { Language } from '@models/language';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

export const useListStore = defineStore('list', () => {
  const { t } = useI18n();
  const toast = useToast();
  const apiService = new ApiService();

  const languages = ref<Language[]>([]);

  const fetchLanguages = async () => {
    try {
      const data = await apiService.getLanguages();
      languages.value = data.sort((a, b) => a.name.localeCompare(b.name));
    } catch (error) {
      console.error(t('api.errors.fetch.title', { item: 'languages' }), error);
      toast.add({
        title: t('api.errors.fetch.title', { item: 'languages' }),
        description: t('api.errors.fetch.description', { item: 'languages' }),
        icon: 'i-lucide-alert-triangle',
        color: 'error',
      });
    }
  };

  const getAll = async () => {
    await fetchLanguages();
  };

  return { languages, fetchLanguages, getAll };
});
