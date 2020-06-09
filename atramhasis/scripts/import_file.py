# -*- coding: utf-8 -*-
import sys
import os
import argparse

from skosprovider_rdf.providers import RDFProvider
from rdflib import Graph
from rdflib.util import SUFFIX_FORMAT_MAP, guess_format

from skosprovider.providers import SimpleCsvProvider
from skosprovider.uri import UriPatternGenerator
import csv

from skosprovider.providers import DictionaryProvider
import json

from skosprovider_sqlalchemy.utils import import_provider
from skosprovider_sqlalchemy.models import (
    ConceptScheme,
    Label,
    conceptscheme_label
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url


def file_to_rdf_provider(**kwargs):
    """
    Create RDF provider from the input file
    """
    input_file = kwargs.get('input_file')
    input_name, input_ext = os.path.splitext(os.path.basename(input_file))
    graph = Graph()
    graph.parse(input_file, format=guess_format(input_ext))
    return RDFProvider(
        {'id': input_name.upper()},
        graph
    )


def file_to_csv_provider(**kwargs):
    """
    Create CSV provider from the input file
    """
    input_file = kwargs.get('input_file')
    input_name, input_ext = os.path.splitext(os.path.basename(input_file))
    with open(input_file, "r") as ifile:
        reader = csv.reader(ifile)
        uri_pattern = kwargs.get('uri_pattern')
        provider_kwargs = {'uri_generator': UriPatternGenerator(uri_pattern)} if uri_pattern else {}
        return SimpleCsvProvider(
            {'id': input_name.upper()},
            reader,
            **provider_kwargs
        )


def file_to_json_provider(**kwargs):
    """
    Create Dictionary provider from the input file
    """
    input_file = kwargs.get('input_file')
    input_name, input_ext = os.path.splitext(os.path.basename(input_file))
    with open(input_file, 'r') as data_file:
        dictionary = json.load(data_file)
    uri_pattern = kwargs.get('uri_pattern')
    provider_kwargs = {'uri_generator': UriPatternGenerator(uri_pattern)} if uri_pattern else {}
    return DictionaryProvider(
        {'id': input_name.upper()},
        dictionary,
        **provider_kwargs
    )


supported_types = {
    'RDF': {
        'extensions': ['.%s' % suffix for suffix in SUFFIX_FORMAT_MAP],
        'file_to_provider': file_to_rdf_provider
    },
    'CSV': {
        'extensions': ['.csv'],
        'file_to_provider': file_to_csv_provider
    },
    'JSON': {
        'extensions': ['.json'],
        'file_to_provider': file_to_json_provider
    }
}

supported_ext = [item for sublist in [supported_types[filetype]['extensions'] for filetype in supported_types.keys()]
                 for item in sublist]


def parse_argv_for_import(argv):
    """
    Parse parameters and validate
    """
    cmd = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(
        description='Import file to a database',
        usage='{0} [--from path_input_file] [--to conn_string] [--conceptscheme_label cs_label] [--conceptscheme_uri cs_uri] [--uri_pattern uri_pattern]\n '
              '(example: "{1} --from atramhasis/scripts/my_file --to sqlite:///atramhasis.sqlite --conceptscheme_label Labels --conceptscheme_uri urn:x-skosprovider:trees" --uri_pattern urn:x-skosprovider:trees:%s)'.format(
            cmd, cmd)
    )
    parser.add_argument('--from',
                        dest='input_file',
                        type=str,
                        help='local path to the input file',
                        required=True
                        )
    parser.add_argument('--to',
                        dest='to',
                        type=str,
                        help='Connection string of the output database',
                        required=False,
                        default='sqlite:///atramhasis.sqlite'
                        )
    parser.add_argument('--conceptscheme_label',
                        dest='cs_label',
                        type=str,
                        help='Label of the conceptscheme',
                        required=False,
                        default=None
                        )
    parser.add_argument('--conceptscheme_uri',
                        dest='cs_uri',
                        type=str,
                        help='URI of the conceptscheme',
                        required=False,
                        default=None
                        )
    parser.add_argument('--uri_pattern',
                        dest='uri_pattern',
                        type=str,
                        help='URI pattern input for the URIGenerator',
                        required=False,
                        default=None
                        )
    args = parser.parse_args()
    if not validate_file(args.input_file) or not validate_connection_string(args.to):
        sys.exit(1)
    return args


def validate_file(input_file):
    if not os.path.exists(input_file):
        print('The input file {0} does not exists'.format(input_file))
        return False
    elif os.path.splitext(input_file)[1] not in supported_ext:
        print ('the input file {0} is not supported. Allowed extensions are: {1}'.format(input_file, supported_ext))
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
            return True
    elif u.drivername:
        print('The database driver ' + u.drivername + ' is not supported.')
    print('Wrong structure of connection string "' + connection_string + '"')
    print('Structure: postgresql://username:password@host:port/db_name OR sqlite:///path/db_name.sqlite')
    return False


def conn_str_to_session(conn_str):
    """
    create session from database connection string
    """
    connect_uri = conn_str
    engine = create_engine(connect_uri, echo=True)
    return sessionmaker(
        bind=engine,
    )()


def create_conceptscheme(conceptscheme_label, conceptscheme_uri):
    """
    Configure output conceptscheme based on arg values
    """
    cs = ConceptScheme(uri=conceptscheme_uri)
    l = Label(conceptscheme_label, 'prefLabel', 'und')
    cs.labels.append(l)
    return cs

def create_conceptscheme_from_skos(conceptscheme):
    """
    Configure output conceptscheme based on a `skosprovider.skos.ConceptScheme`
    """
    return ConceptScheme(
        uri=conceptscheme.uri,
        labels = [
            Label(l.label, l.type, l.language)
            for l in conceptscheme.labels
        ],
        notes = [
            Note(n.note, n.type, n.language, n.markup)
            for n in conceptscheme.notes
        ],
        sources = [
            Source(s.citation, s.markup)
            for s in conceptscheme.sources
        ],
        languages = [
            l for l in conceptscheme.languages
        ]
    )



def provider_to_db(provider, conceptscheme, session):
    """
    import provider data into the database
    """
    session.add(conceptscheme)
    import_provider(provider, conceptscheme, session)
    session.commit()


def main(argv=sys.argv):
    """
    Documentation: import -h
    Run: import --from <path_input_file> --to <conn_string> --conceptscheme_label <cs_label> --conceptscheme_uri <cs_uri> --uri_pattern <uri_pattern>

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
    input_name, input_ext = os.path.splitext(os.path.basename(args.input_file))
    session = conn_str_to_session(args.to)
    file_to_provider_function = [supported_types[filetype]['file_to_provider'] for filetype in supported_types.keys()
                                 if input_ext in supported_types[filetype]['extensions']][0]
    provider = file_to_provider_function(**vars(args))
    if args.cs_uri:
        cs_uri = args.cs_uri
        cs_label = args.cs_label if args.cs_label else input_name.capitalize()
        cs = create_conceptscheme(cs_label, cs_uri)
    else:
        cs = create_conceptscheme_from_skos(provider.concept_scheme)
    provider_to_db(provider, cs, session)

    # Get info to return to the user
    prov_id = input_name.upper()
    scheme_id = cs.id
    print("\n\n*** The import of conceptscheme {0} from the {1} file to {2} was succesful. ***\
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
            \n\n".
          format(prov_id, args.input_file, args.to,
                 prov_id.replace(' ', '_'), prov_id, scheme_id, prov_id.replace(' ', '_')))
