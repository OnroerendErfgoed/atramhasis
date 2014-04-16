from pyramid.view import view_config
from pyramid.response import Response
from pyramid_skosprovider import ISkosRegistry

err_msg = """
No SKOS registry found, please check your application setup
"""

@view_config(route_name='home', renderer='templates/atramhasis.jinja2')
def my_view(request):
    skos_registry = request.registry.queryUtility(ISkosRegistry)
    if skos_registry is not None:
        conceptschemes = [x.get_metadata() for x in skos_registry.get_providers()]
        return {'project': 'atramhasis', 'conceptschemes': conceptschemes}
    else:
        return Response(err_msg, content_type='text/plain', status_int=500)