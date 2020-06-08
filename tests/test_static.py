import unittest

from webtest import TestApp

from atramhasis import main
from tests import SETTINGS


class StaticTests(unittest.TestCase):
    app = main({}, **SETTINGS)

    def setUp(self):
        self.testapp = TestApp(self.app)

    def test_sitemap_view(self):
        response = self.testapp.get('/sitemap_index.xml')
        self.assertEqual(200, response.status_code)
