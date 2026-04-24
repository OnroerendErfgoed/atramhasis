import type { Provider } from '@models/provider';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useProviderStore = defineStore('provider', () => {
  const adminUiStore = useAdminUiStore();
  const { providerModalIsOpen } = storeToRefs(adminUiStore);

  const selectedProvider = ref<Provider>();

  const setSelectedProvider = (provider: Provider) => {
    selectedProvider.value = provider;
  };

  const resetSelectedProvider = () => {
    selectedProvider.value = undefined;
  };

  watch(providerModalIsOpen, (open) => {
    if (!open && selectedProvider.value) {
      resetSelectedProvider();
    }
  });

  return { selectedProvider, setSelectedProvider, resetSelectedProvider };
});
