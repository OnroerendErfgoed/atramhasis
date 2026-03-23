import os
from unittest import mock
from unittest.mock import Mock

import pytest
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from pyramid.config.settings import Settings
from pyramid.httpexceptions import HTTPNoContent
from pyramid.request import apply_request_extensions
from pyramid.testing import DummyRequest
from skosprovider.registry import Registry
from skosprovider.uri import DefaultUrnGenerator
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import Thing
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from webob.multidict import MultiDict
from skosprovider.skos import Concept as SkosConcept

import atramhasis
from atramhasis.errors import ConceptNotFoundException
from atramhasis.errors import ConceptSchemeNotFoundException
from atramhasis.errors import SkosRegistryNotFoundException
from atramhasis.errors import ValidationError
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.views.crud import AtramhasisCrud
from atramhasis.views.views import AtramhasisAdminView
from atramhasis.views.views import AtramhasisListView
from atramhasis.views.views import AtramhasisView
from atramhasis.views.views import get_definition
from atramhasis.views.views import get_public_conceptschemes
from atramhasis.views.views import labels_to_string
from atramhasis.views.views import sort_by_notetypes
from fixtures.data import trees

TEST_DIR = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(TEST_DIR, 'conf_test.ini'))


def provider(some_id):
    provider_mock = Mock()
    if some_id == 1:
        provider_mock.get_vocabulary_id = Mock(return_value='TREES')
        provider_mock.get_metadata = Mock(return_value={'id': some_id, 'subject': []})
    provider_mock.allowed_instance_scopes = ['single', 'threaded_thread']
    provider_mock.conceptscheme_id = Mock(return_value=some_id)
    provider_mock.metadata = {}
    return provider_mock


def hidden_provider(some_id):
    provider_mock = provider(some_id)
    provider_mock.get_metadata = Mock(
        return_value={'id': some_id, 'subject': ['hidden']}
    )
    return provider_mock


def external_provider(some_id):
    provider_mock = provider(some_id)
    provider_mock.get_metadata = Mock(
        return_value={'id': some_id, 'subject': ['external']}
    )
    return provider_mock


class DummySKOSManager:
    def get_thing(self, concept_id, conceptscheme_id):
        if concept_id == '1':
            return Concept(
                concept_id=concept_id,
                conceptscheme_id=conceptscheme_id,
                labels=[Label(label='test', language_id='any')],
            )
        elif concept_id == '3':
            return Collection(
                concept_id=concept_id,
                conceptscheme_id=conceptscheme_id,
                labels=[Label(label='test', language_id='any')],
            )
        elif concept_id == '555':
            return Thing(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        elif concept_id == '666':
            raise NoResultFound()

    def get_by_list_type(self, _):
        return [
            LabelType(name='prefLabel', description='foo'),
            LabelType(name='altLabel', description='foo'),
        ]


class DummyConceptschemeManager:
    def get_all(self, conceptscheme_id):
        return [
            Concept(
                concept_id=7895,
                conceptscheme_id=conceptscheme_id,
                type='concept',
                labels=[
                    Label(label='De Paardekastanje', language_id='nl'),
                    Label(label='The Chestnut', language_id='en'),
                    Label(label='la châtaigne', language_id='fr'),
                ],
            ),
            Concept(
                concept_id=9863,
                conceptscheme_id=conceptscheme_id,
                type='concept',
                labels=[Label(label='test', language_id='nl')],
            ),
        ]

    def find(self, conceptscheme_id, _):
        return self.get_all(conceptscheme_id)


class DummyAuditManager:
    def save(self, audit):
        return audit


@pytest.fixture(autouse=True)
def pyramid_config():
    config = testing.setUp()
    yield config
    testing.tearDown()


class TestAtramhasisView:
    @pytest.fixture()
    def view_request(self):
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': None,
            'conceptscheme_manager': None,
            'audit_manager': None,
        }
        return request

    def test_no_registry(self, view_request):
        with pytest.raises(SkosRegistryNotFoundException):
            AtramhasisView(view_request)


class TestHomeView:
    @pytest.fixture()
    def regis(self):
        regis = Registry()
        regis.register_provider(trees)
        regis.register_provider(hidden_provider(2))
        return regis

    @pytest.fixture()
    def view_request(self, regis):
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': None,
            'conceptscheme_manager': None,
            'audit_manager': None,
        }
        request.skos_registry = regis
        return request

    def test_passing_view(self, view_request):
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.home_view()
        assert info['conceptschemes'][0] is not None
        assert info['conceptschemes'][0]['id'] == 'TREES'
        assert 1 == len(info['conceptschemes'])


