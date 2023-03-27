import unittest
from unittest.mock import Mock

from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import Match
from skosprovider_sqlalchemy.models import MatchType
from skosprovider_sqlalchemy.models import Source
from sqlalchemy.exc import NoResultFound

from atramhasis import mappers
from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider
from atramhasis.mappers import map_concept
from atramhasis.mappers import map_conceptscheme

test_json = {
    "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
    "label": "Belgium",
    "type": "concept",
    "id": 4,
    "broader": [{"id": 2}, {"id": 11}],
    "related": [{"id": 5}, {"id": 12}],
    "member_of": [{"id": 999}],
    "labels": [{
                   "label": "Belgium",
                   "type": "prefLabel",
                   "language": "en"
               }, {
                   "label": "België",
                   "type": "prefLabel",
                   "language": "nl"
               }],
    "notes": [{
                  "note": "een notitie",
                  "type": "note",
                  "language": "nl"
              }],
    "sources": [{
        "citation": "Atlas."
    }]
}
json_collection = {
    "id": 0,
    "labels": [{
                   "language": "nl",
                   "label": "Stijlen en culturen",
                   "type": "prefLabel"
               }],
    "type": "collection",
    "label": "Stijlen en culturen",
    "members": [{"id": 61}, {"id": 60}, {"id": 12}],
    "member_of": [{"id": 999}, {"id": 7}],
    "notes": [{
                  "note": "een notitie",
                  "type": "note",
                  "language": "nl"
              }]
}
test_json_conceptscheme = {
    "label": "Stijlen en culturen",
    "labels": [{
                   "language": "nl",
                   "label": "Stijlen en culturen",
                   "type": "prefLabel"
               }],
    "notes": [{
                  "note": "een notitie",
                  "type": "note",
                  "language": "nl"
              }],
    "sources": [{
        "citation": "Atlas."
    }]
}
test_json_html = {
    "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
    "label": "Belgium",
    "type": "concept",
    "id": 4,
    "broader": [{"id": 2}, {"id": 11}],
    "related": [{"id": 5}, {"id": 12}],
    "member_of": [{"id": 999}],
    "labels": [{
                   "label": "Belgium",
                   "type": "prefLabel",
                   "language": "en"
               }, {
                   "label": "België",
                   "type": "prefLabel",
                   "language": "nl"
               }],
    "notes": [{
                  "note": "een <a href='#'>notitie</a>",
                  "type": "note",
                  "language": "nl"
              }],
    "sources": [{
        "citation": "<em>Atlas.</em>"
    }]
}


class DummySkosManager:
    def get_thing(self, concept_id, conceptscheme_id):
        if concept_id in (7, 11, 12):
            raise NoResultFound()
        if concept_id in (999, 19):
            return Collection(
                id=concept_id,
                concept_id=concept_id,
                conceptscheme_id=conceptscheme_id
            )
        else:
            return Concept(
                id=concept_id,
                concept_id=concept_id,
                conceptscheme_id=conceptscheme_id
            )

    def change_type(self, _, concept_id, conceptscheme_id, new_type, uri):
        thing = Concept() if new_type == 'concept' else Collection()
        thing.type = new_type
        thing.concept_id = concept_id
        thing.conceptscheme_id = conceptscheme_id
        thing.uri = uri
        return thing

    def get_match_type(self, *_, **__):
        return Mock()

    def get_match(self, uri, matchtype_id, concept_id):
        if concept_id == -1:
            raise NoResultFound()
        else:
            match = Match()
            match.uri = uri
            match.concept_id = concept_id
            if matchtype_id in [
                'broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch', 'relatedMatch'
            ]:
                match.matchtype = MatchType(matchtype_id, 'test')
                return match
            else:
                raise NoResultFound()


