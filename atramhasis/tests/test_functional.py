import os
import unittest
from webtest import TestApp

from pyramid import testing
from atramhasis import main
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config

TEST_DIR = os.path.dirname(__file__)
settings = get_appsettings('atramhasis/tests/conf_test.ini')
engine = engine_from_config(settings, prefix='sqlalchemy.')


class FunctionalTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)
        cls.engine = engine

    def setUp(self):
        connection = self.engine.connect()
        self.trans = connection.begin()
        self.testapp = TestApp(self.app)
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        self.trans.rollback()


class HtmlFunctionalTests(FunctionalTests):

    def _get_default_headers(self):
        return {'Accept': 'text/html'}

    def test_get_home(self):
        res = self.testapp.get('/', headers=self._get_default_headers())
        self.assertEqual('200 OK', res.status)
        self.assertIn('text/html', res.headers['Content-Type'])