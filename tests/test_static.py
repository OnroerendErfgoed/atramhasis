import pytest
from webtest import TestApp

from atramhasis import main
from tests import SETTINGS


@pytest.fixture()
def testapp():
    return TestApp(TestStatic.app)


class TestStatic:
    app = main({}, **SETTINGS)

    def test_sitemap_view(self, testapp):
        response = testapp.get("/sitemap_index.xml")
        assert 200 == response.status_code
