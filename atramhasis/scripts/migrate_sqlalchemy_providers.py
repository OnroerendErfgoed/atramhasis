import argparse
import itertools as it
import json
from datetime import date
from datetime import datetime
from unittest.mock import Mock

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from pyramid.util import DottedNameResolver
from skosprovider.registry import Registry
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy.orm import Session

from atramhasis import utils
from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider


def get_atramhasis_sqlalchemy_providers(session):
    licenses = [
        'https://creativecommons.org/licenses/by/4.0/',
        'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
    ]
    dataseturigenerator = UriPatternGenerator(
        'https://id.erfgoed.net/datasets/thesauri/%s'
    )
    return (
        SQLAlchemyProvider(
            {'id': 'TREES', 'conceptscheme_id': 1},
            session
        ),
        SQLAlchemyProvider(
            {'id': 'GEOGRAPHY', 'conceptscheme_id': 2},
            session
        ),
        SQLAlchemyProvider(
            {
                'id': 'STYLES',
                'conceptscheme_id': 3,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='stijlen_en_culturen'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2008, 2, 14)],
                    'language': ['nl-BE'],
                    'license': licenses
                }

            },
            session,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/stijlen_en_culturen/%s'
            )
        ),
        SQLAlchemyProvider(
            {
                'id': 'MATERIALS',
                'conceptscheme_id': 4,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='materialen'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2011, 3, 16)],
                    'language': ['nl-BE'],
                    'license': licenses
                }
            },
            session,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/materialen/%s'
            )
        ),
        SQLAlchemyProvider(
            {
                'id': 'EVENTTYPE',
                'conceptscheme_id': 5,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='gebeurtenistypes'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2010, 8, 13)],
                    'language': ['nl-BE'],
                    'license': licenses
                }
            },
            session,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/gebeurtenistypes/%s'
            )
        ),
        SQLAlchemyProvider(
            {
                'id': 'HERITAGETYPE',
                'conceptscheme_id': 6,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='erfgoedtypes'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2008, 2, 14)],
                    'language': ['nl-BE'],
                    'license': licenses
                }
            },
            session,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/erfgoedtypes/%s'
            )
        ),
        SQLAlchemyProvider(
            {
                'id': 'PERIOD',
                'conceptscheme_id': 7,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='dateringen'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2008, 2, 14)],
                    'language': ['nl-BE'],
                    'license': licenses
                }
            },
            session,
            uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/dateringen/%s')
        ),
        SQLAlchemyProvider(
            {
                'id': 'SPECIES',
                'conceptscheme_id': 8,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='soorten'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2011, 5, 23)],
                    'language': ['nl-BE', 'la'],
                    'license': licenses
                },
                'atramhasis.force_display_label_language': 'la'
            },
            session,
            uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/soorten/%s')
        ),
        SQLAlchemyProvider(
            {
                'id': 'BLUEBIRDS',
                'conceptscheme_id': 9,
                'atramhasis.id_generation_strategy': IDGenerationStrategy.MANUAL
            },
            session,
            uri_generator=UriPatternGenerator('https://id.bluebirds.org/%s')
        ),
    )


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {obj} not serializable")


def migrate(skos_registry: Registry, session: Session):
    print("Starting migration of SQLAlchemyProvider in the registry...")
    for provider in it.chain(
        skos_registry.get_providers(),
        get_atramhasis_sqlalchemy_providers(session),
    ):
        if not isinstance(provider, SQLAlchemyProvider):
            continue

        if session.get(Provider, provider.get_vocabulary_id()) is not None:
            print(
                f"Provider with id {provider.get_vocabulary_id()} already exists. "
                f"Skipping creation of provider for conceptscheme "
                f"{provider.metadata.get('id') or ''}"
            )
            continue

        print(f"  Migrating provider {provider.concept_scheme.uri}")

        if provider.uri_generator:
            uri_pattern = getattr(provider.uri_generator, 'pattern', None)
        else:
            uri_pattern = None

        db_provider = Provider()
        if 'atramhasis.id_generation_strategy' in provider.metadata:
            # enum must be string to store as json.
            provider.metadata['atramhasis.id_generation_strategy'] = (
                provider.metadata['atramhasis.id_generation_strategy'].name
            )
        else:
            provider.metadata['atramhasis.id_generation_strategy'] = 'NUMERIC'
        db_provider.meta = json.loads(json.dumps(provider.metadata, default=json_serial))
        db_provider.expand_strategy = ExpandStrategy[provider.expand_strategy.upper()]
        db_provider.conceptscheme = session.get(ConceptScheme, provider.conceptscheme_id)
        db_provider.id = provider.get_vocabulary_id()
        db_provider.uri_pattern = uri_pattern
        if 'conceptscheme_id' in db_provider.meta:
            del db_provider.meta['conceptscheme_id']

        session.add(db_provider)
    print("Migration finished.")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate SQLAlchemyProviders from a skosregistry to the database.",
    )
    parser.add_argument('settings_file',
                        help="<The location of the settings file>#<app-name>")
    args = parser.parse_args()

    config_uri = args.settings_file
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    resolver = DottedNameResolver()
    skos_registry_factory = resolver.resolve(settings['skosprovider.skosregistry_factory'])

    with utils.db_session(settings) as session:
        if settings['skosprovider.skosregistry_location'] == 'registry':
            skos_registry = skos_registry_factory()
        else:
            skos_registry = skos_registry_factory(Mock(db=session))
        migrate(skos_registry, session)


if __name__ == '__main__':  # pragma: no cover
    main()
