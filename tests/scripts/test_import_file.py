import json
import os
import tempfile

from skosprovider.providers import DictionaryProvider
from skosprovider.providers import SimpleCsvProvider
from skosprovider_rdf.providers import RDFProvider
from skosprovider_sqlalchemy.models import ConceptScheme
from sqlalchemy import select

import tests
from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import Provider
from atramhasis.scripts import import_file


def setUpModule():
    tests.setup_db(guarantee_empty=True)


class TestValidateFile(tests.DbTest):
    def test_valid_json_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'[]')
            f.flush()
            self.assertTrue(import_file.validate_file(f.name))
        os.unlink(f.name)

    def test_valid_csv_file(self):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            f.write(b'id,label\n1,test')
            f.flush()
            self.assertTrue(import_file.validate_file(f.name))
        os.unlink(f.name)

    def test_file_does_not_exist(self):
        self.assertFalse(import_file.validate_file('/nonexistent/file.json'))

    def test_unsupported_extension(self):
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b'test')
            f.flush()
            self.assertFalse(import_file.validate_file(f.name))
        os.unlink(f.name)


class TestValidateConnectionString(tests.DbTest):
    def test_valid_sqlite(self):
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            pass
        self.assertTrue(import_file.validate_connection_string(f'sqlite:///{f.name}'))
        os.unlink(f.name)

    def test_sqlite_not_exists(self):
        self.assertFalse(
            import_file.validate_connection_string('sqlite:///nonexistent.sqlite')
        )

    def test_valid_postgresql(self):
        self.assertTrue(
            import_file.validate_connection_string(
                'postgresql://user:pass@localhost:5432/mydb'
            )
        )

    def test_invalid_postgresql(self):
        self.assertFalse(
            import_file.validate_connection_string('postgresql://user@localhost/mydb')
        )

    def test_unsupported_driver(self):
        self.assertFalse(
            import_file.validate_connection_string('mysql://user:pass@localhost/mydb')
        )


class TestCreateConceptscheme(tests.DbTest):
    def test_create_conceptscheme(self):
        cs = import_file.create_conceptscheme('urn:test', 'Test Label')
        self.assertEqual(cs.uri, 'urn:test')
        self.assertEqual(cs.labels[0].label, 'Test Label')


class TestFileToJsonProvider(tests.DbTest):
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
        self.assertIsInstance(provider, DictionaryProvider)
        self.assertEqual(provider.get_vocabulary_id(), 'TEST')
        self.assertEqual(len(provider.get_all()), 1)
        os.unlink(f.name)


class TestFileToCsvProvider(tests.DbTest):
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
        self.assertIsInstance(provider, SimpleCsvProvider)
        self.assertEqual(provider.get_vocabulary_id(), 'CSVTEST')
        os.unlink(f.name)


class TestFileToRdfProvider(tests.DbTest):
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
        self.assertIsInstance(provider, RDFProvider)
        self.assertEqual(provider.get_vocabulary_id(), 'RDFTEST')
        os.unlink(f.name)


class TestCreateProvider(tests.DbTest):
    def test_create_provider(self):
        from skosprovider.uri import UriPatternGenerator

        cs = ConceptScheme(uri='urn:x-test:create-provider')
        self.session.add(cs)
        self.session.flush()

        provider = DictionaryProvider(
            {'id': 'CREATETEST', 'subject': []},
            [],
            uri_generator=UriPatternGenerator('urn:x-test:%s'),
        )
        import_file.create_provider(
            id_generation_strategy='NUMERIC',
            provider=provider,
            session=self.session,
            conceptscheme=cs,
        )
        self.session.flush()

        db_provider = self.session.execute(
            select(Provider).filter(Provider.id == 'CREATETEST')
        ).scalar_one()
        self.assertEqual(db_provider.conceptscheme_id, cs.id)
        self.assertEqual(db_provider.expand_strategy, ExpandStrategy.RECURSE)
        self.assertEqual(db_provider.uri_pattern, 'urn:x-test:%s')


class TestValidateUriPattern(tests.DbTest):
    def test_valid_pattern(self):
        # Should not exit
        import_file.validate_uri_pattern('urn:x-test:%s')

    def test_no_pattern(self):
        with self.assertRaises(SystemExit):
            import_file.validate_uri_pattern(None)

    def test_no_placeholder(self):
        with self.assertRaises(SystemExit):
            import_file.validate_uri_pattern('urn:x-test:nope')

    def test_multiple_placeholders(self):
        with self.assertRaises(SystemExit):
            import_file.validate_uri_pattern('urn:x-test:%s/%s')
