import os
import unittest

from skosprovider.registry import Registry
from pyramid import testing
from webob.multidict import MultiDict
from webtest import TestApp
from paste.deploy.loadwsgi import appconfig

from atramhasis.errors import SkosRegistryNotFoundException
from atramhasis.views.views import AtramhasisView
from atramhasis import main
from tests.fixtures.data import trees


TEST_DIR = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(TEST_DIR, 'conf_test.ini'))


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

    def test_passing_collection_view(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '3'
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info['concept'])
        self.assertEqual(info['conceptType'], 'Collection')
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
        request.params.add('_LOCALE_', 'nl')
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


class TestCsvView(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_csv(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.params = MultiDict()
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.results_csv()
        self.assertEqual(res['filename'], 'atramhasis_export')
        self.assertIsInstance(res['header'], list)
        self.assertIsInstance(res['rows'], list)
        self.assertEqual(3, len(res['rows']))
