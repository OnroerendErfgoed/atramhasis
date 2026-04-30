import type { ConceptTypeEnum, Label, Note, Source } from '@models/util';

export interface OverviewConcept {
  id: number;
  uri: string;
  label: string;
  type: ConceptTypeEnum;
}

export interface Concept extends OverviewConcept {
  labels: Label[];
  notes: Note[];
  sources: Source[];
  member_of: Concept[];
}

export interface ConceptForm {
  conceptscheme: string;
  type: ConceptTypeEnum;
  id?: number;
  labels: Label[];
  notes: Note[];
  sources: Source[];
}
