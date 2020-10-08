# -*- coding: utf-8 -*-
import unittest

from sqlalchemy.orm.exc import NoResultFound
from atramhasis.data.datamanagers import SkosManager, LanguagesManager, ConceptSchemeManager
from atramhasis.errors import ValidationError

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
import colander
from pyramid import testing
from skosprovider_sqlalchemy.models import Concept, Collection, LabelType, Language, Thing
from atramhasis.validators import (
    ConceptScheme as ConceptSchemeSchema,
    Concept as ConceptSchema,
    concept_schema_validator,
    conceptscheme_schema_validator,
    LanguageTag, languagetag_validator)


def filter_by_mock_language(id):
    filter_mock = Mock()
    if id in ['af', 'flup']:
        filter_mock.count = Mock(return_value=0)
    else:
        filter_mock.count = Mock(return_value=1)
    return filter_mock


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
    if some_class in [Concept, Collection, Thing]:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_concept)
    elif some_class == Language:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_language)
    if some_class == LabelType:
        query_mock.all = Mock(side_effect=list_all_types)
    if some_class == Language:
        query_mock.all = Mock(side_effect=list_all_languages)
    return query_mock


def session_maker():
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_query_mock)
    return session_mock


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        session = session_maker()
        self.request.data_managers = {'skos_manager': SkosManager(session),
                                      'conceptscheme_manager': ConceptSchemeManager(session),
                                      'languages_manager': LanguagesManager(session)}
        self.concept_schema = ConceptSchema(
            validator=concept_schema_validator
        ).bind(
            request=self.request,
            conceptscheme_id=1
        )
        self.language = LanguageTag(
            validator=languagetag_validator
        ).bind(
            request=self.request,
            new=True
        )
        self.conceptscheme_schema = ConceptSchemeSchema(
            validator=conceptscheme_schema_validator
        ).bind(
            request=self.request
        )
        self.json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "label": "Belgium",
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
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
            "sources": [{
                "citation": "Van Daele K. 2014"
            }],
            "member_of": [{"id": 666}]
        }
        self.json_collection = {
            "id": 0,
            "labels": [{
                "language": "nl-BE",
                "label": "Stijlen en culturen",
                "type": "prefLabel"
            }],
            "type": "collection",
            "label": "Stijlen en culturen",
            "members": [{"id": 61}, {"id": 60}],
            "notes": [{
                "note": "een notitie",
                "type": "note",
                "language": "nl"
            }],
            "member_of": [{"id": 666}]
        }
        self.json_conceptscheme = {
            "labels": [{
                "language": "nl-BE",
                "label": "Stijlen en culturen",
                "type": "prefLabel"
            }],
            "label": "Stijlen en culturen",
            "notes": [{
                "note": "een notitie",
                "type": "note",
                "language": "nl"
            }],
            "sources": [{
                "citation": "Van Daele K. 2014"
            }]
        }

    def tearDown(self):
        testing.tearDown()

    def test_validation_conceptscheme(self):
        validated_conceptscheme = self.conceptscheme_schema.deserialize(self.json_conceptscheme)
        self.assertIsNotNone(validated_conceptscheme)
        self.assertEqual(1, len(validated_conceptscheme['labels']))
        self.assertEqual(1, len(validated_conceptscheme['notes']))
        self.assertEqual(1, len(validated_conceptscheme['sources']))

    def test_invalid_conceptscheme(self):
        self.json_conceptscheme.pop('labels')
        self.assertRaises(ValidationError, self.conceptscheme_schema.deserialize, self.json_conceptscheme)

    def test_validation_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)
        self.assertEqual(1, len(validated_concept['labels']))
        self.assertEqual(1, len(validated_concept['notes']))
        self.assertEqual(1, len(validated_concept['sources']))
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
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'labels': 'Only one prefLabel per language allowed.'}, error.errors)

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
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_related_concept_type_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_related_concept_type_collection(self):
        self.json_concept['related'].append({"id": 666})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'related': 'A narrower, broader or related concept'
                                  ' should always be a concept, not a collection'}, error.errors)

    def test_collection_with_related(self):
        # Collections can not have related relations
        self.json_collection['related'] = []
        self.json_collection['related'].append({"id": 2})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'related': 'Only concepts can have narrower/broader/related relations'}, error.errors)

    def test_narrower_concept_type_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_narrower_concept_type_collection(self):
        self.json_concept['narrower'].append({"id": 666})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'narrower': 'A narrower, broader or related concept'
                                   ' should always be a concept, not a collection'}, error.errors)
    
    def test_infer_concept_relations(self):
        self.json_concept['infer_concept_relations'] = True
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'infer_concept_relations': "'infer_concept_relations' can only "
                                           "be set for collections."
            },
            e.exception.errors
        )
        self.json_collection['infer_concept_relations'] = True
        self.concept_schema.deserialize(self.json_collection)

    def test_collection_with_narrower(self):
        # Collections can not have narrower relations
        self.json_collection['narrower'] = []
        self.json_collection['narrower'].append({"id": 2})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'narrower': 'Only concepts can have narrower/broader/related relations'}, error.errors)

    def test_broader_concept_type_concept(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_broader_concept_type_collection(self):
        self.json_concept['broader'].append({"id": 666})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'broader': 'A narrower, broader or related concept should always be'
                                  ' a concept, not a collection'}, error.errors)

    def test_collection_with_broader(self):
        # Collections can not have broader relations
        self.json_collection['broader'] = []
        self.json_collection['broader'].append({"id": 2})
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError:
            error_raised = True
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)

    def test_related_concept_different_conceptscheme(self):
        self.json_concept['related'].append({"id": 777})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'related': 'Concept not found, check concept_id. Please be aware members'
                                  ' should be within one scheme'}, error.errors)

    def test_narrower_concept_different_conceptscheme(self):
        self.json_concept['narrower'].append({"id": 777})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'narrower': 'Concept not found, check concept_id. Please be aware members'
                                   ' should be within one scheme'}, error.errors)

    def test_narrower_concept_to_self(self):
        self.json_concept['narrower'].append({"id": 4})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'narrower': 'A concept or collection cannot be related to itself'}, error.errors)

    def test_broader_concept_different_conceptscheme(self):
        self.json_concept['broader'].append({"id": 777})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'broader': 'Concept not found, check concept_id. Please be aware members'
                                  ' should be within one scheme'}, error.errors)

    def test_broader_concept_hierarchy(self):
        self.json_concept['broader'].append({"id": 14})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'broader': 'The broader concept of a concept must not itself '
                                  'be a narrower concept of the concept being edited.'}, error.errors)

    def test_broader_concept_hierarchy_no_narrower(self):
        self.json_concept['broader'].append({"id": 8})
        self.json_concept['narrower'] = []
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_narrower_concept_hierarchy(self):
        self.json_concept['narrower'].append({"id": 1})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'narrower': 'The narrower concept of a concept must not itself '
                                   'be a broader concept of the concept being edited.'}, error.errors)

    def test_narrower_concept_hierarchy_no_broader(self):
        self.json_concept['narrower'].append({"id": 1})
        self.json_concept['broader'] = []
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
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
        error = None
        validated_collection = None
        self.json_collection['members'].append({"id": 777})
        try:
            validated_collection = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_collection)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'members': 'Concept not found, check concept_id. Please be aware members'
                                  ' should be within one scheme'}, error.errors)

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
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_label_type_invalid(self):
        error_raised = False
        error = None
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
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'labels': 'Invalid labeltype.'}, error.errors)

    def test_label_language_invalid(self):
        error_raised = False
        error = None
        validated_concept = None
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "eng"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'labels': 'Invalid language tag: Unknown code \'eng\', Missing language tag in \'eng\'.'},
                      error.errors)

    def test_label_language_missing(self):
        error_raised = False
        validated_concept = None
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "af"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_label_invalid(self):
        error_raised = False
        error = None
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
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, colander.Invalid))

    def test_note_invalid(self):
        error_raised = False
        error = None
        validated_concept = None
        self.json_concept['notes'].append({
            "label": "een notitie",
            "type": 5,
            "language": "nl"
        })
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except colander.Invalid as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, colander.Invalid))

    def test_memberof_concept_type_collection(self):
        # A Collection/Concept can be a member_of a Collection
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_memberof_concept_type_concept(self):
        # Nothing can be a member_of a Concept
        self.json_concept['member_of'].append({"id": 2})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'member_of': 'A member_of parent should always be a collection'}, error.errors)

    def test_members_collection_unique(self):
        # A Collection is a Set (every element of the Collection should be unique).
        self.json_collection['members'].append({"id": 61})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'members': 'All members of a collection should be unique.'}, error.errors)

    def test_concept_members(self):
        # A Concept does not have members.
        self.json_concept['members'] = []
        self.json_concept['members'].append({"id": 2})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'members': 'Only collections can have members.'}, error.errors)

    def test_memberof_concept_hierarchy_simple(self):
        # The hierarchy should not contain loops
        self.json_collection['members'].append({"id": 666})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'member_of': 'The parent member_of collection of a concept must not itself'
                                    ' be a member of the concept being edited.'}, error.errors)

    def test_memberof_concept_hierarchy_deep(self):
        # The hierarchy should not contain loops
        self.json_collection['members'].append({"id": 62})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'member_of': 'The parent member_of collection of a concept must not itself'
                                    ' be a member of the concept being edited.'}, error.errors)

    def test_members_concept_hierarchy_simple(self):
        # The hierarchy should not contain loops
        self.json_collection['member_of'].append({"id": 61})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'members': 'The item of a members collection must not itself be a parent of'
                                  ' the concept/collection being edited.'}, error.errors)

    def test_members_concept_hierarchy_deep(self):
        # The hierarchy should not contain loops
        self.json_collection['member_of'].append({"id": 667})
        error_raised = False
        error = None
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'members': 'The item of a members collection must not itself be a parent of'
                                  ' the concept/collection being edited.'}, error.errors)

    def test_min_labels_rule(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_min_labels_rule_empty_labels(self):
        error_raised = False
        validated_concept = None
        self.json_concept['labels'] = []
        error = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertIsNotNone(error)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'labels': 'At least one label is necessary'}, error.errors)

    def test_min_labels_rule_no_labels(self):
        error_raised = False
        validated_concept = None
        json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
            "notes": [{
                "note": "een notitie",
                "type": "note",
                "language": "nl"
            }],
            "member_of": [{"id": 666}]
        }
        error = None
        try:
            validated_concept = self.concept_schema.deserialize(json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertIsNotNone(error)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'labels': 'At least one label is necessary'}, error.errors)

    def test_concept_matches_rule(self):
        error_raised = False
        validated_concept = None
        json_concept = {
            "type": "collection",
            "labels": [{
                "language": "nl",
                "label": "Stijlen en culturen",
                "type": "prefLabel"
            }],
            "id": 4,
            "members": [{"id": 666}],
            "matches": {"exactMatch": ["urn:sample:666"], "broadMatch": ["urn:somewhere:93"]}
        }
        error = None
        try:
            validated_concept = self.concept_schema.deserialize(json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertIsNotNone(error)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'matches': 'Only concepts can have matches'}, error.errors)

    def test_concept_matches_unique_rule(self):
        error_raised = False
        validated_concept = None
        json_concept = {
            "type": "concept",
            "labels": [{
                "language": "nl",
                "label": "Stijlen en culturen",
                "type": "prefLabel"
            }],
            "id": 4,
            "member_of": [{"id": 666}],
            "matches": {"exact": ["urn:sample:666"], "broad": ["urn:sample:666"]}
        }
        error = None
        try:
            validated_concept = self.concept_schema.deserialize(json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_concept)
        self.assertIsNotNone(error)
        self.assertTrue(isinstance(error, ValidationError))
        self.assertIn({'matches': 'All matches of a concept should be unique.'}, error.errors)

    def test_concept_matches_unique_rule_pass(self):
        error_raised = False
        validated_concept = None
        json_concept = {
            "type": "concept",
            "labels": [{
                "language": "nl",
                "label": "Stijlen en culturen",
                "type": "prefLabel"
            }],
            "id": 4,
            "member_of": [{"id": 666}],
            "matches": {"exactMatch": ["urn:sample:666"], "broadMatch": ["urn:sample:93"]}
        }
        try:
            validated_concept = self.concept_schema.deserialize(json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)

    def test_languages_pass(self):
        error_raised = False
        validated_language = None
        json_language = {
            "id": "af",
            "name": "Afrikaans"
        }
        try:
            validated_language = self.language.deserialize(json_language)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_language)

    def test_languages_duplicate(self):
        error_raised = False
        validated_language = None
        json_language = {
            "id": "en",
            "name": "English"
        }
        error = None
        try:
            validated_language = self.language.deserialize(json_language)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_language)
        self.assertIsNotNone(error)
        self.assertIn({'id': 'Duplicate language tag: en'}, error.errors)

    def test_languages_edit_not_raise_duplicate(self):
        error_raised = False
        validated_language = None
        json_language = {
            "id": "en",
            "name": "English"
        }
        language = LanguageTag(
            validator=languagetag_validator
        ).bind(
            request=self.request,
            new=False
        )
        try:
            validated_language = language.deserialize(json_language)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_language)

    def test_languages_invalid(self):
        error_raised = False
        validated_language = None
        json_language = {
            "id": "flup",
            "name": "test"
        }
        error = None
        try:
            validated_language = self.language.deserialize(json_language)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_language)
        self.assertIsNotNone(error)
        self.assertIn({"id": "Invalid language tag: Unknown code 'flup', Missing language tag in 'flup'."},
                      error.errors)

    def test_subordinate_arrays(self):
        error_raised = False
        validated_json = None
        self.json_concept['subordinate_arrays'] = [{"id": 667}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_concept)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_json)

    def test_subordinate_arrays_no_concept(self):
        error_raised = False
        validated_json = None
        error = None
        self.json_collection['subordinate_arrays'] = [{"id": 666}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_json)
        self.assertIsNotNone(error)
        self.assertIn({'subordinate_arrays': 'Only concept can have subordinate arrays.'}, error.errors)

    def test_subordinate_arrays_no_collection(self):
        error_raised = False
        validated_json = None
        error = None
        self.json_concept['subordinate_arrays'] = [{"id": 7}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_json)
        self.assertIsNotNone(error)
        self.assertIn({'subordinate_arrays': 'A subordinate array should always be a collection'}, error.errors)

    def test_subordinate_arrays_hierarchy(self):
        error_raised = False
        validated_json = None
        error = None
        self.json_concept['subordinate_arrays'] = [{"id": 666}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_json)
        self.assertIsNotNone(error)
        self.assertIn({
            'subordinate_arrays': 'The subordinate_array collection of a concept must not itself be a parent of the concept being edited.'},
            error.errors)

    def test_superordinates(self):
        error_raised = False
        validated_json = None
        self.json_collection['superordinates'] = [{"id": 7}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_collection)
        except ValidationError:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_json)

    def test_superordinates_no_concept(self):
        error_raised = False
        validated_json = None
        error = None
        self.json_collection['superordinates'] = [{"id": 666}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_json)
        self.assertIsNotNone(error)
        self.assertIn({'superordinates': 'A superordinate should always be a concept'}, error.errors)

    def test_superordinates_no_collection(self):
        error_raised = False
        validated_json = None
        error = None
        self.json_concept['superordinates'] = [{"id": 7}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_concept)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_json)
        self.assertIsNotNone(error)
        self.assertIn({'superordinates': 'Only collection can have superordinates.'}, error.errors)

    def test_superordinates_hierarchy(self):
        error_raised = False
        validated_json = None
        error = None
        self.json_collection['superordinates'] = [{"id": 61}]
        try:
            validated_json = self.concept_schema.deserialize(self.json_collection)
        except ValidationError as e:
            error_raised = True
            error = e
        self.assertTrue(error_raised)
        self.assertIsNone(validated_json)
        self.assertIsNotNone(error)
        self.assertIn({
            'superordinates': 'The superordinates of a collection must not itself be a member of the collection being edited.'},
            error.errors)

    def test_html_in_notes(self):
        json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "label": "Belgium",
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
            "labels": [{
                "label": "Belgium",
                "type": "prefLabel",
                "language": "en"
            }],
            "notes": [{
                "note": "een <strong><h2>notitie</h2></strong>",
                "type": "note",
                "language": "nl"
            }],
            "sources": [{
                "citation": "Van Daele K. 2014"
            }],
            "member_of": [{"id": 666}]
        }
        validated_json = self.concept_schema.deserialize(json_concept)
        note = validated_json['notes'][0]
        self.assertEqual("een <strong>notitie</strong>", note['note'])

    def test_html_in_sources(self):
        json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "label": "Belgium",
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
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
            "sources": [{
                "citation": "Van Daele K. <strong><h2>2014</h2></strong>"
            }],
            "member_of": [{"id": 666}]
        }
        validated_json = self.concept_schema.deserialize(json_concept)
        source = validated_json['sources'][0]
        self.assertEqual("Van Daele K. <strong>2014</strong>", source['citation'])
