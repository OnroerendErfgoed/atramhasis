# -*- coding: utf-8 -*-

import logging
from skosprovider.uri import UriPatternGenerator

from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

log = logging.getLogger(__name__)


def includeme(config):
    TREES = SQLAlchemyProvider(
        {'id': 'TREES', 'conceptscheme_id': 1},
        config.registry.dbmaker()
    )

    GEO = SQLAlchemyProvider(
        {'id': 'GEOGRAPHY', 'conceptscheme_id': 2},
        config.registry.dbmaker()
    )

    STYLES = SQLAlchemyProvider(
        {'id': 'STYLES', 'conceptscheme_id': 3},
        config.registry.dbmaker()
    )

    MATERIALS = SQLAlchemyProvider(
        {'id': 'MATERIALS', 'conceptscheme_id': 4},
        config.registry.dbmaker(),
        uri_generator=UriPatternGenerator('urn:x-vioe:materials:%s')
    )

    skosregis = config.get_skos_registry()
    skosregis.register_provider(TREES)
    skosregis.register_provider(GEO)
    skosregis.register_provider(STYLES)
    skosregis.register_provider(MATERIALS)
