"""
Module containing health check views.

Provides three endpoints for monitoring and orchestration:

- ``/live``: Liveness probe, very cheap, only indicates the process is alive.
- ``/ready``: Readiness probe, checks dependencies required to serve traffic.
- ``/health``: Aggregate health endpoint for humans and dashboards.

.. versionadded:: 3.2.0
"""

import logging
import os
from importlib.metadata import version

from pyramid.view import view_config
from sqlalchemy import text

log = logging.getLogger(__name__)


def _is_maintenance_mode(request):
    """Check if a maintenance file exists on disk."""
    maintenance_file = request.registry.settings.get(
        'atramhasis.maintenance_file', ''
    )
    if maintenance_file and os.path.isfile(maintenance_file):
        return True
    return False


def _check_db(request):
    """Execute a lightweight query to verify database connectivity."""
    try:
        request.db.execute(text('SELECT 1'))
        return True
    except Exception:
        log.exception('Database health check failed.')
        return False


@view_config(route_name='atramhasis.live', renderer='json')
def live(request):
    """
    Liveness probe: very cheap, only indicates the process is alive.
    """
    return {'status': 'alive'}


@view_config(route_name='atramhasis.ready', renderer='json')
def ready(request):
    """
    Readiness probe: checks dependencies required to serve traffic.

    Returns 200 when all required checks pass, 503 otherwise.
    """
    if _is_maintenance_mode(request):
        request.response.status_int = 503
        return {'status': 'maintenance', 'checks': {}}

    db_ok = _check_db(request)
    if not db_ok:
        request.response.status_int = 503
        return {'status': 'unready', 'checks': {'database': db_ok}}

    return {'status': 'ready', 'checks': {'database': db_ok}}


@view_config(route_name='atramhasis.health', renderer='json')
def health(request):
    """
    Aggregate health endpoint for humans and dashboards.

    Includes version info and deeper checks.
    """
    maintenance = _is_maintenance_mode(request)

    if maintenance:
        request.response.status_int = 503
        return {
            'status': 'maintenance',
            'version': version('atramhasis'),
            'checks': {},
        }

    db_ok = _check_db(request)
    overall = 'ok' if db_ok else 'unhealthy'

    if not db_ok:
        request.response.status_int = 503

    return {
        'status': overall,
        'version': version('atramhasis'),
        'checks': {'database': db_ok},
    }
