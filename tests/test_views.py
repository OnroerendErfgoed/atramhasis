import os
import unittest
from unittest.mock import Mock

import mock
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
from fixtures.data import trees

TEST_DIR = os.path.dirname(__file__)
settings = appconfig("config:" + os.path.join(TEST_DIR, "conf_test.ini"))


def provider(some_id):
    provider_mock = Mock()
    if some_id == 1:
        provider_mock.get_vocabulary_id = Mock(return_value="TREES")
        provider_mock.get_metadata = Mock(return_value={"id": some_id, "subject": []})
    provider_mock.allowed_instance_scopes = ["single", "threaded_thread"]
    provider_mock.conceptscheme_id = Mock(return_value=some_id)
    provider_mock.metadata = {}
    return provider_mock


def hidden_provider(some_id):
    provider_mock = provider(some_id)
    provider_mock.get_metadata = Mock(
        return_value={"id": some_id, "subject": ["hidden"]}
    )
    return provider_mock


def external_provider(some_id):
    provider_mock = provider(some_id)
    provider_mock.get_metadata = Mock(
        return_value={"id": some_id, "subject": ["external"]}
    )
    return provider_mock


class DummySKOSManager:
    def get_thing(self, concept_id, conceptscheme_id):
        if concept_id == "1":
            return Concept(
                concept_id=concept_id,
                conceptscheme_id=conceptscheme_id,
                labels=[Label(label="test", language_id="any")],
            )
        elif concept_id == "3":
            return Collection(
                concept_id=concept_id,
                conceptscheme_id=conceptscheme_id,
                labels=[Label(label="test", language_id="any")],
            )
        elif concept_id == "555":
            return Thing(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        elif concept_id == "666":
            raise NoResultFound()

    def get_by_list_type(self, _):
        return [
            LabelType(name="prefLabel", description="foo"),
            LabelType(name="altLabel", description="foo"),
        ]


class DummyConceptschemeManager:
    def get_all(self, conceptscheme_id):
        return [
            Concept(
                concept_id=7895,
                conceptscheme_id=conceptscheme_id,
                type="concept",
                labels=[
                    Label(label="De Paardekastanje", language_id="nl"),
                    Label(label="The Chestnut", language_id="en"),
                    Label(label="la châtaigne", language_id="fr"),
                ],
            ),
            Concept(
                concept_id=9863,
                conceptscheme_id=conceptscheme_id,
                type="concept",
                labels=[Label(label="test", language_id="nl")],
            )
        ]

    def find(self, conceptscheme_id, _):
        return self.get_all(conceptscheme_id)


class DummyAuditManager:
    def save(self, audit):
        return audit


class TestAtramhasisView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            "skos_manager": None,
            "conceptscheme_manager": None,
            "audit_manager": None,
        }

    def tearDown(self):
        testing.tearDown()

    def test_no_registry(self):
        with self.assertRaises(SkosRegistryNotFoundException):
            AtramhasisView(self.request)


class TestHomeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.regis.register_provider(hidden_provider(2))
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            "skos_manager": None,
            "conceptscheme_manager": None,
            "audit_manager": None,
        }

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.home_view()
        self.assertIsNotNone(info["conceptschemes"][0])
        self.assertEqual(info["conceptschemes"][0]["id"], "TREES")
        self.assertEqual(1, len(info["conceptschemes"]))


class TestFavicoView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            "skos_manager": None,
            "conceptscheme_manager": None,
            "audit_manager": None,
        }

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        response = atramhasisview.favicon_view()
        self.assertEqual(response.status_int, 200)
        self.assertIn("image/x-icon", response.headers["Content-Type"])
        self.assertIsNotNone(response.body)


class TestConceptSchemeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.accept = "text/html"
        self.request.data_managers = {
            "skos_manager": DummySKOSManager(),
            "conceptscheme_manager": DummyConceptschemeManager(),
            "audit_manager": DummyAuditManager(),
        }
        self.request.skos_registry = self.regis

    def tearDown(self):
        testing.tearDown()

    def test_conceptschemes_view(self):
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.conceptschemes_view()
        self.assertIn("conceptschemes", res)
        self.assertEqual(len(res["conceptschemes"]), 1)
        cs = res["conceptschemes"][0]
        self.assertIn("id", cs)
        self.assertIn("conceptscheme", cs)

    def test_conceptscheme_view(self):
        self.request.matchdict["scheme_id"] = "TREES"
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.conceptscheme_view()
        self.assertIsNotNone(res)
        self.assertIsNotNone(res["conceptscheme"])
        self.assertEqual(res["conceptscheme"]["title"], "TREES")
        self.assertEqual(res["conceptscheme"]["scheme_id"], "TREES")
        self.assertEqual(res["conceptscheme"]["uri"], "urn:x-skosprovider:trees")
        self.assertIsNotNone(res["conceptscheme"]["labels"])
        self.assertIsNotNone(res["conceptscheme"]["notes"])
        self.assertIsNotNone(res["conceptscheme"]["top_concepts"])

    def test_conceptscheme_view_language(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.skos_registry.providers["TREES"].metadata[
            "atramhasis.force_display_label_language"
        ] = "nl"

        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.conceptscheme_view()
        self.assertIsNotNone(res)
        self.assertEqual(res["locale"], "nl")


class TestConceptView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route(
            "concept",
            pattern="/conceptschemes/{scheme_id}/c/{c_id}",
            accept="text/html",
            request_method="GET",
        )
        self.request = testing.DummyRequest()
        self.request.accept = "text/html"
        self.regis = Registry()
        self.regis.register_provider(provider(1))
        self.request.data_managers = {
            "skos_manager": DummySKOSManager(),
            "conceptscheme_manager": DummyConceptschemeManager(),
            "audit_manager": DummyAuditManager(),
        }

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        request = self.request
        request.matchdict["scheme_id"] = "TREES"
        request.matchdict["c_id"] = "1"
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info["concept"])
        self.assertEqual(info["conceptType"], "Concept")
        self.assertEqual(info["scheme_id"], "TREES")

    def test_passing_view_with_languague(self):
        request = self.request
        request.matchdict["scheme_id"] = "TREES"
        request.matchdict["c_id"] = "1"
        request.skos_registry = self.regis
        request.skos_registry.providers["TREES"].metadata = {
            "atramhasis.force_display_label_language": "nl"
        }
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info["concept"])
        self.assertEqual(info["locale"], "nl")

    def test_passing_collection_view(self):
        request = self.request
        request.matchdict["scheme_id"] = "TREES"
        request.matchdict["c_id"] = "3"
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        info = atramhasisview.concept_view()
        self.assertIsNotNone(info["concept"])
        self.assertEqual(info["conceptType"], "Collection")
        self.assertEqual(info["scheme_id"], "TREES")

    def test_provider_not_found(self):
        request = self.request
        request.matchdict["scheme_id"] = "ZZ"
        request.matchdict["c_id"] = "1"
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        with self.assertRaises(ConceptSchemeNotFoundException):
            atramhasisview.concept_view()

    def test_not_found(self):
        request = self.request
        request.matchdict["scheme_id"] = "TREES"
        request.matchdict["c_id"] = "666"
        request.skos_registry = self.regis
        atramhasisview = AtramhasisView(request)
        with self.assertRaises(ConceptNotFoundException):
            atramhasisview.concept_view()

    def test_no_type(self):
        request = self.request
        request.matchdict["scheme_id"] = "TREES"
        request.matchdict["c_id"] = "555"
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
        self.request.data_managers = {
            "skos_manager": None,
            "conceptscheme_manager": None,
            "audit_manager": None,
        }

    def tearDown(self):
        testing.tearDown()

    def test_find_by_label(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.params = MultiDict()
        self.request.params.add("label", "De Paardekastanje")
        self.request.params.add("_LOCALE_", "nl")
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info["concepts"])
        concept = info["concepts"][0]
        self.assertIsNotNone(concept)
        self.assertEqual(concept["label"], "De Paardekastanje")
        self.assertEqual(info["scheme_id"], "TREES")

    def test_find_by_concept(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.params = MultiDict()
        self.request.params.add("type", "concept")
        self.request.params.add("_LOCALE_", "nl")
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info["concepts"])
        concept = info["concepts"][0]
        self.assertIsNotNone(concept)
        self.assertEqual(info["scheme_id"], "TREES")

    def test_no_querystring(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.params = MultiDict()
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertIsNotNone(info["concepts"])
        self.assertEqual(len(info["concepts"]), 3)

    def test_no_schema(self):
        self.request.matchdict["scheme_id"] = "GG"
        self.request.params = MultiDict()
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        info = atramhasisview.search_result()
        self.assertEqual(info.status_int, 404)


class TestCsvView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.accept = "*/*"
        self.regis = Registry()
        self.regis.register_provider(provider(1))
        self.request.skos_registry = self.regis
        self.request.data_managers = {
            "skos_manager": DummySKOSManager(),
            "conceptscheme_manager": DummyConceptschemeManager(),
            "audit_manager": DummyAuditManager(),
        }

    def tearDown(self):
        testing.tearDown()

    def test_csv(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.params = MultiDict()
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.results_csv()
        self.assertEqual(res["filename"], "atramhasis_export")
        self.assertIsInstance(res["header"], list)
        self.assertIsInstance(res["rows"], list)
        self.assertEqual(2, len(res["rows"]))

    def test_csv_label(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.params = MultiDict()
        self.request.params.add("label", "De Paardekastanje")
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.results_csv()
        self.assertEqual(res["filename"], "atramhasis_export")
        self.assertIsInstance(res["header"], list)
        self.assertIsInstance(res["rows"], list)
        self.assertEqual(2, len(res["rows"]))

    def test_csv_type(self):
        self.request.matchdict["scheme_id"] = "TREES"
        self.request.params = MultiDict()
        self.request.params.add("type", "concept")
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.results_csv()
        self.assertEqual(res["filename"], "atramhasis_export")
        self.assertIsInstance(res["header"], list)
        self.assertIsInstance(res["rows"], list)
        self.assertEqual(2, len(res["rows"]))


class TestLocaleView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        config = testing.setUp()
        config.add_route("home", "foo")
        config.add_settings(settings)
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            "skos_manager": None,
            "conceptscheme_manager": None,
            "audit_manager": None,
        }

    def tearDown(self):
        testing.tearDown()

    def test_default_locale(self):
        config_default_lang = settings.get("pyramid.default_locale_name")
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue(
            (res.headers.get("Set-Cookie")).startswith(
                "_LOCALE_=" + config_default_lang
            )
        )

    def test_unsupported_lang(self):
        config_default_lang = settings.get("pyramid.default_locale_name")
        self.request.GET["language"] = "XX"
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue(
            (res.headers.get("Set-Cookie")).startswith(
                "_LOCALE_=" + config_default_lang
            )
        )

    def test_locale(self):
        testlang = "it"
        self.request.GET["language"] = testlang
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue(
            (res.headers.get("Set-Cookie")).startswith("_LOCALE_=" + testlang)
        )

    def test_locale_uppercase(self):
        testlang = "it"
        self.request.GET["language"] = testlang.upper()
        self.request.referer = None
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertTrue(
            (res.headers.get("Set-Cookie")).startswith("_LOCALE_=" + testlang)
        )

    def test_referer(self):
        testlang = "it"
        testurl = "http://www.foo.bar"
        self.request.GET["language"] = testlang.upper()
        self.request.referer = testurl
        self.request.skos_registry = self.regis
        atramhasisview = AtramhasisView(self.request)
        res = atramhasisview.set_locale_cookie()
        self.assertEqual(res.status, "302 Found")
        self.assertEqual(res.location, testurl)


class TestHtmlTreeView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            "skos_manager": None,
            "conceptscheme_manager": None,
            "audit_manager": None,
        }

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        self.request.skos_registry = self.regis
        self.request.matchdict["scheme_id"] = "TREES"
        atramhasisview = AtramhasisView(self.request)
        response = atramhasisview.results_tree_html()
        self.assertEqual(response["conceptType"], None)
        self.assertEqual(response["concept"], None)
        self.assertEqual(response["scheme_id"], "TREES")


class TestAdminView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def test_no_registry(self):
        request = testing.DummyRequest()
        with self.assertRaises(SkosRegistryNotFoundException):
            AtramhasisAdminView(request)

    def test_passing_view(self):
        request = testing.DummyRequest()
        request.skos_registry = self.regis
        atramhasis_admin_view = AtramhasisAdminView(request)
        info = atramhasis_admin_view.admin_view()
        self.assertIsNotNone(info)
        self.assertTrue("admin" in info)

    def test_invalidate_scheme_tree(self):
        request = testing.DummyRequest()
        request.matchdict["scheme_id"] = "TREES"
        request.skos_registry = self.regis
        atramhasis_admin_view = AtramhasisAdminView(request)
        info = atramhasis_admin_view.invalidate_scheme_tree()
        self.assertIsNotNone(info)


class TestViewFunctions(unittest.TestCase):
    def test_labels_to_string(self):
        labels = [
            Label(label="De Paardekastanje", language_id="nl"),
            Label(label="la châtaigne", language_id="fr"),
        ]
        s = labels_to_string(labels, "prefLabel")
        self.assertEqual("De Paardekastanje (nl), la châtaigne (fr)", s)

    def test_get_definition(self):
        notes = [
            Note(note="test", language_id="nl", notetype_id="note"),
            Note(note="test2", language_id="nl", notetype_id="definition"),
        ]
        s = get_definition(notes)
        self.assertEqual("test2", s)

    def test_get_public_conceptschemes(self):
        regis = Registry()
        regis.register_provider(trees)
        regis.register_provider(hidden_provider(2))
        regis.register_provider(external_provider(3))
        conceptschemes = get_public_conceptschemes(regis)
        self.assertEqual(1, len(conceptschemes))


class TestListViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.data_managers = {
            "skos_manager": DummySKOSManager(),
        }

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
        self.assertIn({"key": "prefLabel", "label": "prefLabel"}, labellist)


class TestAtramhasisCrudView(unittest.TestCase):
    class SKOSRegistry:
        pass

    class SKOSManager:
        def get_all_label_types(self):
            return [LabelType(name='prefLabel', description=''),
                    LabelType(name='sortLabel', description='')]

        def get_next_cid(self, _, __):
            return "next_cid"

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
        metadata = {'subject': 'stub'}
        conceptscheme_id = 'cs_id'
        uri_generator = DefaultUrnGenerator("voc-id")

        def __init__(self):
            pass

    def setUp(self):
        pyramid_settings = Settings(settings)
        config = testing.setUp(settings=pyramid_settings)
        atramhasis.load_app(config, pyramid_settings)
        self.request = DummyRequest()
        self.request.application_url = "http://localhost:6543"
        apply_request_extensions(self.request)
        self.request.data_managers = {
            "skos_manager": TestAtramhasisCrudView.SKOSManager(),
            "conceptscheme_manager": None,
            "audit_manager": None,
            "languages_manager": TestAtramhasisCrudView.LanguagesManager(),
        }
        self.view = AtramhasisCrud(self.request)
        self.view.skos_registry = TestAtramhasisCrudView.SKOSRegistry()
        self.view.provider = TestAtramhasisCrudView.Provider()
        self.view.scheme_id = "s_id"

    def get_concept_json(self):
        return {
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label": "The Larch"
                },
                {
                    "type": "sortLabel",
                    "language": "en",
                    "label": "a"
                }
            ],
            "notes": [],
            "sources": [
                {
                    "citation": "Citation"
                }
            ]
        }

    def test_add_concept(self):
        self.request.json_body = self.get_concept_json()
        concept = self.view.add_concept()
        self.assertIsInstance(concept, SkosConcept)
        self.assertEqual('next_cid', concept.id)
        self.assertEqual('urn:x-skosprovider:voc-id:next_cid', concept.uri)

    def test_add_concept_manual_id_strategy(self):
        strategy = IDGenerationStrategy.MANUAL
        self.view.provider.metadata['atramhasis.id_generation_strategy'] = strategy
        self.request.json_body = self.get_concept_json()
        self.request.json_body["id"] = 'manual'

        concept = self.view.add_concept()
        self.assertIsInstance(concept, SkosConcept)
        self.assertEqual('manual', concept.id)

        del self.request.json_body["id"]
        with pytest.raises(ValidationError):
            self.view.add_concept()

        # add_concept should fail without id, edit_concept should not because
        # no id validation happens
        self.request.matchdict["c_id"] = 'manual'
        db_concept = Concept()
        db_concept.conceptscheme = ConceptScheme(id=1, uri='urn:x-skosprovider:trees')
        self.request.data_managers["skos_manager"].get_thing = lambda *_: db_concept
        self.view.edit_concept()

    def test_add_provider(self):
        self.request.openapi_validated = Mock()
        self.request.skos_registry = Registry()
        view = 'atramhasis.views.crud'

        with mock.patch(f'{view}.provider.create_provider', autospec=True) as processor, \
                mock.patch(f'{view}.utils.db_provider_to_skosprovider',
                           autospec=True) as renderer:

            response = self.view.add_provider()
            self.assertEqual(201, self.request.response.status_code)
            processor.assert_called()
            renderer.assert_called()
            self.assertEqual(response, renderer.return_value)

    def test_update_provider(self):
        self.request.openapi_validated = Mock()
        self.request.matchdict = {"id": 1}
        view = 'atramhasis.views.crud'

        with mock.patch(f'{view}.provider.update_provider', autospec=True) as processor, \
                mock.patch(f'{view}.utils.db_provider_to_skosprovider',
                           autospec=True) as renderer:

            response = self.view.update_provider()
            processor.assert_called()
            renderer.assert_called()
            self.assertEqual(response, renderer.return_value)

    def test_delete_provider(self):
        self.request.matchdict = {"id": 1}
        view = 'atramhasis.views.crud'

        with mock.patch(f'{view}.provider.delete_provider', autospec=True) as processor:
            response = self.view.delete_provider()
            processor.assert_called()
            self.assertIsInstance(response, HTTPNoContent)
