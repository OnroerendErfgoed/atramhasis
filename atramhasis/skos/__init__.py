# -*- coding: utf-8 -*-

import logging
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from skosprovider_heritagedata.providers import HeritagedataProvider
from skosprovider_getty.providers import AATProvider, TGNProvider

import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import ExpiresAfter

from datetime import date

log = logging.getLogger(__name__)


def includeme(config):   # pragma: no cover
    dataseturigenerator = UriPatternGenerator('https://id.erfgoed.net/datasets/thesauri/%s')

    TREES = SQLAlchemyProvider(
        {'id': 'TREES', 'conceptscheme_id': 1},
        config.registry.dbmaker
    )

    GEO = SQLAlchemyProvider(
        {'id': 'GEOGRAPHY', 'conceptscheme_id': 2},
        config.registry.dbmaker
    )

    STYLES = SQLAlchemyProvider(
        {
            'id': 'STYLES',
            'conceptscheme_id': 3,
            'dataset': {
                'uri': dataseturigenerator.generate(id='stijlen_en_culturen'),
                'publisher': ['https://id.erfgoed.net/actoren/501'],
                'created': [date(2008,2,14)],
                'language': ['nl-BE'],
                'license': [
                    'https://creativecommons.org/licenses/by/4.0/',
                    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
                ]
            }

        },
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/stijlen_en_culturen/%s')
    )

    MATERIALS = SQLAlchemyProvider(
        {
            'id': 'MATERIALS',
            'conceptscheme_id': 4,
            'dataset': {
                'uri': dataseturigenerator.generate(id='materialen'),
                'publisher': ['https://id.erfgoed.net/actoren/501'],
                'created': [date(2011,3,16)],
                'language': ['nl-BE'],
                'license': [
                    'https://creativecommons.org/licenses/by/4.0/',
                    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
                ]
            }
        },
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/materialen/%s')
    )

    EVENTTYPES = SQLAlchemyProvider(
        {
            'id': 'EVENTTYPE',
            'conceptscheme_id': 5,
            'dataset': {
                'uri': dataseturigenerator.generate(id='gebeurtenistypes'),
                'publisher': ['https://id.erfgoed.net/actoren/501'],
                'created': [date(2010,8,13)],
                'language': ['nl-BE'],
                'license': [
                    'https://creativecommons.org/licenses/by/4.0/',
                    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
                ]
            }
        },
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/gebeurtenistypes/%s')
    )

    HERITAGETYPES = SQLAlchemyProvider(
        {
            'id': 'HERITAGETYPE',
            'conceptscheme_id': 6,
            'dataset': {
                'uri': dataseturigenerator.generate(id='erfgoedtypes'),
                'publisher': ['https://id.erfgoed.net/actoren/501'],
                'created': [date(2008,2,14)],
                'language': ['nl-BE'],
                'license': [
                    'https://creativecommons.org/licenses/by/4.0/',
                    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
                ]
            }
        },
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/erfgoedtypes/%s')
    )

    PERIODS = SQLAlchemyProvider(
        {
            'id': 'PERIOD',
            'conceptscheme_id': 7,
            'dataset': {
                'uri': dataseturigenerator.generate(id='dateringen'),
                'publisher': ['https://id.erfgoed.net/actoren/501'],
                'created': [date(2008,2,14)],
                'language': ['nl-BE'],
                'license': [
                    'https://creativecommons.org/licenses/by/4.0/',
                    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
                ]
            }
        },
        config.registry.dbmaker,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/dateringen/%s')
    )

    SPECIES = SQLAlchemyProvider(
        {
            'id': 'SPECIES',
            'conceptscheme_id': 8,
            'dataset': {
                'uri': dataseturigenerator.generate(id='soorten'),
                'publisher': ['https://id.erfgoed.net/actoren/501'],
                'created': [date(2011,5,23)],
                'language': ['nl-BE', 'la'],
                'license': [
                    'https://creativecommons.org/licenses/by/4.0/',
                    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
                ]
            }
        },
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
