# -*- coding: utf-8 -*-
import os
import unittest
from pyramid.paster import get_appsettings
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import transaction
from zope.sqlalchemy import ZopeTransactionExtension
from skosprovider_sqlalchemy.models import Base, ConceptScheme, LabelType, Language, MatchType, Concept, NoteType, Match
from atramhasis.data.models import Base as VisitLogBase
from atramhasis.data.datamanagers import ConceptSchemeManager, SkosManager, LanguagesManager, AuditManager
from fixtures.materials import materials
from fixtures.data import trees, geo
try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch
from datetime import date, datetime
from atramhasis.data.models import ConceptVisitLog

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class DatamangersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.session_maker = sessionmaker(
            bind=cls.engine,
            extension=ZopeTransactionExtension()
        )

    def setUp(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        VisitLogBase.metadata.drop_all(self.engine)
        VisitLogBase.metadata.create_all(self.engine)
        VisitLogBase.metadata.bind = self.engine

        with transaction.manager:
            local_session = self.session_maker()
            local_session.add(Language('nl', 'Dutch'))
            local_session.add(Language('nl-BE', 'Dutch'))
            local_session.add(Language('en', 'English'))

            import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), local_session)
            import_provider(materials, ConceptScheme(id=4, uri='urn:x-vioe:materials'), local_session)
            import_provider(geo, ConceptScheme(id=2, uri='urn:x-vioe:geo'), local_session)
            local_session.add(ConceptScheme(id=3, uri='urn:x-vioe:test'))
            local_session.add(LabelType('hiddenLabel', 'A hidden label.'))
            local_session.add(LabelType('altLabel', 'An alternative label.'))
            local_session.add(LabelType('prefLabel', 'A preferred label.'))

            local_session.add(MatchType('broadMatch', ''))
            local_session.add(MatchType('closeMatch', ''))
            local_session.add(MatchType('exactMatch', ''))
            local_session.add(MatchType('narrowMatch', ''))
            local_session.add(MatchType('relatedMatch', ''))

            local_session.flush()

            match = Match()
            match.matchtype_id = 'narrowMatch'
            match.uri = 'urn:test'
            match.concept_id = 1
            local_session.add(match)

            local_session.add(ConceptVisitLog(concept_id=1, conceptscheme_id=1, origin='REST',
                                              visited_at=datetime(2015, 8, 27, 10, 58, 3)))
            local_session.add(ConceptVisitLog(concept_id=1, conceptscheme_id=1, origin='REST',
                                              visited_at=datetime(2015, 8, 27, 11, 58, 3)))
            local_session.add(ConceptVisitLog(concept_id=2, conceptscheme_id=1, origin='REST',
                                              visited_at=datetime(2015, 8, 27, 10, 58, 3)))
            local_session.add(ConceptVisitLog(concept_id=2, conceptscheme_id=2, origin='REST',
                                              visited_at=datetime(2015, 8, 27, 10, 58, 3)))


class ConceptSchemeManagerTest(DatamangersTests):

    def setUp(self):
        super(ConceptSchemeManagerTest, self).setUp()
        self.conceptscheme_manager = ConceptSchemeManager(self.session_maker())

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
        local_session = self.session_maker()
        conceptscheme = local_session.query(ConceptScheme).filter(Concept.id == 1).first()
        conceptscheme = self.conceptscheme_manager.save(conceptscheme)
        self.assertIsNotNone(conceptscheme.id)
        local_session.close()


class SkosManagerTest(DatamangersTests):

    def setUp(self):
        super(SkosManagerTest, self).setUp()
        self.skos_manager = SkosManager(self.session_maker())

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
        self.assertEqual(3, len(res))

    def test_get_match_type(self):
        matchType= self.skos_manager.get_match_type('narrowMatch')
        self.assertEqual('narrowMatch', matchType.name)

    def test_get_match(self):
        match = self.skos_manager.get_match('urn:test', 'narrowMatch', 1)
        self.assertEqual('urn:test', match.uri)

    def test_get_all_label_types(self):
        res = self.skos_manager.get_all_label_types()
        self.assertEqual(3, len(res))

    def test_get_next_cid(self):
        res = self.skos_manager.get_next_cid(1)
        self.assertIsNotNone(res)


class LanguagesManagerTest(DatamangersTests):

    def setUp(self):
        super(LanguagesManagerTest, self).setUp()
        self.language_manager = LanguagesManager(self.session_maker())

    def test_get(self):
        res = self.language_manager.get('nl')
        self.assertEqual('Dutch', res.name)

    def test_save(self):
        language = Language('de', 'German')
        language = self.language_manager.save(language)
        self.assertEqual('German', language.name)

    def test_delete(self):
        language = self.language_manager.get('en')
        self.language_manager.delete(language)
        self.assertRaises(NoResultFound, self.language_manager.get, 'en')

    def test_get_all(self):
        res = self.language_manager.get_all()
        self.assertGreaterEqual(len(res), 3)

    def test_get_all_sorted(self):
        res = self.language_manager.get_all_sorted('id', False)
        self.assertEqual('en', res[0].id)

    def test_get_all_sorted_desc(self):
        res = self.language_manager.get_all_sorted('id', True)
        self.assertEqual('nl-BE', res[0].id)

    def test_count_languages(self):
        res = self.language_manager.count_languages('nl')
        self.assertEqual(1, res)


class AuditManagerTest(DatamangersTests):

    def setUp(self):
        super(AuditManagerTest, self).setUp()
        self.audit_manager = AuditManager(self.session_maker())

    @patch('atramhasis.data.datamanagers.date', Mock(today=Mock(return_value=date(2015, 8, 1))))
    def test_get_first_day(self):
        self.assertEqual('2015-07-31', self.audit_manager._get_first_day('last_day'))
        self.assertEqual('2015-07-25', self.audit_manager._get_first_day('last_week'))
        self.assertEqual('2015-07-01', self.audit_manager._get_first_day('last_month'))
        self.assertEqual('2014-08-01', self.audit_manager._get_first_day('last_year'))

    @patch('atramhasis.data.datamanagers.date', Mock(today=Mock(return_value=date(2015, 9, 15))))
    def test_get_most_popular_concepts_for_conceptscheme(self):
        self.assertListEqual([{'concept_id': 1, 'scheme_id': 1}, {'concept_id': 2, 'scheme_id': 1}],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(1, 5, 'last_month'))
        self.assertListEqual([{'concept_id': 2, 'scheme_id': 2}],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(2, 5, 'last_month'))
        self.assertListEqual([{'concept_id': 1, 'scheme_id': 1}],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(1, 1, 'last_month'))
        self.assertListEqual([],
                             self.audit_manager.get_most_popular_concepts_for_conceptscheme(1, 5, 'last_day'))
