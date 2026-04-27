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
  const conceptschemeModalIsOpen = ref(false);
  const openConceptschemeModal = () => (conceptschemeModalIsOpen.value = true);
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

  const conceptModalIsOpen = ref(false);
  const openConceptModal = () => (conceptModalIsOpen.value = true);
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
    conceptschemeModalIsOpen,
    openConceptschemeModal,
    closeConceptschemeModal,
    conceptModalIsOpen,
    openConceptModal,
    closeConceptModal,
    labelModalKey,
    labelModalIsOpen,
    labelModalMode,
    openLabelModal,
    closeLabelModal,
    providerModalKey,
    providerModalIsOpen,
    providerModalMode,
    openProviderModal,
    closeProviderModal,
    breadcrumbLabels,
    setBreadcrumbLabel,
  };
});
