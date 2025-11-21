import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from mock import MagicMock
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
        db_session_context_manager = MagicMock()
        db_session_context_manager().__enter__.return_value = self.session
        self.patcher = patch.object(
            import_file, 'db_session', db_session_context_manager
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def _check_trees(self, conceptscheme_label):
        sql_prov = SQLAlchemyProvider(
            {'id': 'TREES', 'conceptscheme_id': 1}, self.session
        )
        dump = dict_dumper(sql_prov)

        self.assertEqual(conceptscheme_label, sql_prov.concept_scheme.label('en').label)
        obj_1 = [item for item in dump if item['uri'] == 'http://id.trees.org/2'][0]
        self.assertEqual(obj_1['broader'], [])
        self.assertEqual(obj_1['id'], '2')
        self.assertEqual(obj_1['member_of'], ['3'])
        self.assertEqual(obj_1['narrower'], [])
        label_en = [label for label in obj_1['labels'] if label['language'] == 'en'][0]
        self.assertDictEqual(
            label_en, {'label': 'The Chestnut', 'language': 'en', 'type': 'prefLabel'}
        )
        label_nl = [label for label in obj_1['labels'] if label['language'] == 'nl'][0]
        self.assertDictEqual(
            label_nl,
            {'label': 'De Paardekastanje', 'language': 'nl', 'type': 'altLabel'},
        )
        label_fr = [label for label in obj_1['labels'] if label['language'] == 'fr'][0]
        self.assertDictEqual(
            label_fr, {'label': 'la châtaigne', 'language': 'fr', 'type': 'altLabel'}
        )
        self.assertDictEqual(
            obj_1['notes'][0],
            {
                'language': 'en',
                'note': 'A different type of tree.',
                'type': 'definition',
                'markup': None,
            },
        )

    def _check_menu(self, uri_pattern=None):
        if not uri_pattern:
            uri_pattern = 'urn:x-skosprovider:menu:%s'
        sql_prov = SQLAlchemyProvider(
            {'id': 'MENU', 'conceptscheme_id': 1}, self.session
        )
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

    def _check_parrots(self):
        sql_prov = SQLAlchemyProvider(
            {'id': 'PARROTS', 'conceptscheme_id': 1}, self.session
        )

        bird = sql_prov.get_by_id('https://id.parrots.org/bird')
        assert sql_prov.get_by_uri('https://id.parrots.org/bird') == bird
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
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_trees('Verschillende soorten bomen')

    def test_import_ttl(self):
        sys.argv = [
            'import_file',
            test_data_ttl,
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_trees('Different types of trees')

    def test_import_ttl_string_id(self):
        sys.argv = [
            'import_file',
            test_data_ttl_string_id,
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        tests.db_filled = True

    def test_import_json(self):
        sys.argv = [
            'import_file',
            test_data_json,
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
            '--conceptscheme-label',
            'Trees Conceptscheme',
            '--conceptscheme-uri',
            'http://id.trees.org',
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_trees('Trees Conceptscheme')

    def test_import_csv(self):
        sys.argv = [
            'import_file',
            test_data_csv,
            '--uri-pattern',
            'urn:x-skosprovider:menu:%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_menu()

    def test_import_csv_uri_generator(self):
        sys.argv = [
            'import_file',
            test_data_csv,
            '--uri-pattern',
            'https://id.menu.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
            '--conceptscheme-label',
            'Menu Conceptscheme',
            '--conceptscheme-uri',
            'https://id.menu.org',
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        self._check_menu('https://id.menu.org/%s')

    def test_import_csv_with_provider_all_args(self):
        sys.argv = [
            'import_file',
            test_data_csv,
            '--uri-pattern',
            'urn:x-skosprovider:test:%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
            '--provider-id',
            'MENU',
            '--create-provider',
            '--id-generation-strategy',
            'guid',
        ]
        import_file.main(sys.argv)
        tests.db_filled = True
        provider = self.session.execute(select(Provider)).scalar_one()
        self.assertEqual(provider.meta['atramhasis.id_generation_strategy'], 'GUID')
        self.assertEqual(provider.uri_pattern, 'urn:x-skosprovider:test:%s')
        self.assertEqual(provider.expand_strategy.value, 'recurse')
        self.assertEqual(provider.id, 'MENU')


class ValidateUriPatternTests(unittest.TestCase):
    """Test cases for the validate_uri_pattern function"""

    def test_validate_uri_pattern_valid(self):
        """Test that a valid URI pattern passes validation"""
        # This should not raise SystemExit
        try:
            import_file.validate_uri_pattern('https://example.org/%s')
        except SystemExit:
            self.fail(
                'validate_uri_pattern() raised SystemExit unexpectedly for valid pattern'
            )

    def test_validate_uri_pattern_none(self):
        """Test that None URI pattern raises SystemExit"""
        with self.assertRaises(SystemExit) as cm:
            import_file.validate_uri_pattern(None)  # type: ignore
        self.assertEqual(cm.exception.code, 1)

    def test_validate_uri_pattern_empty_string(self):
        """Test that empty string URI pattern raises SystemExit"""
        with self.assertRaises(SystemExit) as cm:
            import_file.validate_uri_pattern('')
        self.assertEqual(cm.exception.code, 1)

    def test_validate_uri_pattern_no_placeholder(self):
        """Test that URI pattern without %s placeholder raises SystemExit"""
        with self.assertRaises(SystemExit) as cm:
            import_file.validate_uri_pattern('https://example.org/concept')
        self.assertEqual(cm.exception.code, 1)

    def test_validate_uri_pattern_multiple_placeholders(self):
        """Test that URI pattern with multiple %s placeholders raises SystemExit"""
        with self.assertRaises(SystemExit) as cm:
            import_file.validate_uri_pattern('https://example.org/%s/concept/%s')
        self.assertEqual(cm.exception.code, 1)

    def test_validate_uri_pattern_valid_complex(self):
        """Test that a more complex valid URI pattern passes validation"""
        try:
            import_file.validate_uri_pattern('urn:x-skosprovider:trees:%s')
        except SystemExit:
            self.fail(
                'validate_uri_pattern() raised SystemExit unexpectedly for valid complex pattern'
            )

    def test_validate_uri_pattern_valid_with_numbers(self):
        """Test that URI pattern with numbers but single %s passes validation"""
        try:
            import_file.validate_uri_pattern('https://example.org/v1/concepts/%s')
        except SystemExit:
            self.fail(
                'validate_uri_pattern() raised SystemExit unexpectedly for valid pattern with numbers'
            )


class ValidateConnectionStringTests(unittest.TestCase):
    """Test cases for the validate_connection_string function"""

    def test_validate_connection_string_sqlite_exists(self):
        """Test that SQLite connection string with existing file returns True"""
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            connection_string = f'sqlite:///{temp_path}'
            result = import_file.validate_connection_string(connection_string)
            self.assertTrue(result)
        finally:
            os.unlink(temp_path)

    def test_validate_connection_string_sqlite_does_not_exist(self):
        """Test that SQLite connection string with non-existing file returns False"""
        non_existent_path = '/path/that/does/not/exist/test.sqlite'
        connection_string = f'sqlite:///{non_existent_path}'

        result = import_file.validate_connection_string(connection_string)
        self.assertFalse(result)

    def test_validate_connection_string_postgresql_valid(self):
        """Test that valid PostgreSQL connection string returns True"""
        connection_string = 'postgresql://user:pass@localhost:5432/testdb'
        result = import_file.validate_connection_string(connection_string)
        self.assertTrue(result)

    def test_validate_connection_string_postgresql_invalid(self):
        """Test that invalid PostgreSQL connection string returns False"""
        connection_string = 'postgresql://incomplete'
        result = import_file.validate_connection_string(connection_string)
        self.assertFalse(result)

    def test_validate_connection_string_unsupported_driver(self):
        """Test that unsupported database driver returns False"""
        connection_string = 'mysql://user:pass@localhost:3306/testdb'
        result = import_file.validate_connection_string(connection_string)
        self.assertFalse(result)

    def test_validate_connection_string_invalid_format(self):
        """Test that completely invalid connection string raises ArgumentError"""
        connection_string = 'not-a-valid-connection-string'
        with self.assertRaises(
            Exception
        ):  # SQLAlchemy raises ArgumentError which inherits from Exception
            import_file.validate_connection_string(connection_string)


class ParseArgvForImportTests(unittest.TestCase):
    """Test cases for the parse_argv_for_import function"""

    def setUp(self):
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(b'id,label\n1,test\n')
            self.temp_input_file = temp_file.name

        # Create a temporary SQLite database for testing
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_db:
            self.temp_db_file = temp_db.name

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.temp_input_file):
            os.unlink(self.temp_input_file)
        if os.path.exists(self.temp_db_file):
            os.unlink(self.temp_db_file)

    def test_parse_argv_create_provider_false_with_conflicting_args(self):
        """Test that --no-create-provider with conflicting args prints error and exits"""
        argv = [
            'import_file',
            self.temp_input_file,
            '--no-create-provider',
            '--uri-pattern',
            'https://example.org/%s',
            '--to',
            f'sqlite:///{self.temp_db_file}',
        ]

        # Mock sys.argv to control argparse
        with patch('sys.argv', argv):
            with (
                self.assertRaises(SystemExit) as cm,
                patch('builtins.print') as mock_print,
            ):
                import_file.parse_argv_for_import(argv)

            # Check that our custom error message was printed
            mock_print.assert_called_with(
                '--uri-pattern, --provider-id and --id-generation-strategy can only be '
                'used when --create-provider is set to True'
            )
            # The exit code should be 1 (our custom error)
            self.assertEqual(cm.exception.code, 1)
