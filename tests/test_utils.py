import unittest
from skosprovider_sqlalchemy.models import Concept, Collection, Note, Label, ConceptScheme
from atramhasis.utils import from_thing

from skosprovider.skos import(
    Concept as SkosConcept,
    Collection as SkosCollection
)


class TestFromThing(unittest.TestCase):
    def setUp(self):
        conceptscheme = ConceptScheme()
        conceptscheme.uri = 'urn:x-atramhasis-demo'
        conceptscheme.id = 1
        self.concept = Concept()
        self.concept.type = 'concept'
        self.concept.id = 11
        self.concept.concept_id = 101
        self.concept.uri = 'urn:x-atramhasis-demo:TREES:101'
        self.concept.conceptscheme_id = 1
        self.concept.conceptscheme = conceptscheme

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

        self.collection = Collection()
        self.collection.type = 'collection'
        self.collection.id = 12
        self.collection.concept_id = 102
        self.collection.uri = 'urn:x-atramhasis-demo:TREES:102'
        self.collection.conceptscheme_id = 1
        self.collection.conceptscheme = conceptscheme

    def test_thing_to_concept(self):
        skosconcept = from_thing(self.concept)
        self.assertTrue(isinstance(skosconcept, SkosConcept))
        self.assertEqual(skosconcept.id, 101)
        self.assertEqual(len(skosconcept.labels), 3)
        self.assertEqual(len(skosconcept.notes), 2)
        self.assertEqual(skosconcept.uri, 'urn:x-atramhasis-demo:TREES:101')

    def test_thing_to_collection(self):
        skoscollection = from_thing(self.collection)
        self.assertTrue(isinstance(skoscollection, SkosCollection))
        self.assertEqual(skoscollection.id, 102)
        self.assertEqual(skoscollection.uri, 'urn:x-atramhasis-demo:TREES:102')
