export interface ListType {
  label: string;
  value: string;
}

export enum ModalMode {
  ADD = 'add',
  EDIT = 'edit',
}

export interface Label {
  label: string;
  language: string;
  type: LabelEnum;
}

export interface Note {
  note: string;
  language: string;
  type: NoteEnum;
}

export enum LabelEnum {
  PREF = 'prefLabel',
  ALT = 'altLabel',
  HIDDEN = 'hiddenLabel',
  SORT = 'sortLabel',
}

export enum NoteEnum {
  CHANGE = 'changeNote',
  DEFINITION = 'definition',
  EDITORIAL = 'editorialNote',
  EXAMPLE = 'example',
  HISTORY = 'historyNote',
  SCOPE = 'scopeNote',
  NOTE = 'note',
}
