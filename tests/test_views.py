# -*- coding: utf-8 -*-
import os
import unittest

from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from skosprovider.registry import Registry
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import Thing
from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict

from atramhasis.data.datamanagers import AuditManager
from atramhasis.data.datamanagers import ConceptSchemeManager
from atramhasis.data.datamanagers import SkosManager
from atramhasis.errors import ConceptNotFoundException
from atramhasis.errors import ConceptSchemeNotFoundException
from atramhasis.errors import SkosRegistryNotFoundException
from atramhasis.views.views import AtramhasisAdminView
from atramhasis.views.views import AtramhasisListView
from atramhasis.views.views import AtramhasisView
from atramhasis.views.views import get_definition
from atramhasis.views.views import labels_to_string
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
        provider_mock.get_metadata = Mock(return_value={'id': some_id, 'subject': []})
    provider_mock.allowed_instance_scopes = ['single', 'threaded_thread']
    provider_mock.conceptscheme_id = Mock(return_value=some_id)
    provider_mock.metadata={}
    return provider_mock


def hidden_provider(some_id):
    provider_mock = provider(some_id)
    provider_mock.get_metadata = Mock(return_value={'id': some_id, 'subject': ['hidden']})
    return provider_mock


def data_managers(request):
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_query_mock)
    skos_manager = SkosManager(session_mock)
    conceptscheme_manager = ConceptSchemeManager(session_mock)
    audit_manager = AuditManager(session_mock)
    return {
        'skos_manager': skos_manager,
        'conceptscheme_manager': conceptscheme_manager,
        'audit_manager': audit_manager
    }


def create_query_mock(some_class):
    query_mock = Mock()
    if some_class == Concept or some_class == Collection or some_class == Thing:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_concept)
    elif some_class == ConceptScheme:
        query_mock.filter_by = Mock(side_effect=filter_by_mock_conceptscheme)
    query_mock.all = get_all_mock()
    query_mock.options = Mock(side_effect=options_mock)
    return query_mock


def options_mock(options, **kwargs):
    options = Mock()
    options.filter = Mock(side_effect=filter_mock)
    return options


def filter_mock(filer, **kwargs):
    filtermock = Mock()
    filtermock.filter = Mock(side_effect=filter_mock)
    filtermock.all = get_all_mock()
    return filtermock


def get_all_mock():
    a_concept = Concept(concept_id=7895, conceptscheme_id=1, type='concept')
    a_labels = [Label(label='De Paardekastanje', language_id='nl'), Label(label='The Chestnut', language_id='en'),
                Label(label='la châtaigne', language_id='fr')]
    a_concept.labels = a_labels
    b_concept = Concept(concept_id=9863, conceptscheme_id=1, type='concept')
    b_labels = [Label(label='test', language_id='nl')]
    b_concept.labels = b_labels
    all_mock = Mock(return_value=[a_concept, b_concept])
    return all_mock


def filter_by_mock_conceptscheme(**kwargs):
    filter_mock = Mock()
    concept_scheme = ConceptScheme()
    concept_scheme.id = 1
    concept_scheme.uri = "urn:test:test"
    filter_mock.one = Mock(return_value=concept_scheme)
    return filter_mock


