import os
import random
import shutil

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
        random_dump_loc = f'dump{random.randint(0, 100)}'
        settings['atramhasis.dump_location'] = os.path.join(here, random_dump_loc)
        app = main({}, **settings)
        self.assertIsNotNone(app)
        if os.path.exists(random_dump_loc):
            shutil.rmtree(random_dump_loc)