class TestFavicoView:
    @pytest.fixture()
    def regis(self):
        regis = Registry()
        regis.register_provider(trees)
        return regis

    @pytest.fixture()
    def view_request(self, regis):
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': None,
            'conceptscheme_manager': None,
            'audit_manager': None,
        }
        request.skos_registry = regis
        return request

    def test_passing_view(self, view_request):
        atramhasisview = AtramhasisView(view_request)
        response = atramhasisview.favicon_view()
        assert response.status_int == 200
        assert 'image/x-icon' in response.headers['Content-Type']
        assert response.body is not None


class TestConceptSchemeView:
    @pytest.fixture()
    def regis(self):
        regis = Registry()
        regis.register_provider(trees)
        return regis

    @pytest.fixture()
    def view_request(self, regis):
        request = testing.DummyRequest()
        request.accept = 'text/html'
        request.data_managers = {
            'skos_manager': DummySKOSManager(),
            'conceptscheme_manager': DummyConceptschemeManager(),
            'audit_manager': DummyAuditManager(),
        }
        request.skos_registry = regis
        return request

    def test_conceptschemes_view(self, view_request):
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.conceptschemes_view()
        assert 'conceptschemes' in res
        assert len(res['conceptschemes']) == 1
        cs = res['conceptschemes'][0]
        assert 'id' in cs
        assert 'conceptscheme' in cs

    def test_conceptscheme_view(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.conceptscheme_view()
        assert res is not None
        assert res['conceptscheme'] is not None
        assert res['conceptscheme']['title'] == 'TREES'
        assert res['conceptscheme']['scheme_id'] == 'TREES'
        assert res['conceptscheme']['uri'] == 'urn:x-skosprovider:trees'
        assert res['conceptscheme']['labels'] is not None
        assert res['conceptscheme']['notes'] is not None
        assert res['conceptscheme']['top_concepts'] is not None

    def test_conceptscheme_view_language(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.skos_registry.providers['TREES'].metadata[
            'atramhasis.force_display_label_language'
        ] = 'nl'

        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.conceptscheme_view()
        assert res is not None
        assert res['locale'] == 'nl'


class TestConceptView:
    @pytest.fixture()
    def regis(self):
        regis = Registry()
        regis.register_provider(provider(1))
        return regis

    @pytest.fixture()
    def concept_route(self, pyramid_config):
        pyramid_config.add_route(
            'skosprovider.c',
            pattern='/conceptschemes/{scheme_id}/c/{c_id}',
            accept='text/html',
            request_method='GET',
        )

    @pytest.fixture()
    def view_request(self, regis, concept_route):
        request = testing.DummyRequest()
        request.accept = 'text/html'
        request.data_managers = {
            'skos_manager': DummySKOSManager(),
            'conceptscheme_manager': DummyConceptschemeManager(),
            'audit_manager': DummyAuditManager(),
        }
        return request

    def test_passing_view(self, view_request, regis):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.matchdict['c_id'] = '1'
        view_request.skos_registry = regis
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.concept_view()
        assert info['concept'] is not None
        assert info['conceptType'] == 'Concept'
        assert info['scheme_id'] == 'TREES'

    def test_passing_view_with_languague(self, view_request, regis):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.matchdict['c_id'] = '1'
        view_request.skos_registry = regis
        view_request.skos_registry.providers['TREES'].metadata = {
            'atramhasis.force_display_label_language': 'nl'
        }
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.concept_view()
        assert info['concept'] is not None
        assert info['locale'] == 'nl'

    def test_passing_collection_view(self, view_request, regis):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.matchdict['c_id'] = '3'
        view_request.skos_registry = regis
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.concept_view()
        assert info['concept'] is not None
        assert info['conceptType'] == 'Collection'
        assert info['scheme_id'] == 'TREES'

    def test_provider_not_found(self, view_request, regis):
        view_request.matchdict['scheme_id'] = 'ZZ'
        view_request.matchdict['c_id'] = '1'
        view_request.skos_registry = regis
        atramhasisview = AtramhasisView(view_request)
        with pytest.raises(ConceptSchemeNotFoundException):
            atramhasisview.concept_view()

    def test_not_found(self, view_request, regis):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.matchdict['c_id'] = '666'
        view_request.skos_registry = regis
        atramhasisview = AtramhasisView(view_request)
        with pytest.raises(ConceptNotFoundException):
            atramhasisview.concept_view()

    def test_no_type(self, view_request, regis):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.matchdict['c_id'] = '555'
        view_request.skos_registry = regis
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.concept_view()
        assert info.status_int == 500


class TestSearchResultView:
    @pytest.fixture()
    def regis(self):
        regis = Registry()
        regis.register_provider(trees)
        return regis

    @pytest.fixture()
    def view_request(self, regis):
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': None,
            'conceptscheme_manager': None,
            'audit_manager': None,
        }
        request.skos_registry = regis
        return request

    def test_find_by_label(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.params = MultiDict()
        view_request.params.add('label', 'De Paardekastanje')
        view_request.params.add('_LOCALE_', 'nl')
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.search_result()
        assert info['concepts'] is not None
        concept = info['concepts'][0]
        assert concept is not None
        assert concept['label'] == 'De Paardekastanje'
        assert info['scheme_id'] == 'TREES'

    def test_find_by_concept(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.params = MultiDict()
        view_request.params.add('type', 'concept')
        view_request.params.add('_LOCALE_', 'nl')
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.search_result()
        assert info['concepts'] is not None
        concept = info['concepts'][0]
        assert concept is not None
        assert info['scheme_id'] == 'TREES'

    def test_no_querystring(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.params = MultiDict()
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.search_result()
        assert info['concepts'] is not None
        assert len(info['concepts']) == 3

    def test_no_schema(self, view_request):
        view_request.matchdict['scheme_id'] = 'GG'
        view_request.params = MultiDict()
        atramhasisview = AtramhasisView(view_request)
        info = atramhasisview.search_result()
        assert info.status_int == 404


class TestCsvView:
    @pytest.fixture()
    def view_request(self):
        request = testing.DummyRequest()
        request.accept = '*/*'
        regis = Registry()
        regis.register_provider(provider(1))
        request.skos_registry = regis
        request.data_managers = {
            'skos_manager': DummySKOSManager(),
            'conceptscheme_manager': DummyConceptschemeManager(),
            'audit_manager': DummyAuditManager(),
        }
        return request

    def test_csv(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.params = MultiDict()
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.results_csv()
        assert res['filename'] == 'atramhasis_export'
        assert isinstance(res['header'], list)
        assert isinstance(res['rows'], list)
        assert 2 == len(res['rows'])

    def test_csv_label(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.params = MultiDict()
        view_request.params.add('label', 'De Paardekastanje')
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.results_csv()
        assert res['filename'] == 'atramhasis_export'
        assert isinstance(res['header'], list)
        assert isinstance(res['rows'], list)
        assert 2 == len(res['rows'])

    def test_csv_type(self, view_request):
        view_request.matchdict['scheme_id'] = 'TREES'
        view_request.params = MultiDict()
        view_request.params.add('type', 'concept')
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.results_csv()
        assert res['filename'] == 'atramhasis_export'
        assert isinstance(res['header'], list)
        assert isinstance(res['rows'], list)
        assert 2 == len(res['rows'])


class TestLocaleView:
    @pytest.fixture()
    def view_request(self, pyramid_config):
        regis = Registry()
        regis.register_provider(trees)
        pyramid_config.add_route('home', 'foo')
        pyramid_config.add_settings(settings)
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': None,
            'conceptscheme_manager': None,
            'audit_manager': None,
        }
        request.skos_registry = regis
        return request

    def test_default_locale(self, view_request):
        config_default_lang = settings.get('pyramid.default_locale_name')
        view_request.referer = None
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.set_locale_cookie()
        assert (res.headers.get('Set-Cookie')).startswith(
            '_LOCALE_=' + config_default_lang
        )

    def test_unsupported_lang(self, view_request):
        config_default_lang = settings.get('pyramid.default_locale_name')
        view_request.GET['language'] = 'XX'
        view_request.referer = None
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.set_locale_cookie()
        assert (res.headers.get('Set-Cookie')).startswith(
            '_LOCALE_=' + config_default_lang
        )

    def test_locale(self, view_request):
        testlang = 'it'
        view_request.GET['language'] = testlang
        view_request.referer = None
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.set_locale_cookie()
        assert (res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + testlang)

    def test_locale_uppercase(self, view_request):
        testlang = 'it'
        view_request.GET['language'] = testlang.upper()
        view_request.referer = None
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.set_locale_cookie()
        assert (res.headers.get('Set-Cookie')).startswith('_LOCALE_=' + testlang)

    def test_referer(self, view_request):
        testlang = 'it'
        testurl = 'https://www.foo.bar'
        view_request.GET['language'] = testlang.upper()
        view_request.referer = testurl
        atramhasisview = AtramhasisView(view_request)
        res = atramhasisview.set_locale_cookie()
        assert res.status == '302 Found'
        assert res.location == testurl


class TestHtmlTreeView:
    @pytest.fixture()
    def view_request(self):
        regis = Registry()
        regis.register_provider(trees)
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': None,
            'conceptscheme_manager': None,
            'audit_manager': None,
        }
        request.skos_registry = regis
        return request


class TestAdminView:
    @pytest.fixture()
    def regis(self):
        regis = Registry()
        regis.register_provider(trees)
        return regis

    def test_no_registry(self):
        request = testing.DummyRequest()
        with pytest.raises(SkosRegistryNotFoundException):
            AtramhasisAdminView(request)

    def test_passing_view(self, regis):
        request = testing.DummyRequest()
        request.skos_registry = regis
        atramhasis_admin_view = AtramhasisAdminView(request)
        info = atramhasis_admin_view.admin_view()
        assert info is not None
        assert 'admin' in info

    def test_invalidate_scheme_tree(self, regis):
        request = testing.DummyRequest()
        request.matchdict['scheme_id'] = 'TREES'
        request.skos_registry = regis
        atramhasis_admin_view = AtramhasisAdminView(request)
        info = atramhasis_admin_view.invalidate_scheme_tree()
        assert info is not None


class TestViewFunctions:
    def test_labels_to_string(self):
        labels = [
            Label(label='De Paardekastanje', language_id='nl'),
            Label(label='la châtaigne', language_id='fr'),
        ]
        s = labels_to_string(labels, 'prefLabel')
        assert 'De Paardekastanje (nl), la châtaigne (fr)' == s

    def test_get_definition(self):
        notes = [
            Note(note='test', language_id='nl', notetype_id='note'),
            Note(note='test2', language_id='nl', notetype_id='definition'),
        ]
        s = get_definition(notes)
        assert 'test2' == s

    def test_sort_by_notetypes(self):
        notes = [
            Note(note='editorial', language_id='nl', notetype_id='editorialNote'),
            Note(note='scope', language_id='nl', notetype_id='scopeNote'),
            Note(note='definition', language_id='nl', notetype_id='definition'),
            Note(note='change', language_id='nl', notetype_id='changeNote'),
            Note(note='example', language_id='nl', notetype_id='example'),
            Note(note='history', language_id='nl', notetype_id='historyNote'),
            Note(note='note', language_id='nl', notetype_id='note'),
        ]
        sorted_notes = sort_by_notetypes(notes, {})
        assert [n.notetype_id for n in sorted_notes] == [
            'definition',
            'scopeNote',
            'note',
            'example',
            'historyNote',
            'changeNote',
            'editorialNote',
        ]

    def test_sort_by_notetypes_unknown_type_last(self):
        notes = [
            Note(note='unknown', language_id='nl', notetype_id='unknownType'),
            Note(note='definition', language_id='nl', notetype_id='definition'),
        ]
        sorted_notes = sort_by_notetypes(notes, {})
        assert [n.notetype_id for n in sorted_notes] == [
            'definition',
            'unknownType',
        ]

    def test_sort_by_notetypes_empty(self):
        assert sort_by_notetypes([], {}) == []

    def test_get_public_conceptschemes(self):
        regis = Registry()
        regis.register_provider(trees)
        regis.register_provider(hidden_provider(2))
        regis.register_provider(external_provider(3))
        conceptschemes = get_public_conceptschemes(regis)
        assert 1 == len(conceptschemes)


class TestListViews:
    @pytest.fixture()
    def view_request(self):
        request = testing.DummyRequest()
        request.data_managers = {
            'skos_manager': DummySKOSManager(),
        }
        return request

    def test_get_list(self, view_request):
        atramhasis_list_view = AtramhasisListView(view_request)
        labellist = atramhasis_list_view.get_list(LabelType)
        assert labellist is not None
        assert labellist[0] is not None

    def test_labeltype_list_view(self, view_request):
        atramhasis_list_view = AtramhasisListView(view_request)
        labellist = atramhasis_list_view.labeltype_list_view()
        assert labellist is not None
        assert {'key': 'prefLabel', 'label': 'prefLabel'} in labellist


class TestAtramhasisCrudView:
    class SKOSRegistry:
        pass

    class SKOSManager:
        def get_all_label_types(self):
            return [
                LabelType(name='prefLabel', description=''),
                LabelType(name='sortLabel', description=''),
            ]

        def get_next_cid(self, _, __):
            return 'next_cid'

        def save(self, concept):
            if concept.id is None:
                concept.id = 1
            concept.conceptscheme = ConceptScheme(uri='urn:x-skosprovider:test')
            return concept

        def get_thing(self, concept_id, scheme_id):
            raise NoResultFound()

    class LanguagesManager:
        def count_languages(self, _):
            return 1

    class Provider(SQLAlchemyProvider):
        conceptscheme_id = 'cs_id'
        uri_generator = DefaultUrnGenerator('voc-id')

        def __init__(self):
            self.metadata = {'subject': 'stub'}

    @pytest.fixture()
    def crud_request(self):
        pyramid_settings = Settings(settings)
        config = testing.setUp(settings=pyramid_settings)
        atramhasis.load_app(config)
        request = DummyRequest()
        request.application_url = 'http://localhost:6543'
        apply_request_extensions(request)
        request.data_managers = {
            'skos_manager': TestAtramhasisCrudView.SKOSManager(),
            'conceptscheme_manager': None,
            'audit_manager': None,
            'languages_manager': TestAtramhasisCrudView.LanguagesManager(),
        }
        return request

    @pytest.fixture()
    def crud_view(self, crud_request):
        view = AtramhasisCrud(crud_request)
        view.skos_registry = TestAtramhasisCrudView.SKOSRegistry()
        view.provider = TestAtramhasisCrudView.Provider()
        view.scheme_id = 's_id'
        return view

    def get_concept_json(self):
        return {
            'type': 'concept',
            'broader': [],
            'narrower': [],
            'related': [],
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
                {'type': 'sortLabel', 'language': 'en', 'label': 'a'},
            ],
            'notes': [],
            'sources': [{'citation': 'Citation'}],
        }

    def test_add_concept(self, crud_request, crud_view):
        crud_request.json_body = self.get_concept_json()
        concept = crud_view.add_concept()
        assert isinstance(concept, SkosConcept)
        assert 'next_cid' == concept.id
        assert 'urn:x-skosprovider:voc-id:next_cid' == concept.uri

    def test_add_concept_manual_id_strategy(self, crud_request, crud_view):
        strategy = IDGenerationStrategy.MANUAL
        crud_view.provider.metadata['atramhasis.id_generation_strategy'] = strategy
        crud_request.json_body = self.get_concept_json()
        crud_request.json_body['id'] = 'manual'

        concept = crud_view.add_concept()
        assert isinstance(concept, SkosConcept)
        assert 'manual' == concept.id

        del crud_request.json_body['id']
        with pytest.raises(ValidationError):
            crud_view.add_concept()

        # add_concept should fail without id, edit_concept should not because
        # no id validation happens
        crud_request.matchdict['c_id'] = 'manual'
        db_concept = Concept()
        db_concept.conceptscheme = ConceptScheme(id=1, uri='urn:x-skosprovider:trees')
        crud_request.data_managers['skos_manager'].get_thing = lambda *_: db_concept
        crud_view.edit_concept()

    def test_add_provider(self, crud_request, crud_view):
        crud_request.openapi_validated = Mock()
        crud_request.skos_registry = Registry()
        view = 'atramhasis.views.crud'

        with (
            mock.patch(f'{view}.provider.create_provider', autospec=True) as processor,
            mock.patch(
                f'{view}.utils.db_provider_to_skosprovider', autospec=True
            ) as renderer,
        ):
            response = crud_view.add_provider()
            assert 201 == crud_request.response.status_code
            processor.assert_called()
            renderer.assert_called()
            assert response == renderer.return_value

    def test_update_provider(self, crud_request, crud_view):
        crud_request.openapi_validated = Mock()
        crud_request.matchdict = {'id': 1}
        view = 'atramhasis.views.crud'

        with (
            mock.patch(f'{view}.provider.update_provider', autospec=True) as processor,
            mock.patch(
                f'{view}.utils.db_provider_to_skosprovider', autospec=True
            ) as renderer,
        ):
            response = crud_view.update_provider()
            processor.assert_called()
            renderer.assert_called()
            assert response == renderer.return_value

    def test_delete_provider(self, crud_request, crud_view):
        crud_request.matchdict = {'id': 1}
        view = 'atramhasis.views.crud'

        with mock.patch(f'{view}.provider.delete_provider', autospec=True) as processor:
            response = crud_view.delete_provider()
            processor.assert_called()
            assert isinstance(response, HTTPNoContent)