class TestMappers(unittest.TestCase):
    def setUp(self):
        self.skos_manager = DummySkosManager()
        self.concept = Concept()
        self.concept.concept_id = 1
        self.concept.conceptscheme_id = 1
        self.collection = Collection()
        self.collection.concept_id = 0
        self.collection.conceptscheme_id = 1
        self.collection.uri = "urn:x-skosprovider:trees/3"
        self.conceptscheme = ConceptScheme()
        self.conceptscheme.id = 1
        member_concept_1 = Concept()
        member_concept_1.concept_id = 5
        member_concept_1.conceptscheme_id = 1
        member_concept_2 = Collection()
        member_concept_2.concept_id = 6
        member_concept_2.conceptscheme_id = 1
        self.collection.members.add(member_concept_1)
        self.collection.members.add(member_concept_2)
        self.concept.narrower_concepts.add(member_concept_1)
        self.concept.narrower_collections.add(member_concept_2)

    def tearDown(self):
        self.concept = None

    def test_mapping(self):
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(2, len(result_concept.broader_concepts))
        self.assertEqual(2, len(result_concept.related_concepts))
        self.assertEqual(1, len(result_concept.member_of))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))
        self.assertEqual(1, len(result_concept.sources))
        self.assertFalse(hasattr(result_concept, 'members'))
        self.assertIsNone(result_concept.notes[0].markup)

    def test_mapping_collections_filled(self):
        label = Label(label='test', labeltype_id='altLabel', language_id='nl')
        self.concept.labels.append(label)
        related_concept = Concept(concept_id=6, conceptscheme_id=1)
        self.concept.related_concepts.add(related_concept)
        source = Source(citation='testCitation')
        self.concept.sources.append(source)
        source = Source(citation='AnotherTestCitation')
        self.concept.sources.append(source)
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(2, len(result_concept.broader_concepts))
        self.assertEqual(2, len(result_concept.related_concepts))
        self.assertEqual(1, len(result_concept.member_of))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))
        self.assertEqual(1, len(result_concept.sources))

    def test_mapping_check_db_lookup(self):
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        for narrower_concept in result_concept.narrower_concepts:
            self.assertIsNotNone(narrower_concept)
            if narrower_concept.concept_id == 7:
                self.assertIsNone(narrower_concept.id)

    def test_mapping_check_db_lookup_member_of(self):
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        for member_of in result_concept.member_of:
            self.assertIsNotNone(member_of)
            if member_of.concept_id == 7:
                self.assertIsNone(member_of.id)

    def test_mapping_collection(self):
        result_collection = map_concept(self.collection, json_collection, self.skos_manager)
        self.assertIsNotNone(result_collection)
        self.assertEqual(3, len(result_collection.members))
        self.assertEqual(2, len(result_collection.member_of))
        self.assertEqual(1, len(result_collection.labels))
        self.assertEqual(1, len(result_collection.notes))
        self.assertFalse(hasattr(result_collection, 'related_concepts'))

    def test_mapping_matches(self):
        test_json["matches"] = {"exact": ["urn:sample:666"], "broad": ["urn:somewhere:93"]}
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertTrue(hasattr(result_concept, 'matches'))
        self.assertEqual(2, len(result_concept.matches))
        self.assertIn(result_concept.matches[0].uri, ["urn:sample:666", "urn:somewhere:93"])

    def test_mapping_matches_new_concept(self):
        test_json["matches"] = {"exact": ["urn:sample:666"], "broad": ["urn:somewhere:93"]}
        del test_json["id"]
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertTrue(hasattr(result_concept, 'matches'))
        self.assertEqual(2, len(result_concept.matches))
        self.assertIn(result_concept.matches[0].uri, ["urn:sample:666", "urn:somewhere:93"])

    def test_mapping_subordinate_arrays(self):
        test_json["subordinate_arrays"] = [{"id": 19}]
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertTrue(hasattr(result_concept, 'narrower_collections'))
        self.assertEqual(1, len(result_concept.narrower_collections))
        self.assertEqual([c for c in result_concept.narrower_collections][0].concept_id, 19)

    def test_mapping_subordinate_arrays_no_result(self):
        test_json["subordinate_arrays"] = [{"id": 11}]
        result_concept = map_concept(self.concept, test_json, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertTrue(hasattr(result_concept, 'narrower_collections'))
        self.assertEqual(1, len(result_concept.narrower_collections))
        self.assertEqual([c for c in result_concept.narrower_collections][0].concept_id, 11)

    def test_mapping_superordinates(self):
        json_collection["superordinates"] = [{"id": 12}]
        result_collection = map_concept(self.collection, json_collection, self.skos_manager)
        self.assertIsNotNone(result_collection)
        self.assertTrue(hasattr(result_collection, 'broader_concepts'))
        self.assertEqual(1, len(result_collection.broader_concepts))
        self.assertEqual([c for c in result_collection.broader_concepts][0].concept_id, 12)

    def test_mapping_concept_to_collection(self):
        result_collection = map_concept(self.concept, json_collection, self.skos_manager)
        self.assertIsNotNone(result_collection)
        self.assertTrue(hasattr(result_collection, 'members'))
        self.assertFalse(hasattr(result_collection, 'related_concepts'))
        self.assertFalse(hasattr(result_collection, 'narrower_concepts'))
        self.assertFalse(hasattr(result_collection, 'narrower_collections'))

    def test_mapping_collection_to_concept(self):
        result_concept = map_concept(self.collection, test_json, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertFalse(hasattr(result_concept, 'members'))
        self.assertTrue(hasattr(result_concept, 'related_concepts'))
        self.assertTrue(hasattr(result_concept, 'narrower_concepts'))
        self.assertTrue(hasattr(result_concept, 'narrower_collections'))
        self.assertEqual(result_concept.uri, 'urn:x-skosprovider:trees/3')

    def test_mapping_conceptscheme(self):
        result_conceptscheme = map_conceptscheme(self.conceptscheme, test_json_conceptscheme)
        self.assertIsNotNone(result_conceptscheme)
        self.assertEqual(1, len(result_conceptscheme.labels))
        self.assertEqual(1, len(result_conceptscheme.notes))
        self.assertEqual(1, len(result_conceptscheme.sources))

    def test_mapping_html_note(self):
        result_concept = map_concept(self.concept, test_json_html, self.skos_manager)
        self.assertIsNotNone(result_concept)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(2, len(result_concept.broader_concepts))
        self.assertEqual(2, len(result_concept.related_concepts))
        self.assertEqual(1, len(result_concept.member_of))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))
        self.assertEqual(1, len(result_concept.sources))
        self.assertFalse(hasattr(result_concept, 'members'))
        self.assertEqual('HTML', result_concept.notes[0].markup)
        self.assertEqual('HTML', result_concept.sources[0].markup)


