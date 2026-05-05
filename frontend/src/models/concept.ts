import type { ConceptTypeEnum, Label, MatchTypeEnum, Note, Source } from '@models/util';

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
  infer_concept_relations?: boolean;
  matches: Matches;
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
  infer_concept_relations?: boolean;
  matches: Matches;
}

export interface Relation {
  id: string;
  uri: string;
  label: string;
  type: ConceptTypeEnum;
}

export interface Matches {
  narrow: string[];
  broad: string[];
  related: string[];
  close: string[];
  exact: string[];
}

export interface Match {
  label: string;
  uri: string;
  type?: MatchTypeEnum;
}

export interface MatchForm {
  external_scheme: string;
  uris: string[];
  type: MatchTypeEnum;
}
