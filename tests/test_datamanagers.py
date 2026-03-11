import re
from datetime import date
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Language
from skosprovider_sqlalchemy.models import Match
from sqlalchemy import event
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


class TestConceptSchemeManager:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.session = db_session
        self.conceptscheme_manager = ConceptSchemeManager(self.session)

    def test_get(self):
        res = self.conceptscheme_manager.get(1)
        assert res.uri == 'urn:x-skosprovider:trees'

    def test_find(self):
        query = {'type': 'concept', 'label': 'es'}
        res = self.conceptscheme_manager.find(1, query)
        assert len(res) == 1

    def test_get_concepts_for_scheme_tree(self):
        res = self.conceptscheme_manager.get_concepts_for_scheme_tree(2)
        assert len(res) == 1

    def test_get_collections_for_scheme_tree(self):
        res = self.conceptscheme_manager.get_collections_for_scheme_tree(2)
        assert len(res) == 1

    def test_get_all(self):
        res = self.conceptscheme_manager.get_all(2)
        assert len(res) == 10

    def test_save(self):
        conceptscheme = self.session.execute(
            select(ConceptScheme).filter(Concept.id == 1)
        ).scalars().first()
        conceptscheme = self.conceptscheme_manager.save(conceptscheme)
        assert conceptscheme.id is not None


class TestSkosManager:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.session = db_session
        self.skos_manager = SkosManager(self.session)

    def test_get_thing(self):
        res = self.skos_manager.get_thing(1, 1)
        assert res.uri == 'urn:x-skosprovider:trees/1'

    def test_save(self):
        thing = Concept()
        thing.concept_id = 123
        thing.conceptscheme_id = 1
        thing = self.skos_manager.save(thing)
        assert thing.id is not None

    def test_delete_thing(self):
        thing = self.skos_manager.get_thing(1, 1)
        self.skos_manager.delete_thing(thing)
        with pytest.raises(NoResultFound):
            self.skos_manager.get_thing(1, 1)

    def test_get_by_list_type(self):
        res = self.skos_manager.get_by_list_type(LabelType)
        assert len(res) == 4

    def test_get_match_type(self):
        match_type = self.skos_manager.get_match_type('narrowMatch')
        assert match_type.name == 'narrowMatch'

    def test_get_match(self):
        match = Match()
        match.matchtype_id = 'narrowMatch'
        match.uri = 'urn:test'
        match.concept_id = 1
        self.session.add(match)
        match = self.skos_manager.get_match('urn:test', 'narrowMatch', 1)
        assert match.uri == 'urn:test'

    def test_get_all_label_types(self):
        res = self.skos_manager.get_all_label_types()
        assert len(res) == 4

    def test_get_next_cid_numeric(self):
        res = self.skos_manager.get_next_cid(1, IDGenerationStrategy.NUMERIC)
        assert isinstance(res, int)

    def test_get_next_cid_guid(self):
        res = self.skos_manager.get_next_cid(1, IDGenerationStrategy.GUID)
        assert isinstance(res, str)
        char = "[0-9a-fA-F]"
        assert re.search(
            fr"^{char}{{8}}\b-{char}{{4}}\b-{char}{{4}}\b-{char}{{4}}\b-{char}{{12}}$",
            res,
        )

    def test_get_next_cid_manual(self):
        with pytest.raises(ValueError):
            self.skos_manager.get_next_cid(1, IDGenerationStrategy.MANUAL)


class TestLanguagesManager:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.session = db_session
        self.language_manager = LanguagesManager(self.session)

    def test_get(self):
        res = self.language_manager.get('nl')
        assert res.name == 'Dutch'

    def test_save(self):
        language = Language('au', 'Austrian')
        language = self.language_manager.save(language)
        assert language.name == 'Austrian'

    def test_delete(self):
        language = self.language_manager.get('en')
        self.language_manager.delete(language)
        with pytest.raises(NoResultFound):
            self.language_manager.get('en')

    def test_get_all(self):
        res = self.language_manager.get_all()
        assert len(res) >= 3

    def test_get_all_sorted(self):
        result = self.language_manager.get_all_sorted('id', False)
        result_ids = [lang.id for lang in result]
        assert list(sorted(result_ids)) == result_ids

    def test_get_all_sorted_desc(self):
        result = self.language_manager.get_all_sorted('id', True)
        result_ids = [lang.id for lang in result]
        assert list(sorted(result_ids, reverse=True)) == result_ids

    def test_count_languages(self):
        res = self.language_manager.count_languages('nl')
        assert res == 1


