from pyramid.view import view_config
from pyramid.response import Response

err_msg = """
No SKOS registry found, please check your application setup
"""


@view_config(route_name='home', renderer='templates/atramhasis.jinja2')
def home_view(request):
    '''
    This view displays the homepage.

    :param request: A :class:`pyramid.request.Request`
    '''
    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        conceptschemes = [x.get_metadata() for x in request.skos_registry.get_providers()]
        return {'project': 'atramhasis', 'conceptschemes': conceptschemes}
    else:
        return Response(err_msg, content_type='text/plain', status_int=500)


@view_config(route_name='concept', renderer='templates/concept.jinja2')
def concept_view(request):
    '''
    This view displays the concept details

    :param request: A :class:`pyramid.request.Request`
    '''
    scheme_id = request.matchdict['scheme_id']
    c_id = request.matchdict['c_id']
    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        prov = request.skos_registry.get_provider(scheme_id)
        if prov:
            concept = prov.get_by_id(c_id)
            if concept:
                return {'concept': concept}
        return {'concept': None}
    else:
        return Response(err_msg, content_type='text/plain', status_int=500)