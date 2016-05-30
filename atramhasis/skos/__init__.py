# -*- coding: utf-8 -*-

import logging
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from skosprovider_heritagedata.providers import HeritagedataProvider
from skosprovider_getty.providers import AATProvider, TGNProvider

import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import ExpiresAfter

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
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/stijlen_en_culturen/%s')
    )

    MATERIALS = SQLAlchemyProvider(
        {'id': 'MATERIALS', 'conceptscheme_id': 4},
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/materialen/%s')
    )

    EVENTTYPES = SQLAlchemyProvider(
        {'id': 'EVENTTYPE', 'conceptscheme_id': 5},
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/gebeurtenistypes/%s')
    )

    HERITAGETYPES = SQLAlchemyProvider(
        {'id': 'HERITAGETYPE', 'conceptscheme_id': 6},
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/erfgoedtypes/%s')
    )

    PERIODS = SQLAlchemyProvider(
        {'id': 'PERIOD', 'conceptscheme_id': 7},
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/dateringen/%s')
    )

    SPECIES = SQLAlchemyProvider(
        {'id': 'SPECIES', 'conceptscheme_id': 8},
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/soorten/%s')
    )

    # use 'subject': ['external'] for read only external providers (only available in REST service)

    getty_session = CacheControl(requests.Session(), heuristic=ExpiresAfter(weeks=1))

    AAT = AATProvider(
        {'id': 'AAT', 'subject': ['external']},
        session=getty_session
    )

    TGN = TGNProvider(
        {'id': 'TGN', 'subject': ['external']},
        session=getty_session
    )

    eh_session = CacheControl(requests.Session(), heuristic=ExpiresAfter(weeks=1))

    EH_PERIOD = HeritagedataProvider(
        {'id': 'EH_PERIOD', 'subject': ['external']},
        scheme_uri='http://purl.org/heritagedata/schemes/eh_period',
        session=eh_session
    )

    EH_MONUMENT_TYPE = HeritagedataProvider(
        {'id': 'EH_MONUMENT_TYPE', 'subject': ['external']},
        scheme_uri='http://purl.org/heritagedata/schemes/eh_tmt2',
        session=eh_session
    )

    EH_MATERIALS = HeritagedataProvider(
        {'id': 'EH_MATERIALS', 'subject': ['external']},
        scheme_uri='http://purl.org/heritagedata/schemes/eh_tbm',
        session=eh_session
    )

    skosregis = config.get_skos_registry()
    skosregis.register_provider(TREES)
    skosregis.register_provider(GEO)
    skosregis.register_provider(STYLES)
    skosregis.register_provider(MATERIALS)
    skosregis.register_provider(EVENTTYPES)
    skosregis.register_provider(HERITAGETYPES)
    skosregis.register_provider(PERIODS)
    skosregis.register_provider(SPECIES)
    skosregis.register_provider(AAT)
    skosregis.register_provider(TGN)
    skosregis.register_provider(EH_PERIOD)
    skosregis.register_provider(EH_MONUMENT_TYPE)
    skosregis.register_provider(EH_MATERIALS)
