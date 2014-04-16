import unittest

from skosprovider.registry import Registry
from pyramid import testing
from atramhasis.views import home_view, concept_view
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


class TestConceptView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '1'
        request.skos_registry = self.regis
        info = concept_view(request)
        self.assertIsNotNone(info['concept'])

    def test_provider_not_found(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'ZZ'
        request.matchdict['c_id'] = '1'
        request.skos_registry = self.regis
        info = concept_view(request)
        self.assertIsNone(info['concept'])

    def test_not_found(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '666'
        request.skos_registry = self.regis
        info = concept_view(request)
        self.assertIsNone(info['concept'])

    def test_failing_view(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '1'
        info = concept_view(request)
        self.assertEqual(info.status_int, 500)