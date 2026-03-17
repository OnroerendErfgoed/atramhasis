from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from pyramid.testing import DummyRequest

from atramhasis.views.health import _check_db
from atramhasis.views.health import _is_maintenance_mode
from atramhasis.views.health import health
from atramhasis.views.health import live
from atramhasis.views.health import ready


@pytest.fixture
def request_factory():
    """Create a DummyRequest with configurable settings."""

    def _factory(settings=None):
        request = DummyRequest()
        request.registry.settings = settings or {}
        return request

    return _factory


class TestLive:
    def test_live_returns_alive(self, request_factory):
        request = request_factory()
        result = live(request)
        assert result == {'status': 'alive'}

    def test_live_returns_200(self, request_factory):
        request = request_factory()
        live(request)
        assert request.response.status_int == 200


class TestReady:
    def test_ready_when_healthy(self, request_factory):
        request = request_factory()
        request.db = MagicMock()
        result = ready(request)
        assert result == {'status': 'ready', 'checks': {'database': True}}
        assert request.response.status_int == 200

    def test_ready_when_db_down(self, request_factory):
        request = request_factory()
        request.db = MagicMock()
        request.db.execute.side_effect = Exception('connection refused')
        result = ready(request)
        assert result == {'status': 'unready', 'checks': {'database': False}}
        assert request.response.status_int == 503

    def test_ready_when_maintenance(self, tmp_path, request_factory):
        maintenance_file = tmp_path / 'maintenance.txt'
        maintenance_file.write_text('maintenance')
        request = request_factory(
            settings={'atramhasis.maintenance_file': str(maintenance_file)}
        )
        result = ready(request)
        assert result == {'status': 'maintenance', 'checks': {}}
        assert request.response.status_int == 503

    def test_ready_when_maintenance_file_absent(self, request_factory):
        request = request_factory(
            settings={'atramhasis.maintenance_file': '/nonexistent/maintenance.txt'}
        )
        request.db = MagicMock()
        result = ready(request)
        assert result['status'] == 'ready'
        assert request.response.status_int == 200


class TestHealth:
    @patch('atramhasis.views.health.version', return_value='3.1.1')
    def test_health_when_healthy(self, mock_version, request_factory):
        request = request_factory()
        request.db = MagicMock()
        result = health(request)
        assert result == {
            'status': 'ok',
            'version': '3.1.1',
            'checks': {'database': True},
        }
        assert request.response.status_int == 200

    @patch('atramhasis.views.health.version', return_value='3.1.1')
    def test_health_when_db_down(self, mock_version, request_factory):
        request = request_factory()
        request.db = MagicMock()
        request.db.execute.side_effect = Exception('connection refused')
        result = health(request)
        assert result == {
            'status': 'unhealthy',
            'version': '3.1.1',
            'checks': {'database': False},
        }
        assert request.response.status_int == 503

    @patch('atramhasis.views.health.version', return_value='3.1.1')
    def test_health_when_maintenance(self, mock_version, tmp_path, request_factory):
        maintenance_file = tmp_path / 'maintenance.txt'
        maintenance_file.write_text('maintenance')
        request = request_factory(
            settings={'atramhasis.maintenance_file': str(maintenance_file)}
        )
        result = health(request)
        assert result == {
            'status': 'maintenance',
            'version': '3.1.1',
            'checks': {},
        }
        assert request.response.status_int == 503


class TestIsMaintenanceMode:
    def test_no_setting(self, request_factory):
        request = request_factory()
        assert _is_maintenance_mode(request) is False

    def test_empty_setting(self, request_factory):
        request = request_factory(settings={'atramhasis.maintenance_file': ''})
        assert _is_maintenance_mode(request) is False

    def test_file_exists(self, tmp_path, request_factory):
        maintenance_file = tmp_path / 'maintenance.txt'
        maintenance_file.write_text('down for maintenance')
        request = request_factory(
            settings={'atramhasis.maintenance_file': str(maintenance_file)}
        )
        assert _is_maintenance_mode(request) is True

    def test_file_does_not_exist(self, request_factory):
        request = request_factory(
            settings={'atramhasis.maintenance_file': '/nonexistent/file'}
        )
        assert _is_maintenance_mode(request) is False


class TestCheckDb:
    def test_db_ok(self, request_factory):
        request = request_factory()
        request.db = MagicMock()
        assert _check_db(request) is True

    def test_db_failure(self, request_factory):
        request = request_factory()
        request.db = MagicMock()
        request.db.execute.side_effect = Exception('boom')
        assert _check_db(request) is False
