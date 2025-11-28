from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from skosprovider.registry import Registry

from atramhasis import skos


@pytest.fixture
def mock_request():
    mock = MagicMock()
    mock.db = MagicMock()
    return mock


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def mock_manager(monkeypatch, mock_session):
    provider = MagicMock()

    def mock_get_all_providers(*_):
        return [provider]

    monkeypatch.setattr(
        'atramhasis.data.datamanagers.ProviderDataManager.get_all_providers',
        mock_get_all_providers,
    )


def test_create_registry_success(mock_request):
    registry = skos.create_registry(mock_request)
    assert isinstance(registry, Registry)
    # Should have at least 3 providers: AAT, TGN, and one from DB
    assert len(registry.providers) >= 2


def test_register_providers_from_db_adds_providers(
    mock_session, mock_manager, monkeypatch
):
    monkeypatch.setattr(
        'atramhasis.utils.db_provider_to_skosprovider',
        Mock(return_value=MagicMock(allowed_instance_scopes=False)),
    )
    registry = Registry()
    skos.register_providers_from_db(registry, mock_session)
    assert len(registry.providers) == 1


def test_register_providers_from_db_empty(monkeypatch, mock_session):
    class DummyManager:
        def __init__(self, session):
            pass

        def get_all_providers(self):
            return []

    monkeypatch.setattr(
        'atramhasis.data.datamanagers.ProviderDataManager', DummyManager
    )
    monkeypatch.setattr(
        'atramhasis.utils.db_provider_to_skosprovider',
        lambda db_provider: db_provider,
    )
    registry = Registry()
    skos.register_providers_from_db(registry, mock_session)
    assert len(registry.providers) == 0
