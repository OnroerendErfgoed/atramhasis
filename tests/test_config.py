import os
import unittest
from pyramid.paster import get_appsettings
from atramhasis import main

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class TestConfig(unittest.TestCase):
    def test_config(self):
        app = main({}, **settings)
        self.assertIsNotNone(app)