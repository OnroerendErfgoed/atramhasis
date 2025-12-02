import argparse
import csv
import json
import logging
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager

import sqlalchemy as sa
from rdflib import Graph
from rdflib.util import SUFFIX_FORMAT_MAP
from rdflib.util import guess_format
from skosprovider.providers import DictionaryProvider
from skosprovider.providers import SimpleCsvProvider
from skosprovider.providers import VocabularyProvider
from skosprovider.skos import ConceptScheme
from skosprovider.uri import UriPatternGenerator
from skosprovider_rdf.providers import RDFProvider
from skosprovider_sqlalchemy.models import ConceptScheme as ConceptschemeDb
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from atramhasis.data.models import Provider
from atramhasis.scripts.migrate_sqlalchemy_providers import json_serial


def file_to_rdf_provider(uri_pattern: str | None = None, **kwargs) -> RDFProvider:
    """
    Create RDF provider from the input file
    """
    input_file = kwargs.get('input_file')
    _, input_ext = os.path.splitext(os.path.basename(input_file))
    meta_id = kwargs.get('provider_id')
    graph = Graph()
    graph.parse(input_file, format=guess_format(input_ext))
    provider_kwargs = {}
    if uri_pattern:
        uri_generator = UriPatternGenerator(uri_pattern)
        provider_kwargs['uri_generator'] = uri_generator
    return RDFProvider({'id': meta_id}, graph, **provider_kwargs)


def _create_provider_kwargs(**kwargs):
    provider_kwargs = {}
    uri_pattern = kwargs.get('uri_pattern')
    if uri_pattern:
        provider_kwargs['uri_generator'] = UriPatternGenerator(uri_pattern)
    concept_scheme = kwargs.get('concept_scheme')
    if concept_scheme:
        provider_kwargs['concept_scheme'] = concept_scheme
    return provider_kwargs


def file_to_csv_provider(**kwargs) -> SimpleCsvProvider:
    """
    Create CSV provider from the input file
    """
    input_file = kwargs.get('input_file')
    meta_id = kwargs.get('provider_id')
    provider_kwargs = _create_provider_kwargs(**kwargs)
    with open(input_file) as ifile:
        reader = csv.reader(ifile)
        return SimpleCsvProvider({'id': meta_id}, reader, **provider_kwargs)


def file_to_json_provider(**kwargs) -> DictionaryProvider:
    """
    Create Dictionary provider from the input file
    """
    input_file = kwargs.get('input_file')
    meta_id = kwargs.get('provider_id')
    provider_kwargs = _create_provider_kwargs(**kwargs)
    with open(input_file) as data_file:
        dictionary = json.load(data_file)
    return DictionaryProvider({'id': meta_id}, dictionary, **provider_kwargs)


supported_types = {
    'JSON': {'extensions': ['.json'], 'file_to_provider': file_to_json_provider},
    'RDF': {
        'extensions': ['.%s' % suffix for suffix in SUFFIX_FORMAT_MAP],
        'file_to_provider': file_to_rdf_provider,
    },
    'CSV': {'extensions': ['.csv'], 'file_to_provider': file_to_csv_provider},
}

supported_ext = [
    item
    for sublist in [
        supported_types[filetype]['extensions'] for filetype in supported_types.keys()
    ]
    for item in sublist
]


