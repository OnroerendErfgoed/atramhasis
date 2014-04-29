# -*- coding: utf-8 -*-
import unittest
import colander
from pyramid import testing
from atramhasis.validators import (
    Concept as ConceptSchema,
    concept_schema_validator
)


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.concept_schema = ConceptSchema(
            validator=concept_schema_validator
        ).bind(
            request=testing.DummyRequest()
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
                      }]
        }

    def tearDown(self):
        testing.tearDown()

    def test_validation(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(self.json_concept)
        except colander.Invalid as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)
        self.assertEqual(1, len(validated_concept['labels']))
        self.assertEqual(1, len(validated_concept['notes']))
        self.assertEqual(3, len(validated_concept['narrower']))
        self.assertEqual(1, len(validated_concept['broader']))
        self.assertEqual(1, len(validated_concept['related']))

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
        except colander.Invalid as e:
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
        except colander.Invalid as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)