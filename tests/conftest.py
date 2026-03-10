import pytest

from tests import fill_db
from tests import reset_db
from tests import setup_db


def pytest_configure(config):
    config.addinivalue_line("markers", "empty_db: reset the database to an empty state")


@pytest.fixture(scope="module", autouse=True)
def _module_db_setup(request):
    """Ensure the correct database state for each test module.

    By default, the database schema is created and filled with standard
    test fixtures. Modules decorated with ``@pytest.mark.empty_db`` get a
    freshly created but empty database instead.
    """
    if request.node.get_closest_marker("empty_db"):
        reset_db()
    else:
        setup_db()
        fill_db()
