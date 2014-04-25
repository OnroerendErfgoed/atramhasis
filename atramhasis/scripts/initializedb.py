import os
import sys

from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.utils import import_provider
import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from pyramid.scripts.common import parse_vars
from atramhasis import DBSession, Base

from atramhasis.tests.fixtures.data import trees, geo
from atramhasis.tests.fixtures.styles_and_cultures import styles_and_cultures


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    with transaction.manager:
        import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), DBSession)
        import_provider(geo, ConceptScheme(id=2, uri='urn:x-skosprovider:geo'), DBSession)
        import_provider(styles_and_cultures, ConceptScheme(id=3, uri='urn:x-vioe:styles'), DBSession)
    print('--atramhasis-db-initialized--')
