import os

from alembic.config import Config
from pyramid.paster import get_appsettings
from skosprovider.providers import DictionaryProvider
from skosprovider.registry import Registry
from skosprovider.skos import ConceptScheme
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from atramhasis import skos
from atramhasis.cache import list_region
from atramhasis.cache import tree_region
from atramhasis.data.models import IDGenerationStrategy
from fixtures import data

TEST_DIR = os.path.dirname(__file__)
SETTINGS = get_appsettings(os.path.join(TEST_DIR, "..", "tests", "conf_test.ini"))

# No test should want caching
tree_region.configure("dogpile.cache.null", replace_existing_backend=True)
list_region.configure("dogpile.cache.null", replace_existing_backend=True)


def get_alembic_config():
    alembic_config = Config(os.path.join(TEST_DIR, "..", "alembic.ini"))
    alembic_config.set_main_option(
        "script_location", os.path.join(TEST_DIR, "..", "atramhasis", "alembic")
    )
    alembic_config.set_main_option(
        "ini_location", os.path.join(TEST_DIR, "..", "tests", "conf_test.ini")
    )
    return alembic_config


ALEMBIC_CONFIG = get_alembic_config()


def create_registry(request):
    registry = Registry(instance_scope="threaded_thread")
    trees = SQLAlchemyProvider({"id": "TREES", "conceptscheme_id": 1}, request.db)
    geo = SQLAlchemyProvider(
        {"id": "GEOGRAPHY", "conceptscheme_id": 2},
        request.db,
        uri_generator=UriPatternGenerator("urn:x-vioe:geography:%s"),
    )
    styles = SQLAlchemyProvider({"id": "STYLES", "conceptscheme_id": 3}, request.db)
    materials = SQLAlchemyProvider(
        {"id": "MATERIALS", "conceptscheme_id": 4},
        request.db,
        uri_generator=UriPatternGenerator("urn:x-vioe:materials:%s"),
    )
    test = DictionaryProvider(
        {"id": "TEST", "default_language": "nl", "subject": ["biology"]},
        [data.larch, data.chestnut, data.species],
        concept_scheme=ConceptScheme("http://id.trees.org"),
    )
    missing_label = SQLAlchemyProvider(
        {"id": "MISSING_LABEL", "conceptscheme_id": 9}, request.db
    )
    manual_ids = SQLAlchemyProvider(
        {
            "id": "manual-ids",
            "conceptscheme_id": 10,
            "atramhasis.id_generation_strategy": IDGenerationStrategy.MANUAL,
        },
        request.db,
    )

    registry.register_provider(trees)
    registry.register_provider(geo)
    registry.register_provider(styles)
    registry.register_provider(materials)
    registry.register_provider(test)
    registry.register_provider(missing_label)
    registry.register_provider(manual_ids)

    skos.register_providers_from_db(registry, request.db)

    return registry
