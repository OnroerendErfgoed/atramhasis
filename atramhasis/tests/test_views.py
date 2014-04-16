import unittest

from skosprovider.registry import Registry
from pyramid import testing
from atramhasis.views import home_view
from .fixtures.data import trees


class TestHomeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        request = testing.DummyRequest()
        request.skos_registry = self.regis
        info = home_view(request)
        self.assertEqual(info['project'], 'atramhasis')
        self.assertIsNotNone(info['conceptschemes'][0])
        self.assertEqual(info['conceptschemes'][0]['id'], 'TREES')

    def test_failing_view(self):
        request = testing.DummyRequest()
        info = home_view(request)
        self.assertEqual(info.status_int, 500)