import argparse
import json
import logging
from datetime import date
from datetime import datetime
from unittest.mock import Mock

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from pyramid.util import DottedNameResolver
from skosprovider.registry import Registry
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy.orm import Session

from atramhasis import utils
from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import Provider

log = logging.getLogger(__name__)


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {obj} not serializable")


def migrate(skos_registry: Registry, session: Session):
    print("Starting migration of SQLAlchemyProvider in the registry...")
    for provider in skos_registry.get_providers():
        if not isinstance(provider, SQLAlchemyProvider):
            continue

        print(f"  Migrating provider {provider.concept_scheme.uri}")

        if provider.uri_generator:
            uri_pattern = getattr(provider.uri_generator, 'pattern', None)
        else:
            uri_pattern = None

        db_provider = Provider()
        db_provider.expand_strategy = ExpandStrategy[provider.expand_strategy.upper()]
        db_provider.conceptscheme = session.get(ConceptScheme, provider.conceptscheme_id)
        db_provider.id = provider.conceptscheme_id
        db_provider.meta = json.loads(json.dumps(provider.metadata, default=json_serial))
        db_provider.uri_pattern = uri_pattern

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
