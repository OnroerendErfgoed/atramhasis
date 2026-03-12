import os
import sys
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from skosprovider.skos import Concept
from skosprovider.skos import Note
from skosprovider.utils import dict_dumper
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy import select

from atramhasis.data.models import Provider
from atramhasis.scripts import import_file
from tests import SETTINGS
from tests import TEST_DIR

test_data_rdf = os.path.join(TEST_DIR, 'data', 'trees.rdf')
test_data_ttl = os.path.join(TEST_DIR, 'data', 'trees.ttl')
test_data_ttl_string_id = os.path.join(TEST_DIR, 'data', 'bluebirds.ttl')
test_data_json = os.path.join(TEST_DIR, 'data', 'trees.json')
test_data_csv = os.path.join(TEST_DIR, 'data', 'menu.csv')

pytestmark = pytest.mark.usefixtures("module_db_setup")


def check_trees(session, conceptscheme_label):
    sql_prov = SQLAlchemyProvider(
        {'id': 'TREES', 'conceptscheme_id': 1}, session
    )
    dump = dict_dumper(sql_prov)

    assert sql_prov.concept_scheme.label('en').label == conceptscheme_label
    obj_1 = [item for item in dump if item['uri'] == 'http://id.trees.org/2'][0]
    assert obj_1['broader'] == []
    assert obj_1['id'] == '2'
    assert obj_1['member_of'] == ['3']
    assert obj_1['narrower'] == []
    label_en = [label for label in obj_1['labels'] if label['language'] == 'en'][0]
    assert label_en == {'label': 'The Chestnut', 'language': 'en', 'type': 'prefLabel'}
    label_nl = [label for label in obj_1['labels'] if label['language'] == 'nl'][0]
    assert label_nl == {
        'label': 'De Paardekastanje', 'language': 'nl', 'type': 'altLabel'
    }
    label_fr = [label for label in obj_1['labels'] if label['language'] == 'fr'][0]
    assert label_fr == {
        'label': 'la châtaigne', 'language': 'fr', 'type': 'altLabel'
    }
    assert obj_1['notes'][0] == {
        'language': 'en',
        'note': 'A different type of tree.',
        'type': 'definition',
        'markup': None,
    }


def check_menu(session, uri_pattern=None):
    if not uri_pattern:
        uri_pattern = 'urn:x-skosprovider:menu:%s'
    sql_prov = SQLAlchemyProvider(
        {'id': 'MENU', 'conceptscheme_id': 1}, session
    )
    assert len(sql_prov.get_all()) == 11
    eb = sql_prov.get_by_id(1)
    assert isinstance(eb, Concept)
    assert eb.id == '1'
    assert eb.uri == uri_pattern % '1'
    assert eb.label().label == 'Egg and Bacon'
    assert eb.label().type == 'prefLabel'
    assert eb.notes == []
    eb = sql_prov.get_by_uri(uri_pattern % '3')
    assert isinstance(eb, Concept)
    assert eb.id == '3'
    assert eb.uri == uri_pattern % '3'
    spam = sql_prov.find({'label': 'Spam'})
    assert len(spam) == 8
    eb = sql_prov.get_by_id(11)
    assert isinstance(eb, Concept)
    assert eb.id == '11'
    assert eb.label().label == 'Lobster Thermidor'
    assert isinstance(eb.notes[0], Note)
    assert 'Mornay' in eb.notes[0].note
    assert eb.notes[0].type == 'note'
    provider = session.execute(select(Provider)).scalar_one()
    assert provider.meta['atramhasis.id_generation_strategy'] == 'NUMERIC'
    assert provider.uri_pattern == uri_pattern
    assert provider.expand_strategy.value == 'recurse'
    assert provider.id == str(provider.conceptscheme_id)


