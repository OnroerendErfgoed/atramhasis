import type { Relation } from '@models/concept';
import { RelationTypeEnum } from '@models/util';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useRelationStore = defineStore('relation', () => {
  const selectedRelation = ref<Relation>();
  const selectionType = ref<RelationTypeEnum>();

  const setSelectedRelation = (relation: Relation) => {
    selectedRelation.value = relation;
  };

  const setSelectionType = (type: RelationTypeEnum) => {
    selectionType.value = type;
  };

  return { selectedRelation, setSelectedRelation, selectionType, setSelectionType };
});
