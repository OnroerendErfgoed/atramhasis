import { useApiError } from '@composables/useApiError';
import type { Provider } from '@models/provider';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useProviderStore = defineStore('provider', () => {
  const apiService = new ApiService();
  const adminUiStore = useAdminUiStore();
  const { providerModalIsOpen } = storeToRefs(adminUiStore);

  const providers = ref<Record<string, Provider>>({});
  const selectedProvider = ref<Provider>();

  const { handleApiError } = useApiError();

  const getProvider = async (providerId: string, refresh = false): Promise<Provider> => {
    try {
      if (refresh || !providers.value[providerId]) {
        // Fetch provider from API if not already in store or if refresh is requested
        providers.value[providerId] = await apiService.getProvider(providerId);
      }
      return providers.value[providerId];
    } catch (error) {
      handleApiError(error);
      return Promise.reject(error);
    }
  };

  const setProvider = (providerId: string, provider: Provider) => {
    providers.value[providerId] = provider;
  };

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

  return { providers, selectedProvider, setSelectedProvider, resetSelectedProvider, getProvider, setProvider };
});
