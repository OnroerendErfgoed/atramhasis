<template>
  <div
    v-if="mode === 'fullscreen'"
    class="fixed inset-0 z-50 flex flex-col items-center justify-center gap-3"
    :class="showBackdrop ? 'bg-default/65 backdrop-blur-[1px]' : ''"
  >
    <UIcon name="i-lucide-loader-circle" class="animate-spin text-primary" :class="sizeClass" />
    <span v-if="message" class="text-sm text-muted">{{ message }}</span>
  </div>

  <span v-else class="inline-flex items-center gap-2">
    <UIcon
      name="i-lucide-loader-circle"
      class="inline-block animate-spin align-middle text-primary"
      :class="sizeClass"
    />
    <span v-if="message" class="text-sm text-muted">{{ message }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    mode?: 'inline' | 'fullscreen';
    size?: 'sm' | 'md' | 'lg';
    showBackdrop?: boolean;
    message?: string;
  }>(),
  {
    mode: 'fullscreen',
    size: 'md',
    showBackdrop: true,
    message: '',
  }
);

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'size-4';
  if (props.size === 'lg') return 'size-10';
  return 'size-8';
});
</script>
