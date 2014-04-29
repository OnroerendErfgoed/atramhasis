from pyramid.view import view_config, notfound_view_config

from atramhasis.errors import SkosRegistryNotFoundException, InvalidJsonException, ValidationError


@notfound_view_config(renderer='json')
def failed_not_found(exc, request):
    request.response.status_int = 404
    return {'message': exc.value}


@view_config(context=SkosRegistryNotFoundException, renderer='json')
def failed_skos(exc, request):
    request.response.status_int = 500
    return {'message': exc.value}


@view_config(context=InvalidJsonException, renderer='json')
def failed_json(exc, request):
    request.response.status_int = 400
    return {'message': exc.value}


@view_config(context=ValidationError, renderer='json')
def failed_validation(exc, request):
    request.response.status_int = 400
    return {'message': exc.value, 'errors': exc.errors}