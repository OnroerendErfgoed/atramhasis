# -*- coding: utf-8 -*-

import logging

from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from atramhasis import DBSession

log = logging.getLogger(__name__)

TREES = SQLAlchemyProvider(
    {'id': 'TREES', 'conceptscheme_id': 1},
    DBSession
)

GEO = SQLAlchemyProvider(
    {'id': 'GEOGRAPHY', 'conceptscheme_id': 2},
    DBSession
)


STYLES = SQLAlchemyProvider(
    {'id': 'STYLES', 'conceptscheme_id': 3},
    DBSession
)

def includeme(config):
    skosregis = config.get_skos_registry()
    skosregis.register_provider(TREES)
    skosregis.register_provider(GEO)
    skosregis.register_provider(STYLES)
