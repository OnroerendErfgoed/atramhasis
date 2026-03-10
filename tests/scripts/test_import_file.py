import json
import os
import tempfile

import pytest
from skosprovider.providers import DictionaryProvider
from skosprovider.providers import SimpleCsvProvider
from skosprovider.uri import UriPatternGenerator
from skosprovider_rdf.providers import RDFProvider
from skosprovider_sqlalchemy.models import ConceptScheme
from sqlalchemy import select

from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import Provider
from atramhasis.scripts import import_file

pytestmark = pytest.mark.empty_db


class TestValidateFile:
    def test_valid_json_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'[]')
            f.flush()
            assert import_file.validate_file(f.name)
        os.unlink(f.name)

    def test_valid_csv_file(self):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            f.write(b'id,label\n1,test')
            f.flush()
            assert import_file.validate_file(f.name)
        os.unlink(f.name)

    def test_file_does_not_exist(self):
        assert not import_file.validate_file('/nonexistent/file.json')

    def test_unsupported_extension(self):
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b'test')
            f.flush()
            assert not import_file.validate_file(f.name)
        os.unlink(f.name)


class TestValidateConnectionString:
    def test_valid_sqlite(self):
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            pass
        assert import_file.validate_connection_string(f'sqlite:///{f.name}')
        os.unlink(f.name)

    def test_sqlite_not_exists(self):
        assert not import_file.validate_connection_string('sqlite:///nonexistent.sqlite')

    def test_valid_postgresql(self):
        assert import_file.validate_connection_string(
            'postgresql://user:pass@localhost:5432/mydb'
        )

    def test_invalid_postgresql(self):
        assert not import_file.validate_connection_string('postgresql://user@localhost/mydb')

    def test_unsupported_driver(self):
        assert not import_file.validate_connection_string('mysql://user:pass@localhost/mydb')


class TestCreateConceptscheme:
    def test_create_conceptscheme(self):
        cs = import_file.create_conceptscheme('urn:test', 'Test Label')
        assert cs.uri == 'urn:test'
        assert cs.labels[0].label == 'Test Label'


class TestFileToJsonProvider:
    def test_file_to_json_provider(self):
        data = [
            {
                'id': '1',
                'uri': 'urn:x-test:1',
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Test'}
                ],
            }
        ]
        with tempfile.NamedTemporaryFile(
                suffix='.json', mode='w', delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            provider = import_file.file_to_json_provider(
                input_file=f.name, provider_id='TEST'
            )
        assert isinstance(provider, DictionaryProvider)
        assert provider.get_vocabulary_id() == 'TEST'
        assert len(provider.get_all()) == 1
        os.unlink(f.name)


class TestFileToCsvProvider:
    def test_file_to_csv_provider(self):
        with tempfile.NamedTemporaryFile(
                suffix='.csv', mode='w', delete=False
        ) as f:
            f.write('id,prefLabel,note,source\n')
            f.write('1,Test,,\n')
            f.flush()
            provider = import_file.file_to_csv_provider(
                input_file=f.name, provider_id='CSVTEST'
            )
        assert isinstance(provider, SimpleCsvProvider)
        assert provider.get_vocabulary_id() == 'CSVTEST'
        os.unlink(f.name)


class TestFileToRdfProvider:
    def test_file_to_rdf_provider(self):
        rdf_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:ConceptScheme rdf:about="urn:x-test:scheme">
    <skos:prefLabel xml:lang="en">Test Scheme</skos:prefLabel>
  </skos:ConceptScheme>
  <skos:Concept rdf:about="urn:x-test:1">
    <skos:inScheme rdf:resource="urn:x-test:scheme"/>
    <skos:prefLabel xml:lang="en">Test Concept</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>"""
        with tempfile.NamedTemporaryFile(
                suffix='.rdf', mode='w', delete=False
        ) as f:
            f.write(rdf_content)
            f.flush()
            provider = import_file.file_to_rdf_provider(
                input_file=f.name, provider_id='RDFTEST'
            )
        assert isinstance(provider, RDFProvider)
        assert provider.get_vocabulary_id() == 'RDFTEST'
        os.unlink(f.name)


class TestCreateProvider:
    def test_create_provider(self, db_session):
        cs = ConceptScheme(uri='urn:x-test:create-provider')
        db_session.add(cs)
        db_session.flush()

        provider = DictionaryProvider(
            {'id': 'CREATETEST', 'subject': []},
            [],
            uri_generator=UriPatternGenerator('urn:x-test:%s'),
        )
        import_file.create_provider(
            id_generation_strategy='NUMERIC',
            provider=provider,
            session=db_session,
            conceptscheme=cs,
        )
        db_session.flush()

        db_provider = db_session.execute(
            select(Provider).filter(Provider.id == 'CREATETEST')
        ).scalar_one()
        assert db_provider.conceptscheme_id == cs.id
        assert db_provider.expand_strategy == ExpandStrategy.RECURSE
        assert db_provider.uri_pattern == 'urn:x-test:%s'


class TestValidateUriPattern:
    def test_valid_pattern(self):
        # Should not exit
        import_file.validate_uri_pattern('urn:x-test:%s')

    def test_no_pattern(self):
        with pytest.raises(SystemExit):
            import_file.validate_uri_pattern(None)

    def test_no_placeholder(self):
        with pytest.raises(SystemExit):
            import_file.validate_uri_pattern('urn:x-test:nope')

    def test_multiple_placeholders(self):
        with pytest.raises(SystemExit):
            import_file.validate_uri_pattern('urn:x-test:%s/%s')