def parse_argv_for_import(argv):
    """
    Parse parameters and validate
    """
    cmd = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(
        description='Import file to a database',
        epilog=(
            f'example: {cmd} '
            'atramhasis/scripts/my_file '
            '--uri-pattern urn:x-skosprovider:trees:%s '
            '--to sqlite:///atramhasis.sqlite '
            '--conceptscheme-label Labels '
            '--conceptscheme-uri urn:x-skosprovider:trees '
            '--create-provider '
            '--provider-id ERFGOEDTYPES '
            '--id-generation-strategy numeric'
        ),
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='local path to the input file',
    )
    parser.add_argument(
        '--uri-pattern',
        dest='uri_pattern',
        type=str,
        help='URI pattern input for the URIGenerator',
    )
    parser.add_argument(
        '--to',
        dest='to',
        metavar='conn_string',
        type=str,
        help='Connection string of the output database',
        required=False,
        default='sqlite:///atramhasis.sqlite',
    )
    parser.add_argument(
        '--conceptscheme-label',
        dest='cs_label',
        type=str,
        help='Label of the conceptscheme',
        required=False,
        default=None,
    )
    parser.add_argument(
        '--conceptscheme-uri',
        dest='cs_uri',
        type=str,
        help='URI of the conceptscheme',
        required=False,
        default=None,
    )
    parser.add_argument(
        '--create-provider',
        dest='create_provider',
        default=True,
        action=argparse.BooleanOptionalAction,
        help='An optional parameter if given a provider is created. '
        'Use --no-create-provider to not create a provider',
    )
    parser.add_argument(
        '--provider-id',
        dest='provider_id',
        type=str,
        help='An optional string (eg. ERFGOEDTYPES) to be assigned to the provider id. '
        'If not specified, assign the conceptscheme id to the provider id',
        required=False,
        default=None,
    )
    parser.add_argument(
        '--id-generation-strategy',
        dest='id_generation_strategy',
        type=str,
        help='URI pattern input for the URIGenerator',
        required=False,
        choices=['numeric', 'guid', 'manual'],
        default=None,
    )
    args = parser.parse_args()
    if not validate_file(args.input_file) or not validate_connection_string(args.to):
        sys.exit(1)

    if args.create_provider is False and (
        args.uri_pattern or args.provider_id or args.id_generation_strategy
    ):
        print(
            '--uri-pattern, --provider-id and --id-generation-strategy can only be '
            'used when --create-provider is set to True'
        )
        sys.exit(1)
    else:
        validate_uri_pattern(args.uri_pattern)
    if args.id_generation_strategy is None:
        args.id_generation_strategy = 'numeric'
    return args


def validate_uri_pattern(uri_pattern: str):
    if not uri_pattern:
        print(
            '--uri-pattern is required when creating a provider. '
            'This can be disabled with --no-create-provider'
        )
        sys.exit(1)
    if uri_pattern.count('%s') != 1:
        print('--uri-pattern must contain exactly one %s placeholder')
        sys.exit(1)


def validate_file(input_file):
    if not os.path.exists(input_file):
        print(f'The input file {input_file} does not exists')
        return False
    elif os.path.splitext(input_file)[1] not in supported_ext:
        print(
            f'the input file {input_file} is not supported. Allowed extensions are: {supported_ext}'
        )
        return False
    else:
        return True


def validate_connection_string(connection_string):
    """
    Validate the connection string
    :param connection_string
    :return: Boolean True if correct connection string
    """
    u = url.make_url(connection_string)
    if u.drivername == 'postgresql':
        if u.username and u.password and u.host and u.port and u.database:
            return True
    elif u.drivername == 'sqlite':
        if u.database:
            # Extract the file path
            sqlite_path = u.database
            if not os.path.exists(sqlite_path):
                print(f'SQLite database file does not exist: {sqlite_path}')
                return False
            return True
    elif u.drivername:
        print('The database driver ' + u.drivername + ' is not supported.')
    print('Wrong structure of connection string "' + connection_string + '"')
    print(
        'Structure: postgresql://username:password@host:port/db_name OR sqlite:///path/db_name.sqlite'
    )
    return False


@contextmanager
def db_session(connection_string: str) -> Iterator[Session]:
    """
    Create a database session based on the connection string
    :param connection_string: connection string
    :return: session
    """
    print(f'Connecting to database {connection_string} ...')
    engine = create_engine(connection_string)
    try:
        with Session(engine) as session:
            yield session
            session.commit()
    finally:
        engine.dispose()


def create_conceptscheme(
    conceptscheme_uri: str, conceptscheme_label: str
) -> ConceptScheme:
    """
    Create a conceptscheme based on arg values
    """
    return ConceptScheme(uri=conceptscheme_uri, labels=[{'label': conceptscheme_label}])


