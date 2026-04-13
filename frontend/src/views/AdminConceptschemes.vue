<template>
  <pre>{{ conceptschemes }}</pre>
</template>

<script setup lang="ts">
import type { ConceptScheme } from '@/models/conceptscheme';
import { ApiService } from '@/services/api.service';
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
