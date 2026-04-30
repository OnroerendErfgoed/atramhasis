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
  members: Relation[];
  member_of: Relation[];
  broader?: Relation[];
  narrower?: Relation[];
  related?: Relation[];
  subordinate_arrays?: Relation[];
  superordinates?: Relation[];
}

export interface ConceptForm {
  conceptscheme: string;
  type: ConceptTypeEnum;
  id?: number;
  labels: Label[];
  notes: Note[];
  sources: Source[];
  member_of: Relation[];
  members?: Relation[];
  broader?: Relation[];
  narrower?: Relation[];
  related?: Relation[];
  subordinate_arrays?: Relation[];
  superordinates?: Relation[];
}

export interface Relation {
  id: string;
  uri: string;
  label: string;
  type: ConceptTypeEnum;
}
