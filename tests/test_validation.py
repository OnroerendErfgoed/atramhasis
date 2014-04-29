# -*- coding: utf-8 -*-
import unittest
import colander
from pyramid import testing
from atramhasis.validators import Concept as ConceptSchema

json_concept = {
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


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.concept_schema = ConceptSchema().bind(
            request=testing.DummyRequest()
        )

    def tearDown(self):
        testing.tearDown()

    def test_validation(self):
        error_raised = False
        validated_concept = None
        try:
            validated_concept = self.concept_schema.deserialize(json_concept)
        except colander.Invalid as e:
            error_raised = True
        self.assertFalse(error_raised)
        self.assertIsNotNone(validated_concept)
        self.assertEqual(1, len(validated_concept['labels']))
        self.assertEqual(1, len(validated_concept['notes']))
        self.assertEqual(3, len(validated_concept['narrower']))
        self.assertEqual(1, len(validated_concept['broader']))
        self.assertEqual(1, len(validated_concept['related']))