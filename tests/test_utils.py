import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPMethodNotAllowed
from skosprovider.providers import DictionaryProvider
from skosprovider.skos import Collection as SkosCollection
from skosprovider.skos import Concept as SkosConcept
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import Match
from skosprovider_sqlalchemy.models import MatchType
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import Source
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from atramhasis.utils import from_thing
from atramhasis.utils import internal_providers_only
from atramhasis.utils import label_sort
from atramhasis.utils import provider_is_external
from atramhasis.utils import update_last_visited_concepts


species = {
    'id': 3,
    'uri': 'http://id.trees.org/3',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'},
    ],
    'type': 'collection',
    'members': ['1', '2'],
    'notes': [
        {
            'type': 'editorialNote',
            'language': 'en',
            'note': 'As seen in How to Recognise Different Types of Trees from Quite a Long Way Away.',
        }
    ],
}


class TestFromThing(unittest.TestCase):
    def setUp(self):
        conceptscheme = ConceptScheme()
        conceptscheme.uri = 'urn:x-atramhasis-demo'
        conceptscheme.id = 1
        self.concept = Concept()
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
        label3 = Label(
            label='and some other label', labeltype_id='altLabel', language_id='en'
        )
        labels.append(label)
        labels.append(label2)
        labels.append(label3)
        self.concept.labels = labels

        sources = []
        source = Source(citation='Kinsella S. & Carlisle P. 2015: Alice.')
        sources.append(source)
        self.concept.sources = sources

        matches = []
        match1 = Match()
        match1.uri = 'urn:test'
        match1.concept = self.concept
        match1.matchtype = MatchType(name='closeMatch', description='')
        match2 = Match()
        match2.uri = 'urn:test'
        match2.concept = self.concept
        match2.matchtype = MatchType(name='closeMatch', description='')
        matches.append(match1)
        matches.append(match2)
        self.matches = matches

        self.collection = Collection()
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
        self.assertEqual(len(skosconcept.sources), 1)
        self.assertEqual(skosconcept.uri, 'urn:x-atramhasis-demo:TREES:101')

    def test_thing_to_collection(self):
        skoscollection = from_thing(self.collection)
        self.assertTrue(isinstance(skoscollection, SkosCollection))
        self.assertEqual(skoscollection.id, 102)
        self.assertEqual(skoscollection.uri, 'urn:x-atramhasis-demo:TREES:102')


class DummyViewClassForTest:
    def __init__(self):
        self.provider = None
        self.dummy = None

    def all_providers(self, dummy):
        self.dummy = dummy

    @internal_providers_only
    def internal_providers(self, dummy):
        self.dummy = dummy


class TestInternalProviderOnly(unittest.TestCase):
    def setUp(self):
        self.dummy = DummyViewClassForTest()

    def test_all_providers(self):
        self.dummy.provider = DictionaryProvider(
            list=[species], metadata={'id': 'Test'}
        )
        self.dummy.all_providers('ok')
        self.assertEqual(self.dummy.dummy, 'ok')

    def test_internal_providers(self):
        self.dummy.provider = SQLAlchemyProvider(
            metadata={'id': 'Test', 'conceptscheme_id': 1}, session=None
        )
        self.dummy.internal_providers('ok')
        self.assertEqual(self.dummy.dummy, 'ok')

    def test_external_providers(self):
        self.dummy.provider = SQLAlchemyProvider(
            metadata={'id': 'Test', 'conceptscheme_id': 1, 'subject': ['external']},
            session=None,
        )
        self.assertRaises(HTTPMethodNotAllowed, self.dummy.internal_providers, 'ok')
        self.assertIsNone(self.dummy.dummy)

    def test_no_sqlalchemyprovider(self):
        self.dummy.provider = DictionaryProvider(
            list=[species], metadata={'id': 'Test'}
        )
        self.assertRaises(HTTPMethodNotAllowed, self.dummy.internal_providers, 'ok')
        self.assertIsNone(self.dummy.dummy)


