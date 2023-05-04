import logging

import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import ExpiresAfter
from skosprovider.registry import Registry
from skosprovider_getty.providers import AATProvider
from skosprovider_getty.providers import TGNProvider
from sqlalchemy.orm import Session

from atramhasis import utils
from atramhasis.data.datamanagers import ProviderDataManager

log = logging.getLogger(__name__)
LICENSES = [
    'https://creativecommons.org/licenses/by/4.0/',
    'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
]


def register_providers_from_db(registry: Registry, session: Session) -> None:
    """
    Retrieve all providers stored in the database and add them to the registry.

    :param registry: The registry to which the providers will be added.
    :param session: A database session.
    """
    manager = ProviderDataManager(session)
    for db_provider in manager.get_all_providers():
        provider = utils.db_provider_to_skosprovider(db_provider)
        registry.register_provider(provider)


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
        register_providers_from_db(registry, request.db)

        return registry
    except AttributeError:
        log.exception("Attribute error during creation of Registry.")
        raise
