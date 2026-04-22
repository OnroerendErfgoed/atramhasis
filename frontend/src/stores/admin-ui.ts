import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminUiStore = defineStore('admin-ui', () => {
  const addProviderModalIsOpen = ref(false);

  const openAddProviderModal = () => {
    addProviderModalIsOpen.value = true;
  };

  const closeAddProviderModal = () => {
    addProviderModalIsOpen.value = false;
  };

  return {
    addProviderModalIsOpen,
    openAddProviderModal,
    closeAddProviderModal,
  };
});
