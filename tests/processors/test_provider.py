from unittest.mock import Mock
from unittest.mock import patch

from atramhasis.json_processors import provider


def test_create_provider_with_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id='1')
        data = {}
        response = provider.create_provider(data, session)

    mapper.assert_called()
    session.add.assert_called()
    assert response.id != str(response.conceptscheme.id)


def test_create_provider_no_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id=None)
        data = {}
        response = provider.create_provider(data, session)

    mapper.assert_called()
    session.add.assert_called()
    assert response.id == str(response.conceptscheme.id)


def test_update_provider_with_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id='1')
        data = {}
        provider.update_provider('1', data, session)

    mapper.assert_called()


def test_delete_provider_with_id():
    session = Mock()
    with patch.object(provider.mappers, 'map_provider') as mapper:
        mapper.return_value = Mock(id='1')
        provider.delete_provider('1', session)

    session.delete.assert_called()
