export interface ConceptschemeContext {
  '@version': 1.1;
  dct: string;
  skos: string;
  'iso-thes': string;
  rdf: string;
  rdfs: string;
  void: string;
  uri: '@id';
  type: '@type';
  id: 'dct:identifier';
  label: 'rdfs:label';
  concept: 'skos:Concept';
  collection: 'skos:Collection';
  concept_scheme: {
    '@id': 'skos:inScheme';
    '@type': '@id';
  };
  subject: {
    '@id': 'dct:subject';
    '@type': '@id';
  };
}

export interface Conceptscheme {
  '@context': ConceptschemeContext;
  type: 'skos:ConceptScheme';
  id: string;
  uri: string;
  label: string;
  subject: string[];
}
