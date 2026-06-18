<template>
  <UTooltip
    v-model:open="open"
    :disabled="!isOverflowing"
    :text="normalizedText"
    :content="{
      side: 'top',
      sideOffset: 8,
    }"
  >
    <span
      ref="trigger"
      class="block w-full truncate"
      @mouseenter="showTooltip"
      @focus="showTooltip"
      @mouseleave="hideTooltip"
      @blur="hideTooltip"
    >
      <slot />
    </span>
  </UTooltip>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    text?: string;
  }>(),
  {
    text: '',
  }
);

const trigger = ref<HTMLElement | null>(null);
const isOverflowing = ref(false);
const normalizedText = computed(() => props.text ?? '');
const open = ref(false);
let resizeObserver: ResizeObserver | null = null;

const detectOverflow = (el: HTMLElement): boolean => {
  // Ignore transient states where layout is not ready yet.
  if (el.clientWidth <= 0 || el.clientHeight <= 0) return false;

  const horizontalOverflow = el.scrollWidth - el.clientWidth > 1;
  const verticalOverflow = el.scrollHeight - el.clientHeight > 1;
  return horizontalOverflow || verticalOverflow;
};

const updateOverflow = async () => {
  await nextTick();

  const el = trigger.value;
  isOverflowing.value = !!normalizedText.value && !!el && detectOverflow(el);

  if (!isOverflowing.value) {
    open.value = false;
  }
};

const showTooltip = async () => {
  await updateOverflow();
  open.value = isOverflowing.value;
};

const hideTooltip = () => {
  open.value = false;
};

onMounted(async () => {
  await updateOverflow();

  if (trigger.value) {
    resizeObserver = new ResizeObserver(() => {
      void updateOverflow();
    });
    resizeObserver.observe(trigger.value);
  }
});

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  resizeObserver = null;
});

watch(normalizedText, updateOverflow);
</script>
