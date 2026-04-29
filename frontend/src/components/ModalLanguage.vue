<template>
  <UModal
    v-model:open="languageModalIsOpen"
    :dismissible="false"
    :title="t('components.modalLanguage.title')"
    :description="
      t('components.modalLanguage.description', { mode: isEditMode ? t('actions.edit') : t('actions.add') })
    "
  >
    <template #body>
      <UForm class="space-y-4">
        <UFormField
          name="id"
          size="lg"
          :label="t('components.modalLanguage.form.id.label')"
          :hint="t('components.modalLanguage.form.id.hint')"
          :error="(v$.id.$errors[0]?.$message as string) || false"
        >
          <UInput v-model="form.id" class="w-full" :placeholder="t('components.modalLanguage.form.id.placeholder')" />
        </UFormField>

        <UFormField
          name="name"
          size="lg"
          :label="t('components.modalLanguage.form.name.label')"
          :hint="t('components.modalLanguage.form.name.hint')"
          :error="(v$.name.$errors[0]?.$message as string) || false"
        >
          <UInput
            v-model="form.name"
            class="w-full"
            :placeholder="t('components.modalLanguage.form.name.placeholder')"
          />
        </UFormField>
      </UForm>

      <hr class="my-7 border-accented" />

      <p>
        {{ t('components.modalLanguage.reference.beforeLink') }}
        <ULink
          target="_blank"
          external
          href="https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
        >
          {{ t('components.modalLanguage.reference.linkText') }}
          <UIcon name="i-lucide-external-link" class="inline-block" />
        </ULink>
        {{ t('components.modalLanguage.reference.afterLink') }}
      </p>
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
import { useApiError } from '@composables/useApiError';
import type { Language } from '@models/language';
import { ModalMode } from '@models/util';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useLanguageStore } from '@stores/language';
import useVuelidate from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { storeToRefs } from 'pinia';
import { computed, onBeforeMount, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();

const languageStore = useLanguageStore();
const { selectedLanguage } = storeToRefs(languageStore);

const adminUiStore = useAdminUiStore();
const { languageModalIsOpen, languageModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => languageModalMode.value === ModalMode.EDIT);

const apiService = new ApiService();
const { handleApiError } = useApiError();
const LANGUAGE_MODAL_LOADING_KEY = 'language-modal-submit';

// Form state
const form = ref<Language>({
  id: '',
  name: '',
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedLanguage.value) {
    form.value = {
      id: selectedLanguage.value.id,
      name: selectedLanguage.value.name,
    };
  }
});

// Save handler
const save = async () => {
  const valid = await v$.value.$validate();
  if (!valid) {
    toast.add({
      title: t('validation.form.invalid'),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
    return;
  }

  try {
    adminUiStore.startLoading(LANGUAGE_MODAL_LOADING_KEY);

    if (!isEditMode.value) {
      // Create new language
      await apiService.createLanguage(form.value);
      toast.add({
        title: t('api.success.save.title', { item: 'Language' }),
        description: t('api.success.save.description', { item: 'language' }),
        icon: 'i-lucide-check-circle',
        color: 'success',
      });
    } else {
      // Update existing language
      await apiService.updateLanguage(form.value);
      toast.add({
        title: t('api.success.update.title', { item: 'Language' }),
        description: t('api.success.update.description', { item: 'language' }),
        icon: 'i-lucide-check-circle',
        color: 'success',
      });
    }
    adminUiStore.closeLanguageModal();
  } catch (error) {
    handleApiError(error);
  } finally {
    adminUiStore.stopLoading(LANGUAGE_MODAL_LOADING_KEY);
  }
};

// Validation
const rules = computed(() => ({
  id: { required: helpers.withMessage(t('validation.field.required'), required) },
  name: { required: helpers.withMessage(t('validation.field.required'), required) },
}));
const v$ = useVuelidate(rules, form, { $lazy: true });
</script>
