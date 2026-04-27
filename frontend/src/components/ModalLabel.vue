<template>
  <UModal
    v-model:open="labelModalIsOpen"
    :title="title"
    :description="capitalize(t('components.modalLabel.description', { mode: labelModalMode }))"
  >
    <template #body>
      <UForm class="space-y-4">
        <UFormField
          name="label-type"
          size="lg"
          :label="t('components.modalLabel.form.type.label')"
          :error="(v$.type.$errors[0]?.$message as string) || false"
        >
          <USelect
            v-model="form.type"
            :items="labelTypes"
            class="w-full"
            :placeholder="t('components.modalLabel.form.type.placeholder')"
          />
        </UFormField>

        <UFormField
          name="label-language"
          size="lg"
          :label="t('components.modalLabel.form.language.label')"
          :error="(v$.language.$errors[0]?.$message as string) || false"
        >
          <USelect
            v-model="form.language"
            :items="languageOptions"
            class="w-full"
            :placeholder="t('components.modalLabel.form.language.placeholder')"
          />
        </UFormField>

        <UFormField
          name="label-label"
          size="lg"
          :label="t('components.modalLabel.form.label.label')"
          :error="(v$.label.$errors[0]?.$message as string) || false"
        >
          <UInput
            v-model="form.label"
            class="w-full"
            :placeholder="t('components.modalLabel.form.label.placeholder')"
          />
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
import { LabelTypeEnum, ModalMode, type Label } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';
import { capitalize, computed, onBeforeMount, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import useVuelidate from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { useLabelStore } from '@stores/label';

defineProps<{
  title: string;
}>();

const emit = defineEmits<{
  add: [Label];
  edit: [Label];
}>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { labelModalIsOpen, labelModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => labelModalMode.value === ModalMode.EDIT);

const labelStore = useLabelStore();
const { selectedLabel } = storeToRefs(labelStore);

const listStore = useListStore();
const { languageOptions, labelTypes } = storeToRefs(listStore);

const save = async () => {
  const valid = await v$.value.$validate();
  if (!valid) return;

  if (labelModalMode.value === ModalMode.ADD) {
    emit('add', form.value);
  } else {
    emit('edit', form.value);
  }
  adminUiStore.closeLabelModal();
};

// Form state
const form = ref<Label>({
  label: '',
  type: LabelTypeEnum.PREF,
  language: '',
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedLabel.value) {
    form.value = { ...selectedLabel.value };
  }
});

// Validation
const rules = computed(() => ({
  label: {
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
