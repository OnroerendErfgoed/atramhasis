import type { Language } from '@models/language';
import { ConceptTypeEnum, LabelTypeEnum, MatchTypeEnum, NoteTypeEnum, type ListType } from '@models/util';
import { ApiService } from '@services/api.service';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

export const useListStore = defineStore('list', () => {
  const { t } = useI18n();
  const toast = useToast();
  const apiService = new ApiService();

  const labelTypes = computed(() => [
    { label: t('lists.labelTypes.prefLabel'), value: LabelTypeEnum.PREF },
    { label: t('lists.labelTypes.altLabel'), value: LabelTypeEnum.ALT },
    { label: t('lists.labelTypes.hiddenLabel'), value: LabelTypeEnum.HIDDEN },
    { label: t('lists.labelTypes.sortLabel'), value: LabelTypeEnum.SORT },
  ]);
  const noteTypes = computed(() => [
    { label: t('lists.noteTypes.changeNote'), value: NoteTypeEnum.CHANGE },
    { label: t('lists.noteTypes.definition'), value: NoteTypeEnum.DEFINITION },
    { label: t('lists.noteTypes.editorialNote'), value: NoteTypeEnum.EDITORIAL },
    { label: t('lists.noteTypes.example'), value: NoteTypeEnum.EXAMPLE },
    { label: t('lists.noteTypes.historyNote'), value: NoteTypeEnum.HISTORY },
    { label: t('lists.noteTypes.note'), value: NoteTypeEnum.NOTE },
    { label: t('lists.noteTypes.scopeNote'), value: NoteTypeEnum.SCOPE },
  ]);
  const matchTypes = computed(() => [
    { label: t('lists.matchTypes.broad'), value: MatchTypeEnum.BROAD },
    { label: t('lists.matchTypes.close'), value: MatchTypeEnum.CLOSE },
    { label: t('lists.matchTypes.exact'), value: MatchTypeEnum.EXACT },
    { label: t('lists.matchTypes.narrow'), value: MatchTypeEnum.NARROW },
    { label: t('lists.matchTypes.related'), value: MatchTypeEnum.RELATED },
  ]);
  const conceptTypes = computed(() => [
    { label: t('lists.conceptTypes.concept'), value: ConceptTypeEnum.CONCEPT },
    { label: t('lists.conceptTypes.collection'), value: ConceptTypeEnum.COLLECTION },
  ]);
  const languages = ref<Language[]>([]);
  const languageOptions = computed(() =>
    languages.value.map((lang) => ({
      label: lang.name,
      value: lang.id,
    }))
  );

  const conceptschemeOptions = ref<ListType[]>([]);

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

  const fetchConceptschemes = async () => {
    try {
      const data = await apiService.getConceptschemes();
      conceptschemeOptions.value = data.map((c) => ({ label: c.label, value: c.id }));
    } catch (error) {
      console.error(t('api.errors.fetch.title', { item: t('entities.conceptscheme', 1) }), error);
      toast.add({
        title: t('api.errors.fetch.title', { item: t('entities.conceptscheme', 1) }),
        description: t('api.errors.fetch.description', { item: t('entities.conceptscheme', 1) }),
        icon: 'i-lucide-alert-triangle',
        color: 'error',
      });
    }
  };

  const getAll = async () => {
    await Promise.all([fetchLanguages(), fetchConceptschemes()]);
  };

  return {
    labelTypes,
    noteTypes,
    matchTypes,
    conceptTypes,
    languages,
    languageOptions,
    conceptschemeOptions,
    fetchLanguages,
    getAll,
  };
});
