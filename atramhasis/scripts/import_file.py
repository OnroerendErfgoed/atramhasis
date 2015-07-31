# -*- coding: utf-8 -*-
import sys
import os
import argparse

from skosprovider_rdf.providers import RDFProvider
from rdflib import Graph
from rdflib.util import guess_format

from skosprovider.providers import SimpleCsvProvider
import csv

from skosprovider.providers import DictionaryProvider
import json

from skosprovider_sqlalchemy.utils import import_provider
from skosprovider_sqlalchemy.models import (
    ConceptScheme,
    Label
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url


def file_to_rdf_provider(input_file):
    '''
    Create RDF provider from the input file
    '''
    input_name, input_ext = os.path.splitext(os.path.basename(input_file))
    graph = Graph()
    graph.parse(input_file, format=guess_format(input_ext))
    return RDFProvider(
        {'id': input_name.upper()},
        graph
    )


def file_to_csv_provider(input_file):
    '''
    Create CSV provider from the input file
    '''
    input_name, input_ext = os.path.splitext(os.path.basename(input_file))
    with open(input_file, "rb") as ifile:
        reader = csv.reader(ifile)
    return SimpleCsvProvider(
        {'id': input_name.upper()},
        reader,
    )


def file_to_json_provider(input_file):
    '''
    Create Dictionary provider from the input file
    '''
    input_name, input_ext = os.path.splitext(os.path.basename(input_file))
    with open(input_file, 'rb') as data_file:
        dictionary = json.load(data_file)
    return DictionaryProvider(
        {'id': input_name.upper()},
        dictionary,
    )

supported_types = {
    'RDF': {
        'extensions': ['.html', '.hturtle', '.mdata', '.microdata', '.n3', '.nquads', '.nt', '.rdfa', '.rdfa1.0',
                       '.rdfa1.1', '.trix', '.turtle', '.xml'],
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
    '''
    Parse parameters and validate
    '''
    cmd = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(
        description='Import file to a database',
        usage='{0} [--from path_input_file] [--to conn_string]\n '
              '(example: "{1} --from atramhasis/scripts/my_file --to sqlite:///atramhasis.sqlite")'.format(cmd, cmd)
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
    '''
    Validate the connection string
    :param connection_string
    :return: Boolean True if correct connection string
    '''
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
    '''
    create session from database connection string
    '''
    connect_uri = conn_str
    engine = create_engine(connect_uri, echo=True)
    return sessionmaker(
        bind=engine,
    )()


def create_conceptscheme(conceptscheme_id):
    '''
    configure output conceptscheme
    '''
    cs = ConceptScheme()
    l = Label(conceptscheme_id, 'prefLabel', 'nl')
    cs.labels.append(l)
    return cs


def provider_to_db(provider, conceptscheme, session):
    '''
    import provider data into the database
    '''
    session.add(conceptscheme)
    import_provider(provider, conceptscheme, session)
    session.commit()


def main(argv=sys.argv):
    '''
    Documentation: import -h
    Run: import --from <path_input_file> --to <conn_string>

    example path_input_file:
     atramhasis/scripts/my_file

    structure conn_string:
     postgresql://username:password@host:port/db_name
     sqlite:///path/db_name.sqlite

    default conn_string:
     sqlite:///atramhasis.sqlite
    '''

    args = parse_argv_for_import(argv)
    input_name, input_ext = os.path.splitext(os.path.basename(args.input_file))
    session = conn_str_to_session(args.to)
    file_to_provider_function = [supported_types[filetype]['file_to_provider'] for filetype in supported_types.keys()
                                 if input_ext in supported_types[filetype]['extensions']][0]
    if file_to_provider_function == '':
        print('Importer is not yet implemented')
        sys.exit(1)
    else:
        provider = file_to_provider_function(args.input_file)
    cs = create_conceptscheme(input_name.capitalize())
    provider_to_db(provider, cs, session)