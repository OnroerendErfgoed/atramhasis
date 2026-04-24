import { ModalMode } from '@models/util';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminUiStore = defineStore('admin-ui', () => {
  /* Modals */
  const addConceptModalIsOpen = ref(false);
  const openAddConceptModal = () => {
    addConceptModalIsOpen.value = true;
  };
  const closeAddConceptModal = () => {
    addConceptModalIsOpen.value = false;
  };

  const providerModalIsOpen = ref(false);
  const providerModalMode = ref<ModalMode>(ModalMode.ADD);
  const openProviderModal = (modalMode: ModalMode) => {
    providerModalIsOpen.value = true;
    providerModalMode.value = modalMode;
  };
  const closeProviderModal = () => {
    providerModalIsOpen.value = false;
  };

  /* Breadcrumbs */
  const breadcrumbLabels = ref<Record<string, string>>({});

  const setBreadcrumbLabel = (id: string, name: string) => {
    breadcrumbLabels.value[id] = name;
  };

  return {
    addConceptModalIsOpen,
    openAddConceptModal,
    closeAddConceptModal,
    providerModalIsOpen,
    providerModalMode,
    openProviderModal,
    closeProviderModal,
    breadcrumbLabels,
    setBreadcrumbLabel,
  };
});
