import contextlib

import pytest
from alembic import command
from skosprovider.providers import DictionaryProvider
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData

from fixtures import data
from fixtures import materials as material_data
from fixtures.data import trees
from tests import ALEMBIC_CONFIG
from tests import SETTINGS


# ---------------------------------------------------------------------------
# Database bootstrap helpers
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def db_session_ctx():
    engine = engine_from_config(SETTINGS, prefix='sqlalchemy.')
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_and_migrate():
    """Drop all tables and re-apply all alembic migrations from scratch."""
    engine = engine_from_config(SETTINGS, prefix='sqlalchemy.')
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)
    command.stamp(ALEMBIC_CONFIG, 'base')
    engine.dispose()
    command.upgrade(ALEMBIC_CONFIG, 'head')


def fill_db():
    """Fill the database with standard test fixtures."""
    with db_session_ctx() as session:
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
def db_setup():
    """Run once at session start: fresh schema + test data."""
    reset_and_migrate()
    fill_db()


@pytest.fixture(scope="module")
def module_db_setup():
    """Provide a temporary empty database for the duration of the module."""
    reset_and_migrate()
    yield
    reset_and_migrate()
    fill_db()


@pytest.fixture(scope="class")
def db_connection(db_engine):
    """Class-scoped database connection."""
    connection = db_engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
def db_session(db_connection):
    """Per-test database session wrapped in a transaction that is rolled back."""
    transaction = db_connection.begin()
    session = sessionmaker(bind=db_connection)()
    yield session
    session.close()
    transaction.rollback()