def filter_by_mock_concept(**kwargs):
    filter_mock = Mock()
    concept_id = None
    conceptscheme_id = None
    if 'concept_id' in kwargs:
        concept_id = kwargs['concept_id']
    if 'conceptscheme_id' in kwargs:
        conceptscheme_id = kwargs['conceptscheme_id']
    if concept_id == '1':
        c = Concept(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        c.type = 'concept'
        label_mock = Mock()
        label_mock.label = 'test'
        c.label = Mock(return_value=label_mock)
        filter_mock.one = Mock(return_value=c)
    elif concept_id == '3':
        c = Collection(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        c.type = 'collection'
        label_mock = Mock()
        label_mock.label = 'test'
        c.label = Mock(return_value=label_mock)
        filter_mock.one = Mock(return_value=c)
    elif concept_id == '555':
        c = Thing(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        filter_mock.one = Mock(return_value=c)
    elif concept_id == '666':
        raise NoResultFound

    a_concept = Concept(concept_id=7895, conceptscheme_id=conceptscheme_id, type='concept')
    a_labels = [Label(label='De Paardekastanje', language_id='nl'), Label(label='The Chestnut', language_id='en'),
                Label(label='la châtaigne', language_id='fr')]
    a_concept.labels = a_labels
    b_concept = Concept(concept_id=9863, conceptscheme_id=conceptscheme_id, type='concept')
    b_labels = [Label(label='test', language_id='nl')]
    b_concept.labels = b_labels
    filter_mock.all = Mock(return_value=[a_concept, b_concept])
    return filter_mock


def list_db(request):
    session_mock = Mock()
    session_mock.query = Mock(side_effect=create_listquery_mock)
    skos_manager = SkosManager(session_mock)
    conceptscheme_manager = ConceptSchemeManager(session_mock)
    audit_manager = AuditManager(session_mock)
    return {
        'skos_manager': skos_manager,
        'conceptscheme_manager': conceptscheme_manager,
        'audit_manager': audit_manager
    }


def create_listquery_mock(some_class):
    query_mock = Mock()
    query_mock.all = get_all_list_mock()
    return query_mock


def get_all_list_mock():
    lbl1 = LabelType(name="prefLabel", description="foo")
    lbl2 = LabelType(name="altLabel", description="foo")
    all_mock = Mock(return_value=[lbl1, lbl2])
    return all_mock


class TestAtramhasisView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.data_managers = {'skos_manager': None, 'conceptscheme_manager': None, 'audit_manager': None}

    def tearDown(self):
        testing.tearDown()

    def test_no_registry(self):
        error_raised = False
        try:
            AtramhasisView(self.request)
        except SkosRegistryNotFoundException as e:
            error_raised = True
            self.assertIsNotNone(e.__str__())
        self.assertTrue(error_raised)


class TestHomeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.regis.register_provider(hidden_provider(2))
        self.request = testing.DummyRequest()
        self.request.data_managers = {'skos_manager': None, 'conceptscheme_manager': None, 'audit_manager': None}

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.home_view()
        self.assertIsNotNone(info['conceptschemes'][0])
        self.assertEqual(info['conceptschemes'][0]['id'], 'TREES')
        self.assertEqual(1, len(info['conceptschemes']))


class TestFavicoView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.data_managers = {'skos_manager': None, 'conceptscheme_manager': None, 'audit_manager': None}

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        response = atramhasisview.favicon_view()
        self.assertEqual(response.status_int, 200)
        self.assertIn('image/x-icon', response.headers['Content-Type'])
        self.assertIsNotNone(response.body)


class TestConceptSchemeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.accept = 'text/html'
        self.request.data_managers = data_managers(self.request)
        self.request.skos_registry = self.regis

    def tearDown(self):
        testing.tearDown()

    def test_conceptschemes_view(self):
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.conceptschemes_view()
        self.assertIn('conceptschemes', res)
        self.assertEqual(len(res['conceptschemes']), 1)
        cs = res['conceptschemes'][0]
        self.assertIn('id', cs)
        self.assertIn('conceptscheme', cs)

    def test_conceptscheme_view(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.conceptscheme_view()
        self.assertIsNotNone(res)
        self.assertIsNotNone(res['conceptscheme'])
        self.assertEqual(res['conceptscheme']['title'], 'TREES')
        self.assertEqual(res['conceptscheme']['scheme_id'], 'TREES')
        self.assertEqual(res['conceptscheme']['uri'], 'urn:x-skosprovider:trees')
        self.assertIsNotNone(res['conceptscheme']['labels'])
        self.assertIsNotNone(res['conceptscheme']['notes'])
        self.assertIsNotNone(res['conceptscheme']['top_concepts'])

    def test_conceptscheme_view_language(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.skos_registry.providers['TREES'].metadata[
            'atramhasis.force_display_label_language'] = 'nl'

        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.conceptscheme_view()
        self.assertIsNotNone(res)
        self.assertEqual(res['locale'], 'nl')


class TestConceptView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route('concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='text/html',
                              request_method="GET")
        self.request = testing.DummyRequest()
        self.request.accept = 'text/html'
        self.regis = Registry()
        self.regis.register_provider(provider(1))
        self.request.data_managers = data_managers(self.request)

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

    def test_passing_view_with_languague(self):
        request = self.request
        request.matchdict['scheme_id'] = 'TREES'
        request.matchdict['c_id'] = '1'
        request.skos_registry = self.regis
        request.skos_registry.providers['TREES'].metadata = {
            'atramhasis.force_display_label_language': 'nl'
        }
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info['concept'])
        self.assertEqual(info['locale'], 'nl')

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
        self.request = testing.DummyRequest()
        self.request.data_managers = {'skos_manager': None, 'conceptscheme_manager': None, 'audit_manager': None}

    def tearDown(self):
        testing.tearDown()

    def test_find_by_label(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.params = MultiDict()
        self.request.params.add('label', 'De Paardekastanje')
        self.request.params.add('_LOCALE_', 'nl')
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info['concepts'])
        concept = info['concepts'][0]
        self.assertIsNotNone(concept)
        self.assertEqual(concept['label'], 'De Paardekastanje')
        self.assertEqual(info['scheme_id'], 'TREES')

    def test_find_by_concept(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.params = MultiDict()
        self.request.params.add('type', 'concept')
        self.request.params.add('_LOCALE_', 'nl')
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info['concepts'])
        concept = info['concepts'][0]
        self.assertIsNotNone(concept)
        self.assertEqual(info['scheme_id'], 'TREES')

    def test_no_querystring(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.params = MultiDict()
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info['concepts'])
        self.assertEqual(len(info['concepts']), 3)

    def test_no_schema(self):
        self.request.matchdict['scheme_id'] = 'GG'
        self.request.params = MultiDict()
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertEqual(info.status_int, 404)


class TestCsvView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.accept = '*/*'
        self.regis = Registry()
        self.regis.register_provider(provider(1))
        self.request.skos_registry = self.regis
        self.request.data_managers = data_managers(self.request)

    def tearDown(self):
        testing.tearDown()

    def test_csv(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.params = MultiDict()
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.results_csv()
        self.assertEqual(res['filename'], 'atramhasis_export')
        self.assertIsInstance(res['header'], list)
        self.assertIsInstance(res['rows'], list)
        self.assertEqual(2, len(res['rows']))

    def test_csv_label(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.params = MultiDict()
        self.request.params.add('label', 'De Paardekastanje')
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.results_csv()
        self.assertEqual(res['filename'], 'atramhasis_export')
        self.assertIsInstance(res['header'], list)
        self.assertIsInstance(res['rows'], list)
        self.assertEqual(2, len(res['rows']))

    def test_csv_type(self):
        self.request.matchdict['scheme_id'] = 'TREES'
        self.request.params = MultiDict()
        self.request.params.add('type', 'concept')
        atramhasisview = AtramhasisView(self.request)
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
        self.request = testing.DummyRequest()
        self.request.data_managers = {'skos_manager': None, 'conceptscheme_manager': None, 'audit_manager': None}

    def tearDown(self):
        testing.tearDown()

    def test_default_locale(self):
        config_default_lang = settings.get('pyramid.default_locale_name')
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + config_default_lang))

    def test_unsupported_lang(self):
        config_default_lang = settings.get('pyramid.default_locale_name')
        self.request.GET['language'] = 'XX'
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + config_default_lang))

    def test_locale(self):
        testlang = 'it'
        self.request.GET['language'] = testlang
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + testlang))

    def test_locale_uppercase(self):
        testlang = 'it'
        self.request.GET['language'] = testlang.upper()
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue((res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + testlang))

    def test_referer(self):
        testlang = 'it'
        testurl = 'http://www.foo.bar'
        self.request.GET['language'] = testlang.upper()
        self.request.referer = testurl
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, testurl)


class TestHtmlTreeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.data_managers = {'skos_manager': None, 'conceptscheme_manager': None, 'audit_manager': None}

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        self.request.skos_registry = self.regis
        self.request.matchdict['scheme_id'] = 'TREES'
        atramhasisview = AtramhasisView(self.request)
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
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.skos_registry = self.regis
        atramhasisAdminview = AtramhasisAdminView(request)
        info = atramhasisAdminview.invalidate_scheme_tree()
        self.assertIsNotNone(info)


class TestViewFunctions(unittest.TestCase):
    def test_labels_to_string(self):
        labels = [Label(label='De Paardekastanje', language_id='nl'), Label(label='la châtaigne', language_id='fr')]
        s = labels_to_string(labels, 'prefLabel')
        self.assertEqual('De Paardekastanje (nl), la châtaigne (fr)', s)

    def test_get_definition(self):
        notes = [Note(note='test', language_id='nl', notetype_id='note'),
                 Note(note='test2', language_id='nl', notetype_id='definition')]
        s = get_definition(notes)
        self.assertEqual('test2', s)


class TestListViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.data_managers = list_db(self.request)

    def test_get_list(self):
        request = self.request
        atramhasis_list_view = AtramhasisListView(request)
        labellist = atramhasis_list_view.get_list(LabelType)
        self.assertIsNotNone(labellist)
        self.assertIsNotNone(labellist[0])

    def test_labeltype_list_view(self):
        request = self.request
        atramhasis_list_view = AtramhasisListView(request)
        labellist = atramhasis_list_view.labeltype_list_view()
        self.assertIsNotNone(labellist)
        self.assertIn(
            {'key': 'prefLabel', 'label': u'prefLabel'},
            labellist
        )
