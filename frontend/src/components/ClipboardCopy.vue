<template>
  <UButton
    icon="i-lucide-copy"
    color="neutral"
    variant="ghost"
    size="xs"
    class="p-0.5 cursor-pointer"
    :aria-label="ariaLabel ?? t('components.clipboardCopy.copy')"
    @click="handleCopy"
  />
</template>

<script setup lang="ts">
import { useClipboard } from '@vueuse/core';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps<{
  text: string;
  ariaLabel?: string;
}>();

const toast = useToast();
const { copy } = useClipboard({ legacy: true });

const handleCopy = () => {
  copy(props.text);
  toast.add({
    title: t('components.clipboardCopy.copied'),
    icon: 'i-lucide-check',
    color: 'success',
  });
};
</script>
