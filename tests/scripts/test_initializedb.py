from unittest.mock import patch

import pytest
from sqlalchemy import select

from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider
from atramhasis.scripts import initializedb as script
from tests import DbTest

pytestmark = pytest.mark.empty_db


def _fast_import_provider(provider, session, conceptscheme):
    """Skip the heavy concept import, just persist the ConceptScheme."""
    session.add(conceptscheme)
    session.flush()
    return conceptscheme


class TestMigrateTests(DbTest):
    @patch(
        'atramhasis.scripts.initializedb.skosprovider_utils.import_provider',
        side_effect=_fast_import_provider,
    )
    def test_initialize_providers(self, mock_import):
        script.initialize_providers(self.session)

        expected_ids = [
            'TREES',
            'GEOGRAPHY',
            'STYLE',
            'MATERIAL',
            'EVENTTYPE',
            'HERITAGETYPE',
            'PERIOD',
            'SPECIES',
            'BLUEBIRDS',
        ]
        expected_concept_scheme_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for db_provider in self.session.execute(select(Provider)).scalars():  # type: Provider
            self.assertIn(db_provider.conceptscheme.id, expected_concept_scheme_ids)
            self.assertEqual(db_provider.id_generation_strategy, IDGenerationStrategy.NUMERIC)
            self.assertEqual(db_provider.expand_strategy, ExpandStrategy.RECURSE)
            self.assertIn(db_provider.id, expected_ids)
