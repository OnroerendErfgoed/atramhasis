import copy
import logging
import os
import sys
from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import skosprovider.skos
from pyramid.paster import get_appsettings
from pyramid.request import Request
from skosprovider.exceptions import ProviderUnavailableException
from skosprovider.providers import DictionaryProvider
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from sqlalchemy.orm import sessionmaker
from webtest import TestApp

from atramhasis import main
from atramhasis.cache import list_region
from atramhasis.cache import tree_region
from atramhasis.data.models import Provider
from atramhasis.protected_resources import ProtectedResourceEvent
from atramhasis.protected_resources import ProtectedResourceException
from fixtures.data import chestnut
from fixtures.data import larch
from fixtures.data import species
from tests import SETTINGS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, "../", "tests/conf_test.ini"))

_JSON_VALUE = {
    "type": "concept",
    "broader": [],
    "narrower": [],
    "related": [],
    "labels": [
        {"type": "prefLabel", "language": "en", "label": "The Larch"},
        {"type": "sortLabel", "language": "en", "label": "a"},
    ],
    "notes": [],
    "sources": [
        {
            "citation": "Python, M.: Episode Three: How to recognise different types of trees from quite a long way away."
        }
    ],
}

_JSON_VALUE_RELATIONS = {
    "broader": [{"id": "12"}],
    "id": "13",
    "related": [],
    "type": "concept",
    "labels": [{"label": "koperlegeringen", "language": "nl", "type": "prefLabel"}],
    "label": "koperlegeringen",
    "notes": [],
    "narrower": [{"id": "15"}, {"id": "14"}],
}

_JSON_VALUE_INVALID = """{
    "type": "concept",
    "broader": [],
    "narrower": [],
    "related"[]: [],
    "labels": [
        {
            "type": "prefLabel",
            "language": "en",
            "label": "The Larch"
        }
    ],
    "notes": []}
}"""

_JSON_COLLECTION_VALUE = {
    "labels": [{"language": "nl", "label": "Test verzameling", "type": "prefLabel"}],
    "type": "collection",
    "label": "Test verzameling",
    "members": [{"id": "333"}, {"id": "7"}],
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
    "infer_concept_relations": True,
}

TEST = DictionaryProvider(
    {"id": "TEST", "default_language": "nl", "subject": ["biology"]},
    [larch, chestnut, species],
    concept_scheme=skosprovider.skos.ConceptScheme("http://id.trees.org"),
)


def mock_event_handler(event):
    if event.uri == "urn:x-vioe:geography:9":
        referenced_in = ["urn:someobject", "https://test.test.org/object/2"]
        raise ProtectedResourceException(
            f"resource {event.uri} is still in use, preventing operation",
            referenced_in,
        )


def mock_event_handler_provider_unavailable(event):
    if event.uri == "urn:x-vioe:geography:55":
        raise ProviderUnavailableException("test msg")


@pytest.fixture(scope="session")
def testapp():
    """Session-scoped Pyramid/WebTest app (created once, reused across tests)."""
    app = main({}, **SETTINGS)
    test_app = TestApp(app)

    class CommittingRequest(Request):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_finished_callback(lambda req: req.db.commit())

    test_app.app.request_factory = CommittingRequest
    return test_app


@pytest.fixture(autouse=True)
def reset_testapp(testapp, db_connection, db_transaction):
    """Bind a fresh per-test connection and transaction, then reset app state."""
    testapp.app.registry.dbmaker = sessionmaker(
        bind=db_connection,
        join_transaction_mode="rollback_only",
    )
    testapp.reset()


@pytest.fixture
def json_value():
    return copy.deepcopy(_JSON_VALUE)


@pytest.fixture
def json_collection_value():
    return copy.deepcopy(_JSON_COLLECTION_VALUE)


class TestTransactionIsolation:
    """Verify that test-level transaction rollback actually works.

    Each test independently proves isolation: it inserts a row with a unique
    id, commits, verifies it exists, and then a *second* test checks the same
    id is absent.  Because both tests use the same id, whichever runs first
    proves that its committed row was rolled back before the other ran.
    """

    _ISOLATION_ID = 999
    _ISOLATION_URI = "urn:x-test:isolation"

    def _insert_and_verify(self, db_session):
        db_session.add(ConceptScheme(id=self._ISOLATION_ID, uri=self._ISOLATION_URI))
        db_session.commit()
        assert db_session.get(ConceptScheme, self._ISOLATION_ID) is not None

    def test_isolation_a(self, db_session):
        assert db_session.get(ConceptScheme, self._ISOLATION_ID) is None
        self._insert_and_verify(db_session)

    def test_isolation_b(self, db_session):
        assert db_session.get(ConceptScheme, self._ISOLATION_ID) is None
        self._insert_and_verify(db_session)


