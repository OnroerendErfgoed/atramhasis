import type { Label, Note } from '@models/util';

export interface OverviewConcept {
  id: string;
  uri: string;
  label: string;
  type: 'concept' | 'collection';
}

export interface Concept extends OverviewConcept {
  labels: Label[];
  notes: Note[];
  member_of: Concept[];
}
