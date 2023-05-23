from skosprovider.registry import Registry
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy import select

import tests
from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider
from atramhasis.scripts import migrate_sqlalchemy_providers
from tests import DbTest


def setUpModule():
    tests.setup_db(guarantee_empty=True)
    tests.fill_db()


class TestMigrateTests(DbTest):
    def test_migrate(self):
        conceptscheme = ConceptScheme(uri='urn:x-skosprovider:trees')
        self.session.add(conceptscheme)
        self.session.flush()

        db_providers = self.session.execute(select(Provider)).scalars().all()
        self.assertEqual(0, len(db_providers))

        registry = Registry()
        registry.register_provider(
            SQLAlchemyProvider(
                {"id": "EXTRA", "conceptscheme_id": conceptscheme.id}, self.session
            )
        )
        other_providers = migrate_sqlalchemy_providers.get_atramhasis_sqlalchemy_providers(
            self.session
        )
        for provider in other_providers:
            if self.session.get(ConceptScheme, provider.conceptscheme_id) is None:
                self.session.add(
                    ConceptScheme(
                        id=provider.conceptscheme_id,
                        uri=f'urn:x-skosprovider:{provider.conceptscheme_id}'
                    )
                )
        self.session.flush()

        migrate_sqlalchemy_providers.migrate(
            skos_registry=registry,
            session=self.session,
        )

        db_providers = self.session.execute(select(Provider)).scalars().all()
        db_conceptscheme_ids = [p.conceptscheme_id for p in db_providers]
        expected_conceptscheme_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, conceptscheme.id]
        for expected in expected_conceptscheme_ids:
            self.assertIn(expected, db_conceptscheme_ids)
        provider = next(p for p in db_providers if p.conceptscheme_id == conceptscheme.id)
        self.assertEqual(conceptscheme.id, provider.conceptscheme_id)
        self.assertEqual(ExpandStrategy.RECURSE, provider.expand_strategy)
        self.assertEqual(IDGenerationStrategy.NUMERIC, provider.id_generation_strategy)
        self.assertEqual('urn:x-skosprovider:%s:%s', provider.uri_pattern)
        self.assertEqual(
            {
                'id': 'EXTRA',
                'subject': [],
                'atramhasis.id_generation_strategy': 'NUMERIC'
            },
            provider.meta
        )
