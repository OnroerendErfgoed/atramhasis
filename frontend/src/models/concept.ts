import { ConceptLabelEnum } from '@enums/concept-label.enum';
import { ConceptNoteEnum } from '@enums/concept-note.enum';

export interface OverviewConcept {
  id: string;
  uri: string;
  label: string;
  type: 'concept' | 'collection';
}

export interface Concept extends OverviewConcept {
  labels: ConceptLabel[];
  notes: ConceptNote[];
  member_of: Concept[];
}

interface ConceptLabel {
  label: string;
  language: string;
  type: ConceptLabelEnum;
}

interface ConceptNote {
  note: string;
  language: string;
  type: ConceptNoteEnum;
}
