from pyramid.response import Response
from pyramid.view import view_config
from atramhasis.errors import SkosRegistryNotFoundException, InvalidJsonException, ConceptSchemeNotFoundException, \
    ValidationError, ConceptNotFoundException


@view_config(context=SkosRegistryNotFoundException)
def failed_skos(exc, request):
    response = Response(exc.value)
    response.status_int = 500
    return response


@view_config(context=InvalidJsonException)
def failed_json(exc, request):
    response = Response(exc.value)
    response.status_int = 400
    return response


@view_config(context=ConceptSchemeNotFoundException)
def failed_conceptscheme(exc, request):
    response = Response(exc.value)
    response.status_int = 404
    return response


@view_config(context=ConceptNotFoundException)
def failed_conceptscheme(exc, request):
    response = Response(exc.value)
    response.status_int = 404
    return response


@view_config(context=ValidationError)
def failed_validation(exc, request):
    response = Response(exc.value + " " + exc.errors)
    response.status_int = 400
    return response
