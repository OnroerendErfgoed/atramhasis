import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminUiStore = defineStore('admin-ui', () => {
  /* Modals */
  const conceptschemeModalIsOpen = ref(false);
  const openConceptschemeModal = () => (conceptschemeModalIsOpen.value = true);
  const closeConceptschemeModal = () => (conceptschemeModalIsOpen.value = false);

  const addConceptModalIsOpen = ref(false);
  const openAddConceptModal = () => (addConceptModalIsOpen.value = true);
  const closeAddConceptModal = () => (addConceptModalIsOpen.value = false);

  const addProviderModalIsOpen = ref(false);
  const openAddProviderModal = () => (addProviderModalIsOpen.value = true);
  const closeAddProviderModal = () => (addProviderModalIsOpen.value = false);

  /* Breadcrumbs */
  const breadcrumbLabels = ref<Record<string, string>>({});

  const setBreadcrumbLabel = (id: string, name: string) => {
    breadcrumbLabels.value[id] = name;
  };

  return {
    conceptschemeModalIsOpen,
    openConceptschemeModal,
    closeConceptschemeModal,
    addConceptModalIsOpen,
    openAddConceptModal,
    closeAddConceptModal,
    addProviderModalIsOpen,
    openAddProviderModal,
    closeAddProviderModal,
    breadcrumbLabels,
    setBreadcrumbLabel,
  };
});
