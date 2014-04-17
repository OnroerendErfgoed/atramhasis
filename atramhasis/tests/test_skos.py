import unittest

from pyramid import testing
from atramhasis.skos import includeme


class TestSkos(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_include(self):
        self.config.include('pyramid_skosprovider')
        self.config.scan('pyramid_skosprovider')
        includeme(self.config)
        self.assertIsNotNone(self.config.get_skos_registry())

