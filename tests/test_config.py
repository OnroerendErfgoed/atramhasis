import os
import unittest

from pyramid.paster import get_appsettings
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import transaction
from zope.sqlalchemy import ZopeTransactionExtension
from skosprovider_sqlalchemy.models import Base, ConceptScheme

from atramhasis import main
from fixtures.data import trees, geo
from fixtures.materials import materials
from fixtures.styles_and_cultures import styles_and_cultures


here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class TestConfig(unittest.TestCase):
    def setUp(self):
        settings['sqlalchemy.url'] = 'sqlite:///%s/dbtest.sqlite' % here
        self.engine = engine_from_config(settings, prefix='sqlalchemy.')
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        session_maker = sessionmaker(
            bind=self.engine,
            extension=ZopeTransactionExtension()
        )

        with transaction.manager:
            local_session = session_maker()
            import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), local_session)
            import_provider(materials, ConceptScheme(id=4, uri='urn:x-vioe:materials'), local_session)
            import_provider(geo, ConceptScheme(id=2, uri='urn:x-vioe:geo'), local_session)
            import_provider(styles_and_cultures, ConceptScheme(id=3, uri='urn:x-vioe:styles'), local_session)

    def test_config(self):
        app = main({}, **settings)
        self.assertIsNotNone(app)
