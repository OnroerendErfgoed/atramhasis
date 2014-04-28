import os
import unittest
from pyramid.config import Configurator
from skosprovider_sqlalchemy.models import Base, Thing, ConceptScheme
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy.orm import sessionmaker
import transaction
from webtest import TestApp

from pyramid import testing
from zope.sqlalchemy import ZopeTransactionExtension
from atramhasis import includeme
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config, func
from atramhasis.db import db
from tests.fixtures.data import trees

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))

json_string = {
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
        includeme(self.config)

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        Base.metadata.bind = self.engine

        self.config.registry.dbmaker = self.session_maker
        self.config.add_request_method(db, reify=True)

        self.config.include('atramhasis.skos')

        with transaction.manager:
            import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), self.session_maker())

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


class RestFunctionalTests(FunctionalTests):

    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    def test_add_concept(self):
        res = self.testapp.post_json('/conceptschemes/TREES/c', headers=self._get_default_headers(), params=json_string)
        self.assertEqual('201 Created', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsNotNone(res.json['id'])

    # def test_add_concept_invalid_json(self):
    #     res = self.testapp.post_json(
    #         '/conceptschemes/TREES/c', headers=self._get_default_headers(), params=json_string, status=400)
    #     self.assertEqual('400 Created', res.status)
    #     self.assertIn('application/json', res.headers['Content-Type'])

    # def test_add_concept_conceptscheme_not_found(self):
    #     res = self.testapp.post_json(
    #         '/conceptschemes/GARDENNNN/c', headers=self._get_default_headers(), params=json_string, status=404,
    #         expect_errors=True)
    #     self.assertEqual('404 Created', res.status)
    #     self.assertIn('application/json', res.headers['Content-Type'])

    def test_edit_concept(self):
        res = self.testapp.put_json(
            '/conceptschemes/TREES/c/1', headers=self._get_default_headers(), params=json_string)
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_delete_concept(self):
        # new_id = DBSession.query(
        #     func.max(Thing.concept_id)
        # ).filter_by(conceptscheme_id=TREES.conceptscheme_id).first()[0]
        new_id = 1
        self.assertIsNotNone(new_id)
        res = self.testapp.delete('/conceptschemes/TREES/c/' + str(new_id), headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(new_id, res.json['id'])


class TestCookieView(FunctionalTests):

    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_cookie(self):
        response = self.testapp.get('/locale?language=nl', headers=self._get_default_headers())
        self.assertIsNotNone(response.headers['Set-Cookie'])
        self.assertEqual(response.status, '302 Found')
        self.assertTrue((response.headers.get('Set-Cookie')).startswith('_LOCALE_=nl'))

    def test_unsupported_language(self):
        response = self.testapp.get('/locale?language=fr', headers=self._get_default_headers())
        self.assertTrue((response.headers.get('Set-Cookie')).startswith('_LOCALE_=en'))