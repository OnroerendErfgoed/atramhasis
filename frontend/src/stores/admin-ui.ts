import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminUiStore = defineStore('admin-ui', () => {
  /* Modals */
  const addProviderModalIsOpen = ref(false);

  const openAddProviderModal = () => {
    addProviderModalIsOpen.value = true;
  };

  const closeAddProviderModal = () => {
    addProviderModalIsOpen.value = false;
  };

  /* Breadcrumbs */
  const breadcrumbLabels = ref<Record<string, string>>({});

  const setBreadcrumbLabel = (id: string, name: string) => {
    breadcrumbLabels.value[id] = name;
  };

  return {
    addProviderModalIsOpen,
    openAddProviderModal,
    closeAddProviderModal,
    breadcrumbLabels,
    setBreadcrumbLabel,
  };
});
