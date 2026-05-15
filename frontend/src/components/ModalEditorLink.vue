<template>
  <UModal v-model:open="open" :title="t('components.editorLinkModal.title')">
    <template #body>
      <UFormField :label="t('components.editorLinkModal.form.url.label')">
        <UInput v-model="url" placeholder="https://..." class="w-full" @keydown.enter="$emit('save')" />
      </UFormField>
    </template>
    <template #footer>
      <div class="flex w-full items-center">
        <UButton
          v-if="isLinkActive"
          :label="t('components.editorLinkModal.actions.remove')"
          color="error"
          variant="outline"
          @click="$emit('remove')"
        />
        <div class="flex gap-2 ml-auto">
          <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="open = false" />
          <UButton :label="isLinkActive ? t('actions.edit') : t('actions.add')" @click="$emit('save')" />
        </div>
      </div>
    </template>
  </UModal>

  <Teleport to="body">
    <div
      v-if="hoveredLink"
      class="fixed z-50 flex items-center gap-1.5 rounded bg-gray-800 px-2 py-1 text-xs text-white shadow-md pointer-events-none max-w-xs"
      :style="{ top: `${hoveredLink.top}px`, left: `${hoveredLink.left}px` }"
    >
      <UIcon name="i-lucide-link" class="size-3 shrink-0" />
      <span class="truncate">{{ hoveredLink.href }}</span>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { HoveredLink } from '@composables/useEditorLink';

const { t } = useI18n();

const open = defineModel<boolean>('open', { required: true });
const url = defineModel<string>('url', { required: true });

defineProps<{
  isLinkActive: boolean;
  hoveredLink: HoveredLink | null;
}>();

defineEmits<{
  save: [];
  remove: [];
}>();
</script>
