import type { Provider } from '@models/provider';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useProviderStore = defineStore('provider', () => {
  const selectedProvider = ref<Provider>();

  const setSelectedProvider = (provider: Provider) => {
    selectedProvider.value = provider;
  };

  const resetSelectedProvider = () => {
    selectedProvider.value = undefined;
  };

  return { selectedProvider, setSelectedProvider, resetSelectedProvider };
});
