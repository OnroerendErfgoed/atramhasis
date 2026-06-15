<template>
  <UModal
    v-model:open="importConceptModalIsOpen"
    :dismissible="false"
    :title="t('components.modalImportConcept.title')"
    :description="t('components.modalImportConcept.description')"
  >
    <template #body>
      <UForm class="space-y-4" @submit.prevent="search">
        <UFormField
          name="external-scheme"
          size="lg"
          :label="t('components.modalImportConcept.form.externalScheme.label')"
        >
          <USelect v-model="selectedScheme" :items="externalConceptschemeOptions" class="w-full" />
        </UFormField>

        <UFormField name="label-search" size="lg" :label="t('components.modalImportConcept.form.labelSearch.label')">
          <div class="flex gap-2">
            <UInput
              v-model="labelSearch"
              class="flex-1"
              :placeholder="t('components.modalImportConcept.form.labelSearch.placeholder')"
            />
            <UButton :loading="isSearching" type="submit" :label="t('actions.search')" />
          </div>
        </UFormField>

        <UFormField name="results" size="lg" :label="t('components.modalImportConcept.form.results.label')">
          <UListbox
            v-model="selectedUri"
            size="lg"
            value-key="value"
            :loading="isSearching"
            :items="resultItems"
            :placeholder="t('components.modalImportConcept.form.results.placeholder')"
          >
            <template #item-description="{ item }">
              <span class="block text-sm text-muted">
                {{ item.description }}
                <ULink class="inline-block" :href="item.uri" external target="_blank">
                  <UIcon class="ml-1" name="i-lucide-external-link" />
                </ULink>
              </span>
            </template>

            <template #empty>
              <p class="text-center text-sm text-muted">
                {{ t('components.modalImportConcept.form.results.noResults') }}
              </p>
            </template>
          </UListbox>
        </UFormField>
      </UForm>
    </template>

    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton
          :label="t('actions.import')"
          icon="i-lucide-download"
          :disabled="!selectedUri"
          :loading="isImporting"
          @click="importConcept"
        />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { Concept, OverviewConcept } from '@models/concept';
import { ConceptTypeEnum, ModalMode } from '@models/util';
import type { ListboxItem } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useConceptStore } from '@stores/concept';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';
import { capitalize, computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const apiService = new ApiService();

const adminUiStore = useAdminUiStore();
const { importConceptModalIsOpen } = storeToRefs(adminUiStore);
const listStore = useListStore();
const { externalConceptschemeOptions } = storeToRefs(listStore);
const conceptStore = useConceptStore();

const selectedScheme = ref(externalConceptschemeOptions.value[0]?.value ?? '');
const labelSearch = ref('');
const results = ref<OverviewConcept[]>([]);
const selectedUri = ref('');
const isSearching = ref(false);
const isImporting = ref(false);

const resultItems = computed<ListboxItem[]>(() =>
  results.value.map((concept) => ({
    label: capitalize(concept.label),
    value: concept.uri,
    description: `${capitalize(concept.type)} - ID ${concept.id}`,
    uri: concept.uri,
  }))
);

const selectedConcept = computed(() => results.value.find((c) => c.uri === selectedUri.value) ?? null);

const search = async () => {
  if (!selectedScheme.value || !labelSearch.value.trim()) return;

  isSearching.value = true;
  selectedUri.value = '';
  try {
    results.value = await apiService.getConceptsByConceptscheme(selectedScheme.value, {
      label: labelSearch.value,
      type: 'all',
      sort: 'label',
    });
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.concept', 2) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.concept', 2) }),
      description: t('api.errors.fetch.description', { item: t('entities.concept', 2) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    isSearching.value = false;
  }
};

const importConcept = async () => {
  if (!selectedConcept.value) return;

  isImporting.value = true;
  try {
    const concept = await apiService.getConceptByConceptschemeAndId(selectedScheme.value, selectedConcept.value.id);
    const preFill: Concept = {
      ...concept,
      id: '',
      matches: {
        narrow: concept.matches?.narrow ?? [],
        broad: concept.matches?.broad ?? [],
        related: concept.matches?.related ?? [],
        close: concept.matches?.close ?? [],
        exact:
          concept.type !== ConceptTypeEnum.COLLECTION
            ? [concept.uri, ...(concept.matches?.exact ?? [])]
            : (concept.matches?.exact ?? []),
      },
    };

    conceptStore.setSelectedConcept(preFill);
    adminUiStore.openConceptModal(ModalMode.ADD);
    adminUiStore.closeImportConceptModal();
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.concept') }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.concept') }),
      description: t('api.errors.fetch.description', { item: t('entities.concept') }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    isImporting.value = false;
  }
};
</script>
