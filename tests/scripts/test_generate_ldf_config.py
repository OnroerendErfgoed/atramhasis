import json
import os
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

from atramhasis.scripts import generate_ldf_config


class _MockLabel:
    def __init__(self, label):
        self.label = label


class _MockConceptScheme:
    def __init__(self, uri, label_text=None, notes=None):
        self.uri = uri
        self._label = _MockLabel(label_text) if label_text else None
        self.notes = notes or []

    def label(self):
        return self._label


class _MockProvider:
    def __init__(self, pid, subject=None, label_text=None, notes=None):
        self._metadata = {'id': pid, 'subject': subject or []}
        self.concept_scheme = _MockConceptScheme(
            f'urn:x-test:{pid}', label_text, notes
        )

    def get_metadata(self):
        return self._metadata


def test_no_args_returns_2():
    import sys
    with patch.object(sys, 'argv', ['generate_ldf_config']):
        result = generate_ldf_config.main()
    assert result == 2


@patch('atramhasis.scripts.generate_ldf_config.setup_logging')
@patch('atramhasis.scripts.generate_ldf_config.bootstrap')
def test_generates_config_file(mock_bootstrap, mock_logging):
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': tmpdir,
        }
        provider = _MockProvider('TREES', label_text='Trees')
        mock_skos_registry = MagicMock()
        mock_skos_registry.get_providers.return_value = [provider]
        mock_request = MagicMock()
        mock_request.skos_registry = mock_skos_registry

        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': mock_request,
            'closer': MagicMock(),
        }

        import sys
        with patch.object(
            sys, 'argv', ['generate_ldf_config', 'test.ini', '-l', tmpdir]
        ):
            generate_ldf_config.main()

        config_path = os.path.join(tmpdir, 'ldf_server_config.json')
        assert os.path.isfile(config_path)
        with open(config_path) as f:
            config = json.load(f)
        assert config['title'] == 'Atramhasis LDF server'
        assert len(config['datasources']) == 2  # provider + composite
        assert config['datasources'][0]['datasourceTitle'] == 'Trees'
        assert config['datasources'][1]['@type'] == 'CompositeDatasource'


@patch('atramhasis.scripts.generate_ldf_config.setup_logging')
@patch('atramhasis.scripts.generate_ldf_config.bootstrap')
def test_external_providers_excluded(mock_bootstrap, mock_logging):
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': tmpdir,
        }
        external = _MockProvider('EXT', subject=['external'])
        mock_skos_registry = MagicMock()
        mock_skos_registry.get_providers.return_value = [external]
        mock_request = MagicMock()
        mock_request.skos_registry = mock_skos_registry

        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': mock_request,
            'closer': MagicMock(),
        }

        import sys
        with patch.object(
            sys, 'argv', ['generate_ldf_config', 'test.ini', '-l', tmpdir]
        ):
            generate_ldf_config.main()

        config_path = os.path.join(tmpdir, 'ldf_server_config.json')
        with open(config_path) as f:
            config = json.load(f)
        assert len(config['datasources']) == 0


@patch('atramhasis.scripts.generate_ldf_config.setup_logging')
@patch('atramhasis.scripts.generate_ldf_config.bootstrap')
def test_hdt_file_preferred_over_ttl(mock_bootstrap, mock_logging):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an HDT file so the config uses HdtDatasource
        hdt_path = os.path.join(tmpdir, 'TREES-full.hdt')
        with open(hdt_path, 'w') as f:
            f.write('dummy')

        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': tmpdir,
        }
        provider = _MockProvider('TREES', label_text='Trees')
        mock_skos_registry = MagicMock()
        mock_skos_registry.get_providers.return_value = [provider]
        mock_request = MagicMock()
        mock_request.skos_registry = mock_skos_registry

        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': mock_request,
            'closer': MagicMock(),
        }

        import sys
        with patch.object(
            sys, 'argv', ['generate_ldf_config', 'test.ini', '-l', tmpdir]
        ):
            generate_ldf_config.main()

        config_path = os.path.join(tmpdir, 'ldf_server_config.json')
        with open(config_path) as f:
            config = json.load(f)
        ds = config['datasources'][0]
        assert ds['@type'] == 'HdtDatasource'
        assert 'hdtFile' in ds


@patch('atramhasis.scripts.generate_ldf_config.setup_logging')
@patch('atramhasis.scripts.generate_ldf_config.bootstrap')
def test_ttl_fallback_when_no_hdt(mock_bootstrap, mock_logging):
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': tmpdir,
        }
        provider = _MockProvider('TREES', label_text='Trees')
        mock_skos_registry = MagicMock()
        mock_skos_registry.get_providers.return_value = [provider]
        mock_request = MagicMock()
        mock_request.skos_registry = mock_skos_registry

        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': mock_request,
            'closer': MagicMock(),
        }

        import sys
        with patch.object(
            sys, 'argv', ['generate_ldf_config', 'test.ini', '-l', tmpdir]
        ):
            generate_ldf_config.main()

        config_path = os.path.join(tmpdir, 'ldf_server_config.json')
        with open(config_path) as f:
            config = json.load(f)
        ds = config['datasources'][0]
        assert ds['@type'] == 'TurtleDatasource'
        assert 'file' in ds


@patch('atramhasis.scripts.generate_ldf_config.setup_logging')
@patch('atramhasis.scripts.generate_ldf_config.bootstrap')
def test_baseurl_and_protocol(mock_bootstrap, mock_logging):
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': tmpdir,
            'atramhasis.ldf.baseurl': 'http://ldf.example.com',
            'atramhasis.ldf.protocol': 'https',
        }
        mock_skos_registry = MagicMock()
        mock_skos_registry.get_providers.return_value = []
        mock_request = MagicMock()
        mock_request.skos_registry = mock_skos_registry

        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': mock_request,
            'closer': MagicMock(),
        }

        import sys
        with patch.object(
            sys, 'argv', ['generate_ldf_config', 'test.ini', '-l', tmpdir]
        ):
            generate_ldf_config.main()

        config_path = os.path.join(tmpdir, 'ldf_server_config.json')
        with open(config_path) as f:
            config = json.load(f)
        assert config['baseURL'] == 'http://ldf.example.com'
        assert config['protocol'] == 'https'


@patch('atramhasis.scripts.generate_ldf_config.setup_logging')
@patch('atramhasis.scripts.generate_ldf_config.bootstrap')
def test_provider_with_no_label(mock_bootstrap, mock_logging):
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_registry = MagicMock()
        mock_registry.settings = {
            'atramhasis.dump_location': tmpdir,
        }
        # Provider without a label - should fall back to pid
        provider = _MockProvider('NOLABEL')
        mock_skos_registry = MagicMock()
        mock_skos_registry.get_providers.return_value = [provider]
        mock_request = MagicMock()
        mock_request.skos_registry = mock_skos_registry

        mock_bootstrap.return_value = {
            'registry': mock_registry,
            'request': mock_request,
            'closer': MagicMock(),
        }

        import sys
        with patch.object(
            sys, 'argv', ['generate_ldf_config', 'test.ini', '-l', tmpdir]
        ):
            generate_ldf_config.main()

        config_path = os.path.join(tmpdir, 'ldf_server_config.json')
        with open(config_path) as f:
            config = json.load(f)
        assert config['datasources'][0]['datasourceTitle'] == 'NOLABEL'
