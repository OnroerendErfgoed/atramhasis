import os
import sys
from unittest.mock import Mock
from unittest.mock import patch

from skosprovider.skos import Concept
from skosprovider.skos import Note
from skosprovider.utils import dict_dumper
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy import select

import tests
from atramhasis.data.models import Provider
from atramhasis.scripts import import_file
from tests import DbTest
from tests import SETTINGS
from tests import TEST_DIR
from tests import setup_db

test_data_rdf = os.path.join(TEST_DIR, 'data', 'trees.rdf')
test_data_ttl = os.path.join(TEST_DIR, 'data', 'trees.ttl')
test_data_ttl_string_id = os.path.join(TEST_DIR, 'data', 'bluebirds.ttl')
test_data_json = os.path.join(TEST_DIR, 'data', 'trees.json')
test_data_csv = os.path.join(TEST_DIR, 'data', 'menu.csv')


def setUpModule():
    setup_db(guarantee_empty=True)


class ImportTests(DbTest):

    def setUp(self):
        super().setUp()
        # Patch the session that scripts will use to the session of the tests.
        # This makes everything rollback after every test.
        self.patcher = patch.object(import_file, 'conn_str_to_session',
                                    Mock(return_value=self.session))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def _check_trees(self, conceptscheme_label):
        sql_prov = SQLAlchemyProvider({'id': 'TREES', 'conceptscheme_id': 1}, self.session)
        dump = dict_dumper(sql_prov)

        self.assertEqual(conceptscheme_label, sql_prov.concept_scheme.label('en').label)
        obj_1 = [item for item in dump if item['uri'] == 'http://id.trees.org/2'][0]
        self.assertEqual(obj_1['broader'], [])
        self.assertEqual(obj_1['id'], '2')
        self.assertEqual(obj_1['member_of'], ['3'])
        self.assertEqual(obj_1['narrower'], [])
        label_en = [label for label in obj_1['labels'] if label['language'] == 'en'][0]
        self.assertDictEqual(label_en, {'label': 'The Chestnut', 'language': 'en', 'type': 'prefLabel'})
        label_nl = [label for label in obj_1['labels'] if label['language'] == 'nl'][0]
        self.assertDictEqual(label_nl, {'label': 'De Paardekastanje', 'language': 'nl', 'type': 'altLabel'})
        label_fr = [label for label in obj_1['labels'] if label['language'] == 'fr'][0]
        self.assertDictEqual(label_fr, {'label': 'la châtaigne', 'language': 'fr', 'type': 'altLabel'})
        self.assertDictEqual(obj_1['notes'][0],
                             {'language': 'en', 'note': 'A different type of tree.', 'type': 'definition', 'markup': None})

    def _check_menu(self, uri_pattern=None):
        if not uri_pattern:
            uri_pattern = 'urn:x-skosprovider:menu:%s'
        sql_prov = SQLAlchemyProvider({'id': 'MENU', 'conceptscheme_id': 1}, self.session)
        self.assertEqual(11, len(sql_prov.get_all()))
        eb = sql_prov.get_by_id(1)
        self.assertIsInstance(eb, Concept)
        self.assertEqual('1', eb.id)
        self.assertEqual(uri_pattern % '1', eb.uri)
        self.assertEqual('Egg and Bacon', eb.label().label)
        self.assertEqual('prefLabel', eb.label().type)
        self.assertEqual([], eb.notes)
        eb = sql_prov.get_by_uri(uri_pattern % '3')
        self.assertIsInstance(eb, Concept)
        self.assertEqual('3', eb.id)
        self.assertEqual(uri_pattern % '3', eb.uri)
        spam = sql_prov.find({'label': 'Spam'})
        self.assertEqual(8, len(spam))
        eb = sql_prov.get_by_id(11)
        self.assertIsInstance(eb, Concept)
        self.assertEqual('11', eb.id)
        self.assertEqual('Lobster Thermidor', eb.label().label)
        self.assertIsInstance(eb.notes[0], Note)
        self.assertIn('Mornay', eb.notes[0].note)
        self.assertEqual('note', eb.notes[0].type)
        provider = self.session.execute(select(Provider)).scalar_one()
        self.assertEqual(provider.meta['atramhasis.id_generation_strategy'], 'NUMERIC')
        self.assertEqual(provider.uri_pattern, uri_pattern)
        self.assertEqual(provider.expand_strategy.value, 'recurse')
        self.assertEqual(provider.id, str(provider.conceptscheme_id))

    def _check_parrots(self, conceptscheme_label):
        sql_prov = SQLAlchemyProvider({'id': 'PARROTS', 'conceptscheme_id': 1}, self.session)

        bird = sql_prov.get_by_id('http://id.parrots.org/bird')
        assert sql_prov.get_by_uri('http://id.parrots.org/bird') == \
                sql_prov.get_by_id('http://id.parrots.org/bird')
        parrot = sql_prov.get_by_id('parrot')
        assert parrot 
        assert not sql_prov.get_by_id('bird')
        blue = sql_prov.get_by_id('norwegianblue')
        assert blue in parrot.narrower
        reiger = sql_prov.get_by_id('579A439C-1A7A-476A-92C3-8A74ABD6B3DB')
        blauwereiger = sql_prov.get_by_id('blauwereiger')
        assert blauwereiger in reiger.narrower

    def test_import_rdf(self):
        sys.argv = [
            'import_file',
            test_data_rdf,
            'http://id.trees.org/%s',
            '--to', SETTINGS['sqlalchemy.url']
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_trees('Verschillende soorten bomen')

    def test_import_ttl(self):
        sys.argv = [
            'import_file',
            test_data_ttl,
            'http://id.trees.org/%s',
            '--to', SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_trees('Different types of trees')

    def test_import_ttl_string_id(self):
        sys.argv = [
            'import_file',
            test_data_ttl_string_id,
            'http://id.trees.org/%s',
            '--to', SETTINGS['sqlalchemy.url']
        ]
        import_file.main(sys.argv)
        tests.db_filled = True

    def test_import_json(self):
        sys.argv = [
            'import_file',
            test_data_json,
            'http://id.trees.org/%s',
            '--to', SETTINGS['sqlalchemy.url'],
            '--conceptscheme-label', 'Trees Conceptscheme',
            '--conceptscheme-uri', 'http://id.trees.org',
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_trees('Trees Conceptscheme')

    def test_import_csv(self):
        sys.argv = [
            'import_file',
            test_data_csv,
            'urn:x-skosprovider:menu:%s',
            '--to', SETTINGS['sqlalchemy.url'
            ],
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_menu()

    def test_import_csv_uri_generator(self):
        sys.argv = [
            'import_file', test_data_csv, 'http://id.menu.org/%s',
            '--to', SETTINGS['sqlalchemy.url'],
            '--conceptscheme-label', 'Menu Conceptscheme',
            '--conceptscheme-uri', 'http://id.menu.org'
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_menu('http://id.menu.org/%s')

    def test_import_csv_with_provider_all_args(self):
        sys.argv = [
            'import_file',
            test_data_csv,
            'urn:x-skosprovider:test:%s',
            '--to', SETTINGS['sqlalchemy.url'],
            '--provider-id', 'MENU',
            '--create-provider',
            '--id-generation-strategy', 'guid',
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        provider = self.session.execute(select(Provider)).scalar_one()
        self.assertEqual(provider.meta['atramhasis.id_generation_strategy'], 'GUID')
        self.assertEqual(provider.uri_pattern, 'urn:x-skosprovider:test:%s')
        self.assertEqual(provider.expand_strategy.value, 'recurse')
        self.assertEqual(provider.id, 'MENU')
