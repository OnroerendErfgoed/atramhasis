<template>
  <UModal :title="t('modalProvider.title')" :description="t('modalProvider.description')">
    <template #body>
      <UForm class="space-y-4">
        <UFormField
          name="id"
          size="lg"
          :label="t('modalProvider.form.id.label')"
          :description="t('modalProvider.form.id.description')"
        >
          <UInput v-model="form.id" class="w-full" :placeholder="t('modalProvider.form.id.placeholder')" />
        </UFormField>

        <UFormField
          name="conceptschemeUri"
          size="lg"
          :label="t('modalProvider.form.conceptschemeUri.label')"
          :hint="t('modalProvider.form.conceptschemeUri.hint')"
          :error="(v$.conceptscheme_uri.$errors[0]?.$message as string) || false"
        >
          <UInput
            v-model="form.conceptscheme_uri"
            class="w-full"
            :placeholder="t('modalProvider.form.conceptschemeUri.placeholder')"
          />
        </UFormField>

        <UFormField
          name="uriPattern"
          size="lg"
          :label="t('modalProvider.form.uriPattern.label')"
          :hint="t('modalProvider.form.uriPattern.hint')"
          :error="(v$.uri_pattern.$errors[0]?.$message as string) || false"
        >
          <UInput
            v-model="form.uri_pattern"
            class="w-full"
            :placeholder="t('modalProvider.form.uriPattern.placeholder')"
          />
        </UFormField>

        <UFormField name="subject" size="lg" :label="t('modalProvider.form.subject.label')">
          <UInput
            :model-value="form.subject?.[0]"
            class="w-full"
            :placeholder="t('modalProvider.form.subject.placeholder')"
            @update:model-value="form.subject = !!$event ? [$event] : null"
          />
        </UFormField>

        <UFormField name="defaultLanguage" size="lg" :label="t('modalProvider.form.defaultLanguage.label')">
          <USelect
            v-model="form.default_language"
            :items="languageOptions"
            class="w-full"
            :placeholder="t('modalProvider.form.defaultLanguage.placeholder')"
          />
        </UFormField>

        <UFormField name="displayLanguage" size="lg" :label="t('modalProvider.form.displayLanguage.label')">
          <USelect
            v-model="form.force_display_language"
            :items="languageOptions"
            class="w-full"
            :placeholder="t('modalProvider.form.displayLanguage.placeholder')"
          />
        </UFormField>

        <UFormField name="idGenerationStrategy" size="lg" :label="t('modalProvider.form.idGenerationStrategy.label')">
          <USelect
            v-model="form.id_generation_strategy"
            :items="generationStrategyOptions"
            class="w-full"
            :placeholder="t('modalProvider.form.idGenerationStrategy.placeholder')"
          />
        </UFormField>

        <UFormField name="expandStrategy" size="lg" :label="t('modalProvider.form.expandStrategy.label')">
          <USelect
            v-model="form.expand_strategy"
            :items="expandStrategyOptions"
            class="w-full"
            :placeholder="t('modalProvider.form.expandStrategy.placeholder')"
          />
        </UFormField>
      </UForm>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton
          :label="t('modalProvider.cancel')"
          color="neutral"
          variant="outline"
          class="cursor-pointer"
          @click="close"
        />
        <UButton :label="t('modalProvider.save')" class="cursor-pointer" @click="save" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useApiError } from '@composables/useApiError';
import { ExpandStrategy, GenerationStarategyId, type ProviderForm } from '@models/provider';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useLanguageStore } from '@stores/language';
import useVuelidate from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { storeToRefs } from 'pinia';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();

const adminUiStore = useAdminUiStore();
const languageStore = useLanguageStore();
const { languages } = storeToRefs(languageStore);

const apiService = new ApiService();
const { handleApiError } = useApiError();

// Options for select inputs
const languageOptions = computed(() =>
  languages.value.map((lang) => ({
    label: lang.name,
    value: lang.id,
  }))
);

const generationStrategyOptions = computed(() => [
  { label: t('modalProvider.form.idGenerationStrategy.options.GUID'), value: GenerationStarategyId.GUID as string },
  {
    label: t('modalProvider.form.idGenerationStrategy.options.NUMERIC'),
    value: GenerationStarategyId.NUMERIC as string,
  },
  { label: t('modalProvider.form.idGenerationStrategy.options.MANUAL'), value: GenerationStarategyId.MANUAL as string },
]);

const expandStrategyOptions = computed(() => [
  { label: t('modalProvider.form.expandStrategy.options.RECURSE'), value: ExpandStrategy.RECURSE as string },
  { label: t('modalProvider.form.expandStrategy.options.VISIT'), value: ExpandStrategy.VISIT as string },
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

// Save handler
const save = async () => {
  const valid = await v$.value.$validate();
  if (!valid) {
    toast.add({
      title: t('modalProvider.validation.error'),
      description: t('modalProvider.validation.description'),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
    return;
  }

  try {
    await apiService.createProvider(form.value);
    toast.add({
      title: t('modalProvider.success.title'),
      description: t('modalProvider.success.description'),
      icon: 'i-lucide-check-circle',
      color: 'success',
    });
    adminUiStore.closeAddProviderModal();
  } catch (error) {
    handleApiError(error);
  }
};

// Validation
const rules = computed(() => ({
  conceptscheme_uri: {
    required: helpers.withMessage(t('validation.required'), required),
    uri: helpers.withMessage(t('validation.uri'), (value: string) => {
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    }),
  },
  uri_pattern: {
    required: helpers.withMessage(t('validation.required'), required),
  },
}));
const v$ = useVuelidate(rules, form, { $lazy: true });
</script>
