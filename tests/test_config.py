import os
import tempfile

from pyramid.paster import get_appsettings

from atramhasis import main
from tests import DbTest
from tests import setup_db


here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


def setUpModule():
    setup_db()


class TestConfig(DbTest):
    def test_config(self):
        app = main({}, **settings)
        self.assertIsNotNone(app)

    def test_config_alt_dump_location(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings['atramhasis.dump_location'] = temp_dir
            app = main({}, **settings)
            self.assertIsNotNone(app)
