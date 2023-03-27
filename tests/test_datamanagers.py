from datetime import date
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Language
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from atramhasis.data.datamanagers import AuditManager
from atramhasis.data.datamanagers import ConceptSchemeManager
from atramhasis.data.datamanagers import CountsManager
from atramhasis.data.datamanagers import LanguagesManager
from atramhasis.data.datamanagers import ProviderDataManager
from atramhasis.data.datamanagers import SkosManager
from atramhasis.data.models import ConceptVisitLog
from atramhasis.data.models import ConceptschemeCounts
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider
from tests import DbTest
from tests import fill_db
from tests import setup_db


def setUpModule():
    setup_db()
    fill_db()


class ConceptSchemeManagerTest(DbTest):
    def setUp(self):
        super().setUp()
        self.conceptscheme_manager = ConceptSchemeManager(self.session)

    def test_get(self):
        res = self.conceptscheme_manager.get(1)
        self.assertEqual('urn:x-skosprovider:trees', res.uri)

    def test_find(self):
        query = {'type': 'concept', 'label': 'es'}
        res = self.conceptscheme_manager.find(1, query)
        self.assertEqual(1, len(res))

    def test_get_concepts_for_scheme_tree(self):
        res = self.conceptscheme_manager.get_concepts_for_scheme_tree(2)
        self.assertEqual(1, len(res))

    def test_get_collections_for_scheme_tree(self):
        res = self.conceptscheme_manager.get_collections_for_scheme_tree(2)
        self.assertEqual(1, len(res))

    def test_get_all(self):
        res = self.conceptscheme_manager.get_all(2)
        self.assertEqual(10, len(res))

    def test_save(self):
        conceptscheme = self.session.execute(
            select(ConceptScheme).filter(Concept.id == 1)
        ).scalars().first()
        conceptscheme = self.conceptscheme_manager.save(conceptscheme)
        self.assertIsNotNone(conceptscheme.id)


class SkosManagerTest(DbTest):
    def setUp(self):
        super().setUp()
        self.skos_manager = SkosManager(self.session)

    def test_get_thing(self):
        res = self.skos_manager.get_thing(1, 1)
        self.assertEqual('urn:x-skosprovider:trees/1', res.uri)

    def test_save(self):
        thing = Concept()
        thing.concept_id = 123
        thing.conceptscheme_id = 1
        thing = self.skos_manager.save(thing)
        self.assertIsNotNone(thing.id)

    def test_delete_thing(self):
        thing = self.skos_manager.get_thing(1, 1)
        self.skos_manager.delete_thing(thing)
        self.assertRaises(NoResultFound, self.skos_manager.get_thing, 1, 1)

    def test_get_by_list_type(self):
        res = self.skos_manager.get_by_list_type(LabelType)
        self.assertEqual(4, len(res))

    def test_get_match_type(self):
        match_type = self.skos_manager.get_match_type('narrowMatch')
        self.assertEqual('narrowMatch', match_type.name)

    def test_get_match(self):
        from skosprovider_sqlalchemy.models import Match
        match = Match()
        match.matchtype_id = 'narrowMatch'
        match.uri = 'urn:test'
        match.concept_id = 1
        self.session.add(match)
        match = self.skos_manager.get_match('urn:test', 'narrowMatch', 1)
        self.assertEqual('urn:test', match.uri)

    def test_get_all_label_types(self):
        res = self.skos_manager.get_all_label_types()
        self.assertEqual(4, len(res))

    def test_get_next_cid_numeric(self):
        res = self.skos_manager.get_next_cid(1, IDGenerationStrategy.NUMERIC)
        self.assertIsInstance(res, int)

    def test_get_next_cid_guid(self):
        res = self.skos_manager.get_next_cid(1, IDGenerationStrategy.GUID)
        self.assertIsInstance(res, str)
        char = "[0-9a-fA-F]"
        self.assertRegex(
            res,
            fr"^{char}{{8}}\b-{char}{{4}}\b-{char}{{4}}\b-{char}{{4}}\b-{char}{{12}}$"
        )

    def test_get_next_cid_manual(self):
        with self.assertRaises(ValueError):
            self.skos_manager.get_next_cid(1, IDGenerationStrategy.MANUAL)