class TestAuditManager:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.session = db_session
        self.audit_manager = AuditManager(self.session)

    @patch('atramhasis.data.datamanagers.date', Mock(today=Mock(return_value=date(2015, 8, 1))))
    def test_get_first_day(self):
        assert self.audit_manager._get_first_day('last_day') == '2015-07-31'
        assert self.audit_manager._get_first_day('last_week') == '2015-07-25'
        assert self.audit_manager._get_first_day('last_month') == '2015-07-01'
        assert self.audit_manager._get_first_day('last_year') == '2014-08-01'

    @patch('atramhasis.data.datamanagers.date', Mock(today=Mock(return_value=date(2015, 9, 15))))
    def test_get_most_popular_concepts_for_conceptscheme(self):
        self.session.add(
            ConceptVisitLog(concept_id='1', conceptscheme_id='1', origin='REST',
                            visited_at=datetime(2015, 8, 27, 10, 58, 3))
        )
        self.session.add(
            ConceptVisitLog(concept_id='1', conceptscheme_id='1', origin='REST',
                            visited_at=datetime(2015, 8, 27, 11, 58, 3))
        )
        self.session.add(
            ConceptVisitLog(concept_id='2', conceptscheme_id='1', origin='REST',
                            visited_at=datetime(2015, 8, 27, 10, 58, 3))
        )
        self.session.add(
            ConceptVisitLog(concept_id='2', conceptscheme_id='2', origin='REST',
                            visited_at=datetime(2015, 8, 27, 10, 58, 3))
        )

        manager = self.audit_manager
        result = manager.get_most_popular_concepts_for_conceptscheme(1, 5, 'last_month')
        expected = [
            {'concept_id': '1', 'scheme_id': 1}, {'concept_id': '2', 'scheme_id': 1}
        ]
        assert expected == result
        result = manager.get_most_popular_concepts_for_conceptscheme(2, 5, 'last_month')
        assert [{'concept_id': '2', 'scheme_id': 2}] == result
        result = manager.get_most_popular_concepts_for_conceptscheme(1, 1, 'last_month')
        assert [{'concept_id': '1', 'scheme_id': 1}] == result
        result = manager.get_most_popular_concepts_for_conceptscheme(1, 5, 'last_day')
        assert [] == result


class TestCountsManager:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.session = db_session
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
        assert res is not None
        assert res.triples == 3


class TestProviderDataManager:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.session = db_session
        self.manager = ProviderDataManager(self.session)

    def test_get_provider_by_id(self):
        provider = Provider(
            id='a', conceptscheme=ConceptScheme(), uri_pattern='u-p', meta={}
        )
        self.session.add(provider)
        self.session.flush()

        result = self.manager.get_provider_by_id(provider.id)
        assert result == provider

    def test_get_provider_by_id_no_result(self):
        with pytest.raises(NoResultFound):
            self.manager.get_provider_by_id('...')

    def test_get_all_providers(self):
        provider = Provider(
            id='a', conceptscheme=ConceptScheme(), uri_pattern='u-p', meta={}
        )
        self.session.add(provider)
        self.session.flush()

        result = self.manager.get_all_providers()
        assert result == [provider]


