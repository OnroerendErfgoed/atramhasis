# -*- coding: utf-8 -*-
import unittest

from sqlalchemy.orm.exc import NoResultFound
from atramhasis.errors import ValidationError


try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
import colander
from pyramid import testing
from skosprovider_sqlalchemy.models import Concept, Collection, LabelType, Language
from atramhasis.validators import (
    Concept as ConceptSchema,
    concept_schema_validator
)


def filter_by_mock_concept(concept_id, conceptscheme_id):
    concept = Concept(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
    concept.type = 'concept'
    if concept_id == 2:
        broader_concept = Concept(concept_id=1, conceptscheme_id=conceptscheme_id)
        broader_concepts = set()
        broader_concepts.add(broader_concept)
        concept.broader_concepts = broader_concepts
    if concept_id == 7:
        narrower_concept = Concept(concept_id=14, conceptscheme_id=conceptscheme_id)
        narrower_concepts = set()
        narrower_concepts.add(narrower_concept)
        concept.narrower_concepts = narrower_concepts
    if concept_id == 666:
        concept = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        concept.type = 'collection'
    if concept_id == 667:
        concept = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        concept.type = 'collection'
        memberof = Collection(concept_id=60, conceptscheme_id=conceptscheme_id)
        memberofs = set()
        memberofs.add(memberof)
        concept.member_of = memberofs
    if concept_id == 62:
        concept = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        concept.type = 'collection'
        member = Collection(concept_id=666, conceptscheme_id=conceptscheme_id)
        members = set()
        members.add(member)
        concept.members = members
    if concept_id == 777:
        if conceptscheme_id != 3:
            raise NoResultFound()
    filter_mock = Mock()
    filter_mock.one = Mock(return_value=concept)
    return filter_mock


def list_all_types():
    types = [LabelType('hiddenLabel', 'A hidden label.'), LabelType('altLabel', 'An alternative label.'),
             LabelType('prefLabel', 'A preferred label.')]
    return types


def list_all_languages():
    languages = [Language('nl', 'Dutch'), Language('en', 'English')]
    return languages


def create_query_mock(some_class):
    query_mock = Mock()
    query_mock.filter_by = Mock(side_effect=filter_by_mock_concept)
    if some_class == LabelType:
        query_mock.all = Mock(side_effect=list_all_types)
    if some_class == Language:
        query_mock.all = Mock(side_effect=list_all_languages)
    return query_mock


def db(request):
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_query_mock)
    return session_mock


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.db = db(self.request)
        self.concept_schema = ConceptSchema(
            validator=concept_schema_validator
        ).bind(
            request=self.request,
            conceptscheme_id=1
        )
        self.json_concept = {
            "narrower": [8, 7, 9],
            "label": "Belgium",
            "type": "concept",
            "id": 4,
            "broader": [2],
            "related": [5],
            "labels": [{
                           "label": "Belgium",
                           "type": "prefLabel",
                           "language": "en"
                       }],
            "notes": [{
                          "note": "een notitie",
                          "type": "note",
                          "language": "nl"
                      }],
            "member_of": [666]
        }
        self.json_collection = {
            "id": 0,
            "labels": [{
                           "language": "nl",
                           "label": "Stijlen en culturen",
                           "type": "prefLabel"
                       }],
            "type": "collection",
            "label": "Stijlen en culturen",
            "members": [61, 60],
            "notes": [{
                          "note": "een notitie",
                          "type": "note",
                          "language": "nl"
                      }],
            "member_of": [666]
        }

    def tearDown(self):
        testing.tearDown()

    def test_validation_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)
        self.assertEqual(1, len(validated_concept['labels']))
        self.assertEqual(1, len(validated_concept['notes']))
        self.assertEqual(3, len(validated_concept['narrower']))
        self.assertEqual(1, len(validated_concept['broader']))
        self.assertEqual(1, len(validated_concept['related']))
        self.assertEqual(1, len(validated_concept['member_of']))

    def test_max_preflabels_2_en(self):
        self.json_concept['labels'].append({
            "label": "B",
            "type": "prefLabel",
            "language": "en"
        })
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_max_preflabels_1_en_1_nl(self):
        self.json_concept['labels'].append({
            "label": "B",
            "type": "prefLabel",
            "language": "nl"
        })
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_related_concept_type_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_related_concept_type_collection(self):
        self.json_concept['related'].append(666)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_collection_with_related(self):
        # Collections can not have related relations
        self.json_collection['related'] = []
        self.json_collection['related'].append(2)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_narrower_concept_type_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_narrower_concept_type_collection(self):
        self.json_concept['narrower'].append(666)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_collection_with_narrower(self):
        # Collections can not have narrower relations
        self.json_collection['narrower'] = []
        self.json_collection['narrower'].append(2)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_broader_concept_type_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_broader_concept_type_collection(self):
        self.json_concept['broader'].append(666)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_collection_with_broader(self):
        # Collections can not have broader relations
        self.json_collection['broader'] = []
        self.json_collection['broader'].append(2)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_related_concept_different_conceptscheme(self):
        self.json_concept['related'].append(777)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_narrower_concept_different_conceptscheme(self):
        self.json_concept['narrower'].append(777)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_broader_concept_different_conceptscheme(self):
        self.json_concept['broader'].append(777)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_broader_concept_hierarchy(self):
        self.json_concept['broader'].append(14)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_broader_concept_hierarchy_no_narrower(self):
        self.json_concept['broader'].append(8)
        self.json_concept['narrower'] = []
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_narrower_concept_hierarchy(self):
        self.json_concept['narrower'].append(1)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_narrower_concept_hierarchy_no_broader(self):
        self.json_concept['narrower'].append(1)
        self.json_concept['broader'] = []
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_validation_collection(self):
        error_raised = False
        validated_collection = None
        try:
            validated_collection = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_collection)
        self.assertEqual(2, len(validated_collection['members']))
        self.assertEqual(1, len(validated_collection['labels']))
        self.assertEqual(1, len(validated_collection['notes']))

    def test_member_concept_different_conceptscheme(self):
        error_raised = False
        validated_collection = None
        self.json_collection['members'].append(777)
        try:
            validated_collection = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_collection)

    def test_label_type(self):
        error_raised = False
        validated_concept = None
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "en"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_label_type_invalid(self):
        error_raised = False
        validated_concept = None
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "testLabelInvalid",
            "language": "en"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_label_language_invalid(self):
        error_raised = False
        validated_concept = None
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "en-FR"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_label_invalid(self):
        error_raised = False
        validated_concept = None
        self.json_concept['labels'].append({
            "note": "Belgium",
            "type": "altLabel",
            "language": "en"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except colander.Invalid as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_note_invalid(self):
        error_raised = False
        validated_concept = None
        self.json_concept['notes'].append({
            "label": "een notitie",
            "type": "note",
            "language": "nl"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except colander.Invalid as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_memberof_concept_type_collection(self):
        #A Collection/Concept can be a member_of a Collection
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_memberof_concept_type_concept(self):
        # Nothing can be a member_of a Concept
        self.json_concept['member_of'].append(2)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_members_collection_unique(self):
        # A Collection is a Set (every element of the Collection should be unique).
        self.json_collection['members'].append(61)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_concept_members(self):
        # A Concept does not have members.
        self.json_concept['members'] = []
        self.json_concept['members'].append(2)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_memberof_concept_hierarchy_simple(self):
        # The hierarchy should not contain loops
        self.json_collection['members'].append(666)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_memberof_concept_hierarchy_deep(self):
        # The hierarchy should not contain loops
        self.json_collection['members'].append(62)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_members_concept_hierarchy_simple(self):
        # The hierarchy should not contain loops
        self.json_collection['member_of'].append(61)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_members_concept_hierarchy_deep(self):
        # The hierarchy should not contain loops
        self.json_collection['member_of'].append(667)
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)