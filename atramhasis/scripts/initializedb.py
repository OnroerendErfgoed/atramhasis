import os
import sys

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from pyramid.scripts.common import parse_vars
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    from fixtures.data import trees, geo
    from fixtures.styles_and_cultures import styles_and_cultures
    from fixtures.materials import materials
    from fixtures.eventtypes import eventtypes
    from fixtures.heritagetypes import heritagetypes
    from fixtures.periods import periods
    from fixtures.species import species
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    db_session = sessionmaker(bind=engine)()
    import_provider(
        trees,
        ConceptScheme(
            id=1,
            uri='urn:x-skosprovider:trees',
            labels=[
                Label('Verschillende soorten bomen', 'prefLabel', 'nl'),
                Label('Different types of trees', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        geo,
        ConceptScheme(
            id=2,
            uri='urn:x-skosprovider:geo',
            labels=[
                Label('Geografie', 'prefLabel', 'nl'),
                Label('Geography', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        styles_and_cultures,
        ConceptScheme(
            id=3,
            uri='https://id.erfgoed.net/thesauri/stijlen_en_culturen',
            labels=[
                Label('Stijlen en Culturen', 'prefLabel', 'nl'),
                Label('Styles and Cultures', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        materials,
        ConceptScheme(
            id=4,
            uri='https://id.erfgoed.net/thesauri/materialen',
            labels=[
                Label('Materialen', 'prefLabel', 'nl'),
                Label('Materials', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        eventtypes,
        ConceptScheme(
            id=5,
            uri='https://id.erfgoed.net/thesauri/gebeurtenistypes',
            labels=[
                Label('Gebeurtenistypes', 'prefLabel', 'nl'),
                Label('Event types', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        heritagetypes,
        ConceptScheme(
            id=6,
            uri='https://id.erfgoed.net/thesauri/erfgoedtypes',
            labels=[
                Label('Erfgoedtypes', 'prefLabel', 'nl'),
                Label('Heritage types', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        periods,
        ConceptScheme(
            id=7,
            uri='https://id.erfgoed.net/thesauri/dateringen',
            labels=[
                Label('Dateringen', 'prefLabel', 'nl'),
                Label('Periods', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    import_provider(
        species,
        ConceptScheme(
            id=8,
            uri='https://id.erfgoed.net/thesauri/soorten',
            labels=[
                Label('Soorten', 'prefLabel', 'nl'),
                Label('Species', 'prefLabel', 'en')
            ]
        ),
        db_session
    )
    db_session.commit()
    db_session.close()
    print('--atramhasis-db-initialized--')
