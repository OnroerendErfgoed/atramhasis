import os
import unittest
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config, create_engine
from atramhasis import main
from skosprovider_sqlalchemy.models import Base

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class TestConfig(unittest.TestCase):
    def setUp(self):
        settings['sqlalchemy.url'] = 'sqlite:///%s/dbtest.sqlite' % here
        self.engine = engine_from_config(settings, prefix='sqlalchemy.')
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def test_config(self):
        app = main({}, **settings)
        self.assertIsNotNone(app)