def test_map_provider_new_provider_full():
    data = {
        'metadata': {'meta': 'meta'},
        'default_language': 'nl',
        'force_display_language': 'nl-force',
        'id_generation_strategy': 'GUID',
        'subject': ['hidden'],
        'uri_pattern': 'uri-pattern',
        'expand_strategy': 'visit',
        'conceptscheme_uri': 'conceptscheme-uri',
        'id': 'p-id'
    }
    result = mappers.map_provider(data)
    assert result.conceptscheme is not None
    assert result.conceptscheme.uri == 'conceptscheme-uri'
    assert result.id == 'p-id'
    assert result.meta == {
        'atramhasis.force_display_language': 'nl-force',
        'atramhasis.id_generation_strategy': 'GUID',
        'default_language': 'nl',
        'meta': 'meta',
        'subject': ['hidden']
    }
    assert result.default_language == 'nl'
    assert result.force_display_language == 'nl-force'
    assert result.id_generation_strategy is IDGenerationStrategy.GUID
    assert result.subject == ['hidden']
    assert result.uri_pattern == 'uri-pattern'
    assert result.expand_strategy is ExpandStrategy.VISIT


def test_map_provider_new_provider_minimal():
    data = {
        'conceptscheme_uri': 'conceptscheme-uri',
        'uri_pattern': 'uri-pattern',
    }
    result = mappers.map_provider(data)
    assert result.conceptscheme is not None
    assert result.conceptscheme.uri == 'conceptscheme-uri'
    assert result.id is None
    assert result.meta == {
        'atramhasis.force_display_language': None,
        'atramhasis.id_generation_strategy': 'NUMERIC',
        'default_language': None,
        'subject': []
    }
    assert result.default_language is None
    assert result.force_display_language is None
    assert result.id_generation_strategy is IDGenerationStrategy.NUMERIC
    assert result.subject == []
    assert result.uri_pattern == 'uri-pattern'
    assert result.expand_strategy is ExpandStrategy.RECURSE


def test_map_provider_existing():
    data = {
        'metadata': {'meta': 'meta'},
        'default_language': 'nl',
        'force_display_language': 'nl-force',
        'id_generation_strategy': 'GUID',
        'subject': ['hidden'],
        'uri_pattern': 'uri-pattern',
        'expand_strategy': 'visit',
        'id': 'p-id'
    }
    existing = Provider(id='exists')
    result = mappers.map_provider(data, existing)
    assert result is existing
    assert result.conceptscheme is None
    assert result.id == 'exists'
    assert result.meta == {
        'atramhasis.force_display_language': 'nl-force',
        'atramhasis.id_generation_strategy': 'GUID',
        'default_language': 'nl',
        'meta': 'meta',
        'subject': ['hidden']
    }
    assert result.default_language == 'nl'
    assert result.force_display_language == 'nl-force'
    assert result.id_generation_strategy is IDGenerationStrategy.GUID
    assert result.subject == ['hidden']
    assert result.uri_pattern == 'uri-pattern'
    assert result.expand_strategy is ExpandStrategy.VISIT