def main(argv=sys.argv):
    """
    Documentation: import -h
    Run: import
    <path_input_file>
    <uri_pattern>
    --to <conn_string>
    --conceptscheme-uri <cs_uri>
    --conceptscheme-label <cs_label>
    --create-provider
    --provider-id <provider_id>
    --id-generation-strategy <numeric/guid/manual>

    example path_input_file:
     atramhasis/scripts/my_file

    structure conn_string:
     postgresql://username:password@host:port/db_name
     sqlite:///path/db_name.sqlite
    default conn_string:
     sqlite:///atramhasis.sqlite

    example conceptscheme_label
     My Conceptscheme
    default conceptscheme_label is the name of the file if a URI is specified.
    If no URI is specified, a conceptscheme will be imported from the input
    file. This only works for RDf files. For other file types (JSON and CSV)
    conceptscheme_uri is mandatory and conceptscheme_label is recommended.
    """

    # Import the data
    args = parse_argv_for_import(argv)
    print(f'Importing file {args.input_file} to database {args.to} ...')

    setup_logging()

    input_name, input_ext = os.path.splitext(os.path.basename(args.input_file))
    file_to_provider_function = [
        supported_types[filetype]['file_to_provider']
        for filetype in supported_types.keys()
        if input_ext in supported_types[filetype]['extensions']
    ][0]
    if args.cs_uri:
        cs_uri = args.cs_uri
        cs_label = args.cs_label if args.cs_label else input_name.capitalize()
        args.concept_scheme = create_conceptscheme(cs_uri, cs_label)
    provider = file_to_provider_function(**vars(args))

    with db_session(args.to) as session:
        validate_database_not_empty(args, session)
        db_conceptscheme = import_provider(provider, session)
        if args.create_provider:
            if not provider.metadata.get('id'):
                provider.metadata['id'] = db_conceptscheme.id
            create_provider(
                id_generation_strategy=args.id_generation_strategy.upper(),
                provider=provider,
                session=session,
                conceptscheme=db_conceptscheme,
            )

        # Get info to return to the user
        session.flush()
        scheme_id = db_conceptscheme.id
    if not args.create_provider:
        prov_id = getattr(args, 'provider_id', None) or input_name.upper()
        print(
            "\n\n*** The import of conceptscheme {0} from the {1} file to {2} was succesful. ***\
              \n\nTo use the data in Atramhasis, you must edit the file my_thesaurus/skos/__init__.py.\
              \nAdd a configuration similar to:\
                \n\ndef create_registry(request):\
                \n\t# create the SKOS registry\
                \n\tregistry = Registry(instance_scope='threaded_thread')\
                \n\t{3} = SQLAlchemyProvider(\
                \n\t\t{{'id': '{4}', 'conceptscheme_id': {5}}},\
                \n\t\trequest.db\
                \n\t)\
                \n\tregistry.register_provider({6})\
                \n\treturn registry\
                \n\n".format(
                prov_id,
                args.input_file,
                args.to,
                prov_id.replace(' ', '_'),
                prov_id,
                scheme_id,
                prov_id.replace(' ', '_'),
            )
        )
    else:
        prov_id = args.provider_id or scheme_id
        msg = """
***
The import of conceptscheme {0} from the {1} file to {2} was succesful.
You can now continue through the Atramhasis UI.
***
"""
        print(msg.format(prov_id, args.input_file, args.to))


def validate_database_not_empty(args, session):
    query = sa.text('SELECT version_num FROM alembic_version')
    try:
        session.execute(query)
    except DatabaseError:
        print(
            f'The database at {args.to} is not up to date. '
            'Please run the migration script first.'
        )
        sys.exit(1)
    else:
        print(' ∟Database connection healthy')


def setup_logging():
    import_logger = logging.getLogger('skosprovider_sqlalchemy.utils')
    import_logger.setLevel(logging.INFO)
    logging_handler = logging.StreamHandler(sys.stdout)
    logging_handler.setFormatter(logging.Formatter('%(message)s'))
    import_logger.addHandler(logging_handler)


def create_provider(
    id_generation_strategy: str,
    provider: VocabularyProvider,
    session: Session,
    conceptscheme: ConceptschemeDb,
):
    db_provider = Provider()
    provider.metadata['atramhasis.id_generation_strategy'] = id_generation_strategy
    db_provider.meta = json.loads(json.dumps(provider.metadata, default=json_serial))
    db_provider.expand_strategy = 'RECURSE'
    db_provider.conceptscheme = conceptscheme
    db_provider.id = provider.metadata.get('id') or conceptscheme.id
    db_provider.uri_pattern = provider.uri_generator.pattern
    if 'conceptscheme_id' in db_provider.meta:
        del db_provider.meta['conceptscheme_id']
    session.add(db_provider)


if __name__ == '__main__':
    main()
