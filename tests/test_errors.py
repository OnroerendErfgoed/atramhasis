import unittest
from sqlalchemy.exc import IntegrityError
try:
    from unittest.mock import Mock, MagicMock
except ImportError:
    from mock import Mock, MagicMock  # pragma: no cover
from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException, \
    ConceptNotFoundException, DbNotFoundException, ValidationError, LanguageNotFoundException
from atramhasis.views.exception_views import data_integrity


class TestErrors(unittest.TestCase):
    def test_skos_reg_error(self):
        error = SkosRegistryNotFoundException()
        self.assertIsNotNone(error)
        self.assertEqual("'No SKOS registry found, please check your application setup'", str(error))

    def test_conceptsheme_notfound_error(self):
        error = ConceptSchemeNotFoundException('TREES')
        self.assertIsNotNone(error)
        self.assertEqual("'No conceptscheme found with the given id TREES'", str(error))

    def test_concept_notfound_error(self):
        error = ConceptNotFoundException('1')
        self.assertIsNotNone(error)
        self.assertEqual("'No concept found with the given id 1'", str(error))

    def test_validation_error(self):
        error = ValidationError('validation failed', {})
        self.assertIsNotNone(error)
        self.assertEqual("'validation failed'", str(error))

    def test_db_error(self):
        error = DbNotFoundException()
        self.assertIsNotNone(error)
        self.assertEqual("'No database found, please check your application setup'", str(error))

    def test_language_notfound_exception(self):
        error = LanguageNotFoundException("af")
        self.assertIsNotNone(error)
        self.assertEqual("'No language found with the given id af'", str(error))


class TestErrorsViews(unittest.TestCase):
    def test_integrity(self):
        error = IntegrityError(orig=MagicMock(), statement='', params={})
        res = data_integrity(error, MagicMock())
        self.assertEqual({'message': 'this operation violates the data integrity and could not be executed '}, res)