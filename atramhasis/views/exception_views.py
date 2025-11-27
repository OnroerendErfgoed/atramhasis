"""
Module containing error views.
"""

import logging
import sys

from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from pyramid_openapi3 import RequestValidationError
from pyramid_openapi3 import ResponseValidationError
from pyramid_openapi3 import extract_errors
from pyramid_openapi3 import openapi_validation_error
from skosprovider.exceptions import ProviderUnavailableException
from sqlalchemy.exc import IntegrityError

from atramhasis.errors import SkosRegistryNotFoundException
from atramhasis.errors import ValidationError
from atramhasis.protected_resources import ProtectedResourceException


log = logging.getLogger(__name__)


@notfound_view_config(accept='application/json', renderer='json')
@notfound_view_config(accept='text/html', renderer='notfound.jinja2')
def failed_not_found(exc, request):
    """
    View invoked when a resource could not be found.
    """
    log.debug(exc.explanation)
    request.response.status_int = 404
    return {'message': exc.explanation}


@view_config(
    accept='application/json', context=SkosRegistryNotFoundException, renderer='json'
)
@view_config(
    accept='text/html',
    context=SkosRegistryNotFoundException,
    renderer='notfound.jinja2',
)
def failed_skos(exc, request):
    """
    View invoked when Atramhasis can't find a SKOS registry.
    """
    log.error(exc.value, exc_info=sys.exc_info())
    request.response.status_int = 404
    return {'message': exc.value}


@view_config(accept='application/json', context=ValidationError, renderer='json')
def failed_validation(exc, request):
    """
    View invoked when bad data was submitted to Atramhasis.
    """
    log.debug(f"'message': {exc.value}, 'errors': {exc.errors}")
    request.response.status_int = 400
    return {'message': exc.value, 'errors': exc.errors}


@view_config(
    accept='application/json', context=ProtectedResourceException, renderer='json'
)
def protected(exc, request):
    """
    when a protected operation is called on a resource that is still referenced
    """
    log.warning(f"'message': {exc.value}, 'referenced_in': {exc.referenced_in}")
    request.response.status_int = 409
    return {'message': exc.value, 'referenced_in': exc.referenced_in}


@view_config(
    accept='application/json', context=ProviderUnavailableException, renderer='json'
)
def provider_unavailable(exc, request):
    """
    View invoked when ProviderUnavailableException was raised.
    """
    log.error(exc, exc_info=sys.exc_info())
    request.response.status_int = 503
    return {'message': exc.message}


@view_config(accept='application/json', context=IntegrityError, renderer='json')
def data_integrity(exc, request):
    """
    View invoked when IntegrityError was raised.
    """
    log.warning(exc)
    request.response.status_int = 409
    return {
        'message': 'this operation violates the data integrity and could not be executed'
    }


@view_config(accept='application/json', context=Exception, renderer='json')
@view_config(accept='text/html', context=Exception, renderer='error.jinja2')
def failed(exc, request):  # pragma no cover
    """
    View invoked when bad data was submitted to Atramhasis.
    """
    log.error(exc, exc_info=sys.exc_info())
    request.response.status_int = 500
    return {'message': 'unexpected server error'}


@view_config(accept='application/json', context=HTTPMethodNotAllowed, renderer='json')
def failed_method_not_allowed(exc, request):  # pragma no cover
    """
    View invoked when a method is not allowed.
    """
    log.debug(exc.explanation)
    request.response.status_int = 405
    return {'message': exc.explanation}


@view_config(accept='application/json', context=RequestValidationError, renderer='json')
@view_config(
    accept='application/json', context=ResponseValidationError, renderer='json'
)
def failed_openapi_validation(exc, request):
    try:
        errors = [
            f'{error.get("field")}: {error["message"]}'
            for error in list(extract_errors(request, exc.errors))
        ]
        request.response.status_int = 400
        if isinstance(exc, RequestValidationError):
            subject = 'Request'
        else:
            subject = 'Response'
        return {'message': f'{subject} was not valid for schema.', 'errors': errors}
    except Exception as e:
        log.exception('Issue with exception handling.')
        return openapi_validation_error(exc, request)
