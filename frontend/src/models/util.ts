export interface ListType {
  label: string;
  value: string;
}

export enum ModalMode {
  ADD = 'add',
  EDIT = 'edit',
}

export interface Label {
  id?: number;
  label: string;
  language: string;
  type: LabelTypeEnum;
}

export interface Note {
  id?: number;
  note: string;
  language: string;
  type: NoteTypeEnum;
}

export interface Source {
  id?: number;
  citation: string;
}

export enum LabelTypeEnum {
  PREF = 'prefLabel',
  ALT = 'altLabel',
  HIDDEN = 'hiddenLabel',
  SORT = 'sortLabel',
}

export enum NoteTypeEnum {
  CHANGE = 'changeNote',
  DEFINITION = 'definition',
  EDITORIAL = 'editorialNote',
  EXAMPLE = 'example',
  HISTORY = 'historyNote',
  SCOPE = 'scopeNote',
  NOTE = 'note',
}

export enum MatchTypeEnum {
  BROAD = 'broad',
  CLOSE = 'close',
  EXACT = 'exact',
  NARROW = 'narrow',
  RELATED = 'related',
}

export enum ConceptTypeEnum {
  CONCEPT = 'concept',
  COLLECTION = 'collection',
}
