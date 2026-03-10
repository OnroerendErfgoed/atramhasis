import os
import sys
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from rdflib import Graph
from rdflib import RDF
from rdflib import SKOS
from rdflib.term import URIRef

from atramhasis.scripts import dump_rdf


def _create_mock_provider(pid, subject=None, uri='urn:x-test:scheme'):
    """Create a mock skos provider with a simple RDF graph."""
    if subject is None:
        subject = []
    provider = MagicMock()
    provider.get_metadata.return_value = {'id': pid, 'subject': subject}

    concept_scheme = MagicMock()
    concept_scheme.uri = uri
    provider.concept_scheme = concept_scheme
    return provider


def _create_simple_graph(scheme_uri='urn:x-test:scheme'):
    """Create a simple RDF graph with a conceptscheme and concept."""
    graph = Graph()
    cs = URIRef(scheme_uri)
    concept = URIRef(f'{scheme_uri}/1')
    graph.add((cs, RDF.type, SKOS.ConceptScheme))
    graph.add((cs, SKOS.prefLabel, URIRef(f'{scheme_uri}/label')))
    graph.add((concept, RDF.type, SKOS.Concept))
    graph.add((concept, SKOS.inScheme, cs))
    graph.add((concept, SKOS.prefLabel, URIRef(f'{scheme_uri}/concept-label')))
    return graph


class TestDumpRdfMain:
    @patch('atramhasis.scripts.dump_rdf.utils.rdf_dumper')
    @patch('atramhasis.scripts.dump_rdf.setup_logging')
    @patch('atramhasis.scripts.dump_rdf.bootstrap')
    def test_dump_creates_files(self, mock_bootstrap, mock_logging, mock_dumper, db_session):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_registry = MagicMock()
            mock_registry.settings = {
                'atramhasis.dump_location': tmpdir,
            }
            provider = _create_mock_provider('TESTTREES', uri='urn:x-test:trees')
            mock_skos_registry = MagicMock()
            mock_skos_registry.get_providers.return_value = [provider]
            mock_request = MagicMock()
            mock_request.skos_registry = mock_skos_registry
            mock_dbmaker = MagicMock(return_value=db_session)
            mock_registry.dbmaker = mock_dbmaker

            mock_bootstrap.return_value = {
                'registry': mock_registry,
                'request': mock_request,
                'closer': MagicMock(),
            }
            mock_dumper.return_value = _create_simple_graph('urn:x-test:trees')

            with patch.object(sys, 'argv', ['dump_rdf', 'test.ini']):
                dump_rdf.main()

            ttl_file = os.path.join(tmpdir, 'TESTTREES-full.ttl')
            rdf_file = os.path.join(tmpdir, 'TESTTREES-full.rdf')
            assert os.path.isfile(ttl_file)
            assert os.path.isfile(rdf_file)

    @patch('atramhasis.scripts.dump_rdf.utils.rdf_dumper')
    @patch('atramhasis.scripts.dump_rdf.setup_logging')
    @patch('atramhasis.scripts.dump_rdf.bootstrap')
    def test_external_providers_skipped(
            self, mock_bootstrap, mock_logging, mock_dumper, db_session
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_registry = MagicMock()
            mock_registry.settings = {
                'atramhasis.dump_location': tmpdir,
            }
            external_provider = _create_mock_provider(
                'EXT', subject=['external'], uri='urn:x-test:ext'
            )
            mock_skos_registry = MagicMock()
            mock_skos_registry.get_providers.return_value = [external_provider]
            mock_request = MagicMock()
            mock_request.skos_registry = mock_skos_registry
            mock_dbmaker = MagicMock(return_value=db_session)
            mock_registry.dbmaker = mock_dbmaker

            mock_bootstrap.return_value = {
                'registry': mock_registry,
                'request': mock_request,
                'closer': MagicMock(),
            }

            with patch.object(sys, 'argv', ['dump_rdf', 'test.ini']):
                dump_rdf.main()

            mock_dumper.assert_not_called()
            files = [f for f in os.listdir(tmpdir) if f.endswith(('.ttl', '.rdf'))]
            assert len(files) == 0

    def test_no_args_returns_2(self, db_session):
        with patch.object(sys, 'argv', ['dump_rdf']):
            result = dump_rdf.main()
        assert result == 2

    @patch('atramhasis.scripts.dump_rdf.setup_logging')
    @patch('atramhasis.scripts.dump_rdf.bootstrap')
    def test_non_writable_location_returns_2(self, mock_bootstrap, mock_logging, db_session):
        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': '/nonexistent/path',
        }
        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': MagicMock(),
            'closer': MagicMock(),
        }

        with patch.object(sys, 'argv', ['dump_rdf', 'test.ini']):
            result = dump_rdf.main()
        assert result == 2
