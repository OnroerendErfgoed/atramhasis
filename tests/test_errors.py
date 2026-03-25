from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError

from atramhasis.errors import ConceptNotFoundException
from atramhasis.errors import ConceptSchemeNotFoundException
from atramhasis.errors import DbNotFoundException
from atramhasis.errors import LanguageNotFoundException
from atramhasis.errors import SkosRegistryNotFoundException
from atramhasis.errors import ValidationError
from atramhasis.views.exception_views import data_integrity


class TestErrors:
    def test_skos_reg_error(self):
        error = SkosRegistryNotFoundException()
        assert error is not None
        assert "'No SKOS registry found, please check your application setup'" == str(
            error
        )

    def test_conceptsheme_notfound_error(self):
        error = ConceptSchemeNotFoundException("TREES")
        assert error is not None
        assert "'No conceptscheme found with the given id TREES'" == str(error)

    def test_concept_notfound_error(self):
        error = ConceptNotFoundException("1")
        assert error is not None
        assert "'No concept found with the given id 1'" == str(error)

    def test_validation_error(self):
        error = ValidationError("validation failed", {})
        assert error is not None
        assert "'validation failed'" == str(error)

    def test_db_error(self):
        error = DbNotFoundException()
        assert error is not None
        assert "'No database found, please check your application setup'" == str(error)

    def test_language_notfound_exception(self):
        error = LanguageNotFoundException("af")
        assert error is not None
        assert "'No language found with the given id af'" == str(error)


class TestErrorsViews:
    def test_integrity(self):
        error = IntegrityError(orig=MagicMock(), statement="", params={})
        res = data_integrity(error, MagicMock())
        assert {
            "message": "this operation violates the data integrity and could not be executed"
        } == res
