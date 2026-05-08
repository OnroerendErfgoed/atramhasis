<template>
  <UButton
    color="neutral"
    variant="ghost"
    :label="props.label"
    :icon="sortIcon"
    class="-mx-2.5"
    @click="column.toggleSorting(sortState === 'asc')"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';

type SortState = false | 'asc' | 'desc';
type SortableColumnLike = {
  getIsSorted: () => SortState;
  toggleSorting: (desc?: boolean) => void;
};

const props = defineProps<{
  label: string;
  column: SortableColumnLike;
}>();

const sortState = computed(() => props.column.getIsSorted());

const sortIcon = computed(() => {
  if (sortState.value === 'asc') {
    return 'i-lucide-arrow-up-narrow-wide';
  }

  if (sortState.value === 'desc') {
    return 'i-lucide-arrow-down-wide-narrow';
  }

  return 'i-lucide-arrow-up-down';
});
</script>
