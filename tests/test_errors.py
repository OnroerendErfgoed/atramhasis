import unittest
from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException, \
    ConceptNotFoundException, DbNotFoundException, ValidationError


class TestErrors(unittest.TestCase):
    def test_skos_reg_error(self):
        error = SkosRegistryNotFoundException()
        self.assertIsNotNone(error)
        self.assertEqual("'No SKOS registry found, please check your application setup'", str(error))

    def test_conceptsheme_notfound_error(self):
        error = ConceptSchemeNotFoundException('TREES')
        self.assertIsNotNone(error)
        self.assertEqual("'No conteptscheme found with the given id TREES'", str(error))

    def test_concept_notfound_error(self):
        error = ConceptNotFoundException('1')
        self.assertIsNotNone(error)
        self.assertEqual("'No contept found with the given id 1'", str(error))

    def test_validation_error(self):
        error = ValidationError('validation failed', {})
        self.assertIsNotNone(error)
        self.assertEqual("'validation failed'", str(error))

    def test_db_error(self):
        error = DbNotFoundException()
        self.assertIsNotNone(error)
        self.assertEqual("'No database found, please check your application setup'", str(error))