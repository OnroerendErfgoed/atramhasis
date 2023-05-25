import unittest
from unittest.mock import Mock

import colander
from pyramid import testing
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import LabelType
from sqlalchemy.exc import NoResultFound

from atramhasis import validators
from atramhasis.errors import ValidationError
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.validators import Concept as ConceptSchema
from atramhasis.validators import ConceptScheme as ConceptSchemeSchema
from atramhasis.validators import LanguageTag
from atramhasis.validators import concept_schema_validator
from atramhasis.validators import conceptscheme_schema_validator
from atramhasis.validators import languagetag_validator


class DummySkosManager:
    def get_thing(self, concept_id, conceptscheme_id):
        concept = Concept(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        if concept_id == "2":
            broader_concept = Concept(concept_id="1", conceptscheme_id=conceptscheme_id)
            concept.broader_concepts = {broader_concept}
            return concept
        if concept_id == "7":
            narrower_concept = Concept(concept_id="14", conceptscheme_id=conceptscheme_id)
            concept.narrower_concepts = {narrower_concept}
            return concept
        if concept_id == "666":
            concept = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
            return concept
        if concept_id == "667":
            concept = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
            memberof = Collection(concept_id="60", conceptscheme_id=conceptscheme_id)
            memberofs = set()
            memberofs.add(memberof)
            concept.member_of = memberofs
            return concept
        if concept_id == "62":
            concept = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
            member = Collection(concept_id="666", conceptscheme_id=conceptscheme_id)
            members = set()
            members.add(member)
            concept.members = members
            return concept
        if concept_id == "777":
            if conceptscheme_id != "3":
                raise NoResultFound()
        return concept

    def get_all_label_types(self):
        return [
            LabelType('hiddenLabel', 'A hidden label.'),
            LabelType('altLabel', 'An alternative label.'),
            LabelType('prefLabel', 'A preferred label.'),
        ]


class DummyLanguagesManager:
    def count_languages(self, language_id):
        if language_id in ['af', 'flup']:
            return 0
        else:
            return 1

    def save(self, language):
        return language


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            'skos_manager': DummySkosManager(),
            'languages_manager': DummyLanguagesManager()
        }
        self.provider = Mock(conceptscheme_id=1, metadata={})
        self.concept_schema = ConceptSchema(
            validator=concept_schema_validator
        ).bind(
            request=self.request,
            provider=self.provider,
            validate_id_generation=True,
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
            "narrower": [{"id": "8"}, {"id": "7"}, {"id": "9"}],
            "label": "Belgium",
            "type": "concept",
            "id": "4",
            "broader": [{"id": "2"}],
            "related": [{"id": "5"}],
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
            "member_of": [{"id": "666"}]
        }
        self.json_collection = {
            "id": "0",
            "labels": [{
                "language": "nl-BE",
                "label": "Stijlen en culturen",
                "type": "prefLabel"
            }],
            "type": "collection",
            "label": "Stijlen en culturen",
            "members": [{"id": "61"}, {"id": "60"}],
            "notes": [{
                "note": "een notitie",
                "type": "note",
                "language": "nl"
            }],
            "member_of": [{"id": "666"}]
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
        self.assertRaises(
            ValidationError, self.conceptscheme_schema.deserialize, self.json_conceptscheme
        )

    def test_validation_concept(self):
        validated_concept = self.concept_schema.deserialize(self.json_concept)
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
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)

        self.assertIn(
            {'labels': 'Only one prefLabel per language allowed.'}, e.exception.errors
        )

    def test_max_preflabels_1_en_1_nl(self):
        self.json_concept['labels'].append({
            "label": "B",
            "type": "prefLabel",
            "language": "nl"
        })
        validated_concept = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_concept)

    def test_related_concept_type_collection(self):
        self.json_concept['related'].append({"id": 666})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'related': 'A narrower, broader or related concept should '
                           'always be a concept, not a collection'
            },
            e.exception.errors
        )

    def test_collection_with_related(self):
        # Collections can not have related relations
        self.json_collection['related'] = []
        self.json_collection['related'].append({"id": 2})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {'related': 'Only concepts can have narrower/broader/related relations'},
            e.exception.errors
        )

    def test_narrower_concept_type_collection(self):
        self.json_concept['narrower'].append({"id": 666})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'narrower': 'A narrower, broader or related concept should '
                            'always be a concept, not a collection'
            },
            e.exception.errors
        )
    
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
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {'narrower': 'Only concepts can have narrower/broader/related relations'},
            e.exception.errors
        )

    def test_broader_concept_type_collection(self):
        self.json_concept['broader'].append({"id": 666})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'broader': 'A narrower, broader or related concept should '
                           'always be a concept, not a collection'
            },
            e.exception.errors
        )

    def test_collection_with_broader(self):
        # Collections can not have broader relations
        self.json_collection['broader'] = []
        self.json_collection['broader'].append({"id": 2})
        with self.assertRaises(ValidationError):
            self.concept_schema.deserialize(self.json_collection)

    def test_related_concept_different_conceptscheme(self):
        self.json_concept['related'].append({"id": 777})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'related': 'Concept not found, check concept_id. Please be aware '
                           'members should be within one scheme'
            },
            e.exception.errors
        )

    def test_narrower_concept_different_conceptscheme(self):
        self.json_concept['narrower'].append({"id": 777})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'narrower': 'Concept not found, check concept_id. Please be aware '
                            'members should be within one scheme'
            },
            e.exception.errors
        )

    def test_narrower_concept_to_self(self):
        self.json_concept['narrower'].append({"id": 4})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {'narrower': 'A concept or collection cannot be related to itself'},
            e.exception.errors
        )

    def test_broader_concept_different_conceptscheme(self):
        self.json_concept['broader'].append({"id": 777})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'broader': 'Concept not found, check concept_id. Please be aware '
                           'members should be within one scheme'
             },
            e.exception.errors
        )

    def test_broader_concept_hierarchy(self):
        self.json_concept['broader'].append({"id": 14})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'broader': 'The broader concept of a concept must not itself '
                           'be a narrower concept of the concept being edited.'
            },
            e.exception.errors
        )

    def test_broader_concept_hierarchy_no_narrower(self):
        self.json_concept['broader'].append({"id": 8})
        self.json_concept['narrower'] = []
        validated_concept = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_concept)

    def test_narrower_concept_hierarchy(self):
        self.json_concept['narrower'].append({"id": 1})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'narrower': 'The narrower concept of a concept must not itself '
                            'be a broader concept of the concept being edited.'
            },
            e.exception.errors
        )

    def test_narrower_concept_hierarchy_no_broader(self):
        self.json_concept['narrower'].append({"id": 1})
        self.json_concept['broader'] = []
        validated_concept = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_concept)

    def test_validation_collection(self):
        validated_collection = self.concept_schema.deserialize(self.json_collection)
        self.assertIsNotNone(validated_collection)
        self.assertEqual(2, len(validated_collection['members']))
        self.assertEqual(1, len(validated_collection['labels']))
        self.assertEqual(1, len(validated_collection['notes']))

    def test_member_concept_different_conceptscheme(self):
        self.json_collection['members'].append({"id": 777})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {
                'members': 'Concept not found, check concept_id. Please be aware '
                           'members should be within one scheme'
            },
            e.exception.errors
        )

    def test_label_type(self):
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "en"
        })
        validated_concept = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_concept)

    def test_label_type_invalid(self):
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "testLabelInvalid",
            "language": "en"
        })
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn({'labels': 'Invalid labeltype.'}, e.exception.errors)

    def test_label_language_invalid(self):
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "eng"
        })
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'labels': "Invalid language tag: Unknown code 'eng', "
                          "Missing language tag in 'eng'."
            },
            e.exception.errors
        )

    def test_label_language_missing(self):
        self.json_concept['labels'].append({
            "label": "Belgium",
            "type": "altLabel",
            "language": "af"
        })
        validated_concept = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_concept)

    def test_label_invalid(self):
        self.json_concept['labels'].append({
            "note": "Belgium",
            "type": "altLabel",
            "language": "en"
        })
        with self.assertRaises(colander.Invalid):
            self.concept_schema.deserialize(self.json_concept)

    def test_note_invalid(self):
        self.json_concept['notes'].append({
            "label": "een notitie",
            "type": 5,
            "language": "nl"
        })
        with self.assertRaises(colander.Invalid):
            self.concept_schema.deserialize(self.json_concept)

    def test_memberof_concept_type_collection(self):
        # A Collection/Concept can be a member_of a Collection
        validated_concept = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_concept)

    def test_memberof_concept_type_concept(self):
        # Nothing can be a member_of a Concept
        self.json_concept['member_of'].append({"id": 2})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {'member_of': 'A member_of parent should always be a collection'},
            e.exception.errors
        )

    def test_members_collection_unique(self):
        # A Collection is a Set (every element of the Collection should be unique).
        self.json_collection['members'].append({"id": 61})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {'members': 'All members of a collection should be unique.'},
            e.exception.errors
        )

    def test_concept_members(self):
        # A Concept does not have members.
        self.json_concept['members'] = []
        self.json_concept['members'].append({"id": 2})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {'members': 'Only collections can have members.'}, e.exception.errors
        )

    def test_memberof_concept_hierarchy_simple(self):
        # The hierarchy should not contain loops
        self.json_collection['members'].append({"id": 666})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {
                'member_of': 'The parent member_of collection of a concept must not '
                             'itself be a member of the concept being edited.'
            },
            e.exception.errors
        )

    def test_memberof_concept_hierarchy_deep(self):
        # The hierarchy should not contain loops
        self.json_collection['members'].append({"id": 62})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {
                'member_of': 'The parent member_of collection of a concept must not '
                             'itself be a member of the concept being edited.'
            },
            e.exception.errors
        )

    def test_members_concept_hierarchy_simple(self):
        # The hierarchy should not contain loops
        self.json_collection['member_of'].append({"id": 61})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {
                'members': 'The item of a members collection must not itself be a '
                           'parent of the concept/collection being edited.'
            },
            e.exception.errors
        )

    def test_members_concept_hierarchy_deep(self):
        # The hierarchy should not contain loops
        self.json_collection['member_of'].append({"id": 667})
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {
                'members': 'The item of a members collection must not itself be a '
                           'parent of the concept/collection being edited.'
            },
            e.exception.errors
        )

    def test_min_labels_rule_empty_labels(self):
        self.json_concept['labels'] = []
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn({'labels': 'At least one label is necessary'}, e.exception.errors)

    def test_min_labels_rule_no_labels(self):
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
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(json_concept)
        self.assertIn({'labels': 'At least one label is necessary'}, e.exception.errors)

    def test_concept_matches_rule(self):
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
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(json_concept)
        self.assertIn({'matches': 'Only concepts can have matches'}, e.exception.errors)

    def test_concept_matches_unique_rule(self):
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
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(json_concept)

        self.assertIn(
            {'matches': 'All matches of a concept should be unique.'}, e.exception.errors
        )

    def test_concept_matches_unique_rule_pass(self):
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
        validated_concept = self.concept_schema.deserialize(json_concept)
        self.assertIsNotNone(validated_concept)

    def test_languages_pass(self):
        json_language = {
            "id": "af",
            "name": "Afrikaans"
        }
        validated_language = self.language.deserialize(json_language)
        self.assertIsNotNone(validated_language)

    def test_languages_duplicate(self):
        json_language = {
            "id": "en",
            "name": "English"
        }
        with self.assertRaises(ValidationError) as e:
            self.language.deserialize(json_language)
        self.assertIn({'id': 'Duplicate language tag: en'}, e.exception.errors)

    def test_languages_edit_not_raise_duplicate(self):
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
        validated_language = language.deserialize(json_language)
        self.assertIsNotNone(validated_language)

    def test_languages_invalid(self):
        json_language = {
            "id": "flup",
            "name": "test"
        }
        with self.assertRaises(ValidationError) as e:
            self.language.deserialize(json_language)
        self.assertIn(
            {
                "id": "Invalid language tag: Unknown code 'flup', Missing "
                      "language tag in 'flup'."
            },
            e.exception.errors
        )

    def test_subordinate_arrays(self):
        self.json_concept['subordinate_arrays'] = [{"id": 667}]
        validated_json = self.concept_schema.deserialize(self.json_concept)
        self.assertIsNotNone(validated_json)

    def test_subordinate_arrays_no_concept(self):
        self.json_collection['subordinate_arrays'] = [{"id": 666}]
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {'subordinate_arrays': 'Only concept can have subordinate arrays.'},
            e.exception.errors
        )

    def test_subordinate_arrays_no_collection(self):
        self.json_concept['subordinate_arrays'] = [{"id": 7}]
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {'subordinate_arrays': 'A subordinate array should always be a collection'},
            e.exception.errors
        )

    def test_subordinate_arrays_hierarchy(self):
        self.json_concept['subordinate_arrays'] = [{"id": 666}]
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {
                'subordinate_arrays': 'The subordinate_array collection of a concept must '
                                      'not itself be a parent of the concept being edited.'
            },
            e.exception.errors
        )

    def test_superordinates(self):
        self.json_collection['superordinates'] = [{"id": 7}]
        validated_json = self.concept_schema.deserialize(self.json_collection)
        self.assertIsNotNone(validated_json)

    def test_superordinates_no_concept(self):
        self.json_collection['superordinates'] = [{"id": 666}]
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {'superordinates': 'A superordinate should always be a concept'},
            e.exception.errors
        )

    def test_superordinates_no_collection(self):
        self.json_concept['superordinates'] = [{"id": 7}]
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_concept)
        self.assertIn(
            {'superordinates': 'Only collection can have superordinates.'},
            e.exception.errors
        )

    def test_superordinates_hierarchy(self):
        self.json_collection['superordinates'] = [{"id": 61}]
        with self.assertRaises(ValidationError) as e:
            self.concept_schema.deserialize(self.json_collection)
        self.assertIn(
            {
                'superordinates': 'The superordinates of a collection must not itself '
                                  'be a member of the collection being edited.'
            },
            e.exception.errors
        )

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
        self.assertEqual("een <strong>\nnotitie</strong>", note['note'])

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
        self.assertEqual("Van Daele K. <strong>\n2014</strong>", source['citation'])

    def test_id_generation_manual_no_id(self):
        concept_schema = self.concept_schema.bind(
            request=self.request,
            provider=self.provider,
            validate_id_generation=True,
        )
        self.provider.metadata["atramhasis.id_generation_strategy"] = (
            IDGenerationStrategy.MANUAL
        )
        del self.json_concept["id"]
        with self.assertRaises(ValidationError) as e:
            concept_schema.deserialize(self.json_concept)
        self.assertIn({'id': 'Required for this provider.'}, e.exception.errors)
        concept_schema = self.concept_schema.bind(
            request=self.request,
            provider=self.provider,
            validate_id_generation=False,
        )
        concept_schema.deserialize(self.json_concept)

    def test_id_generation_manual_not_unique(self):
        concept_schema = self.concept_schema.bind(
            request=self.request,
            provider=self.provider,
            validate_id_generation=True,
        )
        self.provider.metadata["atramhasis.id_generation_strategy"] = (
            IDGenerationStrategy.MANUAL
        )
        self.json_concept["id"] = "1"
        with self.assertRaises(ValidationError) as e:
            concept_schema.deserialize(self.json_concept)
        self.assertIn({'id': '1 already exists.'}, e.exception.errors)
        concept_schema = self.concept_schema.bind(
            request=self.request,
            provider=self.provider,
            validate_id_generation=False,
        )
        concept_schema.deserialize(self.json_concept)

    def test_validate_provider(self):
        """
        This looks like it does not validate much, but openapi validates the majority.

        We only need to manually validate what openapi cannot.
        """
        json_data = {'metadata': {}}
        validators.validate_provider_json(json_data)

    def test_validate_provider_forbidden_keys(self):
        forbidden_metadata_keys = (
            'default_language',
            'subject',
            'force_display_language',
            'atramhasis.force_display_language',
            'id_generation_strategy',
            'atramhasis.id_generation_strategy',
        )
        for bad_key in forbidden_metadata_keys:
            json_data = {'metadata': {bad_key: 'value'}}
            with self.assertRaises(ValidationError):
                validators.validate_provider_json(json_data)

    def test_validate_provider_bad_language(self):
        json_data = {'default_language': 'notalanguage'}
        with self.assertRaises(ValidationError):
            validators.validate_provider_json(json_data)
        json_data = {'force_display_language': 'notalanguage'}
        with self.assertRaises(ValidationError):
            validators.validate_provider_json(json_data)

    def test_validate_provider_update_with_wrong_id(self):
        json_data = {'id': 'notanid'}
        with self.assertRaises(ValidationError):
            validators.validate_provider_json(json_data, "test")
