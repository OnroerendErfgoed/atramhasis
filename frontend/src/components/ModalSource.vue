<template>
  <UModal
    v-model:open="sourceModalIsOpen"
    :title="title"
    :description="capitalize(t('components.modalSource.description', { mode: sourceModalMode }))"
  >
    <template #body>
      <UForm class="space-y-4">
        <UFormField name="source-citation" size="lg" :error="(v$.citation.$errors[0]?.$message as string) || false">
          <div class="rounded-md border border-gray-300 dark:border-gray-700 min-h-32">
            <UEditor v-slot="{ editor }" v-model="form.citation">
              <div class="border-b border-gray-300 px-2 py-1 dark:border-gray-700">
                <UEditorToolbar :editor="editor" :items="items" />
              </div>
            </UEditor>
          </div>
        </UFormField>
      </UForm>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" class="cursor-pointer" @click="close" />
        <UButton :label="t('actions.save')" class="cursor-pointer" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { ModalMode, type Source } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { storeToRefs } from 'pinia';
import { capitalize, computed, onBeforeMount, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import useVuelidate from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { useSourceStore } from '@stores/source';
import type { EditorToolbarItem } from '@nuxt/ui';

defineProps<{
  title: string;
}>();

const emit = defineEmits<{
  add: [Source];
  edit: [Source];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { sourceModalIsOpen, sourceModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => sourceModalMode.value === ModalMode.EDIT);

const sourceStore = useSourceStore();
const { selectedSource } = storeToRefs(sourceStore);

const items: EditorToolbarItem[] = [
  { kind: 'mark', mark: 'bold', icon: 'i-lucide-bold' },
  { kind: 'mark', mark: 'italic', icon: 'i-lucide-italic' },
  { kind: 'link', icon: 'i-lucide-link' },
];

const save = async () => {
  const valid = await v$.value.$validate();
  if (!valid) return;

  if (sourceModalMode.value === ModalMode.ADD) {
    emit('add', form.value);
  } else {
    emit('edit', form.value);
  }
  adminUiStore.closeSourceModal();
};

// Form state
const form = ref<Source>({
  citation: '',
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedSource.value) {
    form.value = { ...selectedSource.value };
  }
});

// Validation
const rules = computed(() => ({
  citation: {
    required: helpers.withMessage(t('validation.field.required'), required),
  },
}));
const v$ = useVuelidate(rules, form, { $lazy: true });
</script>
