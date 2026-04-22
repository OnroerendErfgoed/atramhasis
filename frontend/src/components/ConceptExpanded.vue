<template>
  <USkeleton v-if="!concept" class="w-full h-48 flex items-center justify-center"> {{ t('loading') }} </USkeleton>
  <div v-else class="px-4 text-neutral-900">
    <!-- Labels -->
    <div>
      <h3 class="font-semibold mb-2 text-lg">
        {{ t('components.conceptExpanded.labels') }}
      </h3>
      <div v-if="prefLabels.length" class="mb-2">
        <div class="font-semibold mb-0.5">{{ t('components.conceptExpanded.prefLabel') }}</div>
        <div v-for="label in prefLabels" :key="label.label + label.language" class="text-muted">
          {{ label.label }} <em>({{ label.language }})</em>
        </div>
      </div>
      <div v-if="altLabels.length" class="mb-2">
        <div class="font-semibold mb-0.5">{{ t('components.conceptExpanded.altLabels') }}</div>
        <div v-for="label in altLabels" :key="label.label + label.language" class="text-muted">
          {{ label.label }} <em>({{ label.language }})</em>
        </div>
      </div>
      <div v-if="hiddenLabels.length" class="mb-2">
        <div class="font-semibold mb-0.5">{{ t('components.conceptExpanded.hiddenLabels') }}</div>
        <div v-for="label in hiddenLabels" :key="label.label + label.language" class="text-muted">
          {{ label.label }} <em>({{ label.language }})</em>
        </div>
      </div>
      <div v-if="sortLabels.length" class="mb-2">
        <div class="font-semibold mb-0.5">{{ t('components.conceptExpanded.sortLabels') }}</div>
        <div v-for="label in sortLabels" :key="label.label + label.language" class="text-muted">
          {{ label.label }} <em>({{ label.language }})</em>
        </div>
      </div>
    </div>

    <!-- Notes -->
    <div v-if="concept?.notes?.length">
      <h3 class="font-semibold mb-2 text-lg">{{ t('components.conceptExpanded.notes') }}</h3>
      <p v-for="note in concept.notes" :key="note.note + note.language" class="mb-1 leading-relaxed whitespace-normal">
        <span class="font-semibold">{{ capitalize(note.type) }}</span>
        <em> ({{ note.language }})</em>. {{ note.note }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ConceptLabelEnum } from '@enums/concept-label.enum';
import type { Concept } from '@models/concept';
import { useConceptStore } from '@stores/concept';
import { capitalize, computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  schemeId: string;
  conceptId: number;
}>();

const { t } = useI18n();
const toast = useToast();
const conceptStore = useConceptStore();
const concept = ref<Concept>();

const prefLabels = computed(() => concept.value?.labels.filter((label) => label.type === ConceptLabelEnum.PREF) || []);
const altLabels = computed(() => concept.value?.labels.filter((label) => label.type === ConceptLabelEnum.ALT) || []);
const hiddenLabels = computed(
  () => concept.value?.labels.filter((label) => label.type === ConceptLabelEnum.HIDDEN) || []
);
const sortLabels = computed(() => concept.value?.labels.filter((label) => label.type === ConceptLabelEnum.SORT) || []);

onMounted(async () => {
  try {
    concept.value = await conceptStore.getConcept(props.schemeId, props.conceptId);
  } catch (error) {
    console.error(t('errors.fetch.title'), error);
    toast.add({
      title: t('errors.fetch.title'),
      description: t('errors.fetch.description'),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
    });
  }
});
</script>
