import os
import unittest

from skosprovider.registry import Registry
from pyramid import testing
from skosprovider_sqlalchemy.models import Concept, Collection, Thing
from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict
from paste.deploy.loadwsgi import appconfig

from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException, ConceptNotFoundException
from atramhasis.views import tree_cache_dictionary
from atramhasis.views.views import AtramhasisView, AtramhasisAdminView
from fixtures.data import trees

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover

TEST_DIR = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(TEST_DIR, 'conf_test.ini'))


def provider(some_id):
    provider_mock = Mock()
    if some_id == 1:
        provider_mock.get_vocabulary_id = Mock(return_value='TREES')
    return provider_mock


def db(request):
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_query_mock)
    return session_mock


def create_query_mock(some_class):
    query_mock = Mock()
    query_mock.filter_by = Mock(side_effect=filter_by_mock_concept)
    return query_mock


def filter_by_mock_concept(concept_id, conceptscheme_id):
    filter_mock = Mock()
    if concept_id == '1':
        c = Concept(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        c.type = 'concept'
        filter_mock.one = Mock(return_value=c)
    elif concept_id == '3':
        c = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        c.type = 'collection'
        filter_mock.one = Mock(return_value=c)
    elif concept_id == '555':
        c = Thing(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        filter_mock.one = Mock(return_value=c)
    elif concept_id == '666':
        raise NoResultFound

    return filter_mock


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


class TestFavicoView(unittest.TestCase):
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
        response = atramhasisview.favicon_view()
        self.assertEqual(response.status_int, 200)
        self.assertIn('image/x-icon', response.headers['Content-Type'])
        self.assertIsNotNone(response.body)


class TestConceptView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.regis = Registry()
        self.regis.register_provider(provider(1))
        self.request.db = db(self.request)

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        request = self.request
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '1'
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info['concept'])
        self.assertEqual(info['conceptType'], 'Concept')
        self.assertEqual(info['scheme_id'], 'TREES')

    def test_passing_collection_view(self):
        request = self.request
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '3'
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info['concept'])
        self.assertEqual(info['conceptType'], 'Collection')
        self.assertEqual(info['scheme_id'], 'TREES')

    def test_provider_not_found(self):
        request = self.request
        request.matchdict['scheme_id'] = 'ZZ'
        request.matchdict['c_id'] = '1'
        request.skos_registry = self.regis
        error_raised = False
        try:
            atramhasisview = AtramhasisView(request)
            atramhasisview.concept_view()
        except ConceptSchemeNotFoundException as e:
            error_raised = True
            self.assertIsNotNone(e.__str__())
        self.assertTrue(error_raised)

    def test_not_found(self):
        request = self.request
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '666'
        request.skos_registry = self.regis
        error_raised = False
        try:
            atramhasisview = AtramhasisView(request)
            atramhasisview.concept_view()
        except ConceptNotFoundException as e:
            error_raised = True
            self.assertIsNotNone(e.__str__())
        self.assertTrue(error_raised)

    def test_no_type(self):
        request = self.request
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '555'
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertEqual(info.status_int, 500)


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


class TestHtmlTreeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        request = testing.DummyRequest()
        request.skos_registry = self.regis
        request.matchdict['scheme_id'] = 'TREES'
        atramhasisview = AtramhasisView(request)
        response = atramhasisview.results_tree_html()
        self.assertEqual(response['conceptType'], None)
        self.assertEqual(response['concept'], None)
        self.assertEqual(response['scheme_id'], 'TREES')


class TestAdminView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_no_registry(self):
        error_raised = False
        request = testing.DummyRequest()
        try:
            AtramhasisAdminView(request)
        except SkosRegistryNotFoundException as e:
            error_raised = True
            self.assertIsNotNone(e.__str__())
        self.assertTrue(error_raised)

    def test_passing_view(self):
        request = testing.DummyRequest()
        request.skos_registry = self.regis
        atramhasisAdminview = AtramhasisAdminView(request)
        info = atramhasisAdminview.admin_view()
        self.assertIsNotNone(info)
        self.assertTrue('admin' in info)

    def test_invalidate_scheme_tree(self):
        tree_cache_dictionary['foo |TREES nl'] = []
        tree_cache_dictionary['foo |TREES fr'] = []
        tree_cache_dictionary['bar |MATERIALS fr'] = []

        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.skos_registry = self.regis
        atramhasisAdminview = AtramhasisAdminView(request)
        response = atramhasisAdminview.invalidate_scheme_tree()

        self.assertEqual(response.status_int, 200)
        self.assertIn('bar |MATERIALS fr', tree_cache_dictionary.keys())
        self.assertNotIn('foo |TREES nl', tree_cache_dictionary.keys())
        self.assertNotIn('foo |TREES fr', tree_cache_dictionary.keys())

    def test_invalidate_tree(self):
        tree_cache_dictionary['foo |TREES nl'] = []
        tree_cache_dictionary['foo |TREES fr'] = []
        tree_cache_dictionary['bar |MATERIALS fr'] = []

        request = testing.DummyRequest()
        request.skos_registry = self.regis
        atramhasisAdminview = AtramhasisAdminView(request)
        response = atramhasisAdminview.invalidate_tree()

        self.assertEqual(response.status_int, 200)
        self.assertEqual(len(tree_cache_dictionary), 0)