class TestHtmlFunctional:
    def _get_default_headers(self):
        return {"Accept": "text/html"}

    def test_get_home(self, testapp):
        res = testapp.get("/", headers=self._get_default_headers())
        assert "200 OK" == res.status
        assert "text/html" in res.headers["Content-Type"]

    def test_get_unknown_conceptscheme(self, testapp):
        res = testapp.get(
            "/conceptschemes/does-not-exist",
            headers=self._get_default_headers(),
            status=404,
        )
        assert "niet gevonden" in res.text

    def test_exception_page(self, testapp):
        with mock.patch(
            "atramhasis.views.views.get_public_conceptschemes",
            side_effect=Exception("Test exception"),
        ):
            res = testapp.get(
                "/conceptschemes/does-not-exist",
                headers=self._get_default_headers(),
                status=500,
            )
            assert "technisch probleem" in res.text


class TestCsvFunctional:
    def test_get_csv(self, testapp):
        response = testapp.get("/conceptschemes/TREES/c.csv?type=collection&label=")
        assert "200 OK" == response.status
        assert "text/csv" in response.headers["Content-Type"]
        assert (
            'attachment;filename="atramhasis_export.csv"'
            in response.headers["Content-Disposition"]
        )

    def test_unicode_csv(self, testapp):
        response = testapp.get("/conceptschemes/TREES/c.csv?label=Chestnut&_LOCALE_=fr")
        data = response.body.decode("utf-8")
        assert isinstance(data, str)
        assert "200 OK" == response.status
        assert "text/csv" in response.headers["Content-Type"]
        assert (
            'attachment;filename="atramhasis_export.csv"'
            in response.headers["Content-Disposition"]
        )
        assert "la ch\u00e2taigne" in data

    def test_get_csv_all(self, testapp):
        response = testapp.get("/conceptschemes/TREES/c.csv")
        assert "200 OK" == response.status
        assert "text/csv" in response.headers["Content-Type"]
        assert (
            'attachment;filename="atramhasis_export.csv"'
            in response.headers["Content-Disposition"]
        )


