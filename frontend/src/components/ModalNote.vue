<template>
  <UModal
    v-model:open="noteModalIsOpen"
    :dismissible="false"
    :title="title"
    :description="capitalize(t('components.modalNote.description', { mode: noteModalMode }))"
  >
    <template #body>
      <UForm class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <UFormField
            name="note-type"
            size="lg"
            :label="t('components.modalNote.form.type.label')"
            :hint="t('components.modalNote.form.type.hint')"
            :error="(v$.type.$errors[0]?.$message as string) || false"
          >
            <USelect
              v-model="form.type"
              :items="noteTypes"
              class="w-full"
              :placeholder="t('components.modalNote.form.type.placeholder')"
            />
          </UFormField>

          <UFormField
            name="note-language"
            size="lg"
            :label="t('components.modalNote.form.language.label')"
            :hint="t('components.modalNote.form.language.hint')"
            :error="(v$.language.$errors[0]?.$message as string) || false"
          >
            <USelect
              v-model="form.language"
              :items="languageOptions"
              class="w-full"
              :placeholder="t('components.modalNote.form.language.placeholder')"
            />
          </UFormField>
        </div>

        <UFormField
          name="note-note"
          size="lg"
          :label="t('components.modalNote.form.note.label')"
          :hint="t('components.modalNote.form.note.hint')"
          :error="(v$.note.$errors[0]?.$message as string) || false"
        >
          <div class="rounded-md border border-gray-300 dark:border-gray-700 min-h-32">
            <UEditor
              v-slot="{ editor }"
              v-model="form.note"
              :placeholder="t('components.modalNote.form.note.placeholder')"
            >
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
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.save')" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { ModalMode, NoteTypeEnum, type Note } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';
import { capitalize, computed, onBeforeMount, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import useVuelidate from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { useNoteStore } from '@stores/note';
import type { EditorToolbarItem } from '@nuxt/ui';

defineProps<{
  title: string;
}>();

const emit = defineEmits<{
  add: [Note];
  edit: [Note];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { noteModalIsOpen, noteModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => noteModalMode.value === ModalMode.EDIT);

const noteStore = useNoteStore();
const { selectedNote } = storeToRefs(noteStore);

const listStore = useListStore();
const { languageOptions, noteTypes } = storeToRefs(listStore);

const items: EditorToolbarItem[] = [
  { kind: 'mark', mark: 'bold', icon: 'i-lucide-bold' },
  { kind: 'mark', mark: 'italic', icon: 'i-lucide-italic' },
  { kind: 'link', icon: 'i-lucide-link' },
];

const save = async () => {
  const valid = await v$.value.$validate();
  if (!valid) return;

  if (noteModalMode.value === ModalMode.ADD) {
    emit('add', form.value);
  } else {
    emit('edit', form.value);
  }
  adminUiStore.closeNoteModal();
};

// Form state
const form = ref<Note>({
  note: '',
  type: NoteTypeEnum.CHANGE,
  language: '',
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedNote.value) {
    form.value = { ...selectedNote.value };
  }
});

// Validation
const rules = computed(() => ({
  note: {
    required: helpers.withMessage(t('validation.field.required'), required),
  },
  type: {
    required: helpers.withMessage(t('validation.field.required'), required),
  },
  language: {
    required: helpers.withMessage(t('validation.field.required'), required),
  },
}));
const v$ = useVuelidate(rules, form, { $lazy: true });
</script>
