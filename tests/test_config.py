import os
import tempfile

import pytest
from pyramid.paster import get_appsettings

from atramhasis import main

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class TestConfig:
    def test_config(self, db_session):
        app = main({}, **settings)
        assert app is not None

    def test_config_alt_dump_location(self, db_session):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings['atramhasis.dump_location'] = temp_dir
            app = main({}, **settings)
            assert app is not None
