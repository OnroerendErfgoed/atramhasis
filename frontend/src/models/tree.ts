import type { ConceptTypeEnum } from '@models/util';

export interface Tree {
  concept_id: string;
  id: string;
  label: string;
  type: ConceptTypeEnum;
  children?: Tree[];
}
