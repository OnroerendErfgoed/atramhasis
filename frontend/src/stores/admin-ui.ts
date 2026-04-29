import { ModalMode } from '@models/util';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useAdminUiStore = defineStore('admin-ui', () => {
  /* Loading */
  const loadingByKey = ref<Record<string, number>>({});
  const activeLoadingCount = computed(() =>
    Object.values(loadingByKey.value).reduce((total, count) => total + count, 0)
  );
  const isFullscreenLoading = computed(() => activeLoadingCount.value > 0);

  const startLoading = (key: string) => {
    loadingByKey.value[key] = (loadingByKey.value[key] ?? 0) + 1;
  };
  const stopLoading = (key: string) => {
    const current = loadingByKey.value[key] ?? 0;
    if (current <= 1) {
      delete loadingByKey.value[key];
      return;
    }

    loadingByKey.value[key] = current - 1;
  };
  const isLoading = (key: string) => (loadingByKey.value[key] ?? 0) > 0;

  /* Modals */
  const conceptschemeModalKey = ref(0);
  const conceptschemeModalIsOpen = ref(false);
  const openConceptschemeModal = () => {
    conceptschemeModalKey.value++;
    conceptschemeModalIsOpen.value = true;
  };
  const closeConceptschemeModal = () => (conceptschemeModalIsOpen.value = false);

  const labelModalKey = ref(0);
  const labelModalIsOpen = ref(false);
  const labelModalMode = ref<ModalMode>(ModalMode.ADD);
  const openLabelModal = (modalMode: ModalMode) => {
    labelModalKey.value++;
    labelModalIsOpen.value = true;
    labelModalMode.value = modalMode;
  };
  const closeLabelModal = () => (labelModalIsOpen.value = false);

  const noteModalKey = ref(0);
  const noteModalIsOpen = ref(false);
  const noteModalMode = ref<ModalMode>(ModalMode.ADD);
  const openNoteModal = (modalMode: ModalMode) => {
    noteModalKey.value++;
    noteModalIsOpen.value = true;
    noteModalMode.value = modalMode;
  };
  const closeNoteModal = () => (noteModalIsOpen.value = false);

  const sourceModalKey = ref(0);
  const sourceModalIsOpen = ref(false);
  const sourceModalMode = ref<ModalMode>(ModalMode.ADD);
  const openSourceModal = (modalMode: ModalMode) => {
    sourceModalKey.value++;
    sourceModalIsOpen.value = true;
    sourceModalMode.value = modalMode;
  };
  const closeSourceModal = () => (sourceModalIsOpen.value = false);

  const conceptModalKey = ref(0);
  const conceptModalIsOpen = ref(false);
  const conceptModalMode = ref<ModalMode>(ModalMode.ADD);
  const openConceptModal = (modalMode: ModalMode) => {
    conceptModalKey.value++;
    conceptModalIsOpen.value = true;
    conceptModalMode.value = modalMode;
  };
  const closeConceptModal = () => (conceptModalIsOpen.value = false);

  const providerModalKey = ref(0);
  const providerModalIsOpen = ref(false);
  const providerModalMode = ref<ModalMode>(ModalMode.ADD);
  const openProviderModal = (modalMode: ModalMode) => {
    providerModalKey.value++;
    providerModalIsOpen.value = true;
    providerModalMode.value = modalMode;
  };
  const closeProviderModal = () => (providerModalIsOpen.value = false);

  const languageModalKey = ref(0);
  const languageModalIsOpen = ref(false);
  const languageModalMode = ref<ModalMode>(ModalMode.ADD);
  const openLanguageModal = (modalMode: ModalMode) => {
    languageModalKey.value++;
    languageModalIsOpen.value = true;
    languageModalMode.value = modalMode;
  };
  const closeLanguageModal = () => (languageModalIsOpen.value = false);

  /* Breadcrumbs */
  const breadcrumbLabels = ref<Record<string, string>>({});

  const setBreadcrumbLabel = (id: string, name: string) => {
    breadcrumbLabels.value[id] = name;
  };

  return {
    loadingByKey,
    startLoading,
    stopLoading,
    activeLoadingCount,
    isFullscreenLoading,
    isLoading,
    conceptschemeModalKey,
    conceptschemeModalIsOpen,
    openConceptschemeModal,
    closeConceptschemeModal,
    conceptModalKey,
    conceptModalIsOpen,
    conceptModalMode,
    openConceptModal,
    closeConceptModal,
    labelModalKey,
    labelModalIsOpen,
    labelModalMode,
    openLabelModal,
    closeLabelModal,
    noteModalKey,
    noteModalIsOpen,
    noteModalMode,
    openNoteModal,
    closeNoteModal,
    sourceModalKey,
    sourceModalIsOpen,
    sourceModalMode,
    openSourceModal,
    closeSourceModal,
    providerModalKey,
    providerModalIsOpen,
    providerModalMode,
    openProviderModal,
    closeProviderModal,
    languageModalKey,
    languageModalIsOpen,
    languageModalMode,
    openLanguageModal,
    closeLanguageModal,
    breadcrumbLabels,
    setBreadcrumbLabel,
  };
});
