<template>
  <pre class="conceptschemes-dump">{{ conceptschemes }}</pre>
</template>

<script setup lang="ts">
import type { ConceptScheme } from '@models/conceptscheme';
import { ApiService } from '@services/api.service';
import { ref } from 'vue';

const toast = useToast();
const apiService = new ApiService();
const conceptschemes = ref<ConceptScheme[]>();

try {
  conceptschemes.value = await apiService.getConceptschemes();
} catch (error) {
  console.error('Error fetching conceptschemes:', error);
  toast.add({
    title: 'Failed to fetch conceptschemes.',
    description: 'Please try again later.',
    icon: 'i-lucide-alert-triangle',
    color: 'error',
  });
}
</script>

<style scoped>
.conceptschemes-dump {
  min-height: 24rem;
  margin: 0;
  overflow: auto;
  border: 1px solid var(--ui-border);
  border-radius: 0.875rem;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  padding: 1.5rem;
  color: var(--ui-text);
  font-size: 0.95rem;
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.conceptschemes-dump::selection {
  background: color-mix(in srgb, var(--ui-primary) 18%, white);
}
</style>
