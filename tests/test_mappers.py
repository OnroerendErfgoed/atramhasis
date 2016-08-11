# -*- coding: utf-8 -*-
import unittest

from sqlalchemy.orm.exc import NoResultFound
from atramhasis.data.datamanagers import SkosManager


try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
from pyramid import testing
from skosprovider_sqlalchemy.models import (
    Thing,
    ConceptScheme,
    Concept,
    Collection,
    Label,
    Source,
    MatchType,
    Match,
)
from atramhasis.mappers import map_concept, map_conceptscheme

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
test_json_html={
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



def filter_by_mock_concept(concept_id, conceptscheme_id):
    if concept_id in (7, 11, 12):
        raise NoResultFound()
    filter_mock = Mock()
    if concept_id in (999, 19):
        thing = Collection(id=concept_id, concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        thing.type = 'collection'
    else:
        thing = Concept(id=concept_id, concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        thing.type = 'concept'
    filter_mock.one = Mock(return_value=thing)
    return filter_mock


def filter_by_mock_matchtype(name):
    filter_mock = Mock()
    if name in ['broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch', 'relatedMatch']:
        matchtype = MatchType(name, 'test')
    else:
        raise NoResultFound()
    filter_mock.one = Mock(return_value=matchtype)
    return filter_mock


def filter_by_mock_match(uri, matchtype_id, concept_id):
    filter_mock = Mock()
    if concept_id == -1:
        raise NoResultFound()
    else:
        match = Match()
        match.uri = uri
        match.concept_id = concept_id
        if matchtype_id in ['broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch', 'relatedMatch']:
            match.matchtype = MatchType(matchtype_id, 'test')
        else:
            raise NoResultFound()
    filter_mock.one = Mock(return_value=match)
    return filter_mock


def create_query_mock(some_class):
    query_mock = Mock()
    if some_class in [Thing, Concept, Collection]:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_concept)
    elif some_class == MatchType:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_matchtype)
    elif some_class == Match:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_match)
    return query_mock


def session_maker():
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_query_mock)
    return session_mock


class TestMappers(unittest.TestCase):
    def setUp(self):
        self.skos_manager = SkosManager(session_maker())
        self.concept = Concept()
        self.concept.concept_id = 1
        self.concept.conceptscheme_id = 1
        self.collection = Collection()
        self.collection.concept_id = 0
        self.collection.conceptscheme_id = 1
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
