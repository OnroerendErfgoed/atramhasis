<template>
  <UModal :dismissible="false" :title="t('components.modalDelete.title', { entity: props.entity })">
    <template #body>
      <p>{{ t('components.modalDelete.message', { entity: props.entity, item: props.item }) }}</p>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.ok')" @click="emit('confirm')" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const emit = defineEmits(['confirm']);
const props = defineProps<{ entity: string; item: string }>();
const { t } = useI18n();
</script>
