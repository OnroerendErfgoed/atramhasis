import os
import sys
from pyramid.paster import setup_logging, get_appsettings
from pyramid.scripts.common import parse_vars
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
import transaction
from atramhasis import DBSession

from atramhasis.tests.fixtures.data import geo, trees

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
        import_provider(trees, ConceptScheme(uri='http://id.trees.org'), DBSession)
        import_provider(geo, ConceptScheme(uri='http://id.geo.org'), DBSession)

if __name__ == "__main__":
    main()