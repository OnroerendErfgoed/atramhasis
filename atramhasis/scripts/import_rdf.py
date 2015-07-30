# -*- coding: utf-8 -*-
import sys
import os
import argparse

from skosprovider_sqlalchemy.utils import import_provider

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url

from skosprovider_sqlalchemy.models import (
    ConceptScheme,
    Label
)

from skosprovider_rdf.providers import RDFProvider
from rdflib import Graph
from rdflib.util import guess_format


def main(argv=sys.argv):
    '''
    Documentation: import_rdf -h
    Run: import_rdf --from <path_rdf_file> --to <conn_string>

    example path_rdf_file:
     atramhasis/scripts/my_rdf.rdf

    structure conn_string:
     postgresql://username:password@host:port/db_name
     sqlite:///path/db_name.sqlite

    default conn_string:
     sqlite:///atramhasis.sqlite
    '''

    cmd = os.path.basename(argv[0])

    ###
    # Parse parameters and validate
    ###
    parser = argparse.ArgumentParser(
        description='Import RDF file to a database',
        usage='%s [--from path_rdf_file] [--to conn_string]\n '
              '(example: "%s --from atramhasis/scripts/my_rdf.rdf --to sqlite:///atramhasis.sqlite")' % (cmd, cmd)
    )
    parser.add_argument('--from',
                        dest='rdf_file',
                        type=str,
                        help='local path to the input RDF file',
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
    if not os.path.exists(args.rdf_file) or not validate_connection_string(args.to):
        sys.exit(1)

    # make session to output database
    connect_uri = args.to
    engine = create_engine(connect_uri, echo=True)
    session = sessionmaker(
        bind=engine,
    )()

    # create RDF provider from the input file
    rdf_name, rdf_ext = os.path.splitext(os.path.basename(args.rdf_file))
    graph = Graph()
    graph.parse(args.rdf_file, format=guess_format(rdf_ext))

    rdf_provider = RDFProvider(
        {'id': rdf_name.upper()},
        graph
    )

    # configure output conceptscheme
    rdf_cs = ConceptScheme()
    l = Label(rdf_name.capitalize(), 'prefLabel', 'nl')
    rdf_cs.labels.append(l)

    # import RDF skos data into the database
    session.add(rdf_cs)
    import_provider(rdf_provider, rdf_cs, session)
    session.commit()


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
