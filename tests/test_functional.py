import logging
import os
import sys
from unittest.mock import Mock
from unittest.mock import patch

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
from tests import DbTest
from tests import SETTINGS
from tests import fill_db
from tests import setup_db


def setUpModule():
    setup_db()
    fill_db()


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))

json_value = {
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
            "citation": "Python, M.: Episode Three: How to recognise different types of trees from quite a long way away."
        }
    ]
}

json_value_relations = {
    "broader": [{"id": 12}],
    "id": 13,
    "related": [],
    "type": "concept",
    "labels": [{
        "label": "koperlegeringen",
        "language": "nl",
        "type": "prefLabel"
    }],
    "label": "koperlegeringen",
    "notes": [],
    "narrower": [{"id": 15}, {"id": 14}]
}

json_value_invalid = """{
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

json_collection_value = {
    "labels": [{
        "language": "nl",
        "label": "Test verzameling",
        "type": "prefLabel"
    }],
    "type": "collection",
    "label": "Test verzameling",
    "members": [{"id": 333}, {"id": 7}],
    "notes": [{
        "note": "een notitie",
        "type": "note",
        "language": "nl"
    }],
    'infer_concept_relations': True
}

TEST = DictionaryProvider(
    {
        'id': 'TEST',
        'default_language': 'nl',
        'subject': ['biology']
    },
    [larch, chestnut, species],
    concept_scheme=skosprovider.skos.ConceptScheme('http://id.trees.org')
)


class FunctionalTests(DbTest):
    app = None
    testapp = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_app()

    @classmethod
    def init_app(cls):
        cls.app = main({}, **SETTINGS)
        cls.testapp = TestApp(cls.app)

        # Commit at end of every request. This will trigger listeners.
        class CommittingRequest(Request):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.add_finished_callback(lambda req: req.db.commit())

        cls.testapp.app.request_factory = CommittingRequest
        # change db maker to make sessions bound to the test transaction
        registry = cls.testapp.app.registry
        registry.dbmaker = sessionmaker(bind=cls.connection)

    def setUp(self):
        super().setUp()
        self.testapp.reset()

    @staticmethod
    def mock_event_handler(event):
        if event.uri == 'urn:x-vioe:geography:9':
            referenced_in = ['urn:someobject', 'http://test.test.org/object/2']
            raise ProtectedResourceException(
                f'resource {event.uri} is still in use, preventing operation',
                referenced_in)

    @staticmethod
    def mock_event_handler_provider_unavailable(event):
        if event.uri == 'urn:x-vioe:geography:55':
            raise ProviderUnavailableException('test msg')


class HtmlFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_get_home(self):
        res = self.testapp.get('/', headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('text/html', res.headers['Content-Type'])


class CsvFunctionalTests(FunctionalTests):
    def test_get_csv(self):
        response = self.testapp.get('/conceptschemes/TREES/c.csv?type=collection&label=')
        self.assertEqual('200 OK', response.status)
        self.assertIn('text/csv', response.headers['Content-Type'])
        self.assertIn('attachment;filename="atramhasis_export.csv"',
                      response.headers['Content-Disposition'])

    def test_unicode_csv(self):
        response = self.testapp.get(
            '/conceptschemes/TREES/c.csv?label=Chestnut&_LOCALE_=fr')
        data = response.body.decode('utf-8')
        self.assertIsInstance(data, str)
        self.assertEqual('200 OK', response.status)
        self.assertIn('text/csv', response.headers['Content-Type'])
        self.assertIn('attachment;filename="atramhasis_export.csv"',
                      response.headers['Content-Disposition'])
        self.assertIn('la châtaigne', data)

    def test_get_csv_all(self):
        response = self.testapp.get('/conceptschemes/TREES/c.csv')
        self.assertEqual('200 OK', response.status)
        self.assertIn('text/csv', response.headers['Content-Type'])
        self.assertIn('attachment;filename="atramhasis_export.csv"',
                      response.headers['Content-Disposition'])


class RestFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    def test_get_concept(self):
        res = self.testapp.get('/conceptschemes/TREES/c/1',
                               headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['id'], '1')
        self.assertEqual(res.json['type'], 'concept')
        self.assertIn('sortLabel', [label['type'] for label in res.json['labels']])

    def test_get_conceptscheme(self):
        res = self.testapp.get('/conceptschemes/TREES',
                               headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])

    def test_get_concept_dictprovider(self):
        res = self.testapp.get('/conceptschemes/TEST/c/1',
                               headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['type'], 'concept')

    def test_get_concept_not_found(self):
        res = self.testapp.get('/conceptschemes/TREES/c/89',
                               headers=self._get_default_headers(), status=404,
                               expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_get_concept_dictprovider_not_found(self):
        res = self.testapp.get('/conceptschemes/TEST/c/89',
                               headers=self._get_default_headers(), status=404,
                               expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_add_concept(self):
        res = self.testapp.post_json('/conceptschemes/TREES/c',
                                     headers=self._get_default_headers(),
                                     params=json_value)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['type'], 'concept')

    def test_add_update_concept_manual_id(self):
        json_value['id'] = 'manual-3'
        json_value['sources'][0]['citation'] = 'short'
        res = self.testapp.post_json(
            '/conceptschemes/manual-ids/c',
            headers=self._get_default_headers(),
            params=json_value,
        )
        self.assertEqual(201, res.status_code)
        res_json = res.json
        self.assertDictEqual(
            {
                'id': 'manual-3',
                'type': 'concept',
                'uri': 'urn:x-skosprovider:manual-ids:manual-3',
                'label': 'The Larch',
                'concept_scheme': {
                    'uri': 'urn:x-vioe:manual', 'labels': []
                },
                'labels': [
                    {'label': 'The Larch', 'type': 'prefLabel', 'language': 'en'},
                    {'label': 'a', 'type': 'sortLabel', 'language': 'en'}
                ],
                'notes': [],
                'sources': [
                    {'citation': 'short', 'markup': None}
                ],
                'narrower': [],
                'broader': [],
                'related': [],
                'member_of': [],
                'subordinate_arrays': [],
                'matches': {
                    'close': [], 'exact': [], 'related': [], 'broad': [], 'narrow': []
                }
            },
            res_json
        )
        res_json['labels'][0]['label'] = 'updated'
        res = self.testapp.put_json(
            '/conceptschemes/manual-ids/c/manual-3',
            headers=self._get_default_headers(),
            params=res_json,
        )
        self.assertEqual(200, res.status_code)
        self.assertEqual('updated', res.json['label'])

    def test_add_concept_empty_conceptscheme(self):
        res = self.testapp.post_json('/conceptschemes/STYLES/c',
                                     headers=self._get_default_headers(),
                                     params=json_value)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])

    def test_add_concept_invalid_json(self):
        res = self.testapp.post_json(
            '/conceptschemes/TREES/c', headers=self._get_default_headers(),
            params=json_value_invalid, status=400)
        self.assertEqual('400 Bad Request', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_add_concept_conceptscheme_not_found(self):
        res = self.testapp.post_json(
            '/conceptschemes/GARDENNNN/c', headers=self._get_default_headers(),
            params=json_value, status=404,
            expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_edit_conceptscheme(self):
        res = self.testapp.put_json(
            '/conceptschemes/TREES', headers=self._get_default_headers(),
            params=json_collection_value)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_edit_conceptscheme_invalid(self):
        json_collection_value.pop('labels')
        res = self.testapp.put_json(
            '/conceptschemes/TREES', headers=self._get_default_headers(),
            params=json_collection_value,
            expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {
            "errors": [{'labels': 'At least one label is necessary'}],
            "message": 'ConceptScheme could not be validated'})
        json_collection_value['labels'] = [{
            "language": "nl",
            "label": "Test verzameling",
            "type": "prefLabel"
        }]

    def test_edit_concept(self):
        res = self.testapp.put_json(
            '/conceptschemes/TREES/c/1', headers=self._get_default_headers(),
            params=json_value)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_edit_concept_has_relations(self):
        res = self.testapp.put_json(
            '/conceptschemes/MATERIALS/c/13', headers=self._get_default_headers(),
            params=json_value_relations)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertEqual(2, len(res.json['narrower']))

    def test_edit_concept_not_found(self):
        res = self.testapp.put_json(
            '/conceptschemes/TREES/c/89', headers=self._get_default_headers(),
            params=json_value, status=404,
            expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_delete_concept(self):
        new_id = '1'
        res = self.testapp.delete(f'/conceptschemes/TREES/c/{new_id}',
                                  headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(new_id, res.json['id'])
        from skosprovider_sqlalchemy.models import Concept
        concepten = self.session.query(Concept).all()
        print()

    def test_delete_concept_not_found(self):
        res = self.testapp.delete('/conceptschemes/TREES/c/7895',
                                  headers=self._get_default_headers(),
                                  expect_errors=True)
        self.assertEqual('404 Not Found', res.status)

    def test_add_collection(self):
        res = self.testapp.post_json('/conceptschemes/GEOGRAPHY/c',
                                     headers=self._get_default_headers(),
                                     params=json_collection_value, expect_errors=True)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['type'], 'collection')

    def test_edit_collection(self):
        json_collection_value['members'] = [{"id": 7}, {"id": 8}]
        json_collection_value['infer_concept_relations'] = False
        res = self.testapp.put_json('/conceptschemes/GEOGRAPHY/c/333',
                                    headers=self._get_default_headers(),
                                    params=json_collection_value)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['type'], 'collection')
        self.assertEqual(2, len(res.json['members']))
        self.assertFalse(res.json['infer_concept_relations'])

    def test_delete_collection(self):
        res = self.testapp.delete('/conceptschemes/GEOGRAPHY/c/333',
                                  headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_uri(self):
        res = self.testapp.post_json('/conceptschemes/MATERIALS/c',
                                     headers=self._get_default_headers(),
                                     params=json_value)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertEqual('urn:x-vioe:materials:51', res.json['uri'])

    def test_provider_unavailable_view(self):
        def raise_provider_unavailable_exception():
            raise ProviderUnavailableException('test msg')

        with patch('atramhasis.views.crud.AtramhasisCrud.delete_concept',
                   Mock(side_effect=raise_provider_unavailable_exception)):
            res = self.testapp.delete('/conceptschemes/GEOGRAPHY/c/55',
                                      headers=self._get_default_headers(),
                                      expect_errors=True)
            self.assertEqual('503 Service Unavailable', res.status)
            self.assertIn("test msg", res)

    def test_get_languages(self):
        res = self.testapp.get('/languages', headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res)
        self.assertEqual(len(res.json), 8)

    def test_get_languages_sort(self):
        res = self.testapp.get('/languages', headers=self._get_default_headers(),
                               params={"sort": "id"})
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res)
        self.assertEqual(len(res.json), 8)

    def test_get_languages_sort_desc(self):
        res = self.testapp.get('/languages', headers=self._get_default_headers(),
                               params={"sort": "-id"})
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res)
        self.assertEqual(len(res.json), 8)

    def test_get_language(self):
        res = self.testapp.get('/languages/de', headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual('German', res.json['name'])

    def test_get_language_not_found(self):
        res = self.testapp.get('/languages/jos', headers=self._get_default_headers(),
                               expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {"message": "The resource could not be found."})

    def test_add_language(self):
        res = self.testapp.put_json('/languages/af', headers=self._get_default_headers(),
                                    params={"id": "af", "name": "Afrikaans"})
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['name'], 'Afrikaans')

    def test_add_language_non_valid(self):
        res = self.testapp.put_json('/languages/flup',
                                    headers=self._get_default_headers(),
                                    params={"id": "flup", "name": "flup"},
                                    expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {
            "errors": [{
                "id": "Invalid language tag: Unknown code 'flup', Missing language tag in 'flup'."}],
            "message": "Language could not be validated"})

    def test_add_language_non_valid_json(self):
        res = self.testapp.put_json('/languages/af', headers=self._get_default_headers(),
                                    params={"test": "flup"}, expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {'errors': {'name': 'Required'},
                                    'message': 'Language could not be validated'})

    def test_edit_language(self):
        res = self.testapp.put_json('/languages/de', headers=self._get_default_headers(),
                                    params={"id": "de", "name": "Duits"})
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['name'], 'Duits')

    def test_edit_language_invalid_language_tag(self):
        res = self.testapp.put_json('/languages/joss',
                                    headers=self._get_default_headers(),
                                    params={"id": "joss", "name": "Duits"},
                                    expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {
            'errors': [{
                'id': "Invalid language tag: Unknown code 'joss', Missing language tag in 'joss'."}]
            , "message": "Language could not be validated"})

    def test_edit_language_no_id(self):
        res = self.testapp.put_json('/languages/de', headers=self._get_default_headers(),
                                    params={"name": "Duits"})
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['name'], 'Duits')

    def test_delete_language(self):
        res = self.testapp.delete('/languages/de', headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_delete_language_not_found(self):
        res = self.testapp.delete('/languages/jos', headers=self._get_default_headers(),
                                  expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {"message": "The resource could not be found."})

    def test_delete_protected_resource(self):
        def mock_event_handler(event):
            if isinstance(event, ProtectedResourceEvent):
                referenced_in = ['urn:someobject', 'http://test.test.org/object/2']
                raise ProtectedResourceException(
                    'resource {} is still in use, preventing operation'
                    .format(event.uri),
                    referenced_in
                )

        registry = self.testapp.app.registry
        with patch.object(registry, 'notify',
                          new=Mock(side_effect=mock_event_handler)):
            res = self.testapp.delete('/conceptschemes/GEOGRAPHY/c/9',
                                      headers=self._get_default_headers(),
                                      expect_errors=True)
        self.assertEqual('409 Conflict', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json)
        self.assertEqual(res.json, {
            "message": "resource urn:x-vioe:geography:9 is still in use, preventing operation",
            "referenced_in": ["urn:someobject", "http://test.test.org/object/2"]
        })

    def test_method_not_allowed(self):
        self.testapp.delete('/conceptschemes/TREES', headers=self._get_default_headers(),
                            status=405)
        self.testapp.post('/conceptschemes', headers=self._get_default_headers(),
                          status=405)

    def test_get_conceptschemes(self):
        self.testapp.get('/conceptschemes', headers=self._get_default_headers(),
                         status=200)

    def test_create_provider_openapi_validation(self):
        response = self.testapp.post_json(
            url='/providers',
            params={
                'uri_pattern': 'invalid',
                'subject': 'wrong'
            },
            headers=self._get_default_headers(),
            expect_errors=True
        )
        self.assertEqual(
            {
                'errors': ['None: Failed to cast value to array type: wrong'],
                'message': 'Request was not valid for schema.'
            },
            response.json
        )
        response = self.testapp.post_json(
            url='/providers',
            params={
                'uri_pattern': 'invalid',
                'subject': ['right']
            },
            headers=self._get_default_headers(),
            expect_errors=True
        )
        self.assertEqual(
            {
                'errors': [
                    "uri_pattern: 'invalid' does not match '.*%s.*'",
                    "uri_pattern: 'conceptscheme_uri' is a required property"
                ],
                'message': 'Request was not valid for schema.'
            },
            response.json
        )

    def test_create_minimal_provider(self):
        response = self.testapp.post_json(
            url='/providers',
            params={
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/erfgoedtypes/%s'
            },
            headers=self._get_default_headers(),
            status=201
        )
        self.assertEqual(
            {
                'id': response.json["id"],
                'type': 'SQLAlchemyProvider',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
                'default_language': None,
                'subject': [],
                'force_display_language': None,
                'metadata': {},
                'id_generation_strategy': 'NUMERIC',
                'expand_strategy': 'recurse'
            },
            response.json
        )

    def test_create_full_provider(self):
        response = self.testapp.post_json(
            url='/providers',
            params={
                'id': 'ERFGOEDTYPES',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
                'default_language': 'NL',
                'force_display_language': 'NL',
                'subject': ['hidden'],
                'metadata': {'Info': 'Extra data about this provider'},
                'id_generation_strategy': 'MANUAL',
                'expand_strategy': 'visit',
            },
            headers=self._get_default_headers(),
            status=201
        )
        self.assertEqual(
            {
                'id': 'ERFGOEDTYPES',
                'type': 'SQLAlchemyProvider',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
                'default_language': 'NL',
                'force_display_language': 'NL',
                'subject': ['hidden'],
                'metadata': {'Info': 'Extra data about this provider'},
                'id_generation_strategy': 'MANUAL',
                'expand_strategy': 'visit',
            },
            response.json
        )

    def test_create_full_provider_via_put(self):
        response = self.testapp.put_json(
            url='/providers/ERFGOEDTYPES',
            params={
                'id': 'ERFGOEDTYPES',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
                'default_language': 'NL',
                'force_display_language': 'NL',
                'subject': ['hidden'],
                'metadata': {'Info': 'Extra data about this provider'},
                'id_generation_strategy': 'MANUAL',
                'expand_strategy': 'visit',
            },
            headers=self._get_default_headers(),
            status=201
        )
        self.assertEqual(
            {
                'id': 'ERFGOEDTYPES',
                'type': 'SQLAlchemyProvider',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
                'default_language': 'NL',
                'force_display_language': 'NL',
                'subject': ['hidden'],
                'metadata': {'Info': 'Extra data about this provider'},
                'id_generation_strategy': 'MANUAL',
                'expand_strategy': 'visit',
            },
            response.json
        )

    def test_update_provider(self):
        conceptscheme = ConceptScheme(
            uri='https://id.erfgoed.net/thesauri/conceptschemes')
        provider = Provider(
            id='ERFGOEDTYPES',
            uri_pattern='https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
            conceptscheme=conceptscheme,
            meta={},
        )
        self.session.add(provider)
        self.session.flush()

        response = self.testapp.put_json(
            url='/providers/ERFGOEDTYPES',
            params={
                'id': 'ERFGOEDTYPES',
                'type': 'SQLAlchemyProvider',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/updated/%s',
                'default_language': 'NL',
                'subject': ['hidden'],
                'force_display_language': 'NL',
                'metadata': {'extra': 'test-extra'},
                'id_generation_strategy': 'MANUAL',
                'expand_strategy': 'visit'
            },
            headers=self._get_default_headers(),
            status=200
        )

        self.assertEqual(
            {
                'id': 'ERFGOEDTYPES',
                'type': 'SQLAlchemyProvider',
                'conceptscheme_uri': 'https://id.erfgoed.net/thesauri/conceptschemes',
                'uri_pattern': 'https://id.erfgoed.net/thesauri/updated/%s',
                'default_language': 'NL',
                'subject': ['hidden'],
                'force_display_language': 'NL',
                'metadata': {'extra': 'test-extra'},
                'id_generation_strategy': 'MANUAL',
                'expand_strategy': 'visit'
            },
            response.json
        )

    def test_delete_provider_with_concepts(self):
        conceptscheme = ConceptScheme(
            uri='https://id.erfgoed.net/thesauri/conceptschemes')
        concept = Concept(
            concept_id="testconceptje",
            conceptscheme=conceptscheme
        )
        provider = Provider(
            id='ERFGOEDTYPES',
            uri_pattern='https://id.erfgoed.net/thesauri/erfgoedtypes/%s',
            conceptscheme=conceptscheme,
            meta={},
        )
        self.session.add(concept)
        self.session.add(provider)
        self.session.flush()
        conceptscheme_id = conceptscheme.id

        self.session.expire_all()
        self.assertIsNotNone(self.session.get(Provider, 'ERFGOEDTYPES'))

        self.testapp.delete(
            url='/providers/ERFGOEDTYPES',
            headers=self._get_default_headers(),
            status=204
        )
        self.session.expire_all()
        self.assertIsNone(self.session.get(Provider, 'ERFGOEDTYPES'))
        self.assertIsNone(self.session.get(ConceptScheme, conceptscheme_id))

    def test_get_providers(self):
        response = self.testapp.get(
            url='/providers',
            headers=self._get_default_headers(),
            status=200
        )
        self.assertEqual(7, len(response.json))
        response = self.testapp.get(
            url='/providers?subject=biology',
            headers=self._get_default_headers(),
            status=200
        )
        self.assertEqual(
            [
                {
                    'conceptscheme_uri': 'http://id.trees.org',
                    'default_language': 'nl',
                    'force_display_language': None,
                    'id': 'TEST',
                    'subject': ['biology'],
                    'type': 'DictionaryProvider',
                    'uri_pattern': 'urn:x-skosprovider:%s:%s',
                    'metadata': {},
                }
            ],
            response.json)

    def test_get_provider(self):
        response = self.testapp.get(
            url='/providers/GEOGRAPHY',
            headers=self._get_default_headers(),
            status=200
        )
        self.assertEqual(
            {
                'id': 'GEOGRAPHY',
                'type': 'SQLAlchemyProvider',
                'conceptscheme_uri': 'urn:x-vioe:geography',
                'uri_pattern': 'urn:x-vioe:geography:%s',
                'default_language': None,
                'subject': [],
                'force_display_language': None,
                'id_generation_strategy': 'NUMERIC',
                'metadata': {},
                'expand_strategy': 'recurse'
            },
            response.json
        )


class TestCookieView(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_cookie(self):
        response = self.testapp.get('/locale?language=nl',
                                    headers=self._get_default_headers())
        self.assertIsNotNone(response.headers['Set-Cookie'])
        self.assertEqual(response.status, '302 Found')
        self.assertTrue((response.headers.get('Set-Cookie')).startswith('_LOCALE_=nl'))

    def test_unsupported_language(self):
        config_default_lang = settings.get('pyramid.default_locale_name')
        response = self.testapp.get('/locale?language=fr',
                                    headers=self._get_default_headers())
        self.assertTrue((response.headers.get('Set-Cookie')).startswith(
            '_LOCALE_=' + config_default_lang))


class JsonTreeFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    def test_tree(self):
        response = self.testapp.get('/conceptschemes/GEOGRAPHY/tree?_LOCALE_=nl',
                                    headers=self._get_default_headers())
        self.assertEqual('200 OK', response.status)
        self.assertIn('application/json', response.headers['Content-Type'])
        self.assertIsNotNone(response.json)
        self.assertEqual(2, len(response.json))
        self.assertEqual('World', response.json[0]['label'])

    def test_missing_labels(self):
        response = self.testapp.get('/conceptschemes/MISSING_LABEL/tree?_LOCALE_=nl',
                                    headers=self._get_default_headers())
        self.assertEqual('200 OK', response.status)
        self.assertIsNotNone(response.json)
        self.assertEqual(2, len(response.json))
        self.assertEqual('label', response.json[0]['label'])
        self.assertEqual(None, response.json[1]['label'])

    def test_tree_language(self):
        response = self.testapp.get('/conceptschemes/TREES/tree?language=nl',
                                    headers=self._get_default_headers())
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            ['De Lariks', 'De Paardekastanje'],
            [child['label'] for child in response.json[0]['children']]
        )
        response = self.testapp.get('/conceptschemes/TREES/tree?language=en',
                                    headers=self._get_default_headers())
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            ['The Chestnut', 'The Larch'],
            [child['label'] for child in response.json[0]['children']]
        )

    def test_no_tree(self):
        response = self.testapp.get('/conceptschemes/FOO/tree?_LOCALE_=nl',
                                    headers=self._get_default_headers(),
                                    status=404, expect_errors=True)
        self.assertEqual('404 Not Found', response.status)


class HtmlTreeFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_tree(self):
        response = self.testapp.get('/conceptschemes/GEOGRAPHY/tree?_LOCALE_=nl',
                                    headers=self._get_default_headers())
        self.assertEqual('200 OK', response.status)
        self.assertIn('text/html', response.headers['Content-Type'])

    def test_no_tree(self):
        response = self.testapp.get('/conceptschemes/FOO/tree?_LOCALE_=nl',
                                    headers=self._get_default_headers(),
                                    status=404, expect_errors=True)
        self.assertEqual('404 Not Found', response.status)


class SkosFunctionalTests(FunctionalTests):

    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def _get_json_headers(self):
        return {'Accept': 'application/json'}

    def test_admin_no_skos_provider(self):
        with patch.dict(self.app.request_extensions.descriptors):
            del self.app.request_extensions.descriptors['skos_registry']
            res = self.testapp.get('/admin', headers=self._get_default_headers(),
                                   expect_errors=True)
        self.assertEqual('500 Internal Server Error', res.status)
        self.assertTrue('message' in res)
        self.assertTrue(
            'No SKOS registry found, please check your application setup' in res)

    def test_crud_no_skos_provider(self):
        with patch.dict(self.app.request_extensions.descriptors):
            del self.app.request_extensions.descriptors['skos_registry']
            res = self.testapp.post_json('/conceptschemes/GEOGRAPHY/c',
                                         headers=self._get_json_headers(),
                                         params=json_collection_value, expect_errors=True)
        self.assertEqual('500 Internal Server Error', res.status)
        self.assertTrue('message' in res)
        self.assertTrue(
            'No SKOS registry found, please check your application setup' in res)

    def test_match_filter(self):
        response = self.testapp.get(
            '/conceptschemes/TREES/c',
            headers={'Accept': 'application/json'}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.json))
        response = self.testapp.get(
            '/conceptschemes/TREES/c'
            '?match=http://id.python.org/different/types/of/trees/nr/1/the/larch',
            headers={'Accept': 'application/json'}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [
                {
                    'id': '1',
                    'uri': 'urn:x-skosprovider:trees/1',
                    'type': 'concept',
                    'label': 'De Lariks',
                    '@context': 'http://localhost/jsonld/context/skos'
                }
            ],
            response.json
        )


class CacheFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    def test_create_cache(self):
        # clear entire cache before start
        invalidate_cache_response = self.testapp.get('/admin/tree/invalidate')
        self.assertEqual('200 OK', invalidate_cache_response.status)

        tree_response = self.testapp.get('/conceptschemes/MATERIALS/tree?_LOCALE_=nl',
                                         headers=self._get_default_headers())
        self.assertEqual('200 OK', tree_response.status)
        self.assertIsNotNone(tree_response.json)

        cached_tree_response = self.testapp.get(
            '/conceptschemes/MATERIALS/tree?_LOCALE_=nl',
            headers=self._get_default_headers())
        self.assertEqual('200 OK', cached_tree_response.status)
        self.assertIsNotNone(cached_tree_response.json)

        self.assertEqual(tree_response.json, cached_tree_response.json)

    def test_auto_invalidate_cache(self):
        tree_region.configure('dogpile.cache.memory',
                              expiration_time=7000,
                              arguments={'cache_size': 5000},
                              replace_existing_backend=True)
        list_region.configure('dogpile.cache.memory',
                              expiration_time=7000,
                              arguments={'cache_size': 5000},
                              replace_existing_backend=True)
        # clear entire cache before start
        invalidate_cache_response = self.testapp.get('/admin/tree/invalidate')
        self.assertEqual('200 OK', invalidate_cache_response.status)

        tree_response = self.testapp.get('/conceptschemes/MATERIALS/tree?_LOCALE_=nl',
                                         headers=self._get_default_headers())
        cached_tree_response = self.testapp.get(
            '/conceptschemes/MATERIALS/tree?_LOCALE_=nl',
            headers=self._get_default_headers())
        self.assertEqual(tree_response.json, cached_tree_response.json)

        delete_response = self.testapp.delete('/conceptschemes/MATERIALS/c/31',
                                              headers=self._get_default_headers())
        self.assertEqual('200 OK', delete_response.status)
        self.assertIsNotNone(delete_response.json['id'])

        tree_response2 = self.testapp.get('/conceptschemes/MATERIALS/tree?_LOCALE_=nl',
                                          headers=self._get_default_headers())
        self.assertNotEqual(tree_response.json, tree_response2.json)

        cached_tree_response2 = self.testapp.get(
            '/conceptschemes/MATERIALS/tree?_LOCALE_=nl',
            headers=self._get_default_headers())
        self.assertEqual(tree_response2.json, cached_tree_response2.json)

        tree_region.configure('dogpile.cache.null', replace_existing_backend=True)
        list_region.configure('dogpile.cache.null', replace_existing_backend=True)


class RdfFunctionalTests(FunctionalTests):

    def test_void(self):
        rdf_response = self.testapp.get('/void.ttl')
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('text/turtle', rdf_response.content_type)

    def test_rdf_full_xml(self):
        rdf_response = self.testapp.get('/conceptschemes/MATERIALS/c',
                                        headers={'Accept': 'application/rdf+xml'})
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_full_xml_ext(self):
        rdf_response = self.testapp.get('/conceptschemes/MATERIALS/c.rdf')
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_full_turtle(self):
        ttl_response = self.testapp.get('/conceptschemes/MATERIALS/c',
                                        headers={'Accept': 'text/turtle'})
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_full_turtle_ext(self):
        ttl_response = self.testapp.get('/conceptschemes/MATERIALS/c.ttl')
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_conceptscheme_xml(self):
        rdf_response = self.testapp.get('/conceptschemes/MATERIALS',
                                        headers={'Accept': 'application/rdf+xml'})
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_conceptscheme_xml_ext(self):
        rdf_response = self.testapp.get('/conceptschemes/MATERIALS.rdf')
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_conceptscheme_turtle(self):
        ttl_response = self.testapp.get('/conceptschemes/MATERIALS',
                                        headers={'Accept': 'text/turtle'})
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_conceptscheme_turtle_ext(self):
        ttl_response = self.testapp.get('/conceptschemes/MATERIALS.ttl')
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_conceptscheme_jsonld(self):
        res = self.testapp.get('/conceptschemes/MATERIALS',
                               headers={'Accept': 'application/ld+json'})
        self.assertEqual('200 OK', res.status)
        self.assertEqual('application/ld+json', res.content_type)

    def test_rdf_conceptscheme_jsonld_ext(self):
        res = self.testapp.get('/conceptschemes/MATERIALS.jsonld')
        self.assertEqual('200 OK', res.status)
        self.assertEqual('application/ld+json', res.content_type)

    def test_rdf_individual_jsonld(self):
        res = self.testapp.get('/conceptschemes/MATERIALS/c/1',
                               headers={'Accept': 'application/ld+json'})
        self.assertEqual('200 OK', res.status)
        self.assertEqual('application/ld+json', res.content_type)

    def test_rdf_individual_jsonld_ext(self):
        res = self.testapp.get('/conceptschemes/MATERIALS/c/1.jsonld')
        self.assertEqual('200 OK', res.status)
        self.assertEqual('application/ld+json', res.content_type)

    def test_rdf_individual_xml(self):
        rdf_response = self.testapp.get('/conceptschemes/MATERIALS/c/1',
                                        headers={'Accept': 'application/rdf+xml'})
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_individual_xml_ext(self):
        rdf_response = self.testapp.get('/conceptschemes/MATERIALS/c/1.rdf')
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_individual_turtle(self):
        ttl_response = self.testapp.get('/conceptschemes/MATERIALS/c/1',
                                        headers={'Accept': 'text/turtle'})
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_individual_turtle_ext(self):
        ttl_response = self.testapp.get('/conceptschemes/MATERIALS/c/1.ttl')
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_individual_jsonld_ext_manual(self):
        res = self.testapp.get('/conceptschemes/manual-ids/c/manual-1.jsonld')
        self.assertEqual('200 OK', res.status)
        self.assertEqual('application/ld+json', res.content_type)

    def test_rdf_individual_xml_ext_manual(self):
        rdf_response = self.testapp.get('/conceptschemes/manual-ids/c/manual-2.rdf')
        self.assertEqual('200 OK', rdf_response.status)
        self.assertEqual('application/rdf+xml', rdf_response.content_type)

    def test_rdf_individual_turtle_manual(self):
        ttl_response = self.testapp.get('/conceptschemes/manual-ids/c/manual-1.ttl')
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_individual_turtle_manual_uri(self):
        ttl_response = self.testapp.get(
            '/conceptschemes/manual-ids/c/http://id.manual.org/manual/68.ttl')
        self.assertEqual('200 OK', ttl_response.status)
        self.assertEqual('text/turtle', ttl_response.content_type)

    def test_rdf_individual_not_found(self):
        res = self.testapp.get('/conceptschemes/TREES/c/test.ttl',
                               headers={'Accept': 'text/turtle'}, status=404,
                               expect_errors=True)
        self.assertEqual('404 Not Found', res.status)


class ListFunctionalTests(FunctionalTests):
    def test_labeltypes_list(self):
        labeltypeslist_res = self.testapp.get('/labeltypes')
        self.assertEqual('200 OK', labeltypeslist_res.status)
        self.assertEqual('application/json', labeltypeslist_res.content_type)
        self.assertIsNotNone(labeltypeslist_res.json)
        self.assertEqual(4, len(labeltypeslist_res.json))

    def test_notetypes_list(self):
        labeltypeslist_res = self.testapp.get('/notetypes')
        self.assertEqual('200 OK', labeltypeslist_res.status)
        self.assertEqual('application/json', labeltypeslist_res.content_type)
        self.assertIsNotNone(labeltypeslist_res.json)
