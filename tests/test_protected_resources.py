import unittest
from unittest.mock import MagicMock
from unittest.mock import Mock

from atramhasis.errors import ConceptSchemeNotFoundException
from atramhasis.protected_resources import ProtectedResourceEvent
from atramhasis.protected_resources import ProtectedResourceException
from atramhasis.protected_resources import protected_operation


class DummyParent:

    def __init__(self):
        self.request = MagicMock()
        self.request.path = '/conceptschemes/GEOGRAPHY/c/9'

    @protected_operation
    def protected_dummy(self):
        return 'dummy ok'


class ProtectedTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_protected_resource_event(self):
        event = ProtectedResourceEvent('urn:test', 'request')
        self.assertEqual('urn:test', event.uri)
        self.assertEqual('request', event.request)

    def test_protected_resource_exception(self):
        referenced_in = ['urn:someobject', 'http://test.test.org/object/2']
        error = ProtectedResourceException('test_msg', referenced_in)
        self.assertIsNotNone(error)
        self.assertEqual("'test_msg'", str(error))

    def test_protected_event(self):
        dummy = DummyParent()
        provider = MagicMock()
        provider.uri_generator.generate = lambda id: 'urn:x-vioe:geography:9'
        dummy.request.skos_registry.get_provider = lambda scheme_id: provider
        notify_mock = Mock()
        dummy.request.registry.notify = notify_mock
        dummy.protected_dummy()
        notify_call = notify_mock.mock_calls[0]
        self.assertEqual('urn:x-vioe:geography:9', notify_call[1][0].uri)

    def test_protected_event_error(self):
        dummy = DummyParent()
        dummy.request.skos_registry.get_provider = lambda scheme_id: None
        notify_mock = Mock()
        dummy.request.registry.notify = notify_mock
        self.assertRaises(ConceptSchemeNotFoundException, dummy.protected_dummy)
