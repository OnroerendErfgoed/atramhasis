import logging
import unittest
from unittest.mock import MagicMock
from unittest.mock import Mock

from pyramid.response import Response
from testfixtures import LogCapture

from atramhasis.audit import _origin_from_response
from atramhasis.audit import audit

log = logging.getLogger('')


cs_mock = MagicMock()
cs_mock.get_metadata = Mock(return_value={'subject': ['external']})


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
        return Response(content_type='application/rdf+xml')


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.audit_manager = RecordingManager()
        self.dummy_parent = DummyParent()
        self.dummy_parent.request.data_managers = {
            'audit_manager': self.audit_manager
        }

    def tearDown(self):
        pass

    def _check(self, nr, origin, type_id_list):
        self.assertEqual(nr, len(self.audit_manager.saved_objects))
        self.assertEqual(origin, self.audit_manager.saved_objects[nr - 1].origin)
        for type_id in type_id_list:
            self.assertEqual('1', getattr(self.audit_manager.saved_objects[nr - 1], type_id))

    def test_audit_rest(self):
        self.dummy_parent.request.url = "http://host/conceptschemes/STYLES"
        self.dummy_parent.request.accept = ['application/json']
        self.dummy_parent.request.matchdict = {'scheme_id': '1'}
        self.dummy_parent.dummy()
        self._check(1, 'REST', ['conceptscheme_id'])
        self.dummy_parent.request.matchdict = {'scheme_id': '1', 'c_id': '1'}
        self.dummy_parent.dummy()
        self._check(2, 'REST', ['conceptscheme_id', 'concept_id'])

    def test_audit_html(self):
        self.dummy_parent.request.url = "http://host/conceptschemes/STYLES"
        self.dummy_parent.request.accept = ['text/html']
        self.dummy_parent.request.matchdict = {'scheme_id': '1'}
        self.dummy_parent.dummy()
        self._check(1, 'HTML', ['conceptscheme_id'])
        self.dummy_parent.request.matchdict = {'scheme_id': '1', 'c_id': '1'}
        self.dummy_parent.dummy()
        self._check(2, 'HTML', ['conceptscheme_id', 'concept_id'])

    def test_audit_rdf_xml(self):
        self.dummy_parent.request.matchdict = {'scheme_id': '1'}
        self.dummy_parent.dummy_with_response()
        self._check(1, 'RDF', ['conceptscheme_id'])
        self.dummy_parent.request.matchdict = {'scheme_id': '1', 'c_id': '1'}
        self.dummy_parent.dummy_with_response()
        self._check(2, 'RDF', ['conceptscheme_id', 'concept_id'])

    def test_audit_csv(self):
        self.dummy_parent.request.url = "http://host/conceptschemes/STYLES.csv"
        self.dummy_parent.request.accept = "text/csv"
        self.dummy_parent.request.matchdict = {'scheme_id': '1'}
        self.dummy_parent.dummy()
        self._check(1, 'CSV', ['conceptscheme_id'])
        self.dummy_parent.request.matchdict = {'scheme_id': '1', 'c_id': '1'}
        self.dummy_parent.dummy()
        self._check(2, 'CSV', ['conceptscheme_id', 'concept_id'])

    def test_audit_other(self):
        self.dummy_parent.request.url = "http://host/conceptschemes/STYLES"
        self.dummy_parent.request.accept = ['application/octet-stream']
        self.dummy_parent.request.matchdict = {'scheme_id': '1'}
        self.dummy_parent.dummy()
        self._check(1, None, ['conceptscheme_id'])
        self.dummy_parent.request.matchdict = {'scheme_id': '1', 'c_id': '1'}
        self.dummy_parent.dummy()
        self._check(2, None, ['conceptscheme_id', 'concept_id'])

    def test_audit_do_not_record_external(self):
        self.dummy_parent.request.url = "http://host/conceptschemes/EXT"
        self.dummy_parent.request.accept = ['application/octet-stream']
        self.dummy_parent.request.matchdict = {'scheme_id': '1'}
        self.dummy_parent.request.skos_registry.get_provider = Mock(return_value=cs_mock)
        self.dummy_parent.dummy()
        self.assertEqual(0, len(self.audit_manager.saved_objects))
        self.dummy_parent.request.matchdict = {'scheme_id': '1', 'c_id': '1'}
        self.dummy_parent.dummy()
        self.assertEqual(0, len(self.audit_manager.saved_objects))

    def test_invalid_use(self):
        with LogCapture() as logs:
            self.dummy_parent.request.url = "http://host/conceptschemes/STYLES"
            self.dummy_parent.request.accept = ['application/json']
            self.dummy_parent.request.matchdict = {'invalid_parameter_id': '1'}
            self.dummy_parent.dummy()
        self.assertIn('Misuse of the audit decorator. The url must at least contain a {scheme_id} parameter', str(logs))

    def test_origin_from_response_None(self):
        res = Response(content_type='application/octet-stream')
        self.assertIsNone(_origin_from_response(res))
