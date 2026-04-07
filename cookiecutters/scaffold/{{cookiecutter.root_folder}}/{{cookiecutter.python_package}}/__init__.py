import os

from pyramid.config import Configurator

from atramhasis.data.models import Base as Base
from atramhasis.utils import parse_json_setting


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    # set up dump location
    dump_location = settings["atramhasis.dump_location"]
    if not os.path.exists(dump_location):
        os.makedirs(dump_location)

    parse_json_setting(settings, "atramhasis.note_type_order")

    with Configurator(settings=settings) as config:
        # Set up atramhasis
        config.include("atramhasis")
        # Set up atramhasis db
        config.include("atramhasis:data.db")

        config.scan()
        return config.make_wsgi_app()
