# -*- coding: utf-8 -*-
'''
Module containing error views.
'''

from pyramid.view import view_config, notfound_view_config

from atramhasis.errors import SkosRegistryNotFoundException, ValidationError


@notfound_view_config(renderer='json')
def failed_not_found(exc, request):
    '''
    View invoked when a resource could not be found.
    '''
    request.response.status_int = 404
    return {'message': exc.explanation}


@view_config(context=SkosRegistryNotFoundException, renderer='json')
def failed_skos(exc, request):
    '''
    View invoked when Atramhasis can't find a SKOS registry.
    '''
    request.response.status_int = 500
    return {'message': exc.value}


@view_config(context=ValidationError, renderer='json')
def failed_validation(exc, request):
    '''
    View invoked when bad data was submitted to Atramhasis.
    '''
    request.response.status_int = 400
    return {'message': exc.value, 'errors': exc.errors}
