<template>
  <UModal
    v-model:open="providerModalIsOpen"
    :title="t('components.modalProvider.title')"
    :description="
      t('components.modalProvider.description', { mode: isEditMode ? t('actions.edit') : t('actions.add') })
    "
  >
    <template #body>
      <UForm class="space-y-4">
        <UFormField
          name="id"
          size="lg"
          :label="t('components.modalProvider.form.id.label')"
          :description="t('components.modalProvider.form.id.description')"
        >
          <UInput v-model="form.id" class="w-full" :placeholder="t('components.modalProvider.form.id.placeholder')" />
        </UFormField>

        <UFormField
          name="conceptschemeUri"
          size="lg"
          :label="t('components.modalProvider.form.conceptschemeUri.label')"
          :hint="t('components.modalProvider.form.conceptschemeUri.hint')"
          :error="(v$.conceptscheme_uri.$errors[0]?.$message as string) || false"
        >
          <UInput
            v-model="form.conceptscheme_uri"
            class="w-full"
            :placeholder="t('components.modalProvider.form.conceptschemeUri.placeholder')"
          />
        </UFormField>

        <UFormField
          name="uriPattern"
          size="lg"
          :label="t('components.modalProvider.form.uriPattern.label')"
          :hint="t('components.modalProvider.form.uriPattern.hint')"
          :error="(v$.uri_pattern.$errors[0]?.$message as string) || false"
        >
          <UInput
            v-model="form.uri_pattern"
            class="w-full"
            :placeholder="t('components.modalProvider.form.uriPattern.placeholder')"
          />
        </UFormField>

        <UFormField name="subject" size="lg" :label="t('components.modalProvider.form.subject.label')">
          <UInput
            :model-value="form.subject?.[0]"
            class="w-full"
            :placeholder="t('components.modalProvider.form.subject.placeholder')"
            @update:model-value="form.subject = !!$event ? [$event] : null"
          />
        </UFormField>

        <UFormField name="defaultLanguage" size="lg" :label="t('components.modalProvider.form.defaultLanguage.label')">
          <USelect
            v-model="form.default_language"
            :items="languageOptions"
            class="w-full"
            :placeholder="t('components.modalProvider.form.defaultLanguage.placeholder')"
          />
        </UFormField>

        <UFormField name="displayLanguage" size="lg" :label="t('components.modalProvider.form.displayLanguage.label')">
          <USelect
            v-model="form.force_display_language"
            :items="languageOptions"
            class="w-full"
            :placeholder="t('components.modalProvider.form.displayLanguage.placeholder')"
          />
        </UFormField>

        <UFormField
          name="idGenerationStrategy"
          size="lg"
          :label="t('components.modalProvider.form.idGenerationStrategy.label')"
        >
          <USelect
            v-model="form.id_generation_strategy"
            :items="generationStrategyOptions"
            class="w-full"
            :placeholder="t('components.modalProvider.form.idGenerationStrategy.placeholder')"
          />
        </UFormField>

        <UFormField name="expandStrategy" size="lg" :label="t('components.modalProvider.form.expandStrategy.label')">
          <USelect
            v-model="form.expand_strategy"
            :items="expandStrategyOptions"
            class="w-full"
            :placeholder="t('components.modalProvider.form.expandStrategy.placeholder')"
          />
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
import { useApiError } from '@composables/useApiError';
import { ExpandStrategy, GenerationStarategyId, type ProviderForm } from '@models/provider';
import { ModalMode } from '@models/util';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useListStore } from '@stores/list';
import { useProviderStore } from '@stores/provider';
import useVuelidate from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { storeToRefs } from 'pinia';
import { computed, onBeforeMount, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();

const providerStore = useProviderStore();
const { selectedProvider } = storeToRefs(providerStore);

const adminUiStore = useAdminUiStore();
const { providerModalIsOpen, providerModalMode } = storeToRefs(adminUiStore);
const isEditMode = computed(() => providerModalMode.value === ModalMode.EDIT);

const listStore = useListStore();
const { languageOptions } = storeToRefs(listStore);

const apiService = new ApiService();
const { handleApiError } = useApiError();
const PROVIDER_MODAL_LOADING_KEY = 'provider-modal-submit';

const generationStrategyOptions = computed(() => [
  {
    label: t('components.modalProvider.form.idGenerationStrategy.options.GUID'),
    value: GenerationStarategyId.GUID as string,
  },
  {
    label: t('components.modalProvider.form.idGenerationStrategy.options.NUMERIC'),
    value: GenerationStarategyId.NUMERIC as string,
  },
  {
    label: t('components.modalProvider.form.idGenerationStrategy.options.MANUAL'),
    value: GenerationStarategyId.MANUAL as string,
  },
]);

const expandStrategyOptions = computed(() => [
  { label: t('components.modalProvider.form.expandStrategy.options.RECURSE'), value: ExpandStrategy.RECURSE as string },
  { label: t('components.modalProvider.form.expandStrategy.options.VISIT'), value: ExpandStrategy.VISIT as string },
]);

// Form state
const form = ref<ProviderForm>({
  id: '',
  conceptscheme_uri: '',
  uri_pattern: '',
  subject: null,
  default_language: '',
  force_display_language: '',
  id_generation_strategy: GenerationStarategyId.NUMERIC,
  expand_strategy: ExpandStrategy.RECURSE,
});

// Initial population of form when editing
onBeforeMount(() => {
  if (isEditMode.value && selectedProvider.value) {
    form.value = {
      id: selectedProvider.value.id,
      conceptscheme_uri: selectedProvider.value.conceptscheme_uri,
      uri_pattern: selectedProvider.value.uri_pattern,
      subject: selectedProvider.value.subject,
      default_language: selectedProvider.value.default_language,
      force_display_language: selectedProvider.value.force_display_language,
      id_generation_strategy: selectedProvider.value.id_generation_strategy,
      expand_strategy: selectedProvider.value.expand_strategy,
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
    adminUiStore.startLoading(PROVIDER_MODAL_LOADING_KEY);

    if (!isEditMode.value) {
      // Create new provider
      await apiService.createProvider(form.value);
      toast.add({
        title: t('api.success.save.title', { item: 'Provider' }),
        description: t('api.success.save.description', { item: 'provider' }),
        icon: 'i-lucide-check-circle',
        color: 'success',
      });
    } else {
      // Update existing provider
      await apiService.updateProvider(form.value);
      toast.add({
        title: t('api.success.update.title', { item: 'Provider' }),
        description: t('api.success.update.description', { item: 'provider' }),
        icon: 'i-lucide-check-circle',
        color: 'success',
      });
    }
    adminUiStore.closeProviderModal();
  } catch (error) {
    handleApiError(error);
  } finally {
    adminUiStore.stopLoading(PROVIDER_MODAL_LOADING_KEY);
  }
};

// Validation
const rules = computed(() => ({
  conceptscheme_uri: {
    required: helpers.withMessage(t('validation.field.required'), required),
    uri: helpers.withMessage(t('validation.field.uri'), (value: string) => {
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    }),
  },
  uri_pattern: {
    required: helpers.withMessage(t('validation.field.required'), required),
  },
}));
const v$ = useVuelidate(rules, form, { $lazy: true });
</script>
