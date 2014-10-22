import os
import unittest
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config
from atramhasis import main
from skosprovider_sqlalchemy.models import Base

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class TestConfig(unittest.TestCase):

    def setUp(self):
        engine = engine_from_config(settings, prefix='sqlalchemy.')
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_config(self):
        app = main({}, **settings)
        self.assertIsNotNone(app)