class TestRestFunctional:
    def _get_default_headers(self):
        return {"Accept": "application/json"}

    def test_get_concept(self, testapp):
        res = testapp.get(
            "/conceptschemes/TREES/c/1", headers=self._get_default_headers()
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["id"] == "1"
        assert res.json["type"] == "concept"
        assert "sortLabel" in [label["type"] for label in res.json["labels"]]

    def test_get_conceptscheme(self, testapp):
        res = testapp.get("/conceptschemes/TREES", headers=self._get_default_headers())
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None

    def test_get_concept_dictprovider(self, testapp):
        res = testapp.get(
            "/conceptschemes/TEST/c/1", headers=self._get_default_headers()
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["type"] == "concept"

    def test_get_concept_not_found(self, testapp):
        res = testapp.get(
            "/conceptschemes/TREES/c/89",
            headers=self._get_default_headers(),
            status=404,
            expect_errors=True,
        )
        assert "404 Not Found" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_get_concept_dictprovider_not_found(self, testapp):
        res = testapp.get(
            "/conceptschemes/TEST/c/89",
            headers=self._get_default_headers(),
            status=404,
            expect_errors=True,
        )
        assert "404 Not Found" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_add_concept(self, testapp, json_value):
        res = testapp.post_json(
            "/conceptschemes/TREES/c",
            headers=self._get_default_headers(),
            params=json_value,
        )
        assert "201 Created" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["type"] == "concept"

    def test_add_update_concept_manual_id(self, testapp, json_value):
        json_value["id"] = "manual-3"
        json_value["sources"][0]["citation"] = "short"
        res = testapp.post_json(
            "/conceptschemes/manual-ids/c",
            headers=self._get_default_headers(),
            params=json_value,
        )
        assert 201 == res.status_code
        res_json = res.json
        assert {
            "id": "manual-3",
            "type": "concept",
            "uri": "urn:x-skosprovider:manual-ids:manual-3",
            "label": "The Larch",
            "concept_scheme": {"uri": "urn:x-vioe:manual", "labels": []},
            "labels": [
                {"label": "The Larch", "type": "prefLabel", "language": "en"},
                {"label": "a", "type": "sortLabel", "language": "en"},
            ],
            "notes": [],
            "sources": [{"citation": "short", "markup": None}],
            "narrower": [],
            "broader": [],
            "related": [],
            "member_of": [],
            "subordinate_arrays": [],
            "matches": {
                "close": [],
                "exact": [],
                "related": [],
                "broad": [],
                "narrow": [],
            },
        } == res_json
        res_json["labels"][0]["label"] = "updated"
        res = testapp.put_json(
            "/conceptschemes/manual-ids/c/manual-3",
            headers=self._get_default_headers(),
            params=res_json,
        )
        assert 200 == res.status_code
        assert "updated" == res.json["label"]

    def test_add_concept_empty_conceptscheme(self, testapp, json_value):
        res = testapp.post_json(
            "/conceptschemes/STYLES/c",
            headers=self._get_default_headers(),
            params=json_value,
        )
        assert "201 Created" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None

    def test_add_concept_invalid_json(self, testapp):
        res = testapp.post_json(
            "/conceptschemes/TREES/c",
            headers=self._get_default_headers(),
            params=_JSON_VALUE_INVALID,
            status=400,
        )
        assert "400 Bad Request" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_add_concept_conceptscheme_not_found(self, testapp, json_value):
        res = testapp.post_json(
            "/conceptschemes/GARDENNNN/c",
            headers=self._get_default_headers(),
            params=json_value,
            status=404,
            expect_errors=True,
        )
        assert "404 Not Found" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_edit_conceptscheme(self, testapp, json_collection_value):
        res = testapp.put_json(
            "/conceptschemes/TREES",
            headers=self._get_default_headers(),
            params=json_collection_value,
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_edit_conceptscheme_invalid(self, testapp, json_collection_value):
        json_collection_value.pop("labels")
        res = testapp.put_json(
            "/conceptschemes/TREES",
            headers=self._get_default_headers(),
            params=json_collection_value,
            expect_errors=True,
        )
        assert "400 Bad Request" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {
            "errors": ["labels: 'labels' is a required property"],
            "message": "Request was not valid for schema.",
        }

    def test_edit_concept(self, testapp, json_value):
        res = testapp.put_json(
            "/conceptschemes/TREES/c/1",
            headers=self._get_default_headers(),
            params=json_value,
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_edit_concept_has_relations(self, testapp):
        res = testapp.put_json(
            "/conceptschemes/MATERIALS/c/13",
            headers=self._get_default_headers(),
            params=_JSON_VALUE_RELATIONS,
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert 2 == len(res.json["narrower"])

    def test_edit_concept_not_found(self, testapp, json_value):
        res = testapp.put_json(
            "/conceptschemes/TREES/c/89",
            headers=self._get_default_headers(),
            params=json_value,
            status=404,
            expect_errors=True,
        )
        assert "404 Not Found" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_delete_concept(self, testapp):
        testapp.delete(
            "/conceptschemes/TREES/c/1",
            headers=self._get_default_headers(),
            status=204,
        )

    def test_delete_concept_not_found(self, testapp):
        res = testapp.delete(
            "/conceptschemes/TREES/c/7895",
            headers=self._get_default_headers(),
            expect_errors=True,
        )
        assert "404 Not Found" == res.status

    def test_add_collection(self, testapp, json_collection_value):
        res = testapp.post_json(
            "/conceptschemes/GEOGRAPHY/c",
            headers=self._get_default_headers(),
            params=json_collection_value,
            expect_errors=True,
        )
        assert "201 Created" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["type"] == "collection"

    def test_edit_collection(self, testapp, json_collection_value):
        json_collection_value["members"] = [{"id": "7"}, {"id": "8"}]
        json_collection_value["infer_concept_relations"] = False
        res = testapp.put_json(
            "/conceptschemes/GEOGRAPHY/c/333",
            headers=self._get_default_headers(),
            params=json_collection_value,
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["type"] == "collection"
        assert 2 == len(res.json["members"])
        assert not res.json["infer_concept_relations"]

    def test_delete_collection(self, testapp):
        testapp.delete(
            "/conceptschemes/GEOGRAPHY/c/333",
            headers=self._get_default_headers(),
            status=204,
        )

    def test_uri(self, testapp, json_value):
        res = testapp.post_json(
            "/conceptschemes/MATERIALS/c",
            headers=self._get_default_headers(),
            params=json_value,
        )
        assert "201 Created" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert "urn:x-vioe:materials:51" == res.json["uri"]

    def test_provider_unavailable_view(self, testapp):
        def raise_provider_unavailable_exception():
            raise ProviderUnavailableException("test msg")

        with patch(
            "atramhasis.views.crud.AtramhasisCrud.delete_concept",
            Mock(side_effect=raise_provider_unavailable_exception),
        ):
            res = testapp.delete(
                "/conceptschemes/GEOGRAPHY/c/55",
                headers=self._get_default_headers(),
                status=503,
            )
            assert "503 Service Unavailable" == res.status
            assert "test msg" in res

    def test_get_languages(self, testapp):
        res = testapp.get("/languages", headers=self._get_default_headers())
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res is not None
        assert len(res.json) == 8

    def test_get_languages_sort(self, testapp):
        res = testapp.get(
            "/languages", headers=self._get_default_headers(), params={"sort": "id"}
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res is not None
        assert len(res.json) == 8

    def test_get_languages_sort_desc(self, testapp):
        res = testapp.get(
            "/languages", headers=self._get_default_headers(), params={"sort": "-id"}
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res is not None
        assert len(res.json) == 8

    def test_get_language(self, testapp):
        res = testapp.get("/languages/de", headers=self._get_default_headers())
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert "German" == res.json["name"]

    def test_get_language_not_found(self, testapp):
        res = testapp.get(
            "/languages/jos", headers=self._get_default_headers(), expect_errors=True
        )
        assert "404 Not Found" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {"message": "The resource could not be found."}

    def test_add_language(self, testapp):
        res = testapp.put_json(
            "/languages/af",
            headers=self._get_default_headers(),
            params={"id": "af", "name": "Afrikaans"},
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["name"] == "Afrikaans"

    def test_add_language_non_valid(self, testapp):
        res = testapp.put_json(
            "/languages/flup",
            headers=self._get_default_headers(),
            params={"id": "flup", "name": "flup"},
            expect_errors=True,
        )
        assert "400 Bad Request" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {
            "errors": [
                {
                    "id": "Invalid language tag: Unknown code 'flup', Missing language tag in 'flup'."
                }
            ],
            "message": "Language could not be validated",
        }

    def test_add_language_non_valid_json(self, testapp):
        res = testapp.put_json(
            "/languages/af",
            headers=self._get_default_headers(),
            params={"test": "flup"},
            expect_errors=True,
        )
        assert "400 Bad Request" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {
            "errors": {"name": "Required"},
            "message": "Language could not be validated",
        }

    def test_edit_language(self, testapp):
        res = testapp.put_json(
            "/languages/de",
            headers=self._get_default_headers(),
            params={"id": "de", "name": "Duits"},
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["name"] == "Duits"

    def test_edit_language_invalid_language_tag(self, testapp):
        res = testapp.put_json(
            "/languages/joss",
            headers=self._get_default_headers(),
            params={"id": "joss", "name": "Duits"},
            expect_errors=True,
        )
        assert "400 Bad Request" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {
            "errors": [
                {
                    "id": "Invalid language tag: Unknown code 'joss', Missing language tag in 'joss'."
                }
            ],
            "message": "Language could not be validated",
        }

    def test_edit_language_no_id(self, testapp):
        res = testapp.put_json(
            "/languages/de",
            headers=self._get_default_headers(),
            params={"name": "Duits"},
        )
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json["id"] is not None
        assert res.json["name"] == "Duits"

    def test_delete_language(self, testapp):
        res = testapp.delete("/languages/de", headers=self._get_default_headers())
        assert "200 OK" == res.status
        assert "application/json" in res.headers["Content-Type"]

    def test_delete_language_not_found(self, testapp):
        res = testapp.delete(
            "/languages/jos", headers=self._get_default_headers(), expect_errors=True
        )
        assert "404 Not Found" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {"message": "The resource could not be found."}

    def test_delete_protected_resource(self, testapp):
        def mock_event_handler(event):
            if isinstance(event, ProtectedResourceEvent):
                referenced_in = ["urn:someobject", "https://test.test.org/object/2"]
                raise ProtectedResourceException(
                    "resource {} is still in use, preventing operation".format(
                        event.uri
                    ),
                    referenced_in,
                )

        registry = testapp.app.registry
        with patch.object(registry, "notify", new=Mock(side_effect=mock_event_handler)):
            res = testapp.delete(
                "/conceptschemes/GEOGRAPHY/c/9",
                headers=self._get_default_headers(),
                expect_errors=True,
            )
        assert "409 Conflict" == res.status
        assert "application/json" in res.headers["Content-Type"]
        assert res.json is not None
        assert res.json == {
            "message": "resource urn:x-vioe:geography:9 is still in use, preventing operation",
            "referenced_in": ["urn:someobject", "https://test.test.org/object/2"],
        }

    def test_get_conceptschemes(self, testapp):
        testapp.get("/conceptschemes", headers=self._get_default_headers(), status=200)

    def test_create_provider_openapi_validation(self, testapp):
        response = testapp.post_json(
            url="/providers",
            params={"uri_pattern": "invalid", "subject": "wrong"},
            headers=self._get_default_headers(),
            expect_errors=True,
        )
        assert {
            "errors": [
                "subject: 'wrong' is not of type 'array'",
                "subject: 'conceptscheme_uri' is a required property",
            ],
            "message": "Request was not valid for schema.",
        } == response.json
        testapp.post_json(
            url="/providers",
            params={"uri_pattern": "invalid", "subject": ["right"]},
            headers=self._get_default_headers(),
            expect_errors=True,
        )

    def test_create_minimal_provider(self, testapp):
        response = testapp.post_json(
            url="/providers",
            params={
                "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
                "uri_pattern": "https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
            },
            headers=self._get_default_headers(),
            status=201,
        )
        assert {
            "id": response.json["id"],
            "type": "SQLAlchemyProvider",
            "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
            "uri_pattern": "https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
            "default_language": None,
            "subject": [],
            "force_display_language": None,
            "metadata": {},
            "id_generation_strategy": "NUMERIC",
            "expand_strategy": "recurse",
        } == response.json

    def test_create_full_provider(self, testapp):
        response = testapp.post_json(
            url="/providers",
            params={
                "id": "ERFGOEDTYPES",
                "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
                "uri_pattern": "https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
                "default_language": "NL",
                "force_display_language": "NL",
                "subject": ["hidden"],
                "metadata": {"Info": "Extra data about this provider"},
                "id_generation_strategy": "MANUAL",
                "expand_strategy": "visit",
            },
            headers=self._get_default_headers(),
            status=201,
        )
        assert {
            "id": "ERFGOEDTYPES",
            "type": "SQLAlchemyProvider",
            "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
            "uri_pattern": "https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
            "default_language": "NL",
            "force_display_language": "NL",
            "subject": ["hidden"],
            "metadata": {"Info": "Extra data about this provider"},
            "id_generation_strategy": "MANUAL",
            "expand_strategy": "visit",
        } == response.json

    def test_create_full_provider_via_put(self, testapp):
        response = testapp.put_json(
            url="/providers/ERFGOEDTYPES",
            params={
                "id": "ERFGOEDTYPES",
                "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
                "uri_pattern": "https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
                "default_language": "NL",
                "force_display_language": "NL",
                "subject": ["hidden"],
                "metadata": {"Info": "Extra data about this provider"},
                "id_generation_strategy": "MANUAL",
                "expand_strategy": "visit",
            },
            headers=self._get_default_headers(),
            status=201,
        )
        assert {
            "id": "ERFGOEDTYPES",
            "type": "SQLAlchemyProvider",
            "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
            "uri_pattern": "https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
            "default_language": "NL",
            "force_display_language": "NL",
            "subject": ["hidden"],
            "metadata": {"Info": "Extra data about this provider"},
            "id_generation_strategy": "MANUAL",
            "expand_strategy": "visit",
        } == response.json

    def test_update_provider(self, testapp, db_session):
        conceptscheme = ConceptScheme(
            uri="https://id.erfgoed.net/thesauri/conceptschemes"
        )
        provider = Provider(
            id="ERFGOEDTYPES",
            uri_pattern="https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
            conceptscheme=conceptscheme,
            meta={},
        )
        db_session.add(provider)
        db_session.flush()

        response = testapp.put_json(
            url="/providers/ERFGOEDTYPES",
            params={
                "id": "ERFGOEDTYPES",
                "type": "SQLAlchemyProvider",
                "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
                "uri_pattern": "https://id.erfgoed.net/thesauri/updated/%s",
                "default_language": "NL",
                "subject": ["hidden"],
                "force_display_language": "NL",
                "metadata": {"extra": "test-extra"},
                "id_generation_strategy": "MANUAL",
                "expand_strategy": "visit",
            },
            headers=self._get_default_headers(),
            status=200,
        )

        assert {
            "id": "ERFGOEDTYPES",
            "type": "SQLAlchemyProvider",
            "conceptscheme_uri": "https://id.erfgoed.net/thesauri/conceptschemes",
            "uri_pattern": "https://id.erfgoed.net/thesauri/updated/%s",
            "default_language": "NL",
            "subject": ["hidden"],
            "force_display_language": "NL",
            "metadata": {"extra": "test-extra"},
            "id_generation_strategy": "MANUAL",
            "expand_strategy": "visit",
        } == response.json

    def test_delete_provider_with_concepts(self, testapp, db_session):
        conceptscheme = ConceptScheme(
            uri="https://id.erfgoed.net/thesauri/conceptschemes"
        )
        concept = Concept(concept_id="testconceptje", conceptscheme=conceptscheme)
        provider = Provider(
            id="ERFGOEDTYPES",
            uri_pattern="https://id.erfgoed.net/thesauri/erfgoedtypes/%s",
            conceptscheme=conceptscheme,
            meta={},
        )
        db_session.add(concept)
        db_session.add(provider)
        db_session.flush()
        conceptscheme_id = conceptscheme.id

        db_session.expire_all()
        assert db_session.get(Provider, "ERFGOEDTYPES") is not None

        testapp.delete(
            url="/providers/ERFGOEDTYPES",
            headers=self._get_default_headers(),
            status=204,
        )
        db_session.expire_all()
        assert db_session.get(Provider, "ERFGOEDTYPES") is None
        assert db_session.get(ConceptScheme, conceptscheme_id) is None

    def test_get_providers(self, testapp):
        response = testapp.get(
            url="/providers", headers=self._get_default_headers(), status=200
        )
        assert 7 == len(response.json)
        response = testapp.get(
            url="/providers?subject=biology",
            headers=self._get_default_headers(),
            status=200,
        )
        assert [
            {
                "conceptscheme_uri": "http://id.trees.org",
                "default_language": "nl",
                "force_display_language": None,
                "id": "TEST",
                "subject": ["biology"],
                "type": "DictionaryProvider",
                "uri_pattern": "urn:x-skosprovider:%s:%s",
                "metadata": {},
            }
        ] == response.json

    def test_get_provider(self, testapp):
        response = testapp.get(
            url="/providers/GEOGRAPHY", headers=self._get_default_headers(), status=200
        )
        assert {
            "id": "GEOGRAPHY",
            "type": "SQLAlchemyProvider",
            "conceptscheme_uri": "urn:x-vioe:geography",
            "uri_pattern": "urn:x-vioe:geography:%s",
            "default_language": None,
            "subject": [],
            "force_display_language": None,
            "id_generation_strategy": "NUMERIC",
            "metadata": {},
            "expand_strategy": "recurse",
        } == response.json

    def test_expand_concept(self, testapp):
        res = testapp.get(
            "/conceptschemes/TREES/c/1/expand",
            headers=self._get_default_headers(),
            status=200,
        )
        assert res.json == ["1"]


class TestCookieView:
    def _get_default_headers(self):
        return {"Accept": "text/html"}

    def test_cookie(self, testapp):
        response = testapp.get(
            "/locale?language=nl", headers=self._get_default_headers()
        )
        assert response.headers["Set-Cookie"] is not None
        assert response.status == "302 Found"
        assert (response.headers.get("Set-Cookie")).startswith("_LOCALE_=nl")

    def test_unsupported_language(self, testapp):
        config_default_lang = settings.get("pyramid.default_locale_name")
        response = testapp.get(
            "/locale?language=fr", headers=self._get_default_headers()
        )
        assert (response.headers.get("Set-Cookie")).startswith(
            "_LOCALE_=" + config_default_lang
        )


class TestJsonTreeFunctional:
    def _get_default_headers(self):
        return {"Accept": "application/json"}

    def test_tree(self, testapp):
        response = testapp.get(
            "/conceptschemes/GEOGRAPHY/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert "200 OK" == response.status
        assert "application/json" in response.headers["Content-Type"]
        assert response.json is not None
        assert 2 == len(response.json)
        assert "World" == response.json[0]["label"]

    def test_missing_labels(self, testapp):
        response = testapp.get(
            "/conceptschemes/MISSING_LABEL/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert "200 OK" == response.status
        assert response.json is not None
        assert 2 == len(response.json)
        assert "label" == response.json[0]["label"]
        assert None is response.json[1]["label"]

    def test_tree_language(self, testapp):
        response = testapp.get(
            "/conceptschemes/TREES/tree?language=nl",
            headers=self._get_default_headers(),
        )
        assert 200 == response.status_code
        assert ["De Lariks", "De Paardekastanje"] == [
            child["label"] for child in response.json[0]["children"]
        ]
        response = testapp.get(
            "/conceptschemes/TREES/tree?language=en",
            headers=self._get_default_headers(),
        )
        assert 200 == response.status_code
        assert ["The Chestnut", "The Larch"] == [
            child["label"] for child in response.json[0]["children"]
        ]

    def test_no_tree(self, testapp):
        response = testapp.get(
            "/conceptschemes/FOO/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
            status=404,
            expect_errors=True,
        )
        assert "404 Not Found" == response.status


class TestHtmlTreeFunctional:
    def _get_default_headers(self):
        return {"Accept": "text/html"}

    def test_tree(self, testapp):
        response = testapp.get(
            "/conceptschemes/GEOGRAPHY/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert "200 OK" == response.status
        assert "text/html" in response.headers["Content-Type"]

    def test_no_tree(self, testapp):
        response = testapp.get(
            "/conceptschemes/FOO/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
            status=404,
            expect_errors=True,
        )
        assert "404 Not Found" == response.status


class TestSkosFunctional:
    def _get_default_headers(self):
        return {"Accept": "text/html"}

    def _get_json_headers(self):
        return {"Accept": "application/json"}

    def test_admin_no_skos_provider(self, testapp):
        with patch.dict(testapp.app.request_extensions.descriptors):
            del testapp.app.request_extensions.descriptors["skos_registry"]
            res = testapp.get("/admin", headers=self._get_default_headers(), status=404)
        assert "niet gevonden" in res.text

    def test_crud_no_skos_provider(self, testapp, json_collection_value):
        with patch.dict(testapp.app.request_extensions.descriptors):
            del testapp.app.request_extensions.descriptors["skos_registry"]
            res = testapp.post_json(
                "/conceptschemes/GEOGRAPHY/c",
                headers=self._get_json_headers(),
                params=json_collection_value,
                status=404,
            )
        assert {
            "message": "No SKOS registry found, please check your application setup"
        } == res.json

    def test_match_filter(self, testapp):
        response = testapp.get(
            "/conceptschemes/TREES/c", headers={"Accept": "application/json"}
        )
        assert 200 == response.status_code
        assert 3 == len(response.json)
        response = testapp.get(
            "/conceptschemes/TREES/c"
            "?match=https://id.python.org/different/types/of/trees/nr/1/the/larch",
            headers={"Accept": "application/json"},
        )
        assert 200 == response.status_code
        assert [
            {
                "id": "1",
                "uri": "urn:x-skosprovider:trees/1",
                "type": "concept",
                "label": "De Lariks",
                "@context": "http://localhost/jsonld/context/skos",
            }
        ] == response.json


class TestCacheFunctional:
    def _get_default_headers(self):
        return {"Accept": "application/json"}

    def test_create_cache(self, testapp):
        # clear entire cache before start
        invalidate_cache_response = testapp.get("/admin/tree/invalidate")
        assert "200 OK" == invalidate_cache_response.status

        tree_response = testapp.get(
            "/conceptschemes/MATERIALS/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert "200 OK" == tree_response.status
        assert tree_response.json is not None

        cached_tree_response = testapp.get(
            "/conceptschemes/MATERIALS/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert "200 OK" == cached_tree_response.status
        assert cached_tree_response.json is not None

        assert tree_response.json == cached_tree_response.json

    def test_auto_invalidate_cache(self, testapp):
        tree_region.configure(
            "dogpile.cache.memory",
            expiration_time=7000,
            arguments={"cache_size": 5000},
            replace_existing_backend=True,
        )
        list_region.configure(
            "dogpile.cache.memory",
            expiration_time=7000,
            arguments={"cache_size": 5000},
            replace_existing_backend=True,
        )
        # clear entire cache before start
        invalidate_cache_response = testapp.get("/admin/tree/invalidate")
        assert "200 OK" == invalidate_cache_response.status

        tree_response = testapp.get(
            "/conceptschemes/MATERIALS/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        cached_tree_response = testapp.get(
            "/conceptschemes/MATERIALS/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert tree_response.json == cached_tree_response.json

        testapp.delete(
            "/conceptschemes/MATERIALS/c/31",
            headers=self._get_default_headers(),
            status=204,
        )

        tree_response2 = testapp.get(
            "/conceptschemes/MATERIALS/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert tree_response.json != tree_response2.json

        cached_tree_response2 = testapp.get(
            "/conceptschemes/MATERIALS/tree?_LOCALE_=nl",
            headers=self._get_default_headers(),
        )
        assert tree_response2.json == cached_tree_response2.json

        tree_region.configure("dogpile.cache.null", replace_existing_backend=True)
        list_region.configure("dogpile.cache.null", replace_existing_backend=True)


class TestRdfFunctional:
    def test_void(self, testapp):
        rdf_response = testapp.get("/void.ttl")
        assert "200 OK" == rdf_response.status
        assert "text/turtle" == rdf_response.content_type

    def test_rdf_full_xml(self, testapp):
        rdf_response = testapp.get(
            "/conceptschemes/MATERIALS/c", headers={"Accept": "application/rdf+xml"}
        )
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_full_xml_ext(self, testapp):
        rdf_response = testapp.get("/conceptschemes/MATERIALS/c.rdf")
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_full_turtle(self, testapp):
        ttl_response = testapp.get(
            "/conceptschemes/MATERIALS/c", headers={"Accept": "text/turtle"}
        )
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_full_turtle_ext(self, testapp):
        ttl_response = testapp.get("/conceptschemes/MATERIALS/c.ttl")
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_conceptscheme_xml(self, testapp):
        rdf_response = testapp.get(
            "/conceptschemes/MATERIALS", headers={"Accept": "application/rdf+xml"}
        )
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_conceptscheme_xml_ext(self, testapp):
        rdf_response = testapp.get("/conceptschemes/MATERIALS.rdf")
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_conceptscheme_turtle(self, testapp):
        ttl_response = testapp.get(
            "/conceptschemes/MATERIALS", headers={"Accept": "text/turtle"}
        )
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_conceptscheme_turtle_ext(self, testapp):
        ttl_response = testapp.get("/conceptschemes/MATERIALS.ttl")
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_conceptscheme_jsonld(self, testapp):
        res = testapp.get(
            "/conceptschemes/MATERIALS", headers={"Accept": "application/ld+json"}
        )
        assert "200 OK" == res.status
        assert "application/ld+json" == res.content_type

    def test_rdf_conceptscheme_jsonld_ext(self, testapp):
        res = testapp.get("/conceptschemes/MATERIALS.jsonld")
        assert "200 OK" == res.status
        assert "application/ld+json" == res.content_type

    def test_rdf_individual_jsonld(self, testapp):
        res = testapp.get(
            "/conceptschemes/MATERIALS/c/1", headers={"Accept": "application/ld+json"}
        )
        assert "200 OK" == res.status
        assert "application/ld+json" == res.content_type

    def test_rdf_individual_jsonld_ext(self, testapp):
        res = testapp.get("/conceptschemes/MATERIALS/c/1.jsonld")
        assert "200 OK" == res.status
        assert "application/ld+json" == res.content_type

    def test_rdf_individual_xml(self, testapp):
        rdf_response = testapp.get(
            "/conceptschemes/MATERIALS/c/1", headers={"Accept": "application/rdf+xml"}
        )
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_individual_xml_ext(self, testapp):
        rdf_response = testapp.get("/conceptschemes/MATERIALS/c/1.rdf")
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_individual_turtle(self, testapp):
        ttl_response = testapp.get(
            "/conceptschemes/MATERIALS/c/1", headers={"Accept": "text/turtle"}
        )
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_individual_turtle_ext(self, testapp):
        ttl_response = testapp.get("/conceptschemes/MATERIALS/c/1.ttl")
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_individual_jsonld_ext_manual(self, testapp):
        res = testapp.get("/conceptschemes/manual-ids/c/manual-1.jsonld")
        assert "200 OK" == res.status
        assert "application/ld+json" == res.content_type

    def test_rdf_individual_xml_ext_manual(self, testapp):
        rdf_response = testapp.get("/conceptschemes/manual-ids/c/manual-2.rdf")
        assert "200 OK" == rdf_response.status
        assert "application/rdf+xml" == rdf_response.content_type

    def test_rdf_individual_turtle_manual(self, testapp):
        ttl_response = testapp.get("/conceptschemes/manual-ids/c/manual-1.ttl")
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_individual_turtle_manual_uri(self, testapp):
        ttl_response = testapp.get(
            "/conceptschemes/manual-ids/c/https://id.manual.org/manual/68.ttl"
        )
        assert "200 OK" == ttl_response.status
        assert "text/turtle" == ttl_response.content_type

    def test_rdf_individual_not_found(self, testapp):
        testapp.get(
            "/conceptschemes/TREES/c/test.ttl",
            headers={"Accept": "text/turtle"},
            status=404,
        )


class TestListFunctional:
    def test_labeltypes_list(self, testapp):
        labeltypeslist_res = testapp.get("/labeltypes")
        assert "200 OK" == labeltypeslist_res.status
        assert "application/json" == labeltypeslist_res.content_type
        assert labeltypeslist_res.json is not None
        assert 4 == len(labeltypeslist_res.json)

    def test_notetypes_list(self, testapp):
        labeltypeslist_res = testapp.get("/notetypes")
        assert "200 OK" == labeltypeslist_res.status
        assert "application/json" == labeltypeslist_res.content_type
        assert labeltypeslist_res.json is not None


class TestHeadRequestsFunctional:
    """Test that HEAD requests return the same status code and headers as GET, with no body."""

    def _get_default_headers(self):
        return {"Accept": "application/json"}

    def test_head_languages(self, testapp):
        get_res = testapp.get("/languages", headers=self._get_default_headers())
        head_res = testapp.head("/languages", headers=self._get_default_headers())
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""

    def test_head_language(self, testapp):
        get_res = testapp.get("/languages/de", headers=self._get_default_headers())
        head_res = testapp.head("/languages/de", headers=self._get_default_headers())
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""

    def test_head_labeltypes(self, testapp):
        get_res = testapp.get("/labeltypes", headers=self._get_default_headers())
        head_res = testapp.head("/labeltypes", headers=self._get_default_headers())
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""

    def test_head_notetypes(self, testapp):
        get_res = testapp.get("/notetypes", headers=self._get_default_headers())
        head_res = testapp.head("/notetypes", headers=self._get_default_headers())
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""

    def test_head_concept(self, testapp):
        get_res = testapp.get(
            "/conceptschemes/TREES/c/1", headers=self._get_default_headers()
        )
        head_res = testapp.head(
            "/conceptschemes/TREES/c/1", headers=self._get_default_headers()
        )
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""

    def test_head_conceptscheme(self, testapp):
        get_res = testapp.get(
            "/conceptschemes/TREES", headers=self._get_default_headers()
        )
        head_res = testapp.head(
            "/conceptschemes/TREES", headers=self._get_default_headers()
        )
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""

    def test_head_providers(self, testapp):
        get_res = testapp.get("/providers", headers=self._get_default_headers())
        head_res = testapp.head("/providers", headers=self._get_default_headers())
        assert get_res.status == head_res.status
        assert get_res.content_type == head_res.content_type
        assert head_res.body == b""
