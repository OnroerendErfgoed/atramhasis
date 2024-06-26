import logging

import requests
from atramhasis import skos
from cachecontrol import CacheControl
from cachecontrol.heuristics import ExpiresAfter
from skosprovider.registry import Registry
from skosprovider_getty.providers import AATProvider
from skosprovider_getty.providers import TGNProvider

log = logging.getLogger(__name__)
LICENSES = [
    'https://creativecommons.org/licenses/by/4.0/',
    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
]


def create_registry(request):
    try:
        registry = Registry(instance_scope='threaded_thread')

        getty_session = CacheControl(requests.Session(), heuristic=ExpiresAfter(weeks=1))

        aat = AATProvider(
            {'id': 'AAT', 'subject': ['external']},
            session=getty_session
        )

        tgn = TGNProvider(
            {'id': 'TGN', 'subject': ['external']},
            session=getty_session
        )

        registry.register_provider(aat)
        registry.register_provider(tgn)
        skos.register_providers_from_db(registry, request.db)

        return registry
    except AttributeError:
        log.exception("Attribute error during creation of Registry.")
        raise
