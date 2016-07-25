import unittest
from skosprovider_sqlalchemy.models import Concept, Collection, Note, Label, Source, Match, MatchType, Language, ConceptScheme
from pyramid import testing
from fixtures.data import trees
from skosprovider.registry import Registry


class TestJsonRenderer(unittest.TestCase):

    def setUp(self):
        self.concept = Concept()
        self.concept.type = 'concept'
        self.concept.id = 11
        self.concept.concept_id = 101
        self.concept.uri = 'urn:x-atramhasis-demo:TREES:101'
        self.concept.conceptscheme_id = 1

        notes = []
        note = Note(note='test note', notetype_id='example', language_id='en')
        note2 = Note(note='note def', notetype_id='definition', language_id='en')
        notes.append(note)
        notes.append(note2)
        self.concept.notes = notes

        labels = []
        label = Label(label='een label', labeltype_id='prefLabel', language_id='nl')
        label2 = Label(label='other label', labeltype_id='altLabel', language_id='en')
        label3 = Label(label='and some other label', labeltype_id='altLabel', language_id='en')
        labels.append(label)
        labels.append(label2)
        labels.append(label3)
        self.concept.labels = labels

        sources = []
        source = Source('Van Daele K. 2009')
        sources.append(source)
        self.concept.sources = sources

        matches = []
        match = Match()
        match.matchtype = MatchType(name='closeMatch', description='test')
        match.uri = 'urn:somethingelse:st1'
        matches.append(match)
        match2 = Match()
        match2.matchtype = MatchType(name='closeMatch', description='test')
        match2.uri = 'urn:somethingelse:st2'
        matches.append(match2)
        match3 = Match()
        match3.matchtype = MatchType(name='exactMatch', description='test')
        match3.uri = 'urn:something:thingy'
        matches.append(match3)
        self.concept.matches = matches

        self.collection = Collection()
        self.collection.type = 'collection'
        self.collection.id = 12
        self.collection.concept_id = 102
        self.collection.uri = 'urn:x-atramhasis-demo:TREES:102'
        self.collection.conceptscheme_id = 1

        self.conceptscheme = ConceptScheme()
        self.conceptscheme.id = 1
        self.conceptscheme.labels = labels
        self.conceptscheme.notes = notes
        self.conceptscheme.sources = sources
        self.conceptscheme.uri = None

        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.skos_registry = self.regis
        self.request.matchdict = {'scheme_id': 'TREES'}
        self.request.locale_name = 'nl'

        self.concept.member_of.add(self.collection)
        self.collection.members.add(self.concept)

    def test_label_adapter(self):
        from atramhasis.renderers import label_adapter
        l = self.concept.labels[2]
        label = label_adapter(l, {})
        self.assertIsInstance(label, dict)
        self.assertEqual(label['label'], 'and some other label')
        self.assertEqual(label['type'], 'altLabel')
        self.assertEqual(label['language'], 'en')

    def test_note_adapter(self):
        from atramhasis.renderers import note_adapter
        n = self.concept.notes[0]
        note = note_adapter(n, {})
        self.assertIsInstance(note, dict)
        self.assertEqual(note['note'], 'test note')
        self.assertEqual(note['type'], 'example')
        self.assertEqual(note['language'], 'en')

    def test_source_adapter(self):
        from atramhasis.renderers import source_adapter
        s = self.concept.sources[0]
        source = source_adapter(s, {})
        self.assertIsInstance(source, dict)
        self.assertEqual(source['citation'], 'Van Daele K. 2009')

    def test_concept_adapter(self):
        from atramhasis.renderers import concept_adapter
        c = self.concept
        concept = concept_adapter(c, self.request)
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 101)
        self.assertEqual(concept['type'], 'concept')
        self.assertEqual(concept['uri'], 'urn:x-atramhasis-demo:TREES:101')
        self.assertIsNotNone(concept['label'], 'een label')
        self.assertIsInstance(concept['labels'], list)
        self.assertEqual(len(concept['labels']), 3)
        self.assertIsInstance(concept['notes'], list)
        self.assertEqual(len(concept['notes']), 2)
        self.assertIsInstance(concept['sources'], list)
        self.assertEqual(len(concept['sources']), 1)
        self.assertIsInstance(concept['member_of'], list)
        self.assertEqual(len(concept['member_of']), 1)
        self.assertIsInstance(concept['narrower'], list)
        self.assertEqual(len(concept['narrower']), 0)
        self.assertIsInstance(concept['broader'], list)
        self.assertEqual(len(concept['broader']), 0)
        self.assertIsInstance(concept['related'], list)
        self.assertEqual(len(concept['related']), 0)
        self.assertIsInstance(concept['matches'], dict)
        self.assertEqual(len(concept['matches']['exact']), 1)
        self.assertEqual(len(concept['matches']['close']), 2)

    def test_collection_adapter(self):
        from atramhasis.renderers import collection_adapter
        c = self.collection
        collection = collection_adapter(c, self.request)
        self.assertIsInstance(collection, dict)
        self.assertEqual(collection['id'], 102)
        self.assertEqual(collection['type'], 'collection')
        self.assertEqual(collection['uri'], 'urn:x-atramhasis-demo:TREES:102')
        self.assertIsNone(collection['label'])
        self.assertIsInstance(collection['labels'], list)
        self.assertEqual(len(collection['labels']), 0)
        self.assertIsInstance(collection['member_of'], list)
        self.assertEqual(len(collection['member_of']), 0)
        self.assertIsInstance(collection['members'], list)
        self.assertEqual(len(collection['members']), 1)

    def test_map_relation_concept(self):
        from atramhasis.renderers import map_relation
        c = self.concept
        relation = map_relation(c)
        self.assertIsInstance(relation, dict)
        self.assertEqual(relation['id'], 101)
        self.assertEqual(relation['type'], 'concept')
        self.assertEqual(relation['uri'], 'urn:x-atramhasis-demo:TREES:101')
        self.assertIsNotNone(relation['label'], 'een label')
        self.assertRaises(KeyError, lambda: relation['notes'])
        self.assertRaises(KeyError, lambda: relation['member_of'])
        self.assertRaises(KeyError, lambda: relation['narrower'])
        self.assertRaises(KeyError, lambda: relation['broader'])
        self.assertRaises(KeyError, lambda: relation['related'])

    def test_map_relation_collection(self):
        from atramhasis.renderers import map_relation
        c = self.collection
        relation = map_relation(c)
        self.assertIsInstance(relation, dict)
        self.assertEqual(relation['id'], 102)
        self.assertEqual(relation['type'], 'collection')
        self.assertEqual(relation['uri'], 'urn:x-atramhasis-demo:TREES:102')
        self.assertIsNone(relation['label'])
        self.assertRaises(KeyError, lambda: relation['members'])
        self.assertRaises(KeyError, lambda: relation['member_of'])

    def test_language_adaptor(self):
        from atramhasis.renderers import language_adaptor
        l = Language(id='af', name='Afrikaans')
        res = language_adaptor(l, None)
        self.assertIsNotNone(res)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['id'], 'af')
        self.assertEqual(res['name'], 'Afrikaans')

    def test_conceptscheme_adapter(self):
        from atramhasis.renderers import conceptscheme_adapter
        c = self.conceptscheme
        conceptscheme = conceptscheme_adapter(c, self.request)
        self.assertGreater(len(conceptscheme['notes']), 0)
        self.assertGreater(len(conceptscheme['labels']), 0)
        self.assertGreater(len(conceptscheme['sources']), 0)
        self.assertIsNone(conceptscheme['uri'])
        self.assertEqual('een label', conceptscheme['label'])
        self.assertEqual(1, conceptscheme['id'])
        self.assertEqual(0, len(conceptscheme['subject']))
        self.assertIsInstance(conceptscheme, dict)

    def test_conceptscheme_language_handling(self):
        from atramhasis.renderers import conceptscheme_adapter
        c = self.conceptscheme
        conceptscheme = conceptscheme_adapter(c, self.request)
        self.assertEqual('een label', conceptscheme['label'])
        self.request.locale_name = 'en'
        conceptscheme = conceptscheme_adapter(c, self.request)
        self.assertIn(conceptscheme['label'], ['other label', 'and some other label'])
