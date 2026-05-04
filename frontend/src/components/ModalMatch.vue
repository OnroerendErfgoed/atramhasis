<template>
  <UModal
    v-model:open="matchModalIsOpen"
    :dismissible="false"
    :title="capitalize(t('components.modalMatch.title', { type: matchModalType }))"
    :description="t('components.modalMatch.description')"
  >
    <template #body>
      <UForm class="space-y-4">
        <UFormField name="external-scheme" size="lg" :label="t('components.modalMatch.form.externalScheme.label')">
          <USelect v-model="form.external_scheme" :items="externalConceptschemeOptions" class="w-full" />
        </UFormField>

        <UFormField name="label-search" size="lg" :label="t('components.modalMatch.form.labelSearch.label')">
          <div class="flex gap-2">
            <UInput
              v-model="labelSearch"
              :placeholder="t('components.modalMatch.form.labelSearch.placeholder')"
              class="flex-1"
            />
            <UButton :label="t('actions.search')" @click="console.log('Search for', labelSearch)" />
          </div>
        </UFormField>

        <UFormField name="labels" size="lg" :label="t('components.modalMatch.form.labels.label')">
          <UListbox
            v-model="form.labels"
            size="lg"
            multiple
            value-key="value"
            :loading="false"
            :items="labels"
            :placeholder="t('components.modalMatch.form.labels.placeholder')"
          />
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
import type { MatchForm } from '@models/concept';
import { MatchTypeEnum } from '@models/util';
import type { ListboxItem } from '@nuxt/ui';
import { useAdminUiStore } from '@stores/admin-ui';
import { useListStore } from '@stores/list';
import { storeToRefs } from 'pinia';
import { capitalize, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const emit = defineEmits<{ add: [MatchForm] }>();

const { t } = useI18n();

const adminUiStore = useAdminUiStore();
const { matchModalIsOpen, matchModalType } = storeToRefs(adminUiStore);
const listStore = useListStore();
const { externalConceptschemeOptions, matchTypes } = storeToRefs(listStore);

// Form state
const labelSearch = ref('');
const labels = ref<ListboxItem[]>([
  { label: 'Label 1', value: 'label1' },
  { label: 'Label 2', value: 'label2' },
]);
const form = ref<MatchForm>({
  external_scheme: externalConceptschemeOptions.value.length > 0 ? externalConceptschemeOptions.value[0]!.value : '',
  labels: [],
  type: matchModalType.value ?? MatchTypeEnum.BROAD,
});

const add = () => {
  if (!form.value.labels.length) return;
  emit('add', form.value);
  adminUiStore.closeMatchModal();
};
</script>