class LanguagesManagerTest(DbTest):
    def setUp(self):
        super().setUp()
        self.language_manager = LanguagesManager(self.session)

    def test_get(self):
        res = self.language_manager.get('nl')
        self.assertEqual('Dutch', res.name)

    def test_save(self):
        language = Language('au', 'Austrian')
        language = self.language_manager.save(language)
        self.assertEqual('Austrian', language.name)

    def test_delete(self):
        language = self.language_manager.get('en')
        self.language_manager.delete(language)
        self.assertRaises(NoResultFound, self.language_manager.get, 'en')

    def test_get_all(self):
        res = self.language_manager.get_all()
        self.assertGreaterEqual(len(res), 3)

    def test_get_all_sorted(self):
        result = self.language_manager.get_all_sorted('id', False)
        result_ids = [lang.id for lang in result]
        self.assertEqual(list(sorted(result_ids)), result_ids)

    def test_get_all_sorted_desc(self):
        result = self.language_manager.get_all_sorted('id', True)
        result_ids = [lang.id for lang in result]
        self.assertEqual(list(sorted(result_ids, reverse=True)), result_ids)

    def test_count_languages(self):
        res = self.language_manager.count_languages('nl')
        self.assertEqual(1, res)


class AuditManagerTest(DbTest):
    def setUp(self):
        super().setUp()
        self.audit_manager = AuditManager(self.session)

    @patch('atramhasis.data.datamanagers.date', Mock(today=Mock(return_value=date(2015, 8, 1))))
    def test_get_first_day(self):
        self.assertEqual('2015-07-31', self.audit_manager._get_first_day('last_day'))
        self.assertEqual('2015-07-25', self.audit_manager._get_first_day('last_week'))
        self.assertEqual('2015-07-01', self.audit_manager._get_first_day('last_month'))
        self.assertEqual('2014-08-01', self.audit_manager._get_first_day('last_year'))

    @patch('atramhasis.data.datamanagers.date', Mock(today=Mock(return_value=date(2015, 9, 15))))
    def test_get_most_popular_concepts_for_conceptscheme(self):
        self.session.add(
            ConceptVisitLog(concept_id=1, conceptscheme_id='1', origin='REST',
                            visited_at=datetime(2015, 8, 27, 10, 58, 3))
        )
        self.session.add(
            ConceptVisitLog(concept_id=1, conceptscheme_id='1', origin='REST',
                            visited_at=datetime(2015, 8, 27, 11, 58, 3))
        )
        self.session.add(
            ConceptVisitLog(concept_id=2, conceptscheme_id='1', origin='REST',
                            visited_at=datetime(2015, 8, 27, 10, 58, 3))
        )
        self.session.add(
            ConceptVisitLog(concept_id=2, conceptscheme_id='2', origin='REST',
                            visited_at=datetime(2015, 8, 27, 10, 58, 3))
        )
        self.assertListEqual(
            [
                {'concept_id': 1, 'scheme_id': 1},
                {'concept_id': 2, 'scheme_id': 1}
            ],
            self.audit_manager.get_most_popular_concepts_for_conceptscheme(
                1, 5, 'last_month'
            )
        )
        self.assertListEqual([{'concept_id': 2, 'scheme_id': 2}],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(2, 5, 'last_month'))
        self.assertListEqual([{'concept_id': 1, 'scheme_id': 1}],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(1, 1, 'last_month'))
        self.assertListEqual([],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(1, 5, 'last_day'))


class CountsManagerTest(DbTest):
    def setUp(self):
        super().setUp()
        self.counts_manager = CountsManager(self.session)

    def test_count_for_scheme(self):
        counts = ConceptschemeCounts()
        counts.conceptscheme_id = 'TREES'
        counts.counted_at = datetime.now()
        counts.triples = 3
        counts.conceptscheme_triples = 2
        counts.avg_concept_triples = 1
        self.counts_manager.save(counts)
        res = self.counts_manager.get_most_recent_count_for_scheme('TREES')
        self.assertIsNotNone(res)
        self.assertEqual(3, res.triples)


class ProviderDataManagerTest(DbTest):
    def setUp(self):
        super().setUp()
        self.manager = ProviderDataManager(self.session)

    def test_get_provider_by_id(self):
        provider = Provider(
            id='a', conceptscheme=ConceptScheme(), uri_pattern='u-p', meta={}
        )
        self.session.add(provider)
        self.session.flush()

        result = self.manager.get_provider_by_id(provider.id)
        self.assertEqual(result, provider)

    def test_get_provider_by_id_no_result(self):
        with self.assertRaises(NoResultFound):
            self.manager.get_provider_by_id('...')

    def test_get_all_providers(self):
        provider = Provider(
            id='a', conceptscheme=ConceptScheme(), uri_pattern='u-p', meta={}
        )
        self.session.add(provider)
        self.session.flush()

        result = self.manager.get_all_providers()
        self.assertEqual(result, [provider])
