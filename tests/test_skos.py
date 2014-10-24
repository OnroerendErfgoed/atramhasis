import os
import unittest

from pyramid import testing
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from atramhasis.models import Base
from skosprovider_sqlalchemy.models import Base as SkosBase
from atramhasis.skos import includeme

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class TestSkos(unittest.TestCase):
    def setUp(self):
        self.engine = engine_from_config(settings, 'sqlalchemy.')
        Base.metadata.bind = self.engine
        SkosBase.metadata.bind = self.engine
        session_maker = sessionmaker(
            bind=self.engine,
        )
        SkosBase.metadata.drop_all(self.engine)
        SkosBase.metadata.create_all(self.engine)
        self.config = testing.setUp()
        self.config.registry.dbmaker = session_maker

    def tearDown(self):
        testing.tearDown()

    def test_include(self):
        self.config.include('pyramid_skosprovider')
        self.config.scan('pyramid_skosprovider')
        includeme(self.config)
        self.assertIsNotNone(self.config.get_skos_registry())

