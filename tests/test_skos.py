import os
import unittest

from pyramid import testing
from pyramid.paster import get_appsettings
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import transaction
from skosprovider_sqlalchemy.models import Base as SkosBase, ConceptScheme

from atramhasis.data.models import Base
from fixtures.data import geo
from fixtures.materials import materials
from fixtures.styles_and_cultures import styles_and_cultures
from fixtures.data import trees


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

        with transaction.manager:
            local_session = session_maker()
            import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), local_session)
            import_provider(materials, ConceptScheme(id=4, uri='urn:x-vioe:materials'), local_session)
            import_provider(geo, ConceptScheme(id=2, uri='urn:x-vioe:geo'), local_session)
            import_provider(styles_and_cultures, ConceptScheme(id=3, uri='urn:x-vioe:styles'), local_session)

    def tearDown(self):
        testing.tearDown()

    def test_include(self):
        self.config.include('pyramid_skosprovider')
        self.config.scan('pyramid_skosprovider')
        skosregis = self.config.get_skos_registry()
        skosregis.register_provider(trees)
        skosregis.register_provider(geo)
        skosregis.register_provider(styles_and_cultures)
        skosregis.register_provider(materials)
        self.assertIsNotNone(self.config.get_skos_registry())