class TestGetHierarchyIdsQueryCount:
    """
    Tests that ``SkosManager.get_hierarchy_ids`` traverses the hierarchy
    in a constant number of SQL queries (via a recursive CTE), rather than
    issuing one query per node (N+1 problem).

    Uses the geography fixture (conceptscheme_id=2):

        World (1)
        +-- Europe (2)
        |   +-- Belgium (4)
        |   |   +-- Flanders (7)
        |   |   +-- Brussels (8)
        |   |   +-- Wallonie (9)
        |   +-- United Kingdom (5)
        +-- North-America (3)
            +-- USA (6)
        Collection 333: members [4, 7, 8]
    """

    @pytest.fixture(autouse=True)
    def setup(self, db_session, db_connection):
        self.session = db_session
        self.connection = db_connection
        self.skos_manager = SkosManager(self.session)
        self.query_log = []

    def _start_counting(self):
        """Start recording SQL statements executed on the connection."""
        self.query_log.clear()
        event.listen(self.connection, 'before_cursor_execute', self._log_query)

    def _stop_counting(self):
        """Stop recording and return the count."""
        event.remove(self.connection, 'before_cursor_execute', self._log_query)
        return len(self.query_log)

    def _log_query(self, conn, cursor, statement, parameters, context, executemany):
        self.query_log.append(statement)

    def test_narrower_concepts_query_count(self):
        """
        Traversing narrower_concepts from World should find all 8 descendants
        in a small, constant number of queries.
        """
        # Flush any pending lazy loads before counting.
        self.session.flush()

        self._start_counting()
        result = self.skos_manager.get_hierarchy_ids(
            conceptscheme_id=2,
            start_ids=['1'],
            concept_type='concept',
            property_list_name='narrower_concepts',
        )
        count = self._stop_counting()

        # Should find all descendants of World.
        expected_descendants = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
        assert result == expected_descendants

        # CTE approach: expect a small constant number of queries (typically
        # 2-3: one to resolve start_ids, one for the CTE, one to map back).
        # The old N+1 approach would issue 9+ queries (one per node).
        assert count <= 5, (
            f'Expected <= 5 queries but got {count}. Queries: {self.query_log}'
        )

    def test_broader_concepts_query_count(self):
        """
        Traversing broader_concepts from Flanders (7) should find Belgium (4),
        Europe (2), World (1) in a small number of queries.
        """
        self.session.flush()

        self._start_counting()
        result = self.skos_manager.get_hierarchy_ids(
            conceptscheme_id=2,
            start_ids=['7'],
            concept_type='concept',
            property_list_name='broader_concepts',
        )
        count = self._stop_counting()

        # Flanders -> Belgium -> Europe -> World.
        assert '4' in result
        assert '2' in result
        assert '1' in result

        assert count <= 5, (
            f'Expected <= 5 queries but got {count}. Queries: {self.query_log}'
        )

    def test_members_query_count(self):
        """
        Traversing members from collection 333 should find its members
        in a small number of queries.
        """
        self.session.flush()

        self._start_counting()
        result = self.skos_manager.get_hierarchy_ids(
            conceptscheme_id=2,
            start_ids=['333'],
            concept_type=None,
            property_list_name='members',
        )
        count = self._stop_counting()

        # Collection 333 has members: Belgium (4), Flanders (7), Brussels (8).
        assert '4' in result
        assert '7' in result
        assert '8' in result

        assert count <= 5, (
            f'Expected <= 5 queries but got {count}. Queries: {self.query_log}'
        )

    def test_empty_start_ids_no_queries(self):
        """
        Passing empty start_ids should return immediately with no DB queries.
        """
        self.session.flush()

        self._start_counting()
        result = self.skos_manager.get_hierarchy_ids(
            conceptscheme_id=2,
            start_ids=[],
            concept_type='concept',
            property_list_name='narrower_concepts',
        )
        count = self._stop_counting()

        assert result == set()
        assert count == 0, (
            f'Expected 0 queries for empty start_ids but got {count}'
        )

    def test_nonexistent_start_ids_minimal_queries(self):
        """
        Passing start_ids that don't exist should return empty after
        just the initial lookup query.
        """
        self.session.flush()

        self._start_counting()
        result = self.skos_manager.get_hierarchy_ids(
            conceptscheme_id=2,
            start_ids=['99999'],
            concept_type='concept',
            property_list_name='narrower_concepts',
        )
        count = self._stop_counting()

        assert result == set()
        assert count <= 1, (
            f'Expected <= 1 query for nonexistent IDs but got {count}'
        )
