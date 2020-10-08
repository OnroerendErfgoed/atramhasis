# -*- coding: utf-8 -*-
import argparse
import logging

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from pytz import timezone
from sqlalchemy import engine_from_config

try:
    from builtins import input
except ImportError:
    input = raw_input

timezone_brussels = timezone('Europe/Brussels')
log = logging.getLogger(__name__)


def delete_scheme(settings, scheme_id):
    engine = engine_from_config(settings, 'sqlalchemy.')
    with engine.connect() as con:
        concept_ids = con.execute(
            'select id from concept where conceptscheme_id={}'.format(scheme_id)
        )
        for row in concept_ids:
            concept_id = row[0]
            delete_concept(concept_id, con)

        con.execute('delete from note where note.id in'
                    '(select note_id from conceptscheme_note '
                    'where conceptscheme_id={})'.format(scheme_id))
        con.execute('delete from source where source.id in'
                    '(select source_id from conceptscheme_source '
                    'where conceptscheme_id={})'.format(scheme_id))
        con.execute('delete from label where label.id in'
                    '(select label_id from conceptscheme_label '
                    'where conceptscheme_id={})'.format(scheme_id))
        con.execute('delete from conceptscheme where id = {}'.format(scheme_id))


def delete_concept(concept_id, con):
    con.execute('delete from note where note.id in'
                '(select note_id from concept_note where concept_id={})'
                .format(concept_id))
    con.execute('delete from source where source.id in'
                '(select source_id from concept_source '
                'where concept_id={})'.format(concept_id))
    con.execute('delete from label where label.id in'
                '(select label_id from concept_label '
                'where concept_id={})'.format(concept_id))
    delete_child_concepts(concept_id, con)
    con.execute('delete from concept where id = {}'.format(concept_id))


def delete_child_concepts(concept_id, con):
    select_children = ('select collection_id_narrower as child '
                       'from concept_hierarchy_collection '
                       'where concept_id_broader = {0} '
                       'union '
                       'select concept_id_narrower as child '
                       'from concept_hierarchy_concept '
                       'where concept_id_broader = {0};'.format(concept_id))
    children = con.execute(select_children)
    for row in children:
        child_id = row[0]
        delete_concept(child_id, con)


def main():
    parser = argparse.ArgumentParser(
        description="Delete a conceptscheme. ",
        usage="remove_schema development.ini --id=1")
    parser.add_argument('settings_file',
                        help="<The location of the settings file>#<app-name>")
    parser.add_argument("--id", type=int, required=True,
                        help="the conceptscheme id")
    parser.add_argument("--no-input", action='store_true',
                        help="Don't stop script for user input")
    args = parser.parse_args()

    config_uri = args.settings_file
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    id = args.id
    print(
        "The conceptscheme with id {} will be deleted".format(id)
    )
    if not args.no_input:
        input("Press [Enter] to continue.")

    delete_scheme(settings, id)


if __name__ == '__main__':  # pragma: no cover
    main()
