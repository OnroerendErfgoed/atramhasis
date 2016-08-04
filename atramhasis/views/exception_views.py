# -*- coding: utf-8 -*-
"""
Module containing error views.
"""

import logging

from pyramid.view import view_config, notfound_view_config
from sqlalchemy.exc import IntegrityError
import sys

from atramhasis.errors import SkosRegistryNotFoundException, ValidationError
from atramhasis.protected_resources import ProtectedResourceException
from skosprovider.exceptions import ProviderUnavailableException
from pyramid.httpexceptions import HTTPMethodNotAllowed

log = logging.getLogger(__name__)


@notfound_view_config(renderer='json')
def failed_not_found(exc, request):
    """
    View invoked when a resource could not be found.
    """
    log.debug(exc.explanation)
    request.response.status_int = 404
    return {'message': exc.explanation}


@view_config(context=SkosRegistryNotFoundException, renderer='json')
def failed_skos(exc, request):
    """
    View invoked when Atramhasis can't find a SKOS registry.
    """
    log.error(exc.value, exc_info=sys.exc_info())
    request.response.status_int = 500
    return {'message': exc.value}


@view_config(context=ValidationError, renderer='json')
def failed_validation(exc, request):
    """
    View invoked when bad data was submitted to Atramhasis.
    """
    log.debug("'message': {0}, 'errors': {1}".format(exc.value, exc.errors))
    request.response.status_int = 400
    return {'message': exc.value, 'errors': exc.errors}


@view_config(context=ProtectedResourceException, renderer='json')
def protected(exc, request):
    """
    when a protected operation is called on a resource that is still referenced
    """
    log.warn("'message': {0}, 'referenced_in': {1}".format(exc.value, exc.referenced_in))
    request.response.status_int = 409
    return {'message': exc.value, 'referenced_in': exc.referenced_in}


@view_config(context=ProviderUnavailableException, renderer='json')
def provider_unavailable(exc, request):
    """
    View invoked when ProviderUnavailableException was raised.
    """
    log.error(exc, exc_info=sys.exc_info())
    request.response.status_int = 503
    return {'message': exc.message}


@view_config(context=IntegrityError, renderer='json')
def data_integrity(exc, request):
    """
    View invoked when IntegrityError was raised.
    """
    log.warn(exc)
    request.response.status_int = 409
    return {'message': 'this operation violates the data integrity and could not be executed '}


@view_config(context=Exception, renderer='json')
def failed(exc, request):  # pragma no cover
    """
    View invoked when bad data was submitted to Atramhasis.
    """
    log.error(exc, exc_info=sys.exc_info())
    request.response.status_int = 500
    return {'message': 'unexpected server error'}


@view_config(context=HTTPMethodNotAllowed, renderer='json')
def failed_not_method_not_allowed(exc, request):
    """
    View invoked when a method is not allowed.
    """
    log.debug(exc.explanation)
    request.response.status_int = 405
    return {'message': exc.explanation}
