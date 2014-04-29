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

    def test_find_by_concept(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.params = MultiDict()
        request.params.add('ctype', 'concept')
        request.params.add('_LOCALE_', 'nl')
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info['concepts'])
        concept = info['concepts'][0]
        self.assertIsNotNone(concept)
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

    def test_csv_label(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.params = MultiDict()
        request.params.add('label', 'De Paardekastanje')
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.results_csv()
        self.assertEqual(res['filename'], 'atramhasis_export')
        self.assertIsInstance(res['header'], list)
        self.assertIsInstance(res['rows'], list)
        self.assertEqual(1, len(res['rows']))

    def test_csv_ctype(self):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.params = MultiDict()
        request.params.add('ctype', 'concept')
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.results_csv()
        self.assertEqual(res['filename'], 'atramhasis_export')
        self.assertIsInstance(res['header'], list)
        self.assertIsInstance(res['rows'], list)
        self.assertEqual(2, len(res['rows']))


class TestLocaleView(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        config = testing.setUp()
        config.add_route('home', 'foo')
        config.add_settings(settings)

    def tearDown(self):
        testing.tearDown()

    def test_default_locale(self):
        config_default_lang = settings.get('pyramid.default_locale_name')
        request = testing.DummyRequest()
        request.referer = None
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + config_default_lang))

    def test_unsupported_lang(self):
        config_default_lang = settings.get('pyramid.default_locale_name')
        request = testing.DummyRequest()
        request.GET['language'] = 'XX'
        request.referer = None
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + config_default_lang))

    def test_locale(self):
        testlang = 'it'
        request = testing.DummyRequest()
        request.GET['language'] = testlang
        request.referer = None
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + testlang))

    def test_locale_uppercase(self):
        testlang = 'it'
        request = testing.DummyRequest()
        request.GET['language'] = testlang.upper()
        request.referer = None
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + testlang))

    def test_referer(self):
        testlang = 'it'
        testurl = 'http://www.foo.bar'
        request = testing.DummyRequest()
        request.GET['language'] = testlang.upper()
        request.referer = testurl
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        res = atramhasisview.set_locale_cookie()
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, testurl)