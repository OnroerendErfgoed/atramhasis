import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useBreadcrumbStore = defineStore('breadcrumb', () => {
  const labels = ref<Record<string, string>>({});

  const setLabel = (id: string, name: string) => {
    labels.value[id] = name;
  };

  return { labels, setLabel };
});
