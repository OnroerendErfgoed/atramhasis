import type { Language } from '@models/language';
import { ConceptTypeEnum, LabelTypeEnum, MatchTypeEnum, NoteTypeEnum } from '@models/util';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

export const useListStore = defineStore('list', () => {
  const { t } = useI18n();
  const toast = useToast();
  const apiService = new ApiService();

  const labelTypes = computed(() => [
    { label: t('labelTypes.prefLabel'), value: LabelTypeEnum.PREF },
    { label: t('labelTypes.altLabel'), value: LabelTypeEnum.ALT },
    { label: t('labelTypes.hiddenLabel'), value: LabelTypeEnum.HIDDEN },
    { label: t('labelTypes.sortLabel'), value: LabelTypeEnum.SORT },
  ]);
  const noteTypes = computed(() => [
    { label: t('noteTypes.changeNote'), value: NoteTypeEnum.CHANGE },
    { label: t('noteTypes.definition'), value: NoteTypeEnum.DEFINITION },
    { label: t('noteTypes.editorialNote'), value: NoteTypeEnum.EDITORIAL },
    { label: t('noteTypes.example'), value: NoteTypeEnum.EXAMPLE },
    { label: t('noteTypes.historyNote'), value: NoteTypeEnum.HISTORY },
    { label: t('noteTypes.note'), value: NoteTypeEnum.NOTE },
    { label: t('noteTypes.scopeNote'), value: NoteTypeEnum.SCOPE },
  ]);
  const matchTypes = computed(() => [
    { label: t('matchTypes.broad'), value: MatchTypeEnum.BROAD },
    { label: t('matchTypes.close'), value: MatchTypeEnum.CLOSE },
    { label: t('matchTypes.exact'), value: MatchTypeEnum.EXACT },
    { label: t('matchTypes.narrow'), value: MatchTypeEnum.NARROW },
    { label: t('matchTypes.related'), value: MatchTypeEnum.RELATED },
  ]);
  const conceptTypes = computed(() => [
    { label: t('conceptTypes.concept'), value: ConceptTypeEnum.CONCEPT },
    { label: t('conceptTypes.collection'), value: ConceptTypeEnum.COLLECTION },
  ]);
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

  return { labelTypes, noteTypes, matchTypes, conceptTypes, languages, fetchLanguages, getAll };
});
