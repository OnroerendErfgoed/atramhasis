import unittest

from skosprovider.registry import Registry
from pyramid import testing
from webob.multidict import MultiDict
from atramhasis.errors import SkosRegistryNotFoundException

from atramhasis.views.views import AtramhasisView
from .fixtures.data import trees


class TestAtramhasisView(unittest.TestCase):
    def test_no_registry(self):
        error_raised = False
        request = testing.DummyRequest()
        try:
            AtramhasisView(request)
        except SkosRegistryNotFoundException as e:
            error_raised = True
            self.assertIsNotNone(e.__str__())
        self.assertTrue(error_raised)


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
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.home_view()
        self.assertIsNotNone(info['conceptschemes'][0])
        self.assertEqual(info['conceptschemes'][0]['id'], 'TREES')


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
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info['concept'])
        self.assertEqual(info['conceptType'], 'Concept')
        self.assertEqual(info['scheme_id'], 'TREES')

    def test_provider_not_found(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'ZZ'
        request.matchdict['c_id'] = '1'
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertEqual(info.status_int, 404)

    def test_not_found(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '666'
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertEqual(info.status_int, 404)


class TestSearchResultView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_find_by_label(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.params = MultiDict()
        request.params.add('label', 'De Paardekastanje')
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info['concepts'])
        concept = info['concepts'][0]
        self.assertIsNotNone(concept)
        self.assertEqual(concept['label'], 'De Paardekastanje')
        self.assertEqual(info['scheme_id'], 'TREES')

    def test_no_querystring(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.params = MultiDict()
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info['concepts'])
        self.assertEqual(len(info['concepts']), 3)

    def test_no_schema(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'GG'
        request.params = MultiDict()
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.search_result()
        self.assertEqual(info.status_int, 404)