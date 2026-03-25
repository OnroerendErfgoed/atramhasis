import logging
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from pyramid.response import Response
from testfixtures import LogCapture

from atramhasis.audit import _origin_from_response
from atramhasis.audit import audit

log = logging.getLogger("")


cs_mock = MagicMock()
cs_mock.get_metadata = Mock(return_value={"subject": ["external"]})


class RecordingManager:
    def __init__(self):
        self.saved_objects = []

    def save(self, db_object):
        self.saved_objects.append(db_object)


class DummyParent:
    def __init__(self):
        self.request = MagicMock()

    @audit
    def dummy(self):
        return None

    @audit
    def dummy_with_response(self):
        return Response(content_type="application/rdf+xml")


def check_audit(audit_manager, nr, origin, type_id_list):
    assert nr == len(audit_manager.saved_objects)
    assert origin == audit_manager.saved_objects[nr - 1].origin
    for type_id in type_id_list:
        assert "1" == getattr(audit_manager.saved_objects[nr - 1], type_id)


@pytest.fixture()
def audit_manager():
    return RecordingManager()


@pytest.fixture()
def dummy_parent(audit_manager):
    parent = DummyParent()
    parent.request.data_managers = {"audit_manager": audit_manager}
    return parent


class TestAudit:
    def test_audit_rest(self, audit_manager, dummy_parent):
        dummy_parent.request.url = "https://host/conceptschemes/STYLES"
        dummy_parent.request.accept = ["application/json"]
        dummy_parent.request.matchdict = {"scheme_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 1, "REST", ["conceptscheme_id"])
        dummy_parent.request.matchdict = {"scheme_id": "1", "c_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 2, "REST", ["conceptscheme_id", "concept_id"])

    def test_audit_html(self, audit_manager, dummy_parent):
        dummy_parent.request.url = "https://host/conceptschemes/STYLES"
        dummy_parent.request.accept = ["text/html"]
        dummy_parent.request.matchdict = {"scheme_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 1, "HTML", ["conceptscheme_id"])
        dummy_parent.request.matchdict = {"scheme_id": "1", "c_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 2, "HTML", ["conceptscheme_id", "concept_id"])

    def test_audit_rdf_xml(self, audit_manager, dummy_parent):
        dummy_parent.request.matchdict = {"scheme_id": "1"}
        dummy_parent.dummy_with_response()
        check_audit(audit_manager, 1, "RDF", ["conceptscheme_id"])
        dummy_parent.request.matchdict = {"scheme_id": "1", "c_id": "1"}
        dummy_parent.dummy_with_response()
        check_audit(audit_manager, 2, "RDF", ["conceptscheme_id", "concept_id"])

    def test_audit_csv(self, audit_manager, dummy_parent):
        dummy_parent.request.url = "https://host/conceptschemes/STYLES.csv"
        dummy_parent.request.accept = "text/csv"
        dummy_parent.request.matchdict = {"scheme_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 1, "CSV", ["conceptscheme_id"])
        dummy_parent.request.matchdict = {"scheme_id": "1", "c_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 2, "CSV", ["conceptscheme_id", "concept_id"])

    def test_audit_other(self, audit_manager, dummy_parent):
        dummy_parent.request.url = "https://host/conceptschemes/STYLES"
        dummy_parent.request.accept = ["application/octet-stream"]
        dummy_parent.request.matchdict = {"scheme_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 1, None, ["conceptscheme_id"])
        dummy_parent.request.matchdict = {"scheme_id": "1", "c_id": "1"}
        dummy_parent.dummy()
        check_audit(audit_manager, 2, None, ["conceptscheme_id", "concept_id"])

    def test_audit_do_not_record_external(self, audit_manager, dummy_parent):
        dummy_parent.request.url = "https://host/conceptschemes/EXT"
        dummy_parent.request.accept = ["application/octet-stream"]
        dummy_parent.request.matchdict = {"scheme_id": "1"}
        dummy_parent.request.skos_registry.get_provider = Mock(return_value=cs_mock)
        dummy_parent.dummy()
        assert 0 == len(audit_manager.saved_objects)
        dummy_parent.request.matchdict = {"scheme_id": "1", "c_id": "1"}
        dummy_parent.dummy()
        assert 0 == len(audit_manager.saved_objects)

    def test_invalid_use(self, dummy_parent):
        with LogCapture() as logs:
            dummy_parent.request.url = "https://host/conceptschemes/STYLES"
            dummy_parent.request.accept = ["application/json"]
            dummy_parent.request.matchdict = {"invalid_parameter_id": "1"}
            dummy_parent.dummy()
        assert (
            "Misuse of the audit decorator. The url must at least contain a {scheme_id} parameter"
            in str(logs)
        )

    def test_origin_from_response_None(self):
        res = Response(content_type="application/octet-stream")
        assert _origin_from_response(res) is None