def check_parrots(session):
    sql_prov = SQLAlchemyProvider(
        {'id': 'PARROTS', 'conceptscheme_id': 1}, session
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


@pytest.fixture()
def patched_session(db_session):
    """Patch import_file.db_session to use the test's db_session."""
    db_session_context_manager = MagicMock()
    db_session_context_manager().__enter__.return_value = db_session
    with patch.object(import_file, 'db_session', db_session_context_manager):
        yield db_session


class TestImport:
    def test_import_rdf(self, patched_session):
        sys.argv = [
            'import_file',
            test_data_rdf,
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        check_trees(patched_session, 'Verschillende soorten bomen')

    def test_import_ttl(self, patched_session):
        sys.argv = [
            'import_file',
            test_data_ttl,
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        check_trees(patched_session, 'Different types of trees')

    def test_import_ttl_string_id(self, patched_session):
        sys.argv = [
            'import_file',
            test_data_ttl_string_id,
            '--uri-pattern',
            'http://id.trees.org/%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)

    def test_import_json(self, patched_session):
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
        check_trees(patched_session, 'Trees Conceptscheme')

    def test_import_csv(self, patched_session):
        sys.argv = [
            'import_file',
            test_data_csv,
            '--uri-pattern',
            'urn:x-skosprovider:menu:%s',
            '--to',
            SETTINGS['sqlalchemy.url'],
        ]
        import_file.main(sys.argv)
        check_menu(patched_session)

    def test_import_csv_uri_generator(self, patched_session):
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
        check_menu(patched_session, 'https://id.menu.org/%s')

    def test_import_csv_with_provider_all_args(self, patched_session):
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
        provider = patched_session.execute(select(Provider)).scalar_one()
        assert provider.meta['atramhasis.id_generation_strategy'] == 'GUID'
        assert provider.uri_pattern == 'urn:x-skosprovider:test:%s'
        assert provider.expand_strategy.value == 'recurse'
        assert provider.id == 'MENU'


class TestValidateUriPattern:
    """Test cases for the validate_uri_pattern function"""

    def test_validate_uri_pattern_valid(self):
        """Test that a valid URI pattern passes validation"""
        # This should not raise SystemExit
        try:
            import_file.validate_uri_pattern('https://example.org/%s')
        except SystemExit:
            pytest.fail(
                'validate_uri_pattern() raised SystemExit unexpectedly for valid pattern'
            )

    def test_validate_uri_pattern_none(self):
        """Test that None URI pattern raises SystemExit"""
        with pytest.raises(SystemExit) as cm:
            import_file.validate_uri_pattern(None)  # type: ignore
        assert cm.value.code == 1

    def test_validate_uri_pattern_empty_string(self):
        """Test that empty string URI pattern raises SystemExit"""
        with pytest.raises(SystemExit) as cm:
            import_file.validate_uri_pattern('')
        assert cm.value.code == 1

    def test_validate_uri_pattern_no_placeholder(self):
        """Test that URI pattern without %s placeholder raises SystemExit"""
        with pytest.raises(SystemExit) as cm:
            import_file.validate_uri_pattern('https://example.org/concept')
        assert cm.value.code == 1

    def test_validate_uri_pattern_multiple_placeholders(self):
        """Test that URI pattern with multiple %s placeholders raises SystemExit"""
        with pytest.raises(SystemExit) as cm:
            import_file.validate_uri_pattern('https://example.org/%s/concept/%s')
        assert cm.value.code == 1

    def test_validate_uri_pattern_valid_complex(self):
        """Test that a more complex valid URI pattern passes validation"""
        try:
            import_file.validate_uri_pattern('urn:x-skosprovider:trees:%s')
        except SystemExit:
            pytest.fail(
                'validate_uri_pattern() raised SystemExit unexpectedly for valid complex pattern'
            )

    def test_validate_uri_pattern_valid_with_numbers(self):
        """Test that URI pattern with numbers but single %s passes validation"""
        try:
            import_file.validate_uri_pattern('https://example.org/v1/concepts/%s')
        except SystemExit:
            pytest.fail(
                'validate_uri_pattern() raised SystemExit unexpectedly for valid pattern with numbers'
            )


class TestValidateConnectionString:
    """Test cases for the validate_connection_string function"""

    def test_validate_connection_string_sqlite_exists(self):
        """Test that SQLite connection string with existing file returns True"""
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            connection_string = f'sqlite:///{temp_path}'
            result = import_file.validate_connection_string(connection_string)
            assert result
        finally:
            os.unlink(temp_path)

    def test_validate_connection_string_sqlite_does_not_exist(self):
        """Test that SQLite connection string with non-existing file returns False"""
        non_existent_path = '/path/that/does/not/exist/test.sqlite'
        connection_string = f'sqlite:///{non_existent_path}'

        result = import_file.validate_connection_string(connection_string)
        assert not result

    def test_validate_connection_string_postgresql_valid(self):
        """Test that valid PostgreSQL connection string returns True"""
        connection_string = 'postgresql://user:pass@localhost:5432/testdb'
        result = import_file.validate_connection_string(connection_string)
        assert result

    def test_validate_connection_string_postgresql_invalid(self):
        """Test that invalid PostgreSQL connection string returns False"""
        connection_string = 'postgresql://incomplete'
        result = import_file.validate_connection_string(connection_string)
        assert not result

    def test_validate_connection_string_unsupported_driver(self):
        """Test that unsupported database driver returns False"""
        connection_string = 'mysql://user:pass@localhost:3306/testdb'
        result = import_file.validate_connection_string(connection_string)
        assert not result

    def test_validate_connection_string_invalid_format(self):
        """Test that completely invalid connection string raises ArgumentError"""
        connection_string = 'not-a-valid-connection-string'
        with pytest.raises(
            Exception
        ):  # SQLAlchemy raises ArgumentError which inherits from Exception
            import_file.validate_connection_string(connection_string)


@pytest.fixture()
def temp_input_file():
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        f.write(b'id,label\n1,test\n')
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture()
def temp_db_file():
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


class TestParseArgvForImport:
    """Test cases for the parse_argv_for_import function"""

    def test_parse_argv_create_provider_false_with_conflicting_args(
        self, temp_input_file, temp_db_file
    ):
        """Test that --no-create-provider with conflicting args prints error and exits"""
        argv = [
            'import_file',
            temp_input_file,
            '--no-create-provider',
            '--uri-pattern',
            'https://example.org/%s',
            '--to',
            f'sqlite:///{temp_db_file}',
        ]

        # Mock sys.argv to control argparse
        with patch('sys.argv', argv):
            with (
                pytest.raises(SystemExit) as cm,
                patch('builtins.print') as mock_print,
            ):
                import_file.parse_argv_for_import(argv)

            # Check that our custom error message was printed
            mock_print.assert_called_with(
                '--uri-pattern, --provider-id and --id-generation-strategy can only be '
                'used when --create-provider is set to True'
            )
            # The exit code should be 1 (our custom error)
            assert cm.value.code == 1
