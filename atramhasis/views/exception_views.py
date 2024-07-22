"""
Module containing error views.
"""

import logging
import sys

from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
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
    log.debug(f"'message': {exc.value}, 'errors': {exc.errors}")
    request.response.status_int = 400
    return {'message': exc.value, 'errors': exc.errors}


@view_config(context=ProtectedResourceException, renderer='json')
def protected(exc, request):
    """
    when a protected operation is called on a resource that is still referenced
    """
    log.warning(f"'message': {exc.value}, 'referenced_in': {exc.referenced_in}")
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
    log.warning(exc)
    request.response.status_int = 409
    return {
        'message': 'this operation violates the data integrity and could not be executed'
    }


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


@view_config(context=RequestValidationError, renderer="json")
@view_config(context=ResponseValidationError, renderer="json")
def failed_openapi_validation(exc, request):
    try:
        errors = [
            _handle_validation_error(validation_error)
            for error in exc.errors
            if isinstance(error, InvalidSchemaValue)
            for validation_error in error.schema_errors
        ]
        # noinspection PyTypeChecker
        errors.extend(
            [
                f'{error.get("field")}: {error.get("message")}'
                for error in
                list(extract_errors(request, exc.errors))
            ]
        )
        request.response.status_int = 400
        return {"message": "Request was not valid for schema.", "errors": errors}
    except Exception:
        log.exception("Issue with exception handling.")
        return openapi_validation_error(exc, request)


def _handle_validation_error(error, path=""):
    if error.validator in ("anyOf", "oneOf", "allOf"):
        for schema_type in ("anyOf", "oneOf", "allOf"):
            if schema_type not in error.schema:
                continue
            schemas = error.schema.get(schema_type)
            break
        else:
            return None

        response = []
        for i, schema in enumerate(schemas):
            schema.pop("x-scope", None)
            errors = [
                sub_error
                for sub_error in error.context
                if sub_error.relative_schema_path[0] == i
            ]
            if error.path:
                schema = {".".join(str(p) for p in error.path): schema}
            response.append(
                {
                    "schema": schema,
                    "errors": [_handle_validation_error(error) for error in errors],
                }
            )
        return {schema_type: response}
    if path:
        path += "."
    path += ".".join(str(item) for item in error.path)
    if not path:
        path = "<root>"
    return f"{path}: {error.message}"
