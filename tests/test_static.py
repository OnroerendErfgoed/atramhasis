import pytest
from webtest import TestApp

from atramhasis import main
from tests import SETTINGS


class TestStatic:
    app = main({}, **SETTINGS)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.testapp = TestApp(self.app)

    def test_sitemap_view(self):
        response = self.testapp.get('/sitemap_index.xml')
        assert 200 == response.status_code
