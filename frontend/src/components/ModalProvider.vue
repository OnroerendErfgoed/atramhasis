<template>
  <UModal
    :title="t('modalProvider.title')"
    :description="t('modalProvider.description')"
    :ui="{ content: 'sm:max-w-2xl' }"
  >
    <template #body>
      <UForm class="space-y-4">
        <UFormField
          name="id"
          size="lg"
          :label="t('modalProvider.form.id.label')"
          :description="t('modalProvider.form.id.description')"
        >
          <UInput class="w-full" :placeholder="t('modalProvider.form.id.placeholder')" />
        </UFormField>

        <UFormField
          name="conceptschemeUri"
          size="lg"
          :label="t('modalProvider.form.conceptschemeUri.label')"
          :hint="t('modalProvider.form.conceptschemeUri.hint')"
        >
          <UInput class="w-full" :placeholder="t('modalProvider.form.conceptschemeUri.placeholder')" />
        </UFormField>

        <UFormField
          name="uriPattern"
          size="lg"
          :label="t('modalProvider.form.uriPattern.label')"
          :hint="t('modalProvider.form.uriPattern.hint')"
        >
          <UInput class="w-full" :placeholder="t('modalProvider.form.uriPattern.placeholder')" />
        </UFormField>

        <UFormField name="subject" size="lg" :label="t('modalProvider.form.subject.label')">
          <UInput class="w-full" :placeholder="t('modalProvider.form.subject.placeholder')" />
        </UFormField>

        <UFormField name="defaultLanguage" size="lg" :label="t('modalProvider.form.defaultLanguage.label')">
          <USelect
            :items="languageOptions"
            class="w-full"
            :placeholder="t('modalProvider.form.defaultLanguage.placeholder')"
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
        <UButton :label="t('modalProvider.save')" class="cursor-pointer" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useLanguageStore } from '@stores/language';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const languageStore = useLanguageStore();
const { languages } = storeToRefs(languageStore);

const languageOptions = computed(() =>
  languages.value.map((lang) => ({
    label: lang.name,
    value: lang.id,
  }))
);
</script>
