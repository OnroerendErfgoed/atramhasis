# -*- coding: utf-8 -*-

import logging
from skosprovider.uri import UriPatternGenerator
from skosprovider_heritagedata.providers import HeritagedataProvider

from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from skosprovider_getty.providers import AATProvider, TGNProvider

log = logging.getLogger(__name__)


def includeme(config):   # pragma: no cover
    TREES = SQLAlchemyProvider(
        {'id': 'TREES', 'conceptscheme_id': 1},
        config.registry.dbmaker
    )

    GEO = SQLAlchemyProvider(
        {'id': 'GEOGRAPHY', 'conceptscheme_id': 2},
        config.registry.dbmaker
    )

    STYLES = SQLAlchemyProvider(
        {'id': 'STYLES', 'conceptscheme_id': 3},
        config.registry.dbmaker
    )

    MATERIALS = SQLAlchemyProvider(
        {'id': 'MATERIALS', 'conceptscheme_id': 4},
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('urn:x-vioe:materials:%s')
    )

    # use 'subject': ['external'] for read only external providers (only available in REST service)

    # AAT = AATProvider(
    #     {'id': 'AAT', 'subject': ['external']},
    # )
    #
    # TGN = TGNProvider(
    #     {'id': 'TGN', 'subject': ['external']}
    # )

    EH_PERIOD = HeritagedataProvider(
        {'id': 'EH_PERIOD', 'subject': ['external']},
        scheme_uri='http://purl.org/heritagedata/schemes/eh_period'
    )

    EH_MONUMENT_TYPE = HeritagedataProvider(
        {'id': 'EH_MONUMENT_TYPE', 'subject': ['external']},
        scheme_uri='http://purl.org/heritagedata/schemes/eh_tmt2'
    )

    EH_MATERIALS = HeritagedataProvider(
        {'id': 'EH_MATERIALS', 'subject': ['external']},
        scheme_uri='http://purl.org/heritagedata/schemes/eh_tbm'
    )

    skosregis = config.get_skos_registry()
    skosregis.register_provider(TREES)
    skosregis.register_provider(GEO)
    skosregis.register_provider(STYLES)
    skosregis.register_provider(MATERIALS)
    #skosregis.register_provider(AAT)
    #skosregis.register_provider(TGN)
    skosregis.register_provider(EH_PERIOD)
    skosregis.register_provider(EH_MONUMENT_TYPE)
    skosregis.register_provider(EH_MATERIALS)
