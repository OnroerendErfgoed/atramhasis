import json
import os
import sys
from datetime import date
from datetime import datetime

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from pyramid.scripts.common import parse_vars
from skosprovider.providers import VocabularyProvider
from skosprovider_sqlalchemy import utils as skosprovider_utils
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from sqlalchemy import engine_from_config
from sqlalchemy.orm import Session

from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {obj} not serializable")


def initialize_providers(session):
    from fixtures.data import trees, geo
    from fixtures.styles_and_cultures import styles_and_cultures
    from fixtures.materials import materials
    from fixtures.eventtypes import eventtypes
    from fixtures.heritagetypes import heritagetypes
    from fixtures.periods import periods
    from fixtures.species import species
    from fixtures.bluebirds import bluebirds

    import_provider(
        trees,
        session,
        ConceptScheme(
            id=1,
            uri='urn:x-skosprovider:trees',
            labels=[
                Label('Verschillende soorten bomen', 'prefLabel', 'nl'),
                Label('Different types of trees', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        geo,
        session,
        ConceptScheme(
            id=2,
            uri='urn:x-skosprovider:geo',
            labels=[
                Label('Geografie', 'prefLabel', 'nl'),
                Label('Geography', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        styles_and_cultures,
        session,
        ConceptScheme(
            id=3,
            uri='https://id.erfgoed.net/thesauri/stijlen_en_culturen',
            labels=[
                Label('Stijlen en Culturen', 'prefLabel', 'nl'),
                Label('Styles and Cultures', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        materials,
        session,
        ConceptScheme(
            id=4,
            uri='https://id.erfgoed.net/thesauri/materialen',
            labels=[
                Label('Materialen', 'prefLabel', 'nl'),
                Label('Materials', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        eventtypes,
        session,
        ConceptScheme(
            id=5,
            uri='https://id.erfgoed.net/thesauri/gebeurtenistypes',
            labels=[
                Label('Gebeurtenistypes', 'prefLabel', 'nl'),
                Label('Event types', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        heritagetypes,
        session,
        ConceptScheme(
            id=6,
            uri='https://id.erfgoed.net/thesauri/erfgoedtypes',
            labels=[
                Label('Erfgoedtypes', 'prefLabel', 'nl'),
                Label('Heritage types', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        periods,
        session,
        ConceptScheme(
            id=7,
            uri='https://id.erfgoed.net/thesauri/dateringen',
            labels=[
                Label('Dateringen', 'prefLabel', 'nl'),
                Label('Periods', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        species,
        session,
        ConceptScheme(
            id=8,
            uri='https://id.erfgoed.net/thesauri/soorten',
            labels=[
                Label('Soorten', 'prefLabel', 'nl'),
                Label('Species', 'prefLabel', 'en')
            ]
        ),
    )
    import_provider(
        bluebirds,
        session,
        ConceptScheme(
            id=9,
            uri='https://id.bluebirds.org',
            labels=[
                Label('Blauwe vogels', 'prefLabel', 'nl'),
                Label('Blue birds', 'prefLabel', 'en')
            ]
        ),
    )


def import_provider(
    provider: VocabularyProvider, session: Session, conceptscheme: ConceptScheme
):
    concept_scheme = skosprovider_utils.import_provider(
        provider, session, conceptscheme=conceptscheme,
    )

    if provider.uri_generator:
        uri_pattern = getattr(provider.uri_generator, 'pattern', None)
    else:
        uri_pattern = None

    db_provider = Provider()
    db_provider.meta = json.loads(json.dumps(provider.metadata, default=json_serial))
    db_provider.id_generation_strategy = IDGenerationStrategy.NUMERIC
    db_provider.expand_strategy = ExpandStrategy.RECURSE
    db_provider.conceptscheme = concept_scheme
    db_provider.id = provider.get_vocabulary_id()
    db_provider.uri_pattern = uri_pattern
    if 'conceptscheme_id' in db_provider.meta:
        del db_provider.meta['conceptscheme_id']

    session.add(db_provider)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = engine_from_config(settings, 'sqlalchemy.')
    with Session(engine) as session:
        initialize_providers(session)
        session.commit()
    print('--atramhasis-db-initialized--')


if __name__ == '__main__':
    main()