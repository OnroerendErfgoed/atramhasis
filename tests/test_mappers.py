# -*- coding: utf-8 -*-
import unittest

from sqlalchemy.orm.exc import NoResultFound


try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
from pyramid import testing
from skosprovider_sqlalchemy.models import Concept, Label, Collection
from atramhasis.mappers import map_concept

test_json = {
    "narrower": [8, 7, 9],
    "label": "Belgium",
    "type": "concept",
    "id": 4,
    "broader": [2, 11],
    "related": [5, 12],
    "member_of": [999],
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
    "members": [61, 60, 12],
    "member_of": [999, 7],
    "notes": [{
                  "note": "een notitie",
                  "type": "note",
                  "language": "nl"
              }]
}


def filter_by_mock_concept(concept_id, conceptscheme_id):
    if concept_id in (7, 11, 12):
        raise NoResultFound()
    filter_mock = Mock()
    if concept_id == 999:
        thing = Collection(id=concept_id, concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        thing.type = 'collection'
    else:
        thing = Concept(id=concept_id, concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        thing.type = 'concept'
    filter_mock.one = Mock(return_value=thing)
    return filter_mock


def create_query_mock(some_class):
    query_mock = Mock()
    query_mock.filter_by = Mock(side_effect=filter_by_mock_concept)
    return query_mock


def db(request):
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_query_mock)
    return session_mock


class TestMappers(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.db = db(self.request)
        self.concept = Concept()
        self.concept.concept_id = 1
        self.concept.conceptscheme_id = 1
        self.collection = Collection()
        self.collection.concept_id = 0
        self.collection.conceptscheme_id = 1

    def tearDown(self):
        self.concept = None

    def test_mapping(self):
        result_concept = map_concept(self.concept, test_json, self.request.db)
        self.assertIsNotNone(result_concept)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(2, len(result_concept.broader_concepts))
        self.assertEqual(2, len(result_concept.related_concepts))
        self.assertEqual(1, len(result_concept.member_of))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))
        self.assertFalse(hasattr(result_concept, 'members'))

    def test_mapping_collections_filled(self):
        label = Label(label='test', labeltype_id='altLabel', language_id='nl')
        self.concept.labels.append(label)
        related_concept = Concept(concept_id=6, conceptscheme_id=1)
        self.concept.related_concepts.add(related_concept)
        result_concept = map_concept(self.concept, test_json, self.request.db)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(2, len(result_concept.broader_concepts))
        self.assertEqual(2, len(result_concept.related_concepts))
        self.assertEqual(1, len(result_concept.member_of))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))

    def test_mapping_check_db_lookup(self):
        result_concept = map_concept(self.concept, test_json, self.request.db)
        for narrower_concept in result_concept.narrower_concepts:
            self.assertIsNotNone(narrower_concept)
            if narrower_concept.concept_id == 7:
                self.assertIsNone(narrower_concept.id)

    def test_mapping_check_db_lookup_member_of(self):
        result_concept = map_concept(self.concept, test_json, self.request.db)
        for member_of in result_concept.member_of:
            self.assertIsNotNone(member_of)
            if member_of.concept_id == 7:
                self.assertIsNone(member_of.id)

    def test_mapping_collection(self):
        result_collection = map_concept(self.collection, json_collection, self.request.db)
        self.assertIsNotNone(result_collection)
        self.assertEqual(3, len(result_collection.members))
        self.assertEqual(2, len(result_collection.member_of))
        self.assertEqual(1, len(result_collection.labels))
        self.assertEqual(1, len(result_collection.notes))
        self.assertFalse(hasattr(result_collection, 'related_concepts'))