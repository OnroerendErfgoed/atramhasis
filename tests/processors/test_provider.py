from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from skosprovider.registry import Registry
from skosprovider_getty.providers import GettyProvider

from atramhasis.errors import ValidationError
from atramhasis.json_processors import provider


def test_create_provider_with_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id='1')
        data = {}
        response = provider.create_provider(data, session, MagicMock())

    mapper.assert_called()
    session.add.assert_called()
    assert response.id != str(response.conceptscheme.id)


def test_create_provider_no_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id=None)
        data = {}
        response = provider.create_provider(data, session, MagicMock())

    mapper.assert_called()
    session.add.assert_called()
    assert response.id == str(response.conceptscheme.id)


def test_create_provider_duplicate_uri():
    session = Mock()
    registry = Registry()
    registry.register_provider(GettyProvider({}))
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id=None)
        data = {"conceptscheme_uri": 'http://vocab.getty.edu/aat/'}
        with pytest.raises(ValidationError) as e:
            provider.create_provider(data, session, registry)
        assert e.value.value == 'Provider could not be validated.'
        assert e.value.errors == [
            {"conceptscheme_uri": "Collides with existing provider."}
        ]


def test_update_provider_with_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper,\
        patch('atramhasis.json_processors.provider.validate_provider_json') as validator:
        mapper.return_value = Mock(id='1')
        data = {}
        provider.update_provider('1', data, session)

    mapper.assert_called()
    validator.assert_called()


def test_delete_provider_with_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper, \
        patch.object(provider, 'delete_scheme'):
        mapper.return_value = Mock(id='1')
        provider.delete_provider('1', session)

    session.delete.assert_called()
