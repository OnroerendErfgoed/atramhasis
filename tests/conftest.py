import pytest
from alembic import command
from skosprovider.providers import DictionaryProvider
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import Session
from sqlalchemy.schema import MetaData

from fixtures import data
from fixtures import materials as material_data
from fixtures.data import trees
from tests import ALEMBIC_CONFIG
from tests import SETTINGS


# ---------------------------------------------------------------------------
# Database bootstrap helpers
# ---------------------------------------------------------------------------

def reset_and_migrate(engine):
    """Drop all tables and re-apply all alembic migrations from scratch."""
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)
    command.stamp(ALEMBIC_CONFIG, 'base')
    command.upgrade(ALEMBIC_CONFIG, 'head')


def fill_db(engine):
    """Fill the database with standard test fixtures."""
    with Session(engine) as session:
        import_provider(
            trees, session,
            ConceptScheme(id=1, uri='urn:x-skosprovider:trees'),
        )
        import_provider(
            material_data.materials, session,
            ConceptScheme(id=4, uri='urn:x-vioe:materials'),
        )
        import_provider(
            data.geo, session,
            ConceptScheme(id=2, uri='urn:x-vioe:geography'),
        )
        import_provider(
            DictionaryProvider(
                {'id': 'MISSING_LABEL', 'default_language': 'nl'},
                [
                    {'id': '1', 'uri': 'urn:x-skosprovider:test/1'},
                    {
                        'id': '2',
                        'uri': 'urn:x-skosprovider:test/2',
                        'labels': [
                            {'type': 'prefLabel', 'language': 'nl', 'label': 'label'}
                        ],
                    },
                ],
            ),
            session,
            ConceptScheme(id=9, uri='urn:x-vioe:test'),
        )
        import_provider(
            DictionaryProvider(
                {'id': 'manual-ids', 'default_language': 'nl'},
                [
                    {'id': 'manual-1', 'uri': 'urn:x-skosprovider:manual/manual-1'},
                    {
                        'id': 'manual-2',
                        'uri': 'urn:x-skosprovider:manual/manual-2',
                        'labels': [
                            {'type': 'prefLabel', 'language': 'nl', 'label': 'label'}
                        ],
                    },
                    {
                        'id': 'https://id.manual.org/manual/68',
                        'uri': 'https://id.manual.org/manual/68',
                        'labels': [
                            {'type': 'prefLabel', 'language': 'nl', 'label': 'handmatig'}
                        ],
                    },
                ],
            ),
            session,
            ConceptScheme(id=10, uri='urn:x-vioe:manual'),
        )
        session.add(ConceptScheme(id=3, uri='urn:x-vioe:styles'))
        for scheme_id in (5, 6, 7, 8):
            session.add(
                ConceptScheme(id=scheme_id, uri=f'urn:dummy-{scheme_id}')
            )
        session.commit()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_engine():
    """Single engine for the entire test session."""
    engine = engine_from_config(SETTINGS, prefix='sqlalchemy.')
    yield engine
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def db_setup(db_engine):
    """Run once at session start: fresh schema + test data."""
    reset_and_migrate(db_engine)
    fill_db(db_engine)


@pytest.fixture(scope="module")
def module_db_setup(db_engine):
    """Provide a temporary empty database for the duration of the module."""
    reset_and_migrate(db_engine)
    yield
    reset_and_migrate(db_engine)
    fill_db(db_engine)


@pytest.fixture(scope="class")
def db_connection(db_engine):
    """Class-scoped database connection."""
    connection = db_engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
def db_session(db_connection):
    """Per-test database session wrapped in a transaction that is rolled back.

    Uses ``join_transaction_mode="rollback_only"`` so that any
    ``session.commit()`` executed by code under test flushes to the connection
    but does **not** commit the outer connection transaction.  The rollback at
    the end therefore undoes everything, guaranteeing identical DB state
    between tests.
    """
    transaction = db_connection.begin()
    session = Session(bind=db_connection, join_transaction_mode="rollback_only")
    yield session
    session.close()
    transaction.rollback()
