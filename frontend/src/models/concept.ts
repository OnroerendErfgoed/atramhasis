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

export enum ConceptLabelEnum {
  PREF = 'prefLabel',
  ALT = 'altLabel',
  HIDDEN = 'hiddenLabel',
  SORT = 'sortLabel',
}

export enum ConceptNoteEnum {
  CHANGE = 'changeNote',
  DEFINITION = 'definition',
  EDITORIAL = 'editorialNote',
  EXAMPLE = 'example',
  HISTORY = 'historyNote',
  SCOPE = 'scopeNote',
  NOTE = 'note',
}