class TestUpdateLastVisitedConceptsProviderOnly(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.session = {}

    def tearDown(self):
        testing.tearDown()

    def test_update_last_visited_concepts(self):
        c = Concept()
        c.id = 2
        c.labels = [Label('test', language_id='en-us')]
        update_last_visited_concepts(
            self.request, {'label': c.label(), 'url': f'https://test.test/{55}'}
        )
        c = Concept()
        c.id = 33
        c.labels = [Label('test', language_id='nl-be')]
        update_last_visited_concepts(
            self.request, {'label': c.label(), 'url': f'https://test.test/{2}'}
        )
        self.assertEqual(2, len(self.request.session['last_visited']))

    def test_update_last_visited_concepts_max(self):
        for concept_id in range(50):
            c = Concept()
            c.id = concept_id
            c.labels = [Label('test', language_id='en-us')]
            update_last_visited_concepts(
                self.request,
                {'label': c.label(), 'url': f'https://test.test/{concept_id}'},
            )
        self.assertEqual(4, len(self.request.session['last_visited']))
        last = self.request.session['last_visited'].pop()
        self.assertEqual('https://test.test/49', last['url'])

    def test_no_double_last_visited_concepts(self):
        c = Concept()
        c.id = 2
        c.labels = [Label('test', language_id='en-us')]
        update_last_visited_concepts(
            self.request, {'label': c.label(), 'url': f'https://test.test/{55}'}
        )
        update_last_visited_concepts(
            self.request, {'label': c.label(), 'url': f'https://test.test/{55}'}
        )
        c = Concept()
        c.id = 33
        c.labels = [Label('test', language_id='nl-be')]
        update_last_visited_concepts(
            self.request, {'label': c.label(), 'url': f'https://test.test/{2}'}
        )
        self.assertEqual(2, len(self.request.session['last_visited']))


class DummyConcept:
    def __init__(self, sortlabel, language='any'):
        self.sortlabel = sortlabel
        self.language = language

    def _sortkey(self, key='sortlabel', language='any'):
        # Simulate sorting by label and language
        if language == 'any':
            return self.sortlabel
        if hasattr(self, 'labels'):
            for label in self.labels:
                if label['language'] == language:
                    return label['label']
        return self.sortlabel


def test_label_sort_empty():
    assert label_sort([]) == []


def test_label_sort_basic_sorting():
    c1 = DummyConcept('banana')
    c2 = DummyConcept('apple')
    c3 = DummyConcept('cherry')
    sorted_concepts = label_sort([c1, c2, c3])
    assert [c.sortlabel for c in sorted_concepts] == [
        'apple',
        'banana',
        'cherry',
    ]


def test_label_sort_with_language():
    class DummyConceptWithLabels(DummyConcept):
        def __init__(self, labels):
            self.labels = labels

        def _sortkey(self, key='sortlabel', language='any'):
            for label in self.labels:
                if label['language'] == language:
                    return label['label']
            return self.labels[0]['label']

    c1 = DummyConceptWithLabels(
        [
            {'label': 'appel', 'language': 'nl'},
            {'label': 'apple', 'language': 'en'},
        ]
    )
    c2 = DummyConceptWithLabels(
        [
            {'label': 'banaan', 'language': 'nl'},
            {'label': 'banana', 'language': 'en'},
        ]
    )
    c3 = DummyConceptWithLabels(
        [
            {'label': 'kers', 'language': 'nl'},
            {'label': 'cherry', 'language': 'en'},
        ]
    )
    sorted_concepts = label_sort([c1, c2, c3], language='en')
    assert [c._sortkey(language='en') for c in sorted_concepts] == [
        'apple',
        'banana',
        'cherry',
    ]
    sorted_concepts_nl = label_sort([c1, c2, c3], language='nl')
    assert [c._sortkey(language='nl') for c in sorted_concepts_nl] == [
        'appel',
        'banaan',
        'kers',
    ]


class TestProviderIsExternal(unittest.TestCase):
    def test_provider_is_external_with_external_subject(self):
        provider = MockProvider({'subject': ['external', 'other']})
        assert provider_is_external(provider) is True

    def test_provider_is_external_case_insensitive(self):
        provider = MockProvider({'subject': ['EXTERNAL']})
        assert provider_is_external(provider) is True

        provider = MockProvider({'subject': ['External']})
        assert provider_is_external(provider) is True

    def test_provider_is_not_external(self):
        provider = MockProvider({'subject': ['hidden', 'other']})
        assert provider_is_external(provider) is False

    def test_provider_is_external_no_subjects(self):
        provider = MockProvider({})
        assert provider_is_external(provider) is False

    def test_provider_is_external_empty_subjects(self):
        provider = MockProvider({'subject': []})
        assert provider_is_external(provider) is False


class MockProvider:
    """Mock provider for testing."""

    def __init__(self, metadata):
        self._metadata = metadata

    def get_metadata(self):
        return self._metadata
