# -*- coding: utf-8 -*-
'''
Module containing error views.
'''

import logging

from pyramid.view import view_config, notfound_view_config
from sqlalchemy.exc import IntegrityError

from atramhasis.errors import SkosRegistryNotFoundException, ValidationError
from atramhasis.protected_resources import ProtectedResourceException
from skosprovider.exceptions import ProviderUnavailableException

log = logging.getLogger(__name__)


@notfound_view_config(renderer='json')
def failed_not_found(exc, request):
    '''
    View invoked when a resource could not be found.
    '''
    log.error(exc.explanation)
    request.response.status_int = 404
    return {'message': exc.explanation}


@view_config(context=SkosRegistryNotFoundException, renderer='json')
def failed_skos(exc, request):
    '''
    View invoked when Atramhasis can't find a SKOS registry.
    '''
    log.error(exc.value)
    request.response.status_int = 500
    return {'message': exc.value}


@view_config(context=ValidationError, renderer='json')
def failed_validation(exc, request):
    '''
    View invoked when bad data was submitted to Atramhasis.
    '''
    log.error(exc.value)
    log.error(exc.errors)
    request.response.status_int = 400
    return {'message': exc.value, 'errors': exc.errors}


@view_config(context=ProtectedResourceException, renderer='json')
def protected(exc, request):
    '''
    when a protected operation is called on a resource that is still referenced
    '''
    log.warn(exc.value)
    log.warn(exc.referenced_in)
    request.response.status_int = 409
    return {'message': exc.value, 'referenced_in': exc.referenced_in}


@view_config(context=ProviderUnavailableException, renderer='json')
def provider_unavailable(exc, request):
    '''
    View invoked when ProviderUnavailableException was raised.
    '''
    log.error(exc)
    log.error(exc.message)
    request.response.status_int = 503
    return {'message': exc.message}


@view_config(context=IntegrityError, renderer='json')
def data_integrity(exc, request):
    '''
    View invoked when IntegrityError was raised.
    '''
    log.error(exc)
    request.response.status_int = 409
    return {'message': 'this operation violates the data integrity and could not be executed '}


@view_config(context=Exception, renderer='json')
def failed(exc, request):
    '''
    View invoked when bad data was submitted to Atramhasis.
    '''
    log.error(exc)
    request.response.status_int = 500
    return {'message': 'unexpected server error'}

