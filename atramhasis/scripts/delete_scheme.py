import argparse
import logging

from builtins import input
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from pytz import timezone
from sqlalchemy import engine_from_config

timezone_brussels = timezone('Europe/Brussels')
log = logging.getLogger(__name__)


def delete_scheme(settings, scheme_id):
    engine = engine_from_config(settings, 'sqlalchemy.')
    with engine.connect() as con:
        concept_ids = con.execute(
            f'select id from concept where conceptscheme_id={scheme_id}'
        )
        for row in concept_ids:
            concept_id = row[0]
            delete_concept(concept_id, con)

        con.execute(f'delete from note where note.id in'
                    f'(select note_id from conceptscheme_note '
                    f'where conceptscheme_id={scheme_id})')
        con.execute(f'delete from source where source.id in'
                    f'(select source_id from conceptscheme_source '
                    f'where conceptscheme_id={scheme_id})')
        con.execute(f'delete from label where label.id in'
                    f'(select label_id from conceptscheme_label '
                    f'where conceptscheme_id={scheme_id})')
        con.execute(f'delete from conceptscheme where id = {scheme_id}')


def delete_concept(concept_id, con):
    con.execute(f'delete from note where note.id in'
                f'(select note_id from concept_note where concept_id={concept_id})')
    con.execute(f'delete from source where source.id in'
                f'(select source_id from concept_source '
                f'where concept_id={concept_id})')
    con.execute(f'delete from label where label.id in'
                f'(select label_id from concept_label '
                f'where concept_id={concept_id})')
    delete_child_concepts(concept_id, con)
    con.execute(f'delete from concept where id = {concept_id}')


def delete_child_concepts(concept_id, con):
    select_children = (f'select collection_id_narrower as child '
                       f'from concept_hierarchy_collection '
                       f'where concept_id_broader = {concept_id} '
                       f'union '
                       f'select concept_id_narrower as child '
                       f'from concept_hierarchy_concept '
                       f'where concept_id_broader = {concept_id};')
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
        f"The conceptscheme with id {id} will be deleted"
    )
    if not args.no_input:
        input("Press [Enter] to continue.")

    delete_scheme(settings, id)


if __name__ == '__main__':  # pragma: no cover
    main()
