# -*- coding: utf-8 -*-
import unittest
from atramhasis.protected_resources import ProtectedResourceEvent, ProtectedResourceException, protected_operation
try:
    from unittest.mock import Mock, MagicMock
except ImportError:
    from mock import Mock, MagicMock, call  # pragma: no cover


class DummyParent(object):

    def __init__(self):
        self.request = MagicMock()
        self.request.path_url = 'http://localhost/conceptschemes/GEOGRAPHY/c/9'

    @protected_operation
    def protected_dummy(self):
        return 'dummy ok'


class ProtectedTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_protected_resource_event(self):
        event = ProtectedResourceEvent('urn:test')
        self.assertEqual('urn:test', event.uri)

    def test_protected_resource_exception(self):
        referenced_in = ['urn:someobject', 'http://test.test.org/object/2']
        error = ProtectedResourceException('test_msg', referenced_in)
        self.assertIsNotNone(error)
        self.assertEqual("'test_msg'", str(error))

    def test_protected_event(self):
        dummy = DummyParent()
        notify_mock = Mock()
        dummy.request.registry.notify = notify_mock
        dummy.protected_dummy()
        notify_call = notify_mock.mock_calls[0]
        self.assertEqual('http://localhost/conceptschemes/GEOGRAPHY/c/9', notify_call[1][0].uri)