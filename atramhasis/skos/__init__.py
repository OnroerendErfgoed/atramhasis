# -*- coding: utf-8 -*-

import logging

from skosprovider.registry import Registry
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from skosprovider_getty.providers import AATProvider, TGNProvider

import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import ExpiresAfter

from datetime import date

log = logging.getLogger(__name__)
LICENSES = [
    'https://creativecommons.org/licenses/by/4.0/',
    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
]


def create_registry(request):
    try:
        registry = Registry(instance_scope='threaded_thread')
        dataseturigenerator = UriPatternGenerator(
            'https://id.erfgoed.net/datasets/thesauri/%s'
        )

        trees = SQLAlchemyProvider(
            {'id': 'TREES', 'conceptscheme_id': 1},
            request.db
        )

        geo = SQLAlchemyProvider(
            {'id': 'GEOGRAPHY', 'conceptscheme_id': 2},
            request.db
        )

        styles = SQLAlchemyProvider(
            {
                'id': 'STYLES',
                'conceptscheme_id': 3,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='stijlen_en_culturen'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2008, 2, 14)],
                    'language': ['nl-BE'],
                    'license': LICENSES
                }

            },
            request.db,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/stijlen_en_culturen/%s'
            )
        )

        materials = SQLAlchemyProvider(
            {
                'id': 'MATERIALS',
                'conceptscheme_id': 4,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='materialen'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2011, 3, 16)],
                    'language': ['nl-BE'],
                    'license': LICENSES
                }
            },
            request.db,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/materialen/%s'
            )
        )

        eventtypes = SQLAlchemyProvider(
            {
                'id': 'EVENTTYPE',
                'conceptscheme_id': 5,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='gebeurtenistypes'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2010, 8, 13)],
                    'language': ['nl-BE'],
                    'license': LICENSES
                }
            },
            request.db,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/gebeurtenistypes/%s'
            )
        )

        heritagetypes = SQLAlchemyProvider(
            {
                'id': 'HERITAGETYPE',
                'conceptscheme_id': 6,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='erfgoedtypes'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2008, 2, 14)],
                    'language': ['nl-BE'],
                    'license': LICENSES
                }
            },
            request.db,
            uri_generator=UriPatternGenerator(
                'https://id.erfgoed.net/thesauri/erfgoedtypes/%s'
            )
        )

        periods = SQLAlchemyProvider(
            {
                'id': 'PERIOD',
                'conceptscheme_id': 7,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='dateringen'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2008, 2, 14)],
                    'language': ['nl-BE'],
                    'license': LICENSES
                }
            },
            request.db,
            uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/dateringen/%s')
        )

        species = SQLAlchemyProvider(
            {
                'id': 'SPECIES',
                'conceptscheme_id': 8,
                'dataset': {
                    'uri': dataseturigenerator.generate(id='soorten'),
                    'publisher': ['https://id.erfgoed.net/actoren/501'],
                    'created': [date(2011, 5, 23)],
                    'language': ['nl-BE', 'la'],
                    'license': LICENSES
                },
                'atramhasis.force_display_label_language': 'la'
            },
            request.db,
            uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/soorten/%s')
        )

        # use 'subject': ['external'] for read only external providers
        # (only available in REST service)

        getty_session = CacheControl(requests.Session(), heuristic=ExpiresAfter(weeks=1))

        aat = AATProvider(
            {'id': 'AAT', 'subject': ['external']},
            session=getty_session
        )

        tgn = TGNProvider(
            {'id': 'TGN', 'subject': ['external']},
            session=getty_session
        )

        registry.register_provider(trees)
        registry.register_provider(geo)
        registry.register_provider(styles)
        registry.register_provider(materials)
        registry.register_provider(eventtypes)
        registry.register_provider(heritagetypes)
        registry.register_provider(periods)
        registry.register_provider(species)
        registry.register_provider(aat)
        registry.register_provider(tgn)
        return registry
    except AttributeError:
        log.exception("Attribute error during creation of Registry.")
        raise
