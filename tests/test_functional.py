# -*- coding: utf-8 -*-

import os
import unittest

import six
from pyramid.config import Configurator
from skosprovider_sqlalchemy.models import Base, ConceptScheme
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy.orm import sessionmaker
import transaction
from webtest import TestApp
from pyramid import testing
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config

from atramhasis import includeme
from atramhasis.db import db
from fixtures.data import trees, geo
from fixtures.materials import materials


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
        }
    ],
    "notes": []
}

json_value_relations = {
    "broader": [12],
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
    "narrower": [15, 14]
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
    "members": [333, 7],
    "notes": [{
                  "note": "een notitie",
                  "type": "note",
                  "language": "nl"
              }]
}


class FunctionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.session_maker = sessionmaker(
            bind=cls.engine,
            extension=ZopeTransactionExtension()
        )

    def setUp(self):
        self.config = Configurator(settings=settings)
        self.config.add_route('login', '/auth/login')
        self.config.add_route('logout', '/auth/logout')
        includeme(self.config)

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        Base.metadata.bind = self.engine

        self.config.registry.dbmaker = self.session_maker
        self.config.add_request_method(db, reify=True)

        self.config.include('atramhasis.skos')

        with transaction.manager:
            local_session = self.session_maker()
            import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), local_session)
            import_provider(materials, ConceptScheme(id=4, uri='urn:x-vioe:materials:materials'), local_session)
            import_provider(geo, ConceptScheme(id=2), local_session)

        self.app = self.config.make_wsgi_app()
        self.testapp = TestApp(self.app)

    def tearDown(self):
        testing.tearDown()


class HtmlFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_get_home(self):
        res = self.testapp.get('/', headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('text/html', res.headers['Content-Type'])


class CsvFunctionalTests(FunctionalTests):
    def test_get_csv(self):
        response = self.testapp.get('/conceptschemes/TREES/c.csv?ctype=collection&label=')
        self.assertEqual('200 OK', response.status)
        self.assertIn('text/csv', response.headers['Content-Type'])
        self.assertIn('attachment;filename="atramhasis_export.csv"', response.headers['Content-Disposition'])

    def test_unicode_csv(self):
        response = self.testapp.get('/conceptschemes/TREES/c.csv?label=Chestnut&_LOCALE_=fr')
        data = response.body.decode('utf-8')
        self.assertIsInstance(data, six.text_type)
        self.assertIn('châtaigne', data)


class RestFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    def test_add_concept(self):
        res = self.testapp.post_json('/conceptschemes/TREES/c', headers=self._get_default_headers(), params=json_value)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['type'], 'concept')

    def test_add_concept_empty_conceptscheme(self):
        res = self.testapp.post_json('/conceptschemes/GEOGRAPHY/c', headers=self._get_default_headers(),
                                     params=json_value)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])

    def test_add_concept_invalid_json(self):
        res = self.testapp.post_json(
            '/conceptschemes/TREES/c', headers=self._get_default_headers(), params=json_value_invalid, status=400)
        self.assertEqual('400 Bad Request', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_add_concept_conceptscheme_not_found(self):
        res = self.testapp.post_json(
            '/conceptschemes/GARDENNNN/c', headers=self._get_default_headers(), params=json_value, status=404,
            expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_edit_concept(self):
        res = self.testapp.put_json(
            '/conceptschemes/TREES/c/1', headers=self._get_default_headers(), params=json_value)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_edit_concept_has_relations(self):
        res = self.testapp.put_json(
            '/conceptschemes/MATERIALS/c/13', headers=self._get_default_headers(), params=json_value_relations)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertEqual(2, len(res.json['narrower']))

    def test_edit_concept_not_found(self):
        res = self.testapp.put_json(
            '/conceptschemes/TREES/c/89', headers=self._get_default_headers(), params=json_value, status=404,
            expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_delete_concept(self):
        new_id = 1
        self.assertIsNotNone(new_id)
        res = self.testapp.delete('/conceptschemes/TREES/c/' + str(new_id), headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(new_id, res.json['id'])

    def test_add_collection(self):
        res = self.testapp.post_json('/conceptschemes/GEOGRAPHY/c', headers=self._get_default_headers(),
                                     params=json_collection_value)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(res.json['type'], 'collection')


class TestCookieView(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_cookie(self):
        response = self.testapp.get('/locale?language=nl', headers=self._get_default_headers())
        self.assertIsNotNone(response.headers['Set-Cookie'])
        self.assertEqual(response.status, '302 Found')
        self.assertTrue((response.headers.get('Set-Cookie')).startswith('_LOCALE_=nl'))

    def test_unsupported_language(self):
        config_default_lang = settings.get('pyramid.default_locale_name')
        response = self.testapp.get('/locale?language=fr', headers=self._get_default_headers())
        self.assertTrue((response.headers.get('Set-Cookie')).startswith('_LOCALE_=' + config_default_lang))


class JsonTreeFunctionalTests(FunctionalTests):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    def test_tree(self):
        response = self.testapp.get('/conceptschemes/MATERIALS/tree?_LOCALE_=nl', headers=self._get_default_headers())
        self.assertEqual('200 OK', response.status)
        self.assertIn('application/json', response.headers['Content-Type'])
        self.assertIsNotNone(response.json)
        self.assertEqual('Materiaal', response.json[0]['label'])

    def test_no_tree(self):
        response = self.testapp.get('/conceptschemes/FOO/tree?_LOCALE_=nl', headers=self._get_default_headers(),
                                    status=404, expect_errors=True)
        self.assertEqual('404 Not Found', response.status)


class SkosFunctionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.session_maker = sessionmaker(
            bind=cls.engine,
            extension=ZopeTransactionExtension()
        )

    def setUp(self):
        self.config = Configurator(settings=settings)
        includeme(self.config)

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        Base.metadata.bind = self.engine

        self.config.registry.dbmaker = self.session_maker
        self.config.add_request_method(db, reify=True)

        self.app = self.config.make_wsgi_app()
        del self.app.request_extensions.descriptors['skos_registry']
        self.testapp = TestApp(self.app)

    def tearDown(self):
        testing.tearDown()

    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_admin_no_skos_provider(self):
        res = self.testapp.get('/admin', headers=self._get_default_headers(), expect_errors=True)
        self.assertEqual('500 Internal Server Error', res.status)
        self.assertTrue('message' in res)
        self.assertTrue('No SKOS registry found, please check your application setup' in res)