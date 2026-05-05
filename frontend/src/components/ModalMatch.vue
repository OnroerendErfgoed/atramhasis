<template>
  <UModal
    v-model:open="matchModalIsOpen"
    :dismissible="false"
    :title="capitalize(t('components.modalMatch.title', { type: matchModalType }))"
    :description="t('components.modalMatch.description')"
  >
    <template #body>
      <UForm class="space-y-4" @submit.prevent="fetchMatches">
        <UFormField name="external-scheme" size="lg" :label="t('components.modalMatch.form.externalScheme.label')">
          <USelect v-model="form.external_scheme" :items="externalConceptschemeOptions" class="w-full" />
        </UFormField>

        <UFormField
          name="label-search"
          size="lg"
          :label="t('components.modalMatch.form.labelSearch.label')"
          :hint="t('components.modalMatch.form.labelSearch.hint')"
        >
          <div class="flex gap-2">
            <UInput
              v-model="labelSearch"
              class="flex-1"
              :placeholder="t('components.modalMatch.form.labelSearch.placeholder')"
            />
            <UButton type="submit" :label="t('actions.search')" />
          </div>
        </UFormField>

        <UFormField name="labels" size="lg" :label="t('components.modalMatch.form.labels.label')">
          <UListbox
            v-model="form.uris"
            size="lg"
            value-key="value"
            multiple
            :loading="matchesLoading"
            :items="matches"
            :placeholder="t('components.modalMatch.form.labels.placeholder')"
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
              <p class="text-center text-sm text-muted">{{ t('components.modalMatch.form.labels.noResults') }}</p>
            </template>
          </UListbox>
        </UFormField>

        <UFormField name="type" size="lg" :label="t('components.modalMatch.form.type.label')">
          <USelect v-model="form.type" :items="matchTypes" class="w-full" />
        </UFormField>
      </UForm>
    </template>
    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton :label="t('actions.cancel')" color="neutral" variant="outline" @click="close" />
        <UButton :label="t('actions.add')" @click="add" />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { MatchForm, OverviewConcept } from '@models/concept';
import { MatchTypeEnum } from '@models/util';
import type { ListboxItem } from '@nuxt/ui';
import { ApiService } from '@services/api.service';
import { useAdminUiStore } from '@stores/admin-ui';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';
import { capitalize, computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const emit = defineEmits<{ add: [MatchForm] }>();

const toast = useToast();
const { t } = useI18n();
const apiService = new ApiService();

const adminUiStore = useAdminUiStore();
const { matchModalIsOpen, matchModalType } = storeToRefs(adminUiStore);
const listStore = useListStore();
const { externalConceptschemeOptions, matchTypes } = storeToRefs(listStore);

// Form state
const labelSearch = ref('');
const matches = computed<ListboxItem[]>(() =>
  concepts.value.map((concept) => ({
    label: capitalize(concept.label),
    value: concept.uri,
    description: `${capitalize(concept.type)} - ID ${concept.id}`,
    uri: concept.uri,
  }))
);
const form = ref<MatchForm>({
  external_scheme: externalConceptschemeOptions.value.length > 0 ? externalConceptschemeOptions.value[0]!.value : '',
  uris: [],
  type: matchModalType.value ?? MatchTypeEnum.BROAD,
});

const add = () => {
  if (!form.value.uris.length) return;
  emit('add', form.value);
  adminUiStore.closeMatchModal();
};

// Get matches based on form input
const concepts = ref<OverviewConcept[]>([]);
const matchesLoading = ref(false);
const fetchMatches = async () => {
  if (labelSearch.value.trim() === '' || labelSearch.value.length < 3) {
    toast.add({
      title: t('components.modalMatch.form.labelSearch.hint'),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
    return;
  }
  matchesLoading.value = true;
  try {
    concepts.value = await apiService.getConceptsByConceptscheme(form.value.external_scheme, {
      label: labelSearch.value,
      type: 'all',
      sort: 'label',
    });
    console.log(concepts.value);
  } catch (error) {
    console.error(t('api.errors.fetch.title', { item: t('entities.concept', 2) }), error);
    toast.add({
      title: t('api.errors.fetch.title', { item: t('entities.concept', 2) }),
      description: t('api.errors.fetch.description', { item: t('entities.concept', 2) }),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  } finally {
    matchesLoading.value = false;
  }
};
</script>
