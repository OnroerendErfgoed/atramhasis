import unittest
from skosprovider_sqlalchemy.models import Concept, Label
from atramhasis.mappers import map_concept

test_json = {
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


class TestMappers(unittest.TestCase):

    def setUp(self):
        self.concept = Concept()
        self.concept.concept_id = 1
        self.concept.conceptscheme_id = 1

    def tearDown(self):
        self.concept = None

    def test_mapping(self):
        result_concept = map_concept(self.concept, test_json)
        self.assertIsNotNone(result_concept)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(1, len(result_concept.broader_concepts))
        self.assertEqual(1, len(result_concept.related_concepts))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))

    def test_mapping_collections_filled(self):
        label = Label(label='test', labeltype_id='altLabel', language_id='nl')
        self.concept.labels.append(label)
        related_concept = Concept(concept_id=6, conceptscheme_id=1)
        self.concept.related_concepts.add(related_concept)
        result_concept = map_concept(self.concept, test_json)
        self.assertEqual(3, len(result_concept.narrower_concepts))
        self.assertEqual(1, len(result_concept.broader_concepts))
        self.assertEqual(1, len(result_concept.related_concepts))
        self.assertEqual(2, len(result_concept.labels))
        self.assertEqual(1, len(result_concept.